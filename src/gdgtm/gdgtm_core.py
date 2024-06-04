### Functions forming the core workflow of the gdgtm package.



### 1. Data getting functions
### 2. Data processing functions
### 3. Data alignment and validation functions


##############################################################
########## 1. Data getting Functions #########################
##############################################################

### Data getting function list
### 1.1 get_chelsa_daily: gets data from Chelsa
### 1.2 get_cognames_from_stac_coll_static
### 1.3 get_cogs_from_olm
### 1.4 get_chelsa_bio_19812010_data
### 1.5 get_chelsa_clim_19812010_data




# 1.1 get_chelsa_daily ---------------------------------------

def get_chelsa_daily (parameter, bbox, interval, dst_path, dst_name):
    """
    This function gets a cropped raster from Chelsa (https://chelsa-climate.org/), saves it as a .tiff to designated folder, checks that the .tiff exists, and prints a confirmation to the console.

    Args:
        parameter (str): The name of the variable used by Chelsa to find the intended data (has to be CMIP5 standard short name - specifies what climate varia is desired, see https://chelsa-climate.org/wp-admin/download-page/CHELSA_tech_specification_V2.pdf for possible varias).
        bbox (tuple): a tuple of four floats defining the area covered (WNES)
        interval (tuple): a yyyy-mm-dd formatted string determining the start date (position 0) and end date (position 1)
        target_directory (str): location to which the downloaded .tiff is written
        dst_name (str): First part of the file name

    Returns:
        str: string confirming that the intended .tiff indeed exists in the target location

    Assumptions:
    1. The provided interval is covered by Chelsa data.
    2. The parameter name is correct.
    3. os and GDAL are working (function tested using GDAL 3.4.1)
    4. datetime and dateutil are working (function tested using versions 5.5 and 2.8.2)
    4. Function tested using Python 3.10.12

    Usage example:
    >>> get_chelsa_data(parameter = "tas", 
    >>>                 bbox = (7.3, 47.2, 7.5, 47.0), 
    >>>                 interval = ("2023-01-01", "2023-01-05"), 
    >>>                 dst_path = '/home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/',
    >>>                 dst_name = "chelsa_tas_"
    >>>                )
    File exists: /home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_01_01_2023.tif
    File exists: /home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_02_01_2023.tif
    File exists: /home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_03_01_2023.tif
    File exists: /home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_04_01_2023.tif
    File exists: /home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_05_01_2023.tif

    """
    
    ## Import the relevant Python and R packages with names corresponding to those used in the current function
    import os
    from osgeo import gdal
    from datetime import datetime
    from dateutil.rrule import rrule, DAILY ## Note that this has to be imported exactly this way for the function to work

    ## Create a list of dates from the interval
    start_date = datetime.strptime(interval[0], "%Y-%m-%d")
    end_date = datetime.strptime(interval[1], "%Y-%m-%d")
    dates = [dt.strftime("%d_%m_%Y") for dt in rrule(freq = DAILY, dtstart = start_date, until = end_date)]

    ## Transform dates into target_urls
    core_url = "https://os.unil.cloud.switch.ch/chelsa02/chelsa/global/daily/" + parameter + "/YEAR/CHELSA_"+ parameter + "_DATE_V.2.1.tif"
    target_urls = []

    for date in dates:
        year = date[6:10]
        target_url = core_url.replace("YEAR", year)
        target_url = target_url.replace("DATE", date)
        target_urls.append(target_url)
        
    ## Use GDAL to download the rasters and enforce the desired bounding box
    ## First initialize list for filename QC check:
    return_strings = []

    for i in range(len(dates)):
        dst_raster = dst_path + dst_name + dates[i] + ".tif"
        url_to_get = target_urls[i]
    
        ##Get raster from URL and apply the bounding box
        src_raster = gdal.Open(url_to_get)
        gdal.Translate(dst_raster, src_raster, projWin = bbox)
        src_raster = None ## Close connection
    
        if os.path.isfile(dst_raster):
            return_strings.append("File exists: " + dst_raster)
        else:
            return_strings.append("Warning, file does NOT exist: " + dst_raster)

    return return_strings
            

