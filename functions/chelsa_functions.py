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
#along with isimip3b_ba_1km.  If not, see <https://www.gnu.org/licenses/>.


from functions.saga_functions import *
from functions.chelsa_data_classes import *
Load_Tool_Libraries(True)

def calculate_windeffect(Coarse, Dem):
    """
    Function to calculate the orographic wind effect

    :param Coarse: a chelsa_data_class of type coarse
    :param Dem: a chelsa_data_class of type dem

    :return: windef1
    :rtype: CSG_Grid
    """
    ## import the wind files
    Coarse.set('uwind')
    Coarse.set('vwind')

    uwind = Coarse.uwind
    vwind = Coarse.vwind

    ## set coordinate reference system
    set_2_latlong(uwind)
    set_2_latlong(vwind)

    ## change to shapefile for projection
    uwind_shp = gridvalues_to_points(uwind)
    vwind_shp = gridvalues_to_points(vwind)

    ## reproject to mercator projection
    uwind_shp = reproject_shape(uwind_shp)
    vwind_shp = reproject_shape(vwind_shp)

    Dem.set('demproj')
    ## multilevel b spline
    uwind_ras = multilevel_B_spline(uwind_shp,
                                    Dem.demproj, 14)

    vwind_ras = multilevel_B_spline(vwind_shp,
                                    Dem.demproj, 14)

    direction = polar_coords(uwind_ras,
                             vwind_ras)

    windef = windeffect(direction,
                        Dem.demproj)

    Dem.set('dem_high')
    windef1 = proj_2_latlong(windef,
                             Dem.dem_high)
    Dem.delete('dem_high')

    # clean up memory
    saga_api.SG_Get_Data_Manager().Delete(uwind_ras)
    saga_api.SG_Get_Data_Manager().Delete(vwind_ras)
    saga_api.SG_Get_Data_Manager().Delete(uwind_shp)
    saga_api.SG_Get_Data_Manager().Delete(vwind_shp)
    saga_api.SG_Get_Data_Manager().Delete(windef)

    return windef1


def correct_windeffect(windef1, Coarse, Dem):
    """
    Function too correct the wind effect with boundary layer height
    and resample it to the coarse resolution

    :param windef1: wind effect
    :param Coarse: a chelsa_data_class of type coarse
    :param Dem: a chelsa_data_class of type dem

    :return: wind_cor, wind_coarse
    :rtype: CSG_Grid
    """
    Coarse.set('tas')
    Coarse.set('huss')

    cblev = grid_calculator(Coarse.tas,
                            Coarse.huss,
                            '(20+((a-273.15)/5))*(100-b)')

    Coarse.delete('tas')
    Coarse.delete('huss')

    cblev = calc_geopotential(cblev)
    set_2_latlong(cblev)
    cblev_shp = gridvalues_to_points(cblev)

    #dem_geo = calc_geopotential(Dem.dem_low)

    Dem.set('dem_low')
    cblev_ras = multilevel_B_spline(cblev_shp,
                                    Dem.dem_low, 14)

    # correct wind effect by boundary layer height
    pblh = grid_calculatorX(Dem.dem_low,
                            cblev_ras,
                            'a+b')

    Dem.set('dem_high')

    dist2bound = calc_dist2bound(Dem.dem_high,
                                 pblh)
    Dem.delete('dem_high')

    maxdist2bound = resample_up(dist2bound,
                                pblh, 7)

    maxdist2bound2 = invert_dist2bound(dist2bound,
                                       maxdist2bound)

    wind_cor = grid_calculatorX(maxdist2bound2,
                                windef1,
                                '(b/(1-a/9000))')

    wind_coarse = resample_up(wind_cor,
                              Dem.dem_low, 4)

    wind_coarse = closegaps(wind_coarse)

    Dem.delete('dem_low')

    return wind_cor, wind_coarse


def precipitation(wind_cor, wind_coarse, Coarse):
    """
    Function to downscale precipitation

    :param Coarse: a chelsa_data_class of type coarse
    :param wind_cor: high res boundary layer height corrected windeffect
    :param wind_coarse: low res boundary layer height corrected windeffect

    :return: pr
    :rtype: CSG_Grid
    """
    Coarse.set('pr')

    prec = grid_calculator_simple(Coarse.pr,
                                  'a*86400')

    Coarse.delete('pr')

    precip = downscale_precip(wind_cor,
                              wind_coarse,
                              prec,
                              'total surface precipitation', 3)

    precip_ccINT = convert2uinteger10(precip,
                                      'Precipitation')

    # clean memory
    saga_api.SG_Get_Data_Manager().Delete(prec)
    saga_api.SG_Get_Data_Manager().Delete(precip)

    return precip_ccINT


def temperature(Coarse, Dem, var):
    """
    Function to downscale temperatures

    :param Coarse: a chelsa_data_class of type coarse
    :param Dem: a chelsa_data_class of type dem

    :return: tas, tasmax, tasmin
    :rtype: CSG_Grid
    """
    # calculate temperature
    if var == 'tas':
        Coarse.set('tas')
        tas_var = Coarse.tas

    if var == 'tasmax':
        Coarse.set('tasmax')
        tas_var = Coarse.tasmax

    if var == 'tasmin':
        Coarse.set('tasmin')
        tas_var = Coarse.tasmin

    Coarse.set('tlapse_mean')
    Dem.set('dem_high')
    Dem.set('dem_low')

    tmax_highres1 = lapse_rate_based_downscaling(Dem.dem_high,
                                                 Coarse.tlapse_mean,
                                                 Dem.dem_low,
                                                 tas_var)

    Coarse.delete('tlapse_mean')
    Dem.delete('dem_high')
    Dem.delete('dem_low')

    if var == 'tas':
        tas = convert2uinteger10(tmax_highres1,
                                 'Daily Mean Near-Surface Air Temperature')
        Coarse.delete('tas')

    if var == 'tasmax':
        tas = convert2uinteger10(tmax_highres1,
                                 'Daily Maximum Near-Surface Air Temperature')
        Coarse.delete('tasmax')

    if var == 'tasmin':
        tas = convert2uinteger10(tmax_highres1,
                                 'Daily Minimum Near-Surface Air Temperature')
        Coarse.delete('tasmin')

    # clean memory
    saga_api.SG_Get_Data_Manager().Delete(tmax_highres1)

    return tas


def chelsa(coarse_data=None, dem_data=None, TEMP=None):
    """
    Downscales the coarse data to a higher resolution given by the dem data

    :param coarse_data: a chelsa_data_class of type coarse
    :param dem_data: a chelsa_data_class of type dem

    :return: tas, tasmax, tasmin, pr
    :rtype: CSG_Grid
    """
    ### calculate windeffect
    windef1 = calculate_windeffect(Coarse=coarse_data,
                                   Dem=dem_data)

    ### correct windeffect
    wind_cor, windcoarse = correct_windeffect(windef1=windef1,
                                              Coarse=coarse_data,
                                              Dem=dem_data)

    ### downscale precipitation
    pr = precipitation(wind_cor=wind_cor,
                       wind_coarse=windcoarse,
                       Coarse=coarse_data)

    ### downscale tas
    tas = temperature(Coarse=coarse_data,
                      Dem=dem_data,
                      var='tas')

    ### downscale tas
    tasmax = temperature(Coarse=coarse_data,
                         Dem=dem_data,
                         var='tasmax')

    ### downscale tas
    tasmin = temperature(Coarse=coarse_data,
                         Dem=dem_data,
                         var='tasmin')

    return tas, tasmax, tasmin, pr
