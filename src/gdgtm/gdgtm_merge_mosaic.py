### Functions for raster merging and mosaics


# mosaic_rasters() ------------------------------------------------------------

def mosaic_rasters (raster_1, raster_2, dst_raster, delete_source = True):
    '''
    This function takes two raster and mosaics them into a single raster
    
    **Args:**
        - raster_1 (str): link to the location of the first of the two rasters to mosaic
        - raster_2 (str): link to the location of the second raster to mosaic
        - dst_raster (str): path and file name of the destination file
        - delete_source (bool): toggles whether the function deletes the source rasters
        
    **Returns:**
        - str: indication whether the dst_raster exists
        
    **Assumptions:**
    1. Both rasters are GeoTIFFs
    2. Both rasters are same projection
    3. Both rasters have the same bands
    4. Function tested using GDAL 4.3.1 and Python 3.10.12
    
    **Usage:**
    >>> mosaic_rasters(raster_1 = "/home/pete/Documents/tests_and_vals/gdgtm/06_mosaic_merge_prep/olm_humfoot_switz_raw_west_20010101.tif",
    >>>                raster_2 = "/home/pete/Documents/tests_and_vals/gdgtm/06_mosaic_merge_prep/olm_humfoot_switz_raw_east_20010101.tif",
    >>>                dst_raster = "/home/pete/Documents/tests_and_vals/gdgtm/07_mosaic_merge_out/olm_humfoot_switz_raw_whole_20010101.tif")
    
    "/home/pete/Documents/tests_and_vals/gdgtm/07_mosaic_merge_out/olm_humfoot_switz_raw_whole_20010101.tif exists"
    
    '''
    ## import dependencies
    from osgeo import gdal
    import os
    
    ## Load the rasters
    src_1 = gdal.Open(raster_1) ## rasters here need different name from input args - otherwise deletion becomes tricky
    src_2 = gdal.Open(raster_2)
    
    ## Build the mosaic
    mosaic = gdal.BuildVRT('', [src_1, src_2])
    
    ## Sink the mosaic to GeoTIFF
    tiff_driver = gdal.GetDriverByName("GTiff")
    out_mosaic = tiff_driver.CreateCopy(dst_raster, mosaic)
    
    ## Close connections
    src_1 = None
    src_2 = None
    out_mosaic = None
    
    ## Run check
    dst_exists = os.path.exists(dst_raster)
    if dst_exists:
        return_string = dst_raster + " exists"
    else:
        return_string = "Mosaic failed: " + dst_raster + " does not exist"
    
    ## Run deletion
    if dst_exists and delete_source:
        os.remove(raster_1)
        os.remove(raster_2)
        
    return print(return_string)



# merge_rasters() -------------------------------------------------------------

def merge_rasters (raster_1, raster_2, dst_raster, delete_source = True):
    '''
    This function merges two rasters, combining them into a single raster with two bands.
    
    **Args:**
        - raster_1 (str): link to the location of the first of the two rasters to merge
        - raster_2 (str): link to the location of the second raster to merge
        - dst_raster (str): path and file name of the destination file
        - delete_source (bool): toggles whether the function deletes the source rasters
        
    **Returns:**
        - str: indication whether the bound counts match between the source and the destination
        
    **Assumptions:**
    1. The two rasters share the same projection and dimensions
    2. Both rasters are GeoTIFFs
    4. Function tested using GDAL 4.3.1 and Python 3.10.12
    
    **Usage:**
    >>> merge_rasters(raster_1 = "/home/pete/Documents/tests_and_vals/gdgtm/06_mosaic_merge_prep/olm_humfoot_switz_raw_west_20010101.tif", 
    >>>               raster_2 = "/home/pete/Documents/tests_and_vals/gdgtm/06_mosaic_merge_prep/olm_humfoot_switz_raw_west_20020101.tif",
    >>>               dst_raster = "/home/pete/Documents/tests_and_vals/gdgtm/07_mosaic_merge_out/olm_humfoot_switz_raw_west_merge_2001_2002.tif")
    
    "Both source and destination contain 2 bands total."
    
    '''
    
    ## import dependencies
    from osgeo import gdal
    import os
    
    ## Load the rasters and get the number of bands in each
    src_1 = gdal.Open(raster_1) ## rasters here need different name from input args - otherwise deletion becomes tricky
    src_2 = gdal.Open(raster_2)
    
    num_bands_src_1 = src_1.RasterCount
    num_bands_src_2 = src_2.RasterCount
    num_bands_total = num_bands_src_1 + num_bands_src_2

    
    ## Get raster dimensions and projection
    cols = src_1.RasterXSize
    rows = src_1.RasterYSize
    projection = src_1.GetProjection()
    transform = src_1.GetGeoTransform()
    
    ## Create output raster with num_bands_total bands
    driver = gdal.GetDriverByName("GTiff")
    merged_raster = driver.Create(dst_raster, cols, rows, num_bands_total, gdal.GDT_Float32)
    merged_raster.SetProjection(projection)
    merged_raster.SetGeoTransform(transform)
    
    dst_layer_tracker = 1 ## This will be used to keep track on which dst_layer we actually are
    
    ## Copy data out of the first raster
    for i in range(num_bands_src_1):
        src_band_num = i + 1
        out_band = merged_raster.GetRasterBand(dst_layer_tracker)
        out_band.WriteArray(src_1.GetRasterBand(src_band_num).ReadAsArray())
        out_band.FlushCache()
        dst_layer_tracker += 1
    
    ## Copy the data out of the second raster
    for i in range(num_bands_src_2):
        src_band_num = i + 1
        out_band = merged_raster.GetRasterBand(dst_layer_tracker)
        out_band.WriteArray(src_2.GetRasterBand(src_band_num).ReadAsArray())
        out_band.FlushCache()
        dst_layer_tracker += 1
    
    ## Close data sets
    merged_raster = None
    src_1 = None
    src_2 = None
    
    ## Check dst bound count matches
    dst_raster = gdal.Open(dst_raster)
    dst_bands = dst_raster.RasterCount
    dst_check = dst_bands == num_bands_total
    dst_raster = None
    
    ## Prep return string
    if dst_check:
        retrun_string = "Both source and destination have " + str(dst_bands) + " bands total."
    else:
        return_string = "Merge unsuccessful: dst has " + str(dst_bands) + " bands, while source rasters have " + str(num_bands_total) +" bands total."
    
    ## Delete sources
    if dst_check and delete_source:
        os.remove(raster_1)
        os.remove(raster_2)
    
    
    return print(retrun_string)
