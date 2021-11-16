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
    ## import the wind files
    Coarse.set('ua100000')
    Coarse.set('va100000')

    uwind = Coarse.ua100000
    vwind = Coarse.va100000

    ## set coordinate reference system
    set_2_latlong(uwind)
    set_2_latlong(vwind)

    ## change to shapefile for projection
    uwind_shp = gridvalues_to_points(uwind)
    vwind_shp = gridvalues_to_points(vwind)

    #Coarse._delete_grid_list_('ua100000')
    #Coarse._delete_grid_list_('va100000')

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

    #dem = change_data_storage(Dem.dem_latlong3)

    windef = windeffect(direction,
                        Dem.demproj)

    Dem.set('dem_latlong3')
    windef1 = proj_2_latlong(windef,
                             Dem.dem_latlong3)
    Dem.delete('dem_latlong3')

    # clean up memory
    saga_api.SG_Get_Data_Manager().Delete(uwind_ras)
    saga_api.SG_Get_Data_Manager().Delete(vwind_ras)
    saga_api.SG_Get_Data_Manager().Delete(uwind_shp)
    saga_api.SG_Get_Data_Manager().Delete(vwind_shp)
    saga_api.SG_Get_Data_Manager().Delete(windef)
    #saga_api.SG_Get_Data_Manager().Delete(dem)

    return windef1


def correct_windeffect(windef1, Coarse, Dem, Aux):
    Coarse.set('tas_')
    Coarse.set('hurs')

    cblev = grid_calculator(Coarse.tas_,
                            Coarse.hurs,
                            '(20+((a-273.15)/5))*(100-b)')

    Coarse.delete('tas_')
    Coarse.delete('hurs')

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
                            'a+(b/9.80665)')

    Dem.delete('dem_low')
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


    #patchgrid = Aux.patch #load_sagadata(INPUT + 'patch.sgrd')

    exp_index = Aux.expocor #load_sagadata(INPUT + 'expocor.sgrd')

    Aux.set('expocor')
    wind_cor = grid_calculatorX(Aux.expocor,
                                wind_cor,
                                'a*b')

    Aux.delete('expocor')
    Aux.set('patch')

    wind_cor = patching(wind_cor,
                        Aux.patch)

    Aux.delete('patch')
    Aux.set('dummy_W5E5')

    wind_coarse = resample_up(wind_cor,
                              Aux.dummy_W5E5, 4)

    wind_coarse = closegaps(wind_coarse)

    # downscale precipitation and export
    wind_coarse25 = resample_up(wind_cor,
                                pblh, 4)

    Aux.delete('dummy_W5E5')

    return wind_cor, wind_coarse25, wind_coarse


def precipitation(wind_cor, wind_coarse25, wind_coarse, Coarse, Aux):
    Coarse.set('pr_')

    prec = grid_calculator_simple(Coarse.pr_,
                                  'a*86400')

    Coarse.delete('pr_')
    Aux.set('dummy_W5E5')

    prec = resample(prec,
                    Aux.dummy_W5E5)

    Aux.delete('dummy_W5E5')

    prec = closegaps(prec)

    prec2 = downscale_precip(wind_coarse25,
                             wind_coarse,
                             prec,
                             'prec', 1)

    precip = downscale_precip(wind_cor,
                              wind_coarse25,
                              prec2,
                              'total surface precipitation', 3)

    precip_ccINT = convert2uinteger10(precip,
                                      'Precipitation')

    # clean memory
    saga_api.SG_Get_Data_Manager().Delete(prec)
    saga_api.SG_Get_Data_Manager().Delete(prec2)
    saga_api.SG_Get_Data_Manager().Delete(precip)

    return precip_ccINT


