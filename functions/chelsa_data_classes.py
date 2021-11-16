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


from functions.saga_functions import *
Load_Tool_Libraries(True)

#change this that it accepts lat long

class Coarse_data:
    """ coarse grid data """
    def __init__(self, TEMP, lev_low, lev_high):
        self.tas_ = None
        self.tasmax = None
        self.tasmin = None
        self.ua100000 = None
        self.va100000 = None
        self.hurs = None
        self.pr_ = None
        self.tlapse_mean = None
        self.rsds = None
        self.TEMP = TEMP
        self.lev_low = lev_low
        self.lev_high = lev_high

    def set(self, var):
        if getattr(self, var) == None:
           return self._build_(var)

    def delete(self, var):
        saga_api.SG_Get_Data_Manager().Delete(getattr(self, var))
        setattr(self, var, None)

    def _delete_grid_list_(self, list):
        for m in range(0, list.Get_Item_Count()+1):
            print('delete grid no:' + str(m))
            saga_api.SG_Get_Data_Manager().Delete(list.Get_Grid(m))
            list.Del_Items()

    def _build_(self, var):
        if var != 'tlapse_mean' and var != 'rsds':
            ds = import_ncdf(self.TEMP + var + '.nc').Get_Grid(0)
            setattr(self, var, ds)

        if var == 'tlapse_mean':
            talow = import_ncdf(self.TEMP + 'ta_' + str(self.lev_low) + '.nc')
            tahigh = import_ncdf(self.TEMP + 'ta_' + str(self.lev_high) + '.nc')
            zglow = import_ncdf(self.TEMP + 'zg' + str(self.lev_low) + '.nc')
            zghigh = import_ncdf(self.TEMP + 'zg' + str(self.lev_high) + '.nc')
            tlapse_mean = tlapse(zglow.Get_Grid(0), zghigh.Get_Grid(0), talow.Get_Grid(0), tahigh.Get_Grid(0), '(d-c)/(b-a)')
            tlapse_mean1 = change_data_storage(tlapse_mean)
            tlapse_mean2 = grid_calculator_simple(tlapse_mean1, 'a*(-1)')
            setattr(self, var, tlapse_mean2)

            self._delete_grid_list_(talow)
            self._delete_grid_list_(tahigh)
            self._delete_grid_list_(zglow)
            self._delete_grid_list_(zghigh)
            saga_api.SG_Get_Data_Manager().Delete(tlapse_mean)
            saga_api.SG_Get_Data_Manager().Delete(tlapse_mean1)
            #saga_api.SG_Get_Data_Manager().Delete_Unsaved()

        if var == 'rsds':
            rsds1 = import_ncdf(self.TEMP + 'rsds.nc')
            rsds = grid_calculator_simple(rsds1.Get_Grid(0), 'a/0.01157408333')
            setattr(self, var, rsds)
            self._delete_grid_list_(rsds1)
            #saga_api.SG_Get_Data_Manager().Delete_Unsaved()


class Dem_data:
    """ elevational grid data """
    def __init__(self, INPUT):
        self.demproj = None #load_sagadata(INPUT + 'dem_merc3.sgrd')
        self.dem_latlong3 = None #load_sagadata(INPUT + 'dem_latlong3.sgrd')
        self.dem_low = None #load_sagadata(INPUT + 'orography.sgrd')
        self.dem_low = None #change_data_storage(self.dem_low)
        self.dem_high = None #load_sagadata(INPUT + 'dem_latlong.sgrd')
        self.INPUT = INPUT

    def set(self, var):
        if getattr(self, var) == None:
           return self._build_(var)

    def delete(self, var):
        saga_api.SG_Get_Data_Manager().Delete(getattr(self, var))
        setattr(self, var, None)

    def _delete_grid_list_(self, list):
        for m in range(0, list.Get_Item_Count()+1):
            print('delete grid no:' + str(m))
            saga_api.SG_Get_Data_Manager().Delete(list.Get_Grid(m))
            list.Del_Items()

    def _build_(self, var):
        if var == 'demproj':
            ds = load_sagadata(self.INPUT + 'dem_merc3.sgrd')
            setattr(self, var, ds)

        if var == 'dem_latlong3':
            ds = load_sagadata(self.INPUT + 'dem_latlong3.sgrd')
            setattr(self, var, ds)

        if var == 'dem_low':
            ds = load_sagadata(self.INPUT + 'orography.sgrd')
            ds = change_data_storage(ds)
            ds = change_latlong(ds)
            setattr(self, var, ds)

        if var == 'dem_high':
            ds = load_sagadata(self.INPUT + 'dem_latlong.sgrd')
            ds = change_data_storage(ds)
            setattr(self, var, ds)


