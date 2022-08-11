#!/usr/bin/env python

#This file is part of chelsa_isimip3b_ba_1km.
#
#chelsa_isimip3b_ba_1km is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#chelsa_isimip3b_ba_1km is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with chelsa_isimip3b_ba_1km.  If not, see <https://www.gnu.org/licenses/>.

from functions.chelsa_functions import *
from functions.chelsa_data_classes import *
from functions.set_ncdf_attributes import set_ncdf_attributes
import argparse

ap = argparse.ArgumentParser(
    description='''# This python code for CHELSA_V2.1_Paleo
is adapted to the ERA5 data. It runs the CHELSA algorithm for 
air temperature (tas), and total surface precipitation rate (pr). 
The output directory needs the following 
subfolders: /pr, /tas, /tasmax, /tasmin
Dependencies for ubuntu_18.04:
libwxgtk3.0-dev libtiff5-dev libgdal-dev libproj-dev 
libexpat-dev wx-common libogdi3.2-dev unixodbc-dev
g++ libpcre3 libpcre3-dev wget swig-4.0.1 python2.7-dev 
software-properties-common gdal-bin python-gdal 
python2.7-gdal libnetcdf-dev libgdal-dev
python-pip cdsapi saga_gis-8.2.0 cdo nco 
All dependencies are resolved in the chelsa_paleo_V.1.0.sif singularity container
Tested with: singularity version 3.3.0-809.g78ec427cc
''',
    epilog='''author: Dirk N. Karger, dirk.karger@wsl.ch, Version 1.0'''
)

# collect the function arguments
ap.add_argument('-t','--timestep', type=int, help="timestep, integer")
ap.add_argument('-i','--input', type=str, help="input directory, string")
ap.add_argument('-o','--output', type=str,  help="output directory, string")
ap.add_argument('-tmp','--temp', type=str, help="root for temporary directory, string")


args = ap.parse_args()
print(args)


INPUT = args.input
OUTPUT = args.output
TEMP = args.temp
timestep = args.timestep


def main():
    saga_api.SG_Get_Data_Manager().Delete_All()  #
    Load_Tool_Libraries(True)

    ### create the data classes
    coarse_data = Coarse_data(INPUT=INPUT, timestep=timestep)
    dem_data = Dem_data(INPUT=INPUT, time=timestep-1)

    tas, tasmax, tasmin, pr = chelsa(coarse_data=coarse_data,
                                     dem_data=dem_data,
                                     TEMP=TEMP)

    outfile = OUTPUT + 'tas/CHELSA_PALEO_tas_' + str(timestep) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'tas_high.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='tas',
                        scale='0.1',
                        offset='0',
                        standard_name='air_temperature',
                        longname='Near-Surface Air Temperatures',
                        unit='K')

    outfile = OUTPUT + 'pr/CHELSA_HR_pr_' + str(YEAR) + '-' + str("%02d" % MONTH) + '-' + str("%02d" % DAY) + '-' + str("%02d" % HOUR) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'pr_high.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='pr',
                        scale='0.001',
                        offset='0',
                        standard_name='precipitation_flux',
                        longname='Precipitation',
                        unit='kg m-2 h-1')