# 1.2 get_cognames_from_stac_coll_static -----------------------
def get_cognames_from_stac_coll_static (static_coll_link):
    '''
    This function produces a list of names of cog (cloud optimized geotiffs) files from a STAC collection.
    
    Args:
        static_coll_link (str): link to a static STAC collection
        
    Returns:
        list: list of cog names as strings
        
    Assumptions:
    1. Link points at an actual STAC static collection.
    2. pystac is installed ( function tested using pystac 1.10.1).
    3. Python installation includes the re module.
    4. Function tested using Python 3.10.12
    5. Function version for gdgtm version 0.1.0 is only tested against Open Land Map urls
    
    Usage example:
    >>> test = gdgtm.get_cognames_fom_stac_coll_static("https://s3.eu-central-1.wasabisys.com/stac/openlandmap/wilderness_li2022.human.footprint/collection.json")
    >>> print(test[0])
    https://s3.openlandmap.org/arco/wilderness_li2022.human.footprint_p_1km_s_20000101_20001231_go_epsg.4326_v16022022.tif
    
    '''
    ## Import dependencies
    import pystac
    import re
    
    ## Set up empty list
    geotiff_names = []
    
    ## Get collection items
    collection = pystac.read_file(static_coll_link)
    collection_items = collection.get_all_items()
    
    ## Iterate over collection items to the asset level. Then in the asset level determine if something is a geotiff
    for item in collection_items:
        for asset_key in item.assets:
            asset = item.assets[asset_key]
            if re.search("geotiff", asset.media_type):   # Using regex, as the actual media_type string contains much more various data
                geotiff_names.append(asset.href) # asset.href is the link to the actual geotiff
                
    return geotiff_names


# 1.3 get_cogs_from_olm ----------------------------------------
def get_cogs_from_olm (cognames, 
                       target_directory, 
                       target_names, 
                       bbox = (-180, 180, 180, -180), 
                       interval = None
                      ):
    '''
    The function uses a list of OpenLandMap cog locations to download a set of rasters bound in space and time
    
    Args:
        cognames (list): list of names of geotiffs in the OLM S3 bucket associated with the STAC collection of interest
        target_directory (str): directory to which the files will be saved
        target_names (str): the convention name for the files to be downlaoded
        bbox (tupple): a tupple of floats indicating the WGS84 (EPSG:4326) coordinates of the bounding box used to crop the rasters downloaded. Defaults to entire grid (-180, 180, 180, -180)
        interval (tupple or None): dates outside which rasters will be ignored. Needs to be provided in the yyyymmdd format. Defaults to 01JAN0001.
            
    returns:
        str: names of downloaded files in the target_directory
        Downloaded geotiff files named in the target_names_orig_file_date format in the target_directory
        
    Assumptions:
        cognames point to an OLM S3 bucket and OLM data
        All incmong raster refer to data points happenning between 01JAN0001 and 31DEC9999.
        GDAL is available (function tested using GDAL 3.4.1)
    
    Usage:
    >>> bbox = (5.7663, 47.9163, 10.5532, 45.6755)
    >>>
    >>> get_cogs_from_olm(cognames = test, 
    >>>                   target_directory = "/home/pete/Downloads/", 
    >>>                   target_names = "olm_humfoot_switz_raw_",
    >>>                   bbox = bbox,
    >>>                   interval = ("20000601", "20050101")

    
    /home/pete/Downloads/olm_humfoot_switz_raw_20010101.tif
    /home/pete/Downloads/olm_humfoot_switz_raw_20020101.tif
    /home/pete/Downloads/olm_humfoot_switz_raw_20030101.tif
    /home/pete/Downloads/olm_humfoot_switz_raw_20040101.tif
    
    '''
    ## Import GDAL
    from osgeo import gdal
    
    ## Loop getting the rasters
    for raster_name in cognames:
        if type(interval) is tuple:
            ## Filter based on date
            raster_ymd = raster_name.split("-doy")[0].split("_")[-5: -3]  ###This gets the dates out of the raster_name
            if min(raster_ymd) > interval[0] and max(raster_ymd) < interval[1]: ## Apply filter
                src_raster = gdal.Open(raster_name) ##Get the actual raster
                new_raster_name = target_directory + target_names + raster_ymd[0] + ".tif"
                ##Apply bbox and save in target location
                gdal.Translate(new_raster_name, src_raster, projWin = bbox)
                print(new_raster_name) ## Print file name to confirm operation successful
                
        else:
            ## If no interval is set:
            src_raster = gdal.Open(raster_name) ##Get the actual raster
            new_raster_name = target_directory + target_names + ".tif"
            ##Apply bbox and save in target location
            gdal.Translate(new_raster_name, src_raster, projWin = bbox)
            print(new_raster_name) ## Print file name to confirm operation successful
            
       
            
        ## Disconnect from file
        src_raster = None
            
        
