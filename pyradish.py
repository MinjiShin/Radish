a = """
============================================================================
============================================================================  
===========               Radish model (v.1.0)               ===============
============================================================================
                        - for prediction of radish potential yield.

  How to use:
    1. to double click "pyradish.exe"
    2. to type requested data
    3. Weatherdata file should be same directory of "radish.exe".
    4. Output file will be made at same directory.
    
                                                             by Minji Shin                                      
============================================================================
============================================================================
"""
b = """
============================================================================
How to input:
  == Set simulation coditions ==
    ? latitude(default = 37.0) : -> type latitude or just enter
    ? weather file name : -> type weather file name
      * (.csv, .txt, .xlsx, .xls) file types are possible 
      * Data file shoud have specific name and format
        - daily name(format)  : date(YYYY-mm-dd), sunhr, Tmax, Tmin, rain,
                                wind, RH (all float number)
        - hourly name(format) : timestamp(YYYY-mm-dd HH:MM), Irrad, Tair,
                                rain, wind, RH (all float number)             
        - unit: sunhr(hours), Tmax(C), rain(mm), wind(m/s), RH(%), Irrad(W/m2)
    ? is weather data daily(d) or hourly(h) : -> type 'd' or 'h'
    ? output file name : -> type output file name
      * (*.csv, *.txt, *.xlsx) file names are possible    
    ? planting date(YYYY-mm-dd) : -> type YYYY-mm-dd 
    ? end date(YYYY-mm-dd) : -> type YYYY-mm-dd
    
  == Set initial conditions ==
    ? planting density : -> type greater than 3.6 or just enter
==============================================================================
"""

import sys
import datetime
from facade import Facade   

def run():
    """Main entry point for the program.

    Run the model simulation (hourly or daily)

    """

    # set the accepted flags, and parse the options and arguments:
    inifile = outfile = None
    print(a)
    print(b)

    print("\n=== Set simulation conditions. === ")
    latitude  = float(input("? latitude(default = 37.0) : ") or "37.0")
    inifile   = input("? weather file name(including extension) : ")
    dorh      = input("? is weather data daily(d) or hourly(h) : ")
    outfile   = input("? output file name(including extension) : ")
    start     = input("? planting date(YYYY-mm-dd) : ")
    end       = input("? end date(YYYY-mm-dd) : ")
    
    sp_start = start.split('-')
    sp_end   = end.split('-')
    if len(sp_start) < 3 and len(sp_end) < 3 : 
        raise Exception("Planting date format is YYYY-mm-dd ")
    
    # set growing condition
    print("\n=== Set initial condition.===")
    density = float(input('? planting density(plants/m2, >=3.6, default = 4) : ') or "4.0")
#   iniLN = float(input('? leaf number at planting(default = 8) : ') or "8.0")  변경(>삭제, 무는 파종하므로) 
    
    
    if None in [inifile, outfile]:
        print('One or more parameters are missing.')
        print(__doc__)
        sys.exit()

    model = Facade(dorh, inifile, outfile, start, end, density=density, latitude=latitude, lnratio=1.00)
    model.run()

if __name__ == '__main__':
    run()
