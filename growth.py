'''
  Growth class for partitioning assimilates to shoot, root
'''

import numpy as np

## Parameters for radish
Tbase  = 0.0           # base temperature
dm     = 0.6           # max root depth
dg     = 0.012         # root elongation rate (m/day)
hgt    = 0.4           # mean plant height (m)
width  = 0.20          # mean leaf width (m)

## Constants for maintenace respiration at 25C for various plant parts
kgl  = 0.03            # for green leaves (gCH2O/gDM/day)
kr   = 0.015           # for root (gCH2O/gDM/day)
ko   = 0.020           # for rep. org

## Yg : remaining % of assimilate for making structural material 
Yg   = 0.70

## Glucose requirement for synthesis of various plant parts 
ggl  = 1.463           # for green leaves (gCH2O/gDM)
gr   = 1.444           # for root (gCH2O/gDM)
go   = 1.463

## ratio to DM / CH2O
cd     = 1.125         # factor convert mass to CH2O weght, = mass * 45%C / C_MW * CH2O_MW

## ratio of fresh weight to dry weight of leaf
FDR    = 16.76

## time conversion
time  = 'hour'
conv  = 1/24 if time == 'hour' else 1

class Growth(object):
    
    def __init__(self):
        self.wgl = 1.0            # green leaves weight (DW g m-2)
        self.wr = 0.2             # root weight (DW g m-2)
        self.wo = 0.0             # reproductive organ (stem + flower + seed)
        self.maint = 0.0          # maintenace respiration
        
        
    def growCalc(self, Ta, assim, leafNumber, RDT=1.0):
        corr = 1 / 24
        assim_c = assim * RDT     # reduced by water stress 
        
        ## leaf death rate by old age(Total leaf number-death leaf number  relationship)
        #ddage = 0.0                       ##맞아?
        #if leafNumber > 20 :
        #    deathleafnumber = -0.9558 + 0.00359*leafNumber**2  
        #    ddage = deathleafnumber/leafNumber
        #else :
        #    ddage = 0.0
        #ddage = ddage * conv
        
        ## calculaltion green leaves, death laeves, stem, root, storage (g CH2O)
        wgl = self.wgl
        wr = self.wr
        wo = self.wo
        
        ## calculation of maintenances respiration (g CH2O)
        mgl = wgl * kgl
        mr  = wr * kr
        mo  = wo * ko
        RM = mgl + mr + mo
        tempRM = RM * 2 **((Ta - 20)/10)  # temperature correction from Teh
        tempRM = tempRM * corr            # from per day to per hour 
        RMpr = min(tempRM, assim_c)
       
        
        ## calculation of growth respiration (g CH2O)  
        fgl  = 0.2323 + 0.6856/(1+ np.exp(-(leafNumber + 25.5913)/-5.2098))  #sigmoid, 엽수-SMF 관계식 이용(Shoot mass fraction)
        fr = 1 - fgl
        fo  = 0                                                               # reproductive organ (stem + flower + seed), Radish model version1 에서는 계산x
         
        ## nomalization of all partitioning
        fggl = fgl * ggl
        fgr  = fr  * gr
        fgo  = fo  * go
        GT = fggl + fgr + fgo

        available = Yg * (assim_c - RMpr) / GT      # available assim per hour (g DW)

        gr_gl = fgl * available           # for green leaves DW
        gr_r  = fr  * available           # for root DW
        gr_o  = fo  * available           # for rep. organ
        #gr_dl = ggl * ddage               # death leaf weight by aging ##맞아? 

        #self.wgl += (gr_gl - gr_dl)
        self.wgl += gr_gl
        self.wr  += gr_r
        self.wo  += gr_o
        self.maint = assim_c - available 
