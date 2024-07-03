### Functions forming the automated workflow of the gdgtm package.

### Workflow is as follows:
# 1. Create a blank raster with the desired target dimensions
# 2. Load source rasters (from disk or online)
# 3. Reproject source rasters to match the blank raster projection (using functions from gdgtm_core.py)
# 4. Align source rasters to blank (using functions from gdgtm_core.py) 
# 5. Return a dictionary including validation results

## TO DO for 0.7 PROD - re-organize the functions into logical places between this file and gdgtm_core

##############################################################
######################## Functions ###########################
##############################################################

### Function list
### 01. get_proj_transform: extracts the transform and projection data. Used in checks.
### 02. check_if_geotiff: checks if a submitted file is indeed a geotiff
### 1. set_up_blank: sets up a blank raster to user provided specs (projection, resolution, etc...)
### 2. download_raster: downloads a raster. Possible to set a bounding box at download point.
### 3. align_rasters: loads/downloads one or more tiffs and aligns them to a pre-defined blank

# 01 get_proj_transform -------------------------------------------------------
def get_proj_transform (filename):
    '''
    This function extracts the projection and GeoTransform from a GeoTIFF and returns it as a Python list

    **Args:**
        - filename (str): Filename along the relevant path.

    **Returns:**
        - list: List containing projection in the authority:code format and GDAL-formatted geotransform

    **Assumptions:**
        1. Function tested using Python 3.10.12 and GDAL 3.6.2 in a conda 24.4.0 environment
        2. Function currently written to only work with GeoTIFFs

    **Usage:**
    >>>    test = get_proj_transform("/home/pete/Documents/tests_and_vals/gdgtm_dev_copy/dev_blank_cassini.tif")
    >>>    print(test)
    ['ESRI:54028', [200.0, 0.0, 460000.0, 0.0, -200.0, 5300000.0, 0.0, 0.0, 1.0]]
      
    '''
    import rasterio

    ## Open connection
    with rasterio.open(filename) as src:
        crs = src.crs ## Get projection as authority:code
        transform = src.transform ## Get geotransforms

    return [str(crs), list(transform)] ## As string and as list to ensure standardized handling of the outputs, without rasterio auxiliary information cropping up

    
    


# 02 check_if_geotiff ---------------------------------------------------------
def check_if_geotiff (file_path):
    '''
    This function checks if a given file is a geotiff

    **Args:**
        - file_path (str): path (including filename) to the raster to be tested. Can be local or URL.

    **Returns:**
        - dict: Indication of point of failure and whether file is a GeoTIFF

    **Assumptions:**
        1. Function developed and tested using Python 3.10.14 and GDAL 3.6.2 working under conda 24.4.0 virtual environment.

    **Usage:**
    >>>    test = check_if_geotiff("https://s3.openlandmap.org/arco/bulkdens.fineearth_usda.4a1h_m_250m_b0cm_19500101_20171231_go_epsg.4326_v0.2.tif")
    >>>    print(test)
    {"File is GeoTIFF": True}

    >>>    test = check_if_geotiff("/home/pete/Documents/tests_and_vals/gdgtm_dev_copy/lol_cat.tif")
    >>>    print(test)
    {"ds.GetProjection": False}
    '''
    from osgeo import gdal

    ## Suppress GDAL error messages
    gdal.UseExceptions()
    gdal.PushErrorHandler("CPLQuietErrorHandler")

    try:
        ds = gdal.Open(file_path)

        # Check if file opened successfully
        if ds is None:
            return {"gdal.Open": False}

        # Check projection
        if ds.GetProjection == "":
            return {"ds.GetProjection": False}

        # Check if file has a geotransform
        if ds.GetGeoTransform() == (0.0, 1.0, 0.0, 0.0, 0.0, 1.0):
            return {"ds.GetGeoTransform": False}
        
        ds = None ##Close connection
        return {"File is GeoTIFF": True}

    except Exception as e:
        return {e: False}

    finally:
        #Reset GDAL error handling
        gdal.PopErrorHandler()

        
    


