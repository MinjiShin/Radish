import numpy as np

## parameters 
# parameters for germination
Rxleaf_germi  = 0.1679
Txleaf_germi  = 47.0948
Toleaf_germi  = 29.2426
# parameters for leaf number increasing
Rxleaf  = 0.614856
Txleaf  = 54.65071
Toleaf  = 28.41466

#timestep 
time = 'hour'
conv = 1/24  if time == 'hour' else 1

class LeafNumber():
        def __init__(self, plantDensity):
            self.plantDensity = plantDensity 
            # Output         
            self.leafNumber = 0.0           
            self.lai  = 0.0 
            self.germination = 0.0 
            
        # calculate leaf number       
        def calcLN(self, Ta) :   
            #global germination            
            if ((Ta > 0.0) & (Ta < Txleaf_germi)).all(): 
                germinationRate = Rxleaf_germi *((Txleaf_germi-Ta)/(Txleaf_germi-Toleaf_germi))*(Ta/Toleaf_germi)**(Toleaf_germi/(Txleaf_germi-Toleaf_germi))
                germinationRate = germinationRate * conv
            else:
                germinationRate = 0.0
            self.germination += germinationRate
 
        
            if (self.germination >= 1).all() :
                germinated = True
            else:
                germinated = False
                
            if  (germinated & (Ta > 0.0) & (Ta < Txleaf)).all(): 
                leafRate = Rxleaf *((Txleaf-Ta)/(Txleaf-Toleaf))*(Ta/Toleaf)**(Toleaf/(Txleaf-Toleaf))
                leafRate = leafRate * conv
                self.leafNumber += leafRate
                
            else:
                self.leafNumber = 0.0
                return self.germination, self.lai
                

            leafArea = np.exp(9.9863+(-49.4206/(self.leafNumber)))
            self.lai = leafArea *  self.plantDensity / 10000
            
            return self.leafNumber+1, self.lai
