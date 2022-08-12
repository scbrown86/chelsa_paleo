#!/usr/bin/env python

#This file is part of chelsa_paleo.
#
#chelsa_highres is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#chelsa_highres is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with chelsa_paleo.  If not, see <https://www.gnu.org/licenses/>.

from functions.chelsa_functions import *
from functions.chelsa_data_classes import *
from functions.set_ncdf_attributes import set_ncdf_attributes
import argparse
import os

ap = argparse.ArgumentParser(
    description='''# This python code for CHELSA_V2.1_Paleo
is adapted to the ERA5 data. It runs the CHELSA algorithm for 
air temperature (tas), and total surface precipitation rate (pr). 
The output directory needs the following 
subfolders: /pr, /tas, /tasmax, /tasmin
Dependencies for ubuntu_18.04:
libwxgtk3.0-dev libtiff5-dev libgdal-dev libproj-dev 
libexpat-dev wx-common libogdi3.2-dev unixodbc-dev
g++ libpcre3 libpcre3-dev swig-4.0.1 python2.7-dev 
software-properties-common gdal-bin python-gdal 
python2.7-gdal libnetcdf-dev libgdal-dev
python-pip saga_gis-8.2.0 
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

    tas.Save(TEMP + 'tas.sgrd')
    tasmax.Save(TEMP + 'tasmax.sgrd')
    tasmin.Save(TEMP + 'tasmin.sgrd')
    pr.Save(TEMP + 'pr.sgrd')

    outfile = OUTPUT + 'tas/CHELSA_tas_' + str(timestep) + '_V.1.0.nc'
    os.system('gdal_translate -ot Int16 -of netCDF -co "ZLEVEL=9" ' + TEMP + 'tas.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='tas',
                        scale='0.1',
                        offset='0',
                        standard_name='air_temperature',
                        longname='Daily Mean Near-Surface Air Temperatures',
                        unit='K')

    outfile = OUTPUT + 'tasmax/CHELSA_tasmax_' + str(timestep) + '_V.1.0.nc'
    os.system('gdal_translate -ot Int16 -of netCDF -co "ZLEVEL=9" ' + TEMP + 'tasmax.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='tasmax',
                        scale='0.1',
                        offset='0',
                        standard_name='air_temperature',
                        longname='Daily Maximum Near-Surface Air Temperatures',
                        unit='K')

    outfile = OUTPUT + 'tasmin/CHELSA_tasmin_' + str(timestep) + '_V.1.0.nc'
    os.system('gdal_translate -ot Int16 -of netCDF -co "ZLEVEL=9" ' + TEMP + 'tasmin.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='tasmin',
                        scale='0.1',
                        offset='0',
                        standard_name='air_temperature',
                        longname='Daily Minimum Near-Surface Air Temperatures',
                        unit='K')

    outfile = OUTPUT + 'pr/CHELSA_pr_' + str(timestep) + '_V.1.0.nc'
    os.system('gdal_translate -ot Int16 -of netCDF -co "ZLEVEL=9" ' + TEMP + 'pr.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='pr',
                        scale='0.0000011574',
                        offset='0',
                        standard_name='precipitation_flux',
                        longname='Precipitation',
                        unit='kg m-2 s-1')


if __name__ == '__main__':
    main()
