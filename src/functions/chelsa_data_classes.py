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


from functions.saga_functions import *

class Coarse_data:
    """
    coarse grid data class
    """
    def __init__(self, INPUT, timestep):
        self.tas = None
        self.tasmax = None
        self.tasmin = None
        self.uwind = None
        self.vwind = None
        self.huss = None
        self.pr = None
        self.tlapse_mean = None
        self.INPUT = INPUT
        self.timestep = timestep

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
            ds = import_ncdf(self.INPUT + 'clim/' + var + '.nc').Get_Grid(self.timestep)
            setattr(self, var, ds)

        if var == 'tlapse_mean':
            talow = import_ncdf(self.INPUT + 'clim/ta_low.nc').Get_Grid(self.timestep)
            tahigh = import_ncdf(self.INPUT + 'clim/ta_high.nc').Get_Grid(self.timestep)
            zglow = import_ncdf(self.INPUT + 'clim/zg_low.nc').Get_Grid(self.timestep)
            zghigh = import_ncdf(self.INPUT + 'clim/zg_high.nc').Get_Grid(self.timestep)#.Set_Scaling(0.10197162129)
            tlapse_mean = tlapse(tahigh, talow , zghigh, zglow,  '(a-b)/(c-d)')
            tlapse_mean1 = change_data_storage(tlapse_mean)
            tlapse_mean2 = grid_calculator_simple(tlapse_mean1, 'a*(-1)')
            setattr(self, var, tlapse_mean2)

            saga_api.SG_Get_Data_Manager().Delete(tlapse_mean)
            saga_api.SG_Get_Data_Manager().Delete(tlapse_mean1)


class Dem_data:
    """
    elevational grid data class
    """
    def __init__(self, INPUT, time=0):
        self.demproj = None
        self.dem_low = None
        self.dem_high = None
        self.INPUT = INPUT
        self.time = int(time)

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
            ds1 = import_ncdf(self.INPUT + 'orog/oro_high.nc').Get_Grid(self.time)
            set_2_latlong(ds1)
            template = import_ncdf(self.INPUT + 'static/merc_template.nc').Get_Grid(0)
            ds = pj2merc(ds1, template)
            setattr(self, var, ds.asGrid())

        if var == 'dem_low':
            ds = import_ncdf(self.INPUT + 'orog/oro.nc').Get_Grid(self.time)
            ds = change_data_storage(ds)
            setattr(self, var, ds)

        if var == 'dem_high':
            ds = import_ncdf(self.INPUT + 'orog/oro_high.nc').Get_Grid(self.time)
            ds = change_data_storage(ds)
            setattr(self, var, ds)





















