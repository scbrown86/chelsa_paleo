
INPUT = '/storage/karger/chelsa_V2/INPUT_PALEO/'
TEMP = '/home/karger/scratch/'

saga_api.SG_Get_Data_Manager().Delete_All()  #
Load_Tool_Libraries(True)

### create the data classes
coarse_data = Coarse_data(INPUT=INPUT, timestep=1)
dem_data = Dem_data(INPUT=INPUT, time=0)

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




# test with singularity











