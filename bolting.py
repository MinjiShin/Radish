# ============================================================================================
# module bolting.py : floral bud initiation stage
# ============================================================================================


import numpy as np

# temp. function sum for veg. and rep. stage
# tempdvs = sumtemp/satVS or 1 + (sumtemp - satVS)/(satRS - satVS) or 2
satVS     = 50      # flowering 16 days after full vernalization, Guttormsen(1985)
satRS     = 150      # harvest about 60 days after flowering in Jeju
Totemp     = 12       # opt. temp for veg and rep. growth
shape_temp = 2
  

# ver. function sum for vernalization
# verdvs = sumver / satVer or 1
satVer    = 50       
Tover1    = 6        # opt. temp. for vernalization
Tover2    = 6.4         
shape_ver = 4        # shape param. for log-normal function (verrate = np.exp(-1*(np.log(temp/Tover)**shape) )
LNlimit   = 20       # limit leaf number to sense ver. effect

# dvs = tempdvs * verdvs

#timestep 
time = 'hour'
conv = 1/24  if time == 'hour' else 1.0

class BT():
 
    def __init__(self) :       
        self.boltingdvs = 0.0 # development stage (0 - 2)
        self.sumTemp = 0.0     # rate sum of temperature effect
        self.sumVer  = 0.0     # rate sum of vernilization effect
        self.tempdvs = 0.0     # dvs by temperature effect
        self.verdvs  = 0.0     # dev by vernilezation effect
    

    def calcBT(self, Ta):
        
        ## ----------------------------------------------------------------------------------
        # calculate devolpment stage of temp. function and tempdvs.
        # if sum of temp effect is over critical value(satVS), then tempdvs will be over 1.
        
        #temp_rate
        temprate = np.exp(-1*(np.log(Ta/Totemp)**shape_temp)) if Ta > 0 else 0
        self.sumTemp += temprate * conv           
        sumTemp = self.sumTemp
        
        #sum_temp_rate
        if sumTemp > satRS :
            self.tempdvs = 2.0
        elif sumTemp > satVS :
            self.tempdvs = 1 + (sumTemp-satVS)/(satRS-satVS)
        else : 
            self.tempdvs = sumTemp/satVS
           
        # --------------------------------------------------------------------------------------
        # Venalization effect by low temp
        # To calculate verilization effec(verdvs), lognormal function is used for ver. rate. 
      
        #ver_rate
        if 0 < Ta < 5 :
            self.verrate = np.exp(-1*(np.log(Ta/Tover1)**shape_ver))
        elif Ta >= 5 :
            self.verrate = np.exp(-1*(np.log(Ta/Tover2)**shape_ver))
        else : 
            self.verrate = 0
        #sum_ver
        self.sumVer += self.verrate * conv
        sumVer = self.sumVer
        
        
        if (sumVer/satVer) > 1 :
            self.verdvs = 1
        else :
            self.verdvs = sumVer/satVer
            
      
        # ---------------------------------------------------------------------------------
        # Net boltingdvs is calculated by multipling temdvs and verdvs
        # ---------------------------------------------------------------------------------
        self.boltingdvs = self.tempdvs * self.verdvs 
        

