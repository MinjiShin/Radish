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

## matinenance respiration coefficient of the plant part (at 25C) 유지호흡계수
kgl  = 0.031           # for green leaves (g CH2O/DM g/day)
kr   = 0.015           # for root (g CH2O/DM g/day)
ko   = 0.020           # for rep. org

## Yg : growth efficiency (remaining % of assimilate for making structural material)
Yg   = 0.70

## Glucose requirement for synthesis of various plant parts 
ggl  = 1.463           # for green leaves (gCH2O/gDM)
gr   = 1.444           # for root (gCH2O/gDM)
go   = 1.463

## ratio to DM / CH2O
cd     = 1.125         # factor convert mass to CH2O weght, = mass * 45%C / C_MW * CH2O_MW

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
        
        ## calculaltion green leaves, death laeves, stem, root, storage (DW g /m2)
        wgl = self.wgl
        wr = self.wr
        wo = self.wo
        
        ## calculation of maintenances respiration (g CH2O / m2 /day) 유지호흡량 계산
        mgl = wgl * kgl     # 잎의 유지호흡량 (DW g /m2)*(gCH2O/DM g/day)
        mr  = wr * kr       # 뿌리의 유지호흡량
        mo  = wo * ko       # 생식기관의 유지호흡량
        RM = mgl + mr + mo  # 총 유지호흡량 the summation onf the maintenance respiration
        tempRM = RM * 2 **((Ta - 20)/10)  # temperature correction from Teh(Q10 계수 적용 온도보정)
        tempRM = tempRM * corr            # from per day to per hour 
        RMpr = min(tempRM, assim_c)       # 동화량(assim_c)이 유지 호흡량보다 적은 경우 이를 상한으로 설정
       
        
        ## 분배(생장)
        # 식물체 부위별 전체 건물중에서 차지하는 비율
        fgl  = 0.2323 + 0.6856/(1+ np.exp(-(leafNumber + 25.5913)/-5.2098))  # 잎 생장 비율 sigmoid, 엽수-SMF 관계식 이용(Shoot mass fraction)
        fr = 1 - fgl                                                         # 뿌리 생장 비율
        fo  = 0                                                              # 생식기관 생장 비율 reproductive organ (stem + flower + seed), Radish model version1 에서는 계산x
         
        # 부위별 glucose 요구량 (gCH2O/gDM)(부위별 전체 중 비율 * 각 부위별 Glucose 요구량)
        fggl = fgl * ggl          #(g CH2O/gDM)
        fgr  = fr  * gr
        fgo  = fo  * go
        GT = fggl + fgr + fgo     #식물체 전체의 glucose 요구량 (gCH2O/gDM)

        # 가용동화물
        available = Yg * (assim_c - RMpr) / GT  # (g CH2O / m2 /day)/(gCH2O/gDM) = g DM / m2 / day

        gr_gl = fgl * available           # for green leaves DW (g DM / m2 / day)
        gr_r  = fr  * available           # for root DW
        gr_o  = fo  * available           # for rep. organ
        #gr_dl = ggl * ddage              # death leaf weight by aging ##맞아? 

        #self.wgl += (gr_gl - gr_dl)
        self.wgl += gr_gl
        self.wr  += gr_r
        self.wo  += gr_o
        self.maint = assim_c - available  # 생장호흡량