# 1.4 get_chelsa_bio_19812010_data -----------------------------
def get_chelsa_bio_19812010_data (parameter, bbox, dst_raster):
    '''
    This function retrieves 1980 - 2010 BIOCLIM+ data from the Chelsa S3 bucket (https://envicloud.wsl.ch/#/?prefix=chelsa%2Fchelsa_V2%2F).
    The function can be modified to point at a broader range of sources by changing the base_url and adjusting URL construction(indicated below)
    
    **Agrs:**
        - parameter (str): specifies which parameter is being sought. Needs to be exactly one of the paramter names specified in: https://chelsa-climate.org/bioclim/
        - bbox (tuple): specifies the bounding box of the saved raster. Include edges in the following order: WNES in degrees relative to WGS84
        - dst_raster (str): path and filename to the raster destination
        
    **Returns:**
        - str: confirmation that file exists
        
    **Assumptions:**
    1. Function tested using GDAL 3.4.1
    2. Function tested using Python 3.10.12
    3. The downloaded file is a GeoTIFF

    **Usage:**
    >>> extent = (5.7663, 47.9163, 10.5532, 45.6755)
    >>> get_chelsa_bio_19812010_data("swe", bbox = extent, dst_raster = "/home/pete/Downloads/chesla_bio_test.tif")
    File exists: /home/pete/Downloads/chesla_bio_test.tif
      
    '''
    
    from osgeo import gdal
    
    ## Construct URL - Modify here to point at other parts of the CHELSA S3 bucket
    base_url = "https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V2/GLOBAL/climatologies/1981-2010/bio/CHELSA_"
    url_tail = "_1981-2010_V.2.1.tif"
    url_to_get = base_url + parameter + url_tail
    
    ##Get raster from URL and apply the bounding box
    src_raster = gdal.Open(url_to_get)
    gdal.Translate(dst_raster, src_raster, projWin = bbox)
    
    if os.path.exists(dst_raster):
        return_string = "File exists: " + dst_raster
    else:
        return_string = "File does not exist: " + dst_raster
    
    
    ##Disconnect from file
    src_raster = None
    
    return print(return_string)


# 1.5 get_chelsa_clim_19812010_data ----------------------------
def get_chelsa_clim_19812010_data (parameter, month, bbox, dst_raster):
    '''
    This function retrieves 1980 - 2010 CLIM data from the Chelsa S3 bucket (https://envicloud.wsl.ch/#/?prefix=chelsa%2Fchelsa_V2%2F).
    The function can be modified to point at a broader range of sources by changing the base_url and adjusting URL construction(indicated below)
    
    **Agrs:**
        - parameter (str): specifies which parameter is being sought. Needs to be exactly one of the paramter names specified in: https://chelsa-climate.org/bioclim/
        - month (str): string specifying which month of the year is sought. Has to be in the "mm" numeric format (e.g. 01)
        - bbox (tuple): specifies the bounding box of the saved raster. Include edges in the following order: WNES in degrees relative to WGS84
        - dst_raster (str): path and filename to the raster destination
        
    **Returns:**
        - str: confirmation that file exists
        
    **Assumptions:**
    1. Function tested using GDAL 3.4.1
    2. Function tested using Python 3.10.12
    3. The downloaded file is a GeoTIFF

    **Usage:**
    >>> extent = (5.7663, 47.9163, 10.5532, 45.6755)
    >>> get_chelsa_clim_19812010_data("tas", "06", bbox = extent, dst_raster = "/home/pete/Downloads/chesla_clim_test.tif")
    File exists: /home/pete/Downloads/chesla_clim_test.tif
      
    '''
    
    from osgeo import gdal
    
    ## Construct URL - Modify here to point at other parts of the CHELSA S3 bucket
    base_url = "https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V2/GLOBAL/climatologies/1981-2010/PARAM/CHELSA_PARAM_MONTH_1981-2010_V.2.1.tif"
    url_to_get = base_url.replace("PARAM", parameter)
    url_to_get = url_to_get.replace("MONTH", month)
    
    ##Get raster from URL and apply the bounding box
    src_raster = gdal.Open(url_to_get)
    gdal.Translate(dst_raster, src_raster, projWin = bbox)
    
    if os.path.exists(dst_raster):
        return_string = "File exists: " + dst_raster
    else:
        return_string = "File does not exist: " + dst_raster
    
    
    ##Disconnect from file
    src_raster = None
    
    return print(return_string)

