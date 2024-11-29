import sys
import weather as wt
import daytohour as dh
import leafnumber as leaf
import fraction as fr
import gasexchange as gas
import growth as gro
import disease as dl
import bolting as bolt

import pandas as pd
import numpy as np

class Facade(object):
    
    def __init__(self, dorh, fname_in, fname_out, start, end, density, latitude, lnratio):
    
        # assign initial values
        self.pltday = start                    
        self.plantDensity = density
        self.latitude = float(latitude)
        self.lnratio  = lnratio
        
        # initialize attributes:
        self.leafNumber = 0.0
        self.lai = 0.0
        self.assimSum = 0.001 * self.plantDensity  #변경self.assimSum = iniDW * self.plantDensity ##임의 0.001(자엽?본엽? 기준설정x)
        self.assim = 0.0  
        self.netTmm = 0.0
        self.lossPer = 0.0
        self.hourresult = None
        self.dayresult  = None
        self.fname_out = fname_out
        
        # create instances
        if dorh == 'd':
            dayData   = dh.DayToHour(fname_in, start, end, self.latitude)
            dayData.calcHour()
            wthr = dayData
        elif dorh == 'h':
            wthr = wt.Weather(fname_in, start, end)
        else:
            raise Exception("Error: Weather data type (d or h)")
            
           
        self.wthr     = wthr
        self.bolting  = bolt.BT() 
        self.leaf     = leaf.LeafNumber(self.plantDensity) #변경(self.initialLeafNumber 삭제) ##질문 (self.initialLeafNumber, self.plantDensity) 왜 들어가는지?
        self.frac     = fr.Fractionation(latitude = self.latitude)
        self.gasEx    = gas.GasExchange()
        self.growth   = gro.Growth()
        self.loss     = dl.Disease()
        

    def run(self):

        res = {'datetime':[],'LN': [], 'lai':[], 'netTmm':[], 'pltleafDW':[],'pltrootDW':[],
               'pltleafFW':[],'pltrootFW':[], 'lossPer': [], 'bolting':[]}

        ## hourly output *** the column headers in the output  file
        headers = ['datetime', 'LN', 'lai', 'netTmm', 'pltleafDW','pltrootDW','pltleafFW','pltrootFW', 'lossPer', 'bolting']

        # run the model and after every run,
        print('\nRunning ...\n')

        wdata = self.wthr.data
        for i, v in wdata.iterrows():
            # data retrieval from wdata dataframe
            datetime = i
            doy  = i.timetuple().tm_yday
            hour = i.hour
            Irrad = v.Irrad
            Tair = v.Tair
            rain = v.rain
            wind = v.wind
            RH   = v.RH

            # calculate boltingdvs from temp
            self.bolting.calcBT(Tair)
            self.boltingdvs = self.bolting.boltingdvs
            boltingdvs = self.boltingdvs

            if boltingdvs < 1.0:
                bolting = 0
            else:
                bolting = 1
                
                
            # set crop_st for potential growth
            crop_st     = 1.0
            
            # calculate leaf number and lai
            leaf             = self.leaf
            leafNumber_tuple = leaf.calcLN(Tair)
            self.leafNumber  = leafNumber_tuple[0]
            self.lai         = leafNumber_tuple[1]
            leafNumber = self.leafNumber
            lai = self.lai            
            LN               = leafNumber * self.lnratio
            
            # total assimilate
            Ictot = Irrad * 4.57 / 2      # from Wm-2 to umol m-2 s-1 and total Irrad to PAR
            tot   = self.gasEx
            tot.setValue(Ictot, Tair, RH, wind, crop_st)
            tot.routine()
            aAn   = tot.An

            # fractionation PAR
            # doy, hour, lai, Irrad
            self.frac.radFraction(doy=doy, hour=hour, PPFD=Ictot, LAI=lai)
            Icsun = self.frac.Icsun      # umol m-2 s-1 
            Icsh  = self.frac.Icsh        # umol m-2 s-1

            # fractionation lai
            self.frac.laiFraction(doy=doy, hour=hour, LAI=lai)
            laiSun = self.frac.laiSun
            laiSh  = self.frac.laiSh

            # fractionation Vcmax
            # self.frac.rubFraction(doy=doy, hour=hour, LAI=self.lai, Vcmax=110)
            # VcmaxSun = self.frac.VcmaxSun
            # VcmaxSh  = self.frac.VcmaxSh

            # for sunlit leaves
            sun =self.gasEx
            sun.setValue(Icsun, Tair, RH, wind, crop_st)
            sun.routine()
            aWc  = sun.Wc
            aWj  = sun.Wj
            aAn  = sun.An

            # for shaded leaves
            shd = self.gasEx
            shd.setValue(Icsh, Tair, RH, wind, crop_st)
            shd.routine()
            bWc = shd.Wc
            bWj = shd.Wj
            bAn = shd.An

            # net assimilates (umol CO2 m-2 ground s-1)
            netA  = aAn*laiSun + bAn*laiSh            # from umolCO2 m-2leaf s-1 to umolCO2 m-2ground s-1
            assim = netA * 3600 * 30 * 10**(-6)       # convert CO2 umol m-2gr s-1 to CH2O g m-2gr hr-1
            self.assimSum += assim                    # assimilate summation
            self.assim     = assim                    # hourly assimilate, CH2O g m-2gr hr-1

            # net transpiration
            netTmm      = tot.Emm * lai 
            self.netTmm = netTmm


            # partitioning assimilates      
            part = self.growth
            part.growCalc(Tair,assim, leafNumber, RDT=1.0)    
            leafDW = part.wgl
            rootDW = part.wr 
            boltDW = part.wo
            maint = part.maint

            # DW per plant
            pltleafDW = leafDW / self.plantDensity
            pltrootDW = rootDW / self.plantDensity

            # convert DW to FW            
            #leafNumber 8.894 이하 시 FDratio 마이너스 값 나오게 됨
            if leafNumber >= 8.894 :
                FDratio = 6.949*np.log(leafNumber) - 6.5953
            else : 
                FDratio = 0

            pltleafFW = pltleafDW * FDratio 
            pltrootFW = pltrootDW * FDratio 

        

            # calculate heatstress(lossPer 50 이상 시 갈색심 or 흑심증 발생=>pyradish에 기재)
            loss = self.loss
            loss.disease(Tair)
            ds = loss.ds
            lossPer = ds * 100
            self.lossPer = lossPer
            lossPer = self.lossPer
           

            # retrieve the model results
            res['datetime'].append(i)
            res['LN'].append(LN)
            res['lai'].append(lai)
            res['netTmm'].append(netTmm)
            res['pltleafDW'].append(pltleafDW)
            res['pltrootDW'].append(pltrootDW)
            res['pltleafFW'].append(pltleafFW)
            res['pltrootFW'].append(pltrootFW)
            res['lossPer'].append(lossPer)
            res['bolting'].append(boltingdvs)                              
                     
        res   = pd.DataFrame(res).set_index('datetime')

        self.hourresult = res                   # store the model results
        
      
        ## Message for abnomal plant growth
        if self.boltingdvs > 1.0:
            print("Be careful Bolting!!")
        if self.lossPer > 99.9:
            print("Be careful Heat Damage!!")

        out = pd.DataFrame(self.hourresult)
        aggrigation = { 'LN' : 'mean', 'lai' : 'mean', 'netTmm':'sum', 'pltleafDW' : 'mean', 'pltrootDW' : 'mean','pltleafFW' : 'mean', 'pltrootFW' : 'mean','lossPer':'mean', 'bolting':'mean'}
                        
        self.dayresult = out.groupby(out.index.date).agg(aggrigation)
        
        
        
        # write df to various file
        cols = [ 'LN', 'lai', 'netTmm', 'pltleafDW', 'pltrootDW', 'pltleafFW', 'pltrootFW', 'lossPer', 'bolting']
        header  = ['leaf.number', 'LAI', 'net.ET(mm)', 'leafDW(g/m2)',  'rootDW(g/m2)', 'leafFW(g)', 'rootFW(g)', 'loss(%)', 'bolting']
        
        fname = self.fname_out
        
        ext = fname.split('.')[1]
        if ext == 'xlsx':
            self.dayresult[cols].to_excel(pd.ExcelWriter(fname), float_format = '%.1f', header=header)
        elif ext == 'csv':
            self.dayresult[cols].to_csv(fname, sep=',', float_format='%.1f', header=header)
        elif ext == 'txt':
            self.dayresult[cols].to_csv(fname, sep='\t', float_format='%.1f', header=header)
        else:
            raise Exception("Only possible file name is *.xlsx, *.csv, *.txt.")
       
        print('\ndone.')  

        input('\nPress enter to exit.')
        
        
            