def cloudcover(Cc_downscale_data, Aux):
    Aux.set('template_025')
    Aux.set('template_010')
    Cc_downscale_data.set('cc_clim_high')

    cc_h_025 = resample_up(Cc_downscale_data.cc_clim_high,
                           Aux.template_025, 4)

    cc_h_010 = resample_up(Cc_downscale_data.cc_clim_high,
                           Aux.template_010, 4)

    Cc_downscale_data.set('cc_clim_low')
    Cc_downscale_data.set('cc_clim_high')

    cc_h_050 = resample_up(Cc_downscale_data.cc_clim_high,
                           Cc_downscale_data.cc_clim_low, 4)

    shp_050 = gridvalues_to_points(cc_h_050)
    shp_025 = gridvalues_to_points(cc_h_025)
    shp_010 = gridvalues_to_points(cc_h_010)

    #grd_050 = multilevel_B_spline(shp_050,Cc_downscale_data.cc_clim_high, 11)
    grd_025 = multilevel_B_spline(shp_025,
                                  Cc_downscale_data.cc_clim_high, 11)

    grd_010 = multilevel_B_spline(shp_010,
                                  Cc_downscale_data.cc_clim_high, 11)

    grd_025_050 = multilevel_B_spline(shp_050,
                                      Aux.template_025, 11)

    grd_010_050 = multilevel_B_spline(shp_050,
                                      Aux.template_010, 11)

    grd_high_050 = multilevel_B_spline(shp_050,
                                       Cc_downscale_data.cc_clim_high, 11)

    Cc_downscale_data.set('cc_time')

    cc_day_050_shp = gridvalues_to_points(Cc_downscale_data.cc_time)

    Cc_downscale_data.delete('cc_time')

    cc_grd_025 = multilevel_B_spline(cc_day_050_shp,
                                     grd_025, 11)

    cc_025 = downscale_precip(cc_h_025,
                              grd_025_050,
                              cc_grd_025,
                              'cc', 5)

    cc_day_025_shp = gridvalues_to_points(cc_025)

    cc_grd_010 = multilevel_B_spline(cc_day_025_shp,
                                     grd_010,11)

    cc_010 = downscale_precip(cc_h_010,
                              grd_010_050,
                              cc_grd_010,
                              'cc',5)

    cc_day_010_shp = gridvalues_to_points(cc_010)

    cc_grd_high = multilevel_B_spline(cc_day_010_shp,
                                      Cc_downscale_data.cc_clim_high,11)

    cc_high = downscale_precip(Cc_downscale_data.cc_clim_high,
                               grd_high_050,
                               cc_grd_high,
                               'cc',5)

    cc_high1 = grid_calculator_simple(cc_high,
                                      'ifelse(a>1.0,a-a+1.0,a*1.0)')

    cc_fin = grid_calculator_simple(cc_high1,
                                    'ifelse(a<0.0,a-a,a*1.0)')

    # clean memory
    saga_api.SG_Get_Data_Manager().Delete(cc_high1)
    saga_api.SG_Get_Data_Manager().Delete(cc_high)
    saga_api.SG_Get_Data_Manager().Delete(cc_grd_high)
    saga_api.SG_Get_Data_Manager().Delete(cc_day_010_shp)
    saga_api.SG_Get_Data_Manager().Delete(cc_010)
    saga_api.SG_Get_Data_Manager().Delete(cc_grd_010)
    saga_api.SG_Get_Data_Manager().Delete(cc_day_025_shp)
    saga_api.SG_Get_Data_Manager().Delete(cc_025)
    saga_api.SG_Get_Data_Manager().Delete(cc_grd_025)
    saga_api.SG_Get_Data_Manager().Delete(cc_day_050_shp)
    saga_api.SG_Get_Data_Manager().Delete(grd_high_050)
    saga_api.SG_Get_Data_Manager().Delete(grd_010_050)
    saga_api.SG_Get_Data_Manager().Delete(grd_025_050)
    saga_api.SG_Get_Data_Manager().Delete(grd_010)
    saga_api.SG_Get_Data_Manager().Delete(grd_025)
    saga_api.SG_Get_Data_Manager().Delete(shp_050)
    saga_api.SG_Get_Data_Manager().Delete(shp_025)
    saga_api.SG_Get_Data_Manager().Delete(shp_010)
    saga_api.SG_Get_Data_Manager().Delete(cc_h_050)
    saga_api.SG_Get_Data_Manager().Delete(cc_h_025)
    saga_api.SG_Get_Data_Manager().Delete(cc_h_010)

    return cc_fin


def temperature(Coarse, Dem, Aux, var):
    # calculate temperature
    if var == 'tas':
        Coarse.set('tas_')
        tas_var = Coarse.tas_

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

    Aux.set('landseamask')

    tmax_highres = grid_calculator(tmax_highres1,
                                   Aux.landseamask,
                                   'a*b')

    Aux.delete('landseamask')
    Aux.set('oceans')

    tmax1 = grid_calculatorX(Aux.oceans,
                             tas_var,
                             'a*b')

    Aux.delete('oceans')

    tmax1 = closegaps(tmax1)

    tmax_highres1 = patchingBspline(tmax_highres,
                                    tmax1)

    saga_api.SG_Get_Data_Manager().Delete(tmax1)

    if var == 'tas':
        tas = convert2uinteger10(tmax_highres1,
                                 'Daily Near-Surface Air Temperature')
        Coarse.delete('tas_')

    if var == 'tasmax':
        tas = convert2uinteger10(tmax_highres1,
                                 'Daily Near-Surface Air Temperature')
        Coarse.delete('tasmax')

    if var == 'tasmin':
        tas = convert2uinteger10(tmax_highres1,
                                 'Daily Near-Surface Air Temperature')
        Coarse.delete('tasmin')

    # clean memory
    saga_api.SG_Get_Data_Manager().Delete(tmax_highres1)
    saga_api.SG_Get_Data_Manager().Delete(tmax_highres)

    return tas


def solar_radiation(Srad, Coarse, cc_fin):
    # calculate solar radiation
    Srad.set('rsds_day')

    srad_sur = surface_radiation(Srad.rsds_day,
                                 cc_fin,
                                 'Surface Downwelling Shortwave Radiation')

    Srad.delete('rsds_day')

    srad_cor = change_data_storage2(srad_sur, 3)

    Coarse.set('rsds')

    srad_resamp = resample_up(srad_cor,
                              Coarse.rsds, 5)

    srad_bias = grid_calculator(Coarse.rsds,
                                srad_resamp,
                                '(a+1)/(b+1)')

    srad_cor2 = grid_calculatorX(srad_cor,
                                 srad_bias,
                                 'a*b')

    Coarse.delete('rsds')

    srad_cor2 = change_data_storage2(srad_cor2, 3)

    # clean memory
    saga_api.SG_Get_Data_Manager().Delete(srad_sur)
    saga_api.SG_Get_Data_Manager().Delete(srad_cor)
    saga_api.SG_Get_Data_Manager().Delete(srad_resamp)
    saga_api.SG_Get_Data_Manager().Delete(srad_bias)

    return srad_cor2