#---------------------------------------------------------------



##############################################################
########## 2. Data processing Functions ######################
##############################################################

### Data processing function list
### 2.1 reproject_raster: wrapper function for rasterio reprojection
### 2.2 change_raster_res: wrapper for changing resolution with rasterio
### 2.3 set_raster_boundbox: wrapper for re-setting the bounding box with gdal

# 2.1 reproject_raster ---------------------------------------

### The function takes on the target projection, creates a re-projected .tiff
### Function should send a confirm message that it re-projected correctly
### Assumes rasterio and numpy packages are installed on the machine
### Assumes new coord system name is recognized by rasterio
### Assumes the following have been imported:
# import numpy as np
# import rasterio
# from rasterio.warp import calculate_default_transform, reproject, Resampling

def reproject_raster (new_crs, src_raster, dst_raster, delete_source = True):
    '''
    This function takes a geotiff raster (with metadata include coordinate projection) and turns out a geotiff raster with updated projection and a check that the new file exists.
    The function also has the option to do source deletion (e.g. for DM purposes)

    Args:
        new_crs (str): New coordinate system to which the raster is to be projected to.
        source_raster (str): path to the geotiff with relevant metadata that will be reprojected
        dst_raster (str): path and filename into which new (re-projected) raster will be saved
        delete_source (bool): determines whether source raster is deleted following function execution

    Resturns:
        str: string confirming that the new geotiff has the expected projection system

    Assumptions
    1. Input data is a geotiff with a header readable by GDAL
    2. GDAL is working (function tested with GDAL 3.4.1)
    3. Function tested on Python 3.10.12

    Usage example:
    >>> gdgtm.reproject_raster(new_crs = "ESRI:54028", 
    >>>                        source_raster = '/home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_01_01_2023.tif',
    >>>                        dst_raster = '/home/pete/Downloads/chelsa_transformed.tif')
    "File exists: /home/pete/Downloads/chelsa_transformed.tif"
    '''
    import os
    import re
    from osgeo import gdal
    
    ## Open the input raster
    src_ds = gdal.Open(src_raster)

    ## Reproject the input raster to the output raster
    gdal.Warp(dst_raster, src_ds, dstSRS = new_crs)

    ## Close down connections
    dst_ds = None
    src_ds = None
            
    ##Test that the new raster exists
    file_exists = os.path.exists(dst_raster)

    if file_exists:
        return_string = "File exists: " + dst_raster
    else:
        return_string = "Warning, file does not exist: " + dst_raster

    if delete_source and re.match("File exists", return_string):  ## For the delete to work the string in the second part of this condition has to match the successful return string
        os.remove(src_raster)
    
    return return_string
        
                
 
   
