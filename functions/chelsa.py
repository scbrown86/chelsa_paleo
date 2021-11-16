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

def chelsa(coarse_data, dem_data, aux_data, cc_downscale_data, srad_data, TEMP):
    ### This function is to core of chelsa and calcuates
    ### all variables. The functions for the variables
    ### are defined in the chelsa_functions.py file

    ### calculate windeffect
    windef1 = calculate_windeffect(Coarse=coarse_data,
                                   Dem=dem_data)

    ### correct windeffect
    wind_cor, wind_coarse25, windcoarse = correct_windeffect(windef1=windef1,
                                                             Coarse=coarse_data,
                                                             Dem=dem_data,
                                                             Aux=aux_data)

    ### clean up memory
    wind_cor.Save(TEMP + 'wind_cor.sgrd')
    windcoarse.Save(TEMP + 'wincoarse.sgrd')
    wind_coarse25.Save(TEMP + 'wind_coarse25.sgrd')

    saga_api.SG_Get_Data_Manager().Delete_All()

    wind_cor = load_sagadata(TEMP + 'wind_cor.sgrd')
    windcoarse = load_sagadata(TEMP + 'wincoarse.sgrd')
    wind_coarse25 =load_sagadata(TEMP + 'wind_coarse25.sgrd')

    ### downscale precipitation
    pr = precipitation(wind_cor=wind_cor,
                       wind_coarse=windcoarse,
                       wind_coarse25=wind_coarse25,
                       Coarse=coarse_data,
                       Aux=aux_data)

    ### clean up memory
    pr.Save(TEMP + 'pr.sgrd')
    saga_api.SG_Get_Data_Manager().Delete_All()

    ### downscale cloud cover
    cc_fin = cloudcover(Cc_downscale_data=cc_downscale_data,
                        Aux=aux_data)

    rsds = solar_radiation(Srad=srad_data,
                           Coarse=coarse_data,
                           cc_fin=cc_fin)

    ### clean up memory
    rsds.Save(TEMP + 'rsds.sgrd')
    saga_api.SG_Get_Data_Manager().Delete_All()

    ### downscale tas
    tas = temperature(Coarse=coarse_data,
                      Dem=dem_data,
                      Aux=aux_data,
                      var='tas')

    ### clean up memory
    tas.Save(TEMP + 'tas.sgrd')
    saga_api.SG_Get_Data_Manager().Delete_All()

    ### downscale tasmin
    tasmin = temperature(Coarse=coarse_data,
                         Dem=dem_data,
                         Aux=aux_data,
                         var='tasmin')

    ### downscale tasmax
    tasmax = temperature(Coarse=coarse_data,
                         Dem=dem_data,
                         Aux=aux_data,
                         var='tasmax')

    # avoid delta tasmax tasmin being negative due to interpolation artefacts
    tasmax = grid_statistics(tasmax,
                             tasmin, 0).asGrid()

    tasmin = grid_statistics(tasmax,
                             tasmin, 1).asGrid()

    rsds = load_sagadata(TEMP + 'rsds.sgrd')
    pr = load_sagadata(TEMP + 'pr.sgrd')
    tas = load_sagadata(TEMP + 'tas.sgrd')

    return tas, tasmax, tasmin, rsds, pr