class Aux_data:
    """ Auxillary grid data """
    def __init__(self, INPUT, W5E5):
        self.patch = None #load_sagadata(INPUT + 'patch.sgrd')
        self.expocor = None #load_sagadata(INPUT + 'expocor.sgrd')
        self.dummy_W5E5 = None #load_sagadata(INPUT + 'dummy_W5E5.sgrd')
        self.template_025 = None #load_sagadata(W5E5 + 'template_025.sgrd')
        self.template_010 = None #load_sagadata(W5E5 + 'template_010.sgrd')
        self.oceans = None #load_sagadata(W5E5 + 'oceans.sgrd')
        self.continents = None #load_sagadata(W5E5 + 'continents.sgrd')
        self.landseamask = None #load_sagadata(W5E5 + 'landseamask.sgrd')
        self.INPUT = INPUT
        self.W5E5 = W5E5

    def set(self, var):
        if getattr(self, var) == None:
           return self._build_(var)

    def _build_(self, var):
        if var == 'patch' or var == 'expocor' or var == 'dummy_W5E5':
            ds = load_sagadata(self.INPUT + var + '.sgrd')
            setattr(self, var, ds)
        else:
            ds = load_sagadata(self.W5E5 + var + '.sgrd')
            setattr(self, var, ds)
            
    def delete(self, var):
        saga_api.SG_Get_Data_Manager().Delete(getattr(self, var))
        setattr(self, var, None)


class Cc_downscale_data:
    """ cloud cover class """
    def __init__(self, CC, TEMP, month):
        self.cc_clim_high = None #import_gdal(CC + "CHELSA_tcc_" + month + "_1981-2010_V.2.1.tif")
        self.cc_clim_low = None #import_ncdf(TEMP + 'clt_clim.nc').Get_Grid(2)
        self.cc_time = None #import_ncdf(TEMP + 'clt.nc').Get_Grid(3)
        self.CC = CC
        self.TEMP = TEMP
        self.month = month

    def set(self, var):
        if getattr(self, var) == None:
           return self._build_(var)

    def _build_(self, var):
        if var == 'cc_time':
            ds = import_ncdf(self.TEMP + 'clt.nc').Get_Grid(0)
            ds.asGrid().Set_Scaling(0.01, 0)
            setattr(self, var, ds)

        if var == 'cc_clim_low':
            ds = import_ncdf(self.TEMP + 'clt_clim.nc').Get_Grid(0)
            ds.asGrid().Set_Scaling(0.01, 0)
            setattr(self, var, ds)

        if var == 'cc_clim_high':
            ds = import_gdal(self.CC + "CHELSA_tcc_" + self.month + "_1981-2010_V.2.1.tif")
            ds.asGrid().Set_Scaling(0.0001, 0)
            setattr(self, var, ds)

    def delete(self, var):
        saga_api.SG_Get_Data_Manager().Delete(getattr(self, var))
        setattr(self, var, None)


class Srad_data:
    """ cloud cover class """
    def __init__(self, SRAD, dayofyear):
        self.rsds_day = None #import_gdal(SRAD + 'CHELSA_stot_pj_' + dayofyear + '_V.2.1.tif')
        self.SRAD = SRAD
        self.dayofyear = dayofyear

    def set(self, var):
        if getattr(self, var) == None:
           return self._build_(var)

    def delete(self, var):
        saga_api.SG_Get_Data_Manager().Delete(getattr(self, var))
        setattr(self, var, None)

    def _build_(self, var):
        ds = import_gdal(self.SRAD + 'CHELSA_stot_pj_' + self.dayofyear + '_V.2.1.tif')
        setattr(self, var, ds)





