# 2.2 change_raster_res  ---------------------------------------
def change_raster_res (target_res, src_raster, dst_raster, delete_source = True):
    
    '''
    The objective of this function is to load a raster from a geotiff, resample it to a set resolution,
    save it to a new file, and optionally delete the source raster.
    
    Args:
        target_res (float): Target resolution in units relevant to the crs     
        src_raster (str): Path to the original raster documents
        dst_raster (str): Path to the file that will hold the re-resolved raster
        delete_source (bool): toggles whether the source raster is to be deleted at the end of the operation
        
    Returns:
        str: string confirming that the new raster has the desired number of pixels (height and width)
        
    Assumptions:
    1. The source_raster is a geotiff.
    2. os, re and GDAL are installed and working (function tested using GDAL 3.4.1)
    3. Function tested using Python 3.10.12
    4. WARNING: Assumes that the new target resolution is provided within the CRS units
    
    Usage example:
    >>> gdgtm.change_raster_res(target_res = 500,
    >>>                         source_raster = "/home/pete/Downloads/chesla_transformed.tif",
    >>>                         dst_raster = "/home/pete/Downloads/chesla_transformed_500.tif")
    "Resolution meets target, file exists: /home/pete/Downloads/chelsa_transformed_500.tif"
        
    
    '''
    
    ## Get the dependencies
    import os
    import re
    from osgeo import gdal
    
    ## Load the source raster into GDAL
    src_ds = gdal.Open(src_raster)

    ## Set the new res
    new_xres = target_res
    new_yres = target_res

    ## Create output raster with the new resolution
    dst_ds = gdal.Warp(dst_raster, src_ds, xRes = new_xres, yRes = new_yres)

    ## Disconnect
    dst_ds = None
    src_ds = None    

    ## Check if new Res matches target
    file_exists = os.path.exists(dst_raster)

    if not file_exists:
        return_string = "Warning, the file does not exist: " + dst_raster
    else:
        dst_geotransform = gdal.Open(dst_raster).GetGeoTransform()
        dst_res = [dst_geotransform[1], -dst_geotransform[5]]
        if dst_res == [target_res, target_res]:
            return_string = "Resolution meets target, file exists: " + dst_raster
        else:
            return_string = "Warning, resolution does not meet the target, file exists: " + dst_raster
    
    ## Run deletion
    if delete_source and re.match("Resolution meets target", return_string):
        os.remove(src_raster)
        
    return return_string




# 2.3 set_raster_boundbox --------------------------------------
def set_raster_boundbox (target_bbox, src_raster, dst_raster, delete_source = True):
    
    '''
    This function loads a geotiff raster, fits it to a new bounding box, saves it as a geotiff file.
    Optionally it deletes the source raster.
    
    Args:
        target_bbox (tuple): Four numbers defining the target for the new BB (Order: WNES). 
        src_raster (str): Path to the original raster documents
        dst_raster (str): Path to the file that will hold the re-resolved raster
        delete_source (bool): toggles whether the source raster is to be deleted at the end of the operation
        
    Returns:
        str: string confirming that the new BB corners match the target spec.
        
    Assumptions:
    1. The source_raster is a geotiff.
    2. os and rasterio are installed and working (function tested using rasterio 1.3.10)
    3. numpy is working (function tested using numpy 1.24.3)
    4. Function tested using Python 3.10.12
    
    Usage example:
    >>> new_bb = (556400, 5254900, 566200, 5238900)
    >>> gdgtm.set_raster_boundbox(target_bbox = new_bb,
    >>>                           source_raster = "/home/pete/Downloads/chelsa_rescaled_2000.tif",
    >>>                           dst_raster = "/home/pete/Downloads/chelsa_new_bb.tif")
    "Warning, setting errors > 0.01 and file exists: /home/pete/Downloads/chelsa_transformed_500_cropped.tif"
    
    '''
    
    ##Imports:
    import os
    import re
    from osgeo import gdal
    
    ## Load the raster
    src_ds = gdal.Open(src_raster)
    
    ## Get input raster projection and geotransform
    dst_ds = gdal.Translate(dst_raster, src_ds, projWin = target_bbox)

    ## Reset the connections
    dst_ds = None
    src_ds = None
    
    ## QC the outputs
    file_exists = os.path.exists(dst_raster)

    if not file_exists:
        return_string = "Warning, the file does not exist: " + dst_raster
    else:
        ## Set up the QC calculation: difference between the positions of the NW corner in the target_bbox and the actual raster, divided by raster width/height
        dst_geotransform = gdal.Open(dst_raster).GetGeoTransform()
        dst_width = gdal.Open(dst_raster).RasterXSize * dst_geotransform[1]
        dst_height = gdal.Open(dst_raster).RasterYSize * -dst_geotransform[5]
        nw_corner = [dst_geotransform[3], dst_geotransform[0]]

        x_error = abs((nw_corner[1] - target_bbox[0]) / dst_width)
        y_error = abs((nw_corner[0] - target_bbox[1]) / dst_height)

        if max(x_error, y_error) < 0.01:
            return_string = "Setting errors < 0.01 and file exists: " + dst_raster
        else:
            return_string = "Warning, setting errors > 0.01 and file exists: " + dst_raster

    ## Run deletion
    if delete_source and re.match("Setting errors < 0.01", return_string):
        os.remove(src_raster)

    return return_string

    



#-------------------------------------------------------------



