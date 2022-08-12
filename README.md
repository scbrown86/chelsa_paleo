chelsa_paleo
-----------
This package contains functions to downscale min-, max-, mean 
temperature, and precipitation rate from global circulation models
using the CHELSA V2.1 algorithm as. It is part of the
CHELSA Project: (CHELSA, <https://www.chelsa-climate.org/>).


COPYRIGHT
---------
(C) 2022 Dirk Nikolaus Karger


LICENSE
-------
chelsa_paleo is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the
Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

chelsa_paleo is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with chelsa_cmip6. If not, see <http://www.gnu.org/licenses/>.


PYTHON REQUIREMENTS
------------
chelsa_paleo is written in Python 2. It has been tested to run well with the
following Python release and package versions.
- python 2.7
- argparse 1.2.1
- saga_api


SYSTEM REQUIREMENTS
------------
- libwxgtk3.0-dev 
- libtiff5-dev 
- libgdal-dev 
- libproj-dev 
- libexpat-dev 
- wx-common 
- libogdi3.2-dev 
- unixodbc-dev
- g++ 
- libpcre3 
- libpcre3-dev 
- swig-4.0.1 
- python2.7-dev 
- software-properties-common 
- gdal-bin 
- python-gdal 
- python2.7-gdal 
- libnetcdf-dev 
- libgdal-dev
- python-pip 
- saga_gis-8.2.0 


INPUT DATA
------------
It requires input from a global circulation or earth system model in form of gridded 
netCDF files. The following files need to be provided in a single input directory:


INPUT DATA - CLIMATE DATA
-------
files to be stored in a subdirectory /clim

- huss.nc : a netCDF file containing relative humidity at the surface of n timesteps
- pr.nc : a netCDF file containing precipitation rate at the surface of n timesteps
- ta_high.nc : a netCDF file containing air temperatures at the higher pressure level used for the 
lapse rate calculation (e.g. 850 hPa) of n timesteps
- ta_low.nc : a netCDF file containing air temperatures at the lower pressure level used for the 
lapse rate calculation (e.g. 1000 hPa) of n timesteps
- tasmax.nc : a netCDF file containing daily maximum near-surface air temperature of n timesteps
- tasmin.nc : a netCDF file containing daily minimum near-surface air temperature of n timesteps
- tas.nc : a netCDF file containing daily mean near-surface air temperature of n timesteps
- uwind.nc : a netCDF file containing the zonal wind component (u) of n timesteps
- vwind.nc : a netCDF file containing the meridional wind component (v) of n timesteps
- zg_high.nc : a netCDF file containing geopotential height (in meters) at the higher pressure level used for the 
lapse rate calculation (e.g. 850 hPa) of n timesteps
- zg_low.nc : a netCDF file containing geopotential height (in meters) at the lower pressure level used for the 
lapse rate calculation (e.g. 1000 hPa) of n timesteps


INPUT DATA - OROGRAPHIC DATA
-------
files to be stored in a subdirectory /orog

- oro.nc : a netCDF file containing the orography at the coarse (GCM) resolution of n timesteps 
- oro_high.nc : a netCDF file containing the orography at the high (target) resolution of n timesteps


INPUT DATA - STATIC DATA
-------
files to be stored in a subdirectory /static

- merc_template.nc : a netCDF file containing the orography at high (target) resolution in World Mercator projection

EPSG:3395
Proj4 string = '+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'


OUTPUT
------------
The output directory needs the following subdirectories:
- /tas
- /tasmax
- /tasmin
- /pr

The output consist of netCDF4 files. There will be different files for each variable and each timestep. 


HOW TO USE
----------
The chelsa_paleo model is a reduced and generalized version of the CHELSA V2.1 model.
The main function chelsa.py can be called by providing the parameters 
timestep, inputdirectory, and outputdirectory. 

chelsa.py -t \<timestep\> -i \<inputdirectory\> -o \<outputdirectory\>


SINGULARITY
------------
All dependencies are also resolved in the singularity container '/singularity/chelsa_paleo.sif'. Singularity needs to 
be installed on the respective linux system you are using. An installation guide can be found here: 
https://sylabs.io/guides/3.3/user-guide/quick_start.html#quick-installation-steps

If you use chelsa_paleo together with singularity the command should be slightly modified:

singularity exec /singularity/chelsa_paleo.sif python chelsa.py -t \<timestep\> -i \<inputdirectory\> -o \<outputdirectory\> 

We strongly recommend that you use the singularity container instead of trying to resolve all dependencies yourself.


CITATION:
------------
If you need a citation for the output, please refer to the article describing the high
resolution climatologies:

Karger, D.N., Conrad, O., Böhner, J., Kawohl, T., Kreft, H., Soria-Auza, R.W., Zimmermann, N.E., Linder, P., Kessler, M. (2017). Climatologies at high resolution for the Earth land surface areas. Scientific Data. 4 170122. https://doi.org/10.1038/sdata.2017.122


CONTACT
-------
<dirk.karger@wsl.ch>


AUTHOR
------
Dirk Nikolaus Karger
Swiss Federal Research Institute WSL
Zürcherstrasse 111
8903 Birmensdorf
Switzerland