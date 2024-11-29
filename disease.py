"""
   Disease class : calculation of disease loss by rate
"""

import numpy as np

A = 2.0
B = 4.0

# time calibration
time   = 'hour'
conv   = 1 / 24  if time == 'hour' else 1

class Disease():

    def __init__(self):
        self.ds = 0.0                    # Severity (0-1)
        self.rsum = 0.0                  # rate sum

    def disease(self, Tair):      
        # calculation
        if Tair > 0:
            # use modified lognormal function
            rate  = np.exp(-1*(np.log(Tair/100))**4) * conv
        else :
            rate  = 0

        self.rsum += rate
        dx   = -1 * (self.rsum / A)**B      
        ds = 1 - np.exp(dx)
        self.ds = ds