##############################################################
########## 3. Data alignment and validation Functions ########
##############################################################

### Data alignment and validation function list
### 3.1 align_raster: wrapper function for GDAL align raster
### 3.2 validate_raster_alignment: executes checks whether two rasters are truly aligned (coords, pixels, etc.)
### 3.3 align_validate_raster: take a raw and align it, while running the check underneath. Includes automatic re-projection if necessary


# 3.1 align_raster -------------------------------------------
def align_raster (source_raster, target_raster, dst_raster, delete_source = True):
    '''
    This function aligns the source_raster to the target_raster
    
    **Args:**
        - source_raster (str): link to the geotiff location of the source raster.
        - target_raster (str): link to the geotiff location of the target raster.
        - dst_raster (str): path (including name) to the destination where the raster is saved.
        - delete_source (bool): if True, delete source raster after completing the function.
    
    
    **Returns:**
        - str: confirmation that dst_raster exists
    
    **Assumptions:**
    1. All input files are geotiffs.
    2. os and GDAL are installed and working (function tested using GDAL 3.4.1)
    3. Function tested using Python 3.10.12
    
    **Usage:**
    >>> align_raster(source_raster = "/home/pete/Documents/tests_and_vals/gdgtm/02_master_reprojected/olm_alc_switz_reproj_20040101.tif",
    >>>              target_raster = "/home/pete/Documents/tests_and_vals/gdgtm/04_master_rebound/olm_alc_switz_rebound_100_20040101.tif",
    >>>              dst_raster = "/home/pete/Documents/tests_and_vals/gdgtm/05_supplements_aligned/olm_alc_switz_aligned_20040101.tif",
    >>>              delete_source = False)
    "/home/pete/Documents/tests_and_vals/gdgtm/05_supplements_aligned/olm_alc_switz_aligned_20040101.tif exists"
    

    '''
    ##Import dependencies
    from osgeo import gdal
    import os
    
    ##Import the rasters into GDAL
    target_ds = gdal.Open(target_raster)
    source_ds = gdal.Open(source_raster)
    
    ##Extract projection and geotransform meta
    target_geotransform = target_ds.GetGeoTransform()
    target_projection = target_ds.GetProjection()
    
    ##Get target resolution and set output bounds
    x_res = target_geotransform[1]
    y_res = target_geotransform[5]
        
    output_bounds = [target_geotransform[0], 
                     target_geotransform[3] + target_ds.RasterYSize * y_res, 
                     target_geotransform[0] + target_ds.RasterXSize * x_res, 
                     target_geotransform[3]]

    ##Execute the alignment using GDAL warp function        
    aligned_ds = gdal.Warp(dst_raster, source_ds, xRes = x_res, yRes = y_res, 
                           outputBounds = output_bounds, resampleAlg = gdal.GRA_NearestNeighbour, 
                           dstSRS = target_projection)

    ##Disconnect from the files.
    target_ds = None
    source_ds = None
    aligned_ds = None ##Particularly important to ensure that the file is correct
    
    ##Run the checks and the deletion
    aligned_raster_exists = os.path.exists(dst_raster)
    
    if delete_source and aligned_raster_exists:
        os.remove(source_raster)
    
    
    
