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

import xarray as xr
import os

class interpol:
    """Interpolation class"""
    def __init__(self, ds, template):
        """ Create a set of baseline clims """
        self.ds = ds
        self.template = template

    def interpolate(self):
        res = self.ds.interp(lat=self.template["lat"], lon=self.template["lon"])
        return res


class ingest_isimip:
    """ ingest isimip class """
    def __init__(self, inputdir, outputdir, model, ssp, parm, day=False, month=False, year=False, z=False, resample=False, template=None, shiftlong=False, climstart=False, climend=False):
        self.inputdir = inputdir
        self.outputdir = outputdir
        self.model = model
        self.ssp = ssp
        self.parm = parm
        if day == False:
            self.day = day
        if day != False:
            self.day = str(day).zfill(2)
        self.month = str(month).zfill(2)
        self.year = str(year)
        self.z = z
        self.resample = resample
        self.template = template
        self.shiftlong = shiftlong
        self.climstart = climstart
        self.climend = climend

    def _absPaths_(self, directory):
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                yield os.path.abspath(os.path.join(dirpath, f))

    def get_ds(self):
        print(self.inputdir)
        flist = list(self._absPaths_(self.inputdir))
        #print(flist)
        lst = [self.model, self.ssp, self.parm]
        flists = []

        ds = None
        for n in range(1, len(lst)):
            flists = [k for k in flist if lst[n] in k]

        print(flists)

        if (self.day != False and self.climstart == False):
            tstr = str(self.year
                            + '-'
                            + self.month
                            + '-'
                            + self.day)

        if (self.day == False and self.climstart == False):
            tstr = str(self.year
                       + '-'
                       + self.month)

        if (self.z == False and self.climstart == False):
            ds = xr.open_mfdataset(flists).sel(time=tstr)
            ds = ds.sortby('time')
            dsname = self.outputdir + self.parm + '.nc'

        if (self.z != False and self.climstart == False):
            ds = xr.open_mfdataset(flists).sel(time=str(tstr)).sel(plev=self.z)
            ds = ds.sortby('time')
            dsname = self.outputdir + self.parm + str(self.z) + '.nc'

        if self.climstart != False:
            ds = xr.open_mfdataset(flists).sortby('time').sel(time=slice(self.climstart, self.climend)).groupby('time.month').mean('time').sel(month=int(self.month))
            dsname = self.outputdir + self.parm + '_clim.nc'

        if (self.day == False and self.climstart == False):
            ds = ds.groupby('time.month').mean('time')

            if self.z != False:
                dsname = self.outputdir + self.parm + '_Amon_clim.nc'

            if self.z != False:
                dsname = self.outputdir + self.parm + str(self.z) + '_Amon_clim.nc'

        if self.shiftlong == True:
            ds = ds.assign_coords(lon=(((ds.lon + 180) % 360) - 180))

        if self.resample == True:
            ds = interpol(ds=ds, template=self.template).interpolate()

        try:
            ds = ds.groupby('time').mean('time')
        except:
            print('no need to aggregate')

        try:
            ds = ds.drop('lat_bnds')
            print("dimension lat_bnds exist... deleting")
        except:
            print("dimension lat_bnds does not exist... doing nothing")

        try:
            ds = ds.drop('lon_bnds')
            print("dimension lon_bnds exist... deleting")
        except:
            print("dimension lon_bnds does not exist... doing nothing")

        try:
            ds = ds.drop('time')
            print("dimension time exist... deleting")
        except:
            print("dimension time does not exist... doing nothing")

        try:
            ds = ds.drop('time_bnds')
            print("dimension time_bnds exist... deleting")
        except:
            print("dimension time_bnds does not exist... doing nothing")

        ds.to_netcdf(dsname)

        return True