# 1 set_up_blank --------------------------------------------------------------
def set_up_blank (bbox, proj, pixel_size, dst_raster):
    '''
    This function takes a projection and a bbox, and sets up a blank geotiff raster to those specifications

    **Args:**
        - bbox (tuple): a WNES bbox defining the limits of the blank raster. Values need to match the standard set in the projection.
        - proj (str): authority:code formatted projection.
        - pixel_size (float): size of the individual pixels (length of edges). Units need to be concurrent with the projection.
        - dst_raster (str): string indicating the location and filename where the blank raster is to be saved.

    **Returns:**
        - str: cofnirmation that the raster has been created and a check on the basic metadata.

    **Assumptions:**
        1. GDAL installed and operational (function developed and tested using GDAL 3.6.2)
        2. Function was developed and tested in a conda 24.4.0 virtual environment, using miniconda and Python 3.10

    **Usage:**
    >>>    bbox_wgs84 = (5, 47, 8, 45)
    >>>    proj_wgs84 = "EPSG:4326"
    >>>    pixel_size = 0.01
    >>>    dst_raster = "/home/pete/Documents/tests_and_vals/gdgtm_dev_copy/" + "dev_blank_wgs84.tif"
    >>>
    >>>    test = set_up_blank(bbox_wgs84, proj_wgs84, pixel_size, dst_raster)
    >>>    print(test)
    ['EPSG:4326', [0.01, 0.0, 5.0, 0.0, -0.01, 47.0, 0.0, 0.0, 1.0]]    
    '''
    from osgeo import gdal, osr
    import rasterio
    from rasterio.crs import CRS

    ## Define driver
    driver = gdal.GetDriverByName("GTiff")

    ## Calculate dimensions and get the geotransform in place
    x_size = (bbox[2] - bbox[0]) / pixel_size
    y_size = (bbox[1] - bbox[3]) / pixel_size

    x_size = int(x_size)
    y_size = int(y_size) ## Need to transform to integers for GDAL.

    geotransform = (bbox[0], pixel_size, 0, bbox[1], 0, - pixel_size)

    
    ## Create blank raster, set geotransform and no-data value
    dst_ds = driver.Create(dst_raster, x_size, y_size, 1, gdal.GDT_UInt16)
    dst_ds.SetGeoTransform(geotransform)
    dst_ds.GetRasterBand(1).SetNoDataValue(1) 

    ## Get the CRS WKT ("Well-Known-Text"). This allows us to set up projection with a generic functions (rather than having to use a projection-specific one).
    rasterio_crs = CRS.from_string(proj)
    wkt = rasterio_crs.to_wkt()

    ## Get the projection from the newly generated WKT
    projection = osr.SpatialReference()
    projection.ImportFromWkt(wkt)

    ## Set the projection
    dst_ds.SetProjection(projection.ExportToWkt())
    
    ## Disconnect from GDAL
    dst_ds = None
    

    return get_proj_transform(dst_raster)
    


# 2 download_raster -----------------------------------------------------------
def download_raster (raster_link, dst_raster, bbox = None):
    '''
    The function downloads a raster and sets a bounding box

    **Args:**
        - raster_link (str): a link to a raster to be downloaded
        - bbox (tuple): a WNES set of coordinates defining the downloaded raster bounding box

    **Returns:**
        - dict: confirmation that dst_raster exists

    **Assumptions:**
        - raster_link points to a valid raster links
        - Function developed and tested using GDAL version 3.6.2 and Python 3.10.12

    *Usage:*
    >>>    download_raster("https://s3.openlandmap.org/arco/wilderness_li2022.human.footprint_p_1km_s_20000101_20001231_go_epsg.4326_v16022022.tif", 
    >>>                    "/home/pete/Documents/tests_and_vals/gdgtm_dev_copy/down_raster.tif", 
    >>>                     bbox = (4, 48, 9, 44))
    {'dst_raster exists': True}
    '''
    from osgeo import gdal
    import os

    # Check if the file in question really is a GeoTIFF
    is_geotiff = check_if_geotiff(raster_link)
    if not list(is_geotiff.values())[0]:
        raise TypeError(f"{is_geotiff}")

    # Load the raster
    src_raster = gdal.Open(raster_link)

    if bbox is None:
        gdal.Translate(dst_raster, src_raster) ##Save to dst
    else:
        gdal.Translate(dst_raster, src_raster, projWin = bbox) ## Apply bbox and save to dst

    src_raster = None ## Disconnect from raster
    return {"dst_raster exists": os.path.exists(dst_raster)}




