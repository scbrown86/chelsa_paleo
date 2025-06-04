chelsa_paleo
-----------
This package contains functions to downscale min-, max-, mean 
temperature, and precipitation rate from global circulation models
using the CHELSA V2.1 algorithm as. It is part of the
CHELSA Project: (CHELSA, <https://www.chelsa-climate.org/>).

This project is a modified fork from <https://gitlabext.wsl.ch/karger/chelsa_paleo>. 

It has been modified to only require a single (i.e. static) mask regardless of the number of timesteps being simulated, which significantly speeds up the processing of input data

```python
# ds1 = import_ncdf(self.INPUT + 'orog/oro_high.nc').Get_Grid(self.time)
ds1 = import_ncdf(self.INPUT + 'orog/oro_high.nc').Get_Grid(0) #<<< use first time step only
```

It has also been modified to run using a maximum of 2 threads per step which permits us to run 12 steps (i.e. 1 year) in parallel when processing.

```python
def Load_Tool_Libraries(Verbose):
    saga_api.SG_UI_Msg_Lock(True)
    if os.name == 'nt':  # Windows
        os.environ['PATH'] = os.environ['PATH'] + ';' + os.environ['SAGA_32'] + '/dll'
        saga_api.SG_Get_Tool_Library_Manager().Add_Directory(os.environ['SAGA_32'] + '/tools', False)
    else:  # Linux
        saga_api.SG_Get_Tool_Library_Manager().Add_Directory('/usr/local/lib/saga/',
                                                             False)  # Or set the Tool directory like this!
    saga_api.SG_UI_Msg_Lock(False)
   
    saga_api.SG_OMP_Set_Max_Num_Threads(2)  #<<< cores hardcoded to 2

    if Verbose == True:
        print 'Python - Version ' + sys.version
        print saga_api.SAGA_API_Get_Version()        
        print 'number of maximum threads used: ' + str(saga_api.SG_OMP_Get_Max_Num_Threads())
        print 'number of loaded libraries: ' + str(saga_api.SG_Get_Tool_Library_Manager().Get_Count())
        print

    return saga_api.SG_Get_Tool_Library_Manager().Get_Count()
```

COPYRIGHT
---------
(C) 2022 Dirk Nikolaus Karger

(C) 2025 Stuart Brown


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
- ta_high.nc : a netCDF file containing air temperatures at the higher (elevation) pressure level used for the lapse rate calculation (e.g. 600.5 hPa [z=20]) of n timesteps
- ta_low.nc : a netCDF file containing air temperatures at the lower (elevation) pressure level used for the lapse rate calculation (e.g. 992.5 hPa [z=26]) of n timesteps
- tasmax.nc : a netCDF file containing daily maximum near-surface air temperature of n timesteps
- tasmin.nc : a netCDF file containing daily minimum near-surface air temperature of n timesteps
- tas.nc : a netCDF file containing daily mean near-surface air temperature of n timesteps
- uwind.nc : a netCDF file containing the zonal wind component (u) of n timesteps
- vwind.nc : a netCDF file containing the meridional wind component (v) of n timesteps
- zg_high.nc : a netCDF file containing geopotential height (in meters) at the higher (elevation) pressure level used for the lapse rate calculation (e.g. 600.5 hPa [z=20]) of n timesteps
- zg_low.nc : a netCDF file containing geopotential height (in meters) at the lower (elevation) pressure level used for the lapse rate calculation (e.g. 992.5 hPa [z=26]) of n timesteps


INPUT DATA - OROGRAPHIC DATA
-------
files to be stored in a subdirectory /orog
- oro.nc : a netCDF file containing the orography at the coarse (GCM) resolution of n timesteps (modified to work with a single timestep) (i.e. TraCE-21 input orography)
- oro_high.nc : a netCDF file containing the orography at the high (target) resolution of n timesteps (modified to work with a single timestep)


INPUT DATA - STATIC DATA
-------
files to be stored in a subdirectory /static

-merc_template.nc : a netCDF file containing the orography at high (target) resolution in World Mercator projection (here we use a 5-km grid)


`EPSG:3395`

`Proj4 string = '+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'`


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

```shell
chelsa.py -t \<timestep\> -i \<input directory\> -o \<output directory\> -tmp \<temporary directory>
```

SINGULARITY
------------
All dependencies are also resolved in the singularity container '/singularity/chelsa_paleo.sif'. Singularity needs to 
be installed on the respective linux system you are using. An installation guide can be found here: 
https://sylabs.io/guides/3.3/user-guide/quick_start.html#quick-installation-steps

If you use chelsa_paleo together with singularity the command should be slightly modified:

```shell
singularity exec chelsa_paleo.sif python chelsa.py -t \<timestep\> -i \<input directory\> -o \<output directory\> -tmp \<temporary directory>
```

We strongly recommend that you use the singularity container instead of trying to resolve all dependencies yourself.


PARALLEL
-------------
This process of running chelsa_trace can easily be parallelised, to allow multiple timesteps to be generated at once:

```shell
conda activate CHELSA_paleo

END=1080 # expected final number of timesteps
START=1
START_TIME=$(date +%s)

export SINGULARITY_IMG="~/chelsa_paleo/singularity/chelsa_paleo.sif"
export SCRIPT="~/chelsa_paleo/src/chelsa.py"
export INPUT_DIR="~/Documents/CHELSA_paleo_inputs/"
export OUTPUT_DIR="~/Documents/CHELSA_paleo_outputs/"
export SCRATCH_DIR="~/Documents/CHELSA_paleo_scratch/"

seq $END -1 $START | parallel --bar -j 12 -k '
    TMP_PREFIX=$(printf "%04d" {}) &&
    TMP_DIR="$SCRATCH_DIR/tmp_$TMP_PREFIX" &&
    mkdir -p "$TMP_DIR" &&
    singularity exec "$SINGULARITY_IMG" python "$SCRIPT" -t {} -i "$INPUT_DIR" -o "$OUTPUT_DIR" -tmp "$TMP_DIR" > /dev/null 2>&1 &&
    rm -rf "$SCRATCH_DIR/tmp_$TMP_PREFIX"*
'

ELAPSED=$(($(date +%s) - START_TIME))
printf "Elapsed time: %d days %02d hours %02d min %02d sec\n" \
    $((ELAPSED / 86400)) $((ELAPSED % 86400 / 3600)) $((ELAPSED % 3600 / 60)) $((ELAPSED % 60))

```

CITATION:
------------
If you need a citation for the output, please refer to the article describing the high
resolution climatologies:

Karger, D.N., Conrad, O., Böhner, J., Kawohl, T., Kreft, H., Soria-Auza, R.W., Zimmermann, N.E., Linder, P., Kessler, M. (2017). Climatologies at high resolution for the Earth land surface areas. Scientific Data. 4 170122. https://doi.org/10.1038/sdata.2017.122


CONTACT
-------
<s.brown@adelaide.edu.au>

ORIGINAL AUTHOR
------
Dirk Nikolaus Karger
<dirk.karger@wsl.ch>
Swiss Federal Research Institute WSL
Zürcherstrasse 111
8903 Birmensdorf
Switzerland