class ingest:
    """ ingest data class """
    def __init__(self, isimip, isimip_pr, cmip, temp, model, rcp, day, month, year, levlow, levhigh):
        self.isimip = isimip
        self.isimip_pr = isimip_pr
        self.cmip6 = cmip
        self.temp = temp
        self.model = model.lower()
        self.rcp = rcp
        self.day = day
        self.month = month
        self.year = year
        self.lev_low = levlow
        self.lev_high = levhigh

    def ingest_data(self):
        # ingest the isimip data
        ingest_isimip(inputdir=self.isimip,
                      outputdir=self.temp,
                      model=self.model,
                      ssp=self.rcp,
                      parm='tasmax',
                      day=self.day,
                      month=self.month,
                      year=self.year).get_ds()

        # read in one dataset as template for the interpolation of the auxilary cmip6 forcing data
        self.template_ds = xr.open_dataset(self.temp + 'tasmax.nc')

        ingest_isimip(inputdir=self.isimip,
                      outputdir=self.temp,
                      model=self.model,
                      ssp=self.rcp,
                      parm='tasmin',
                      day=self.day,
                      month=self.month,
                      year=self.year).get_ds()

        ingest_isimip(inputdir=self.isimip,
                      outputdir=self.temp,
                      model=self.model,
                      ssp=self.rcp,
                      parm='tas_',
                      day=self.day,
                      month=self.month,
                      year=self.year).get_ds()

        ingest_isimip(inputdir=self.isimip_pr,
                      outputdir=self.temp,
                      model=self.model,
                      ssp=self.rcp,
                      parm='pr_',
                      day=self.day,
                      month=self.month,
                      resample=True,
                      template=self.template_ds,
                      year=self.year).get_ds()

        ingest_isimip(inputdir=self.isimip,
                      outputdir=self.temp,
                      model=self.model,
                      ssp=self.rcp,
                      parm='rsds',
                      day=self.day,
                      month=self.month,
                      year=self.year).get_ds()

        ingest_isimip(inputdir=self.isimip,
                      outputdir=self.temp,
                      model=self.model,
                      ssp=self.rcp,
                      parm='hurs',
                      day=self.day,
                      month=self.month,
                      year=self.year).get_ds()

        # read in the auxilary self.cmip6 forcing data.
        ingest_isimip(inputdir=self.cmip6,
                      outputdir=self.temp,
                      model=self.model.upper(),
                      ssp=self.rcp,
                      parm='ua',
                      day=self.day,
                      month=self.month,
                      year=self.year,
                      z=self.lev_low,
                      resample=True,
                      template=self.template_ds,
                      shiftlong=True).get_ds()

        ingest_isimip(inputdir=self.cmip6,
                      outputdir=self.temp,
                      model=self.model.upper(),
                      ssp=self.rcp,
                      parm='va',
                      day=self.day,
                      month=self.month,
                      year=self.year,
                      z=self.lev_low,
                      resample=True,
                      template=self.template_ds,
                      shiftlong=True).get_ds()

        ingest_isimip(inputdir=self.cmip6,
                      outputdir=self.temp,
                      model=self.model.upper(),
                      ssp=self.rcp,
                      parm='ta_',
                      day=self.day,
                      month=self.month,
                      year=self.year,
                      z=self.lev_low,
                      resample=True,
                      template=self.template_ds,
                      shiftlong=True).get_ds()

        ingest_isimip(inputdir=self.cmip6,
                      outputdir=self.temp,
                      model=self.model.upper(),
                      ssp=self.rcp,
                      parm='ta_',
                      day=self.day,
                      month=self.month,
                      year=self.year,
                      z=self.lev_high,
                      resample=True,
                      template=self.template_ds,
                      shiftlong=True).get_ds()

        ingest_isimip(inputdir=self.cmip6,
                      outputdir=self.temp,
                      model=self.model.upper(),
                      ssp=self.rcp,
                      parm='zg',
                      day=self.day,
                      month=self.month,
                      year=self.year,
                      z=self.lev_low,
                      resample=True,
                      template=self.template_ds,
                      shiftlong=True).get_ds()

        ingest_isimip(inputdir=self.cmip6,
                      outputdir=self.temp,
                      model=self.model.upper(),
                      ssp=self.rcp,
                      parm='zg',
                      day=self.day,
                      month=self.month,
                      year=self.year,
                      z=self.lev_high,
                      resample=True,
                      template=self.template_ds,
                      shiftlong=True).get_ds()

        ingest_isimip(inputdir=self.cmip6,
                      outputdir=self.temp,
                      model=self.model.upper(),
                      ssp=self.rcp,
                      parm='clt',
                      day=self.day,
                      month=self.month,
                      year=self.year,
                      resample=True,
                      template=self.template_ds,
                      shiftlong=True).get_ds()

        ingest_isimip(inputdir=self.cmip6,
                      outputdir=self.temp,
                      model=self.model.upper(),
                      ssp=self.rcp,
                      parm='clt',
                      day=False,
                      month=self.month,
                      year=False,
                      climstart="1981-01-01T12:00:00",
                      climend="2010-12-31T12:00:00",
                      resample=True,
                      template=self.template_ds,
                      shiftlong=True).get_ds()