#3.2 validate_raster_alignment -------------------------------
def validate_raster_alignment (raster_1, raster_2):
    '''
    This function checks whether two rasters are aligned: i.e. whether they have the same number of pixels and whether these pixels have identical coordinates
    
    **Args:**
        - first_raster (str): link to the geotiff location of the first raster
        - second_raster (str): link to the geotiff location of the second raster
        
    **Returns:**
        - bool: check whether the two rasters are aligned
        
    **Assumptions:**
    1. All input files are geotiffs.
    2. os and GDAL are installed and working (function tested using GDAL 3.4.1)
    3. Function tested using Python 3.10.12
    
    **Usage:**
    >>> validate_raster_alignment("/home/pete/Documents/tests_and_vals/gdgtm/04_master_rebound/olm_alc_switz_rebound_100_20040101.tif",
    >>>                           "/home/pete/Documents/tests_and_vals/gdgtm/05_supplements_aligned/olm_alc_switz_aligned_20040101.tif")
       
    {'dimension_match': False,
     'projection_match': True,
     'pixel_count_match': False,
     'geotransform_match': False}
                                
    
    '''
    from osgeo import gdal
    
    ## Get the rasters loaded into GDAL
    raster_1 = gdal.Open(raster_1)
    raster_2 = gdal.Open(raster_2)
    
    ##Check rows and cols (Dimension match)
    rows1, cols1 = raster_1.RasterYSize, raster_1.RasterXSize
    rows2, cols2 = raster_2.RasterYSize, raster_2.RasterXSize
          
    check_results = {"dimension_match": (rows1 == rows2 and cols1 == cols2)}
    
    ##Check projection match
    proj_1 = raster_1.GetProjection()
    proj_2 = raster_2.GetProjection()
    
    check_results.update({"projection_match": proj_1 == proj_2})
    
    ##Check pixels match:
    num_pixels_1 = rows1 * cols1
    num_pixels_2 = rows2 * cols2
    
    check_results.update({"pixel_count_match": num_pixels_1 == num_pixels_2})
    
    ##Check if geotransforms match (implies pixel location match):
    geotransform_1 = raster_1.GetGeoTransform()
    geotransform_2 = raster_2.GetGeoTransform()
    
    check_results.update({"geotransform_match": geotransform_1 == geotransform_2})
    
    ## return val check results
    return check_results
    
    

#3.3 align_validate_raster -----------------------------------

def align_validate_raster (source_raster, target_raster, dst_raster, delete_source = True):
    '''
    This function aligns the source_raster to the target_raster
    
    **Args:**
        - source_raster (str): link to the geotiff location of the source raster.
        - target_raster (str): link to the geotiff location of the target raster.
        - dst_raster (str): path (including name) to the destination where the raster is saved.
        - delete_source (bool): if True, delete source raster after completing the function.
    
    
    **Returns:**
        - str: confirmation that dst_raster exists and matches the target raster
    
    **Assumptions:**
    1. All input files are geotiffs.
    2. os and GDAL are installed and working (function tested using GDAL 3.4.1)
    3. Function tested using Python 3.10.12
    4. Function relies on gdgtm.reproject_raster 
    5. Rasterio is working (function tested with rasterio 1.3.10)
    
    **Usage:**
    >>> align_validate_raster(source_raster = "/home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/olm_alc_switz_reproj_20040101.tif",
    >>>                       target_raster = "/home/pete/Documents/tests_and_vals/gdgtm/04_master_rebound/olm_alc_switz_rebound_100_20040101.tif",
    >>>                       dst_raster = "/home/pete/Documents/tests_and_vals/gdgtm/05_supplements_aligned/olm_alc_switz_aligned_20040101.tif",
    >>>                       delete_source = False)
    
    {'dimension_match': True,
     'projection_match': True,
     'pixel_count_match': True,
     'geotransform_match': True}
    

    '''
    ## Import dependencies
    from osgeo import gdal
    import rasterio
    import os
    from gdgtm import reproject_raster
    
    ##Load the two rasters into GDAL objects
    source_ds = gdal.Open(source_raster)
    target_ds = gdal.Open(target_raster)
    
    ##Check projection match
    source_projection = source_ds.GetProjection()
    target_projection = target_ds.GetProjection()
    
    projection_check = (source_projection == target_projection)
    
    ##If projection does not match, reproject
    if not projection_check:
        with rasterio.open(target_raster) as target:
            target_crs = target.crs
            
        reproject_raster(new_crs = target_crs, 
                         src_raster = source_raster,
                         dst_raster = 'temp_reproj_source.tif',
                         delete_source = False)
    
    ##We want to preserve the original source_raster value, hence the need for a different arg here.
    ##Why? With the input source_raster overwritten, the downstream optional source deletion is no longer a viable option.
    if projection_check:
        projected_source_loc = source_raster
    else:
        projected_source_loc = "temp_reproj_source.tif"
    
    ##Align the two rasters
    align_raster(source_raster = projected_source_loc,
                 target_raster = target_raster,
                 dst_raster = dst_raster,
                 delete_source = False)
    
    ##Run the alignment check
    alignment_outcome = validate_raster_alignment(target_raster, dst_raster)
    
    if not projection_check:
        os.remove("temp_reproj_source.tif")
        
    if delete_source and os.path.exists(dst_raster):
        os.remove(source_raster)
      
    return alignment_outcome
          
        
    
#-------------------------------------------------------------