# 3 align_rasters -------------------------------------------------------------
def align_rasters (bbox, proj, pixel_size, dst_blank, src_rasters, dst_rasters):
    '''
    The function takes on projection, resolution and bbox specs, alongside a list of raster links, or a string with a single raster name.
    It generates a blank raster, checks whether it matches required specs, and then aligns the rasters from the list provided.
    **Args:**
        - bbox (tuple): a WNES bbox defining the limits of the blank raster. Values need to match the standard set in the projection.
        - proj (str): authority:code formatted projection.
        - pixel_size (float): size of the individual pixels (length of edges). Units need to be concurrent with the projection.
        - dst_blank (str): string indicating the location and filename where the blank raster is to be saved.
        - src_rasters (str or list): name of a single input raster or a list of input raster names.
        - dst_rasters (str or list): paths/names of the saved, aligned rasters.
    
    **Returns:**
        -dict: confirmation that the .
        
    **Assumptions:**
        - raster_links points to a valid raster links (local or online)
        - Function developed and tested using GDAL version 3.6.2 and Python 3.10.12
        - Number of src_rasters matches the number of dst_rasters
        
    **Usage:**
    >>>    align_rasters(bbox = (6, 47, 7, 45), proj = "EPSG:21781", pixel_size = 200,
    >>>                  dst_blank = "/home/pete/Documents/tests_and_vals/gdgtm_dev_copy/align_blank.tif",
    >>>                  src_rasters = "home/pete/Documents/tests_and_vals/gdgtm_dev_copy/down_raster.tif",
    >>>                  dst_rasters = "home/pete/Documents/tests_and_vals/gdgtm_dev_copy/down_aligned.tif")
    {"home/pete/Documents/tests_and_vals/gdgtm_dev_copy/down_aligned.tif": TRUE}
         
    '''
    import gdgtm
    import os
    
    ## Convert src_rasters and dst_rasters to lists if necessary
    if isinstance(src_rasters, str):
        src_rasters = [src_rasters]

    if isinstance(dst_rasters, str):
        dst_rasters = [dst_rasters]

    ## Set up blank raster
    set_up_blank(bbox, proj, pixel_size, dst_blank)
      
    ## Download src_rasters
    raw_temps = [] ## Set up the raw temps list to enable correct handling
    
    for i in range(len(src_rasters)):
        raw_temps.append(f"raw_temp{i}.tif")

    for i in range(len(src_rasters)):
        download_raster(src_rasters[i], raw_temps[i])

    ## Re-project src_rasters
    reproject_temps = []
    
    for i in range(len(raw_temps)):
        reproject_temps.append(f"reproject_temp{i}.tif")

    alignment_log = {}
    for i in range(len(raw_temps)):
        gdgtm.reproject_raster(new_crs = proj,
                               src_raster = raw_temps[i],
                               dst_raster = reproject_temps[i],
                               delete_source = True)
        
        alignment_validation = gdgtm.align_validate_raster(source_raster = reproject_temps[i],
                                                           target_raster = dst_blank,
                                                           dst_raster = dst_rasters[i],
                                                           delete_source = True)
        ##Run alignment checks
        if os.path.exists(dst_rasters[i]):
            alignment_log[dst_rasters[i]] = alignment_validation
        else:
            alignment_log[dst_rasters[i]] = "No file"
    
    ## Return alignment log.
    return alignment_log