### Functions forming the core workflow of the gdgtm package.



### 1. Data getting functions
### 2. Data processing functions
### 3. Data alignment and validation functions


##############################################################
########## 1. Data getting Functions #########################
##############################################################

### Data getting function list
### 1.1 get_chelsa_data: gets data from Chelsa (bound-setting available natively)
### 1.2 get_cognames_from_stac_coll_static
### 1.3 get_cogs_from_olm




# 1.1 get_chelsa_data ----------------------------------------

def get_chelsa_data (parameter, extent, start_date, end_date, write_location):
    """
    This function gets a cropped raster from Chelsa (https://chelsa-climate.org/), saves it as a .tiff to designated folder, checks that the .tiff exists, and prints a confirmation to the console.

    Args:
        parameter (str): The name of the variable used by Chelsa to find the intended data (has to be CMIP5 standard short name - specifies what climate varia is desired, see https://chelsa-climate.org/wp-admin/download-page/CHELSA_tech_specification_V2.pdf for possible varias).
        extent (list): a list of four decimals defining the grid square covered. 
        start_date (str): a yyyy-mm-dd formatted string determining the start date for Chelsa data
        end_date (str): a yyyy-mm-dd formatted string determining the end date for Chelsa data
        write_location (str): location to which the downloaded .tiff is written

    Returns:
        str: string confirming that the intended .tiff indeed exists in the target location

    Assumptions:
    1. Rchelsa, lubridate, and terra R packages are installed (function tested using versions 1.0.1, 1.9.3, and 1.7.71 respectively)
    2. os and rpy2 Python modules are working (function tested using rpy 3.5.16)
    3. R version 4.1+ has been installed (function tested using R 4.1.2)
    4. Python 3 (function tested using Python 3.10.12)

    Usage example:
    >>> parameter = "tas"
    >>> extent = [7.3, 7.5, 47.0, 47.2]
    >>> start_date = "2023-1-1"
    >>> end_date = "2023-2-2"
    >>> get_chelsa_data(parameter, extent, start_date, end_date, write_location = '/home/pete/Downloads/chesla_temp.tif')
    "Target .tiff exists"

    """
    
    ## Import the relevant Python and R packages with names corresponding to those used in the current function
    import os
    import rpy2.robjects as robjects
    import rpy2.rinterface as rinterface
    from rpy2.robjects.packages import importr
    
    rchelsa = importr('Rchelsa')
    lubridate = importr('lubridate')
    terra = importr('terra')
    
    ## Convert Python objects to R objects for the Rchelsa to work (https://rpy2.github.io/doc/v2.9.x/html/vector.html)
    start_date = lubridate.ymd(start_date)
    end_date = lubridate.ymd(end_date)
    extent = rinterface.FloatSexpVector(extent)
    overwrite_true = rinterface.BoolSexpVector("TRUE")
    
    ## Get the bounded raster and store it as an R S4 class 'SpatRaster'
    framed_raster = rchelsa.getChelsa(parameter, extent = extent, startdate = start_date, enddate = end_date)
    
    ## Put the Chesla .tiff into a temp location
    terra.writeRaster(framed_raster, write_location, overwrite = overwrite_true)
    
    ## Check the file exists: note this depends on location clearing in downstream processing
    if os.path.isfile(write_location):
        return "Target .tiff exists"
    else:
        raise Exception("Target .tiff does not exist")

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
                       date_start = "00010101", 
                       date_end = "99991231"
                      ):
    '''
    The function uses a list of OpenLandMap cog locations to download a set of rasters bound in space and time
    
    Args:
        cognames (list): list of names of geotiffs in the OLM S3 bucket associated with the STAC collection of interest
        target_directory (str): directory to which the files will be saved
        target_names (str): the convention name for the files to be downlaoded
        bbox (tupple): a tupple of floats indicating the WGS84 (EPSG:4326) coordinates of the bounding box used to crop the rasters downloaded. Defaults to entire grid (-180, 180, 180, -180)
        date_start (str): date before which the data are ignored. Needs to be provided in the yyyymmdd format. Defaults to 01JAN0001.
        date_end (str): date after which the data are ignored. Needs to be provided in the yyyymmdd format. Defaults to 31DEC9999.
    
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
    >>> gdgtm.get_cogs_from_olm(cognames = test, 
    >>>                   	target_directory = "/home/pete/Downloads/", 
    >>>                   	target_names = "olm_humfoot_switz_raw_",
    >>>                   	bbox = bbox,
    >>>                   	date_start = "20000601",
    >>>                   	date_end = "20050101"
    >>>                        )
    
    /home/pete/Downloads/olm_humfoot_switz_raw_20010101.tif
    /home/pete/Downloads/olm_humfoot_switz_raw_20020101.tif
    /home/pete/Downloads/olm_humfoot_switz_raw_20030101.tif
    /home/pete/Downloads/olm_humfoot_switz_raw_20040101.tif
    
    '''
    ## Import GDAL
    from osgeo import gdal
    
    ## Loop getting the rasters
    for raster_name in cognames:
        ## Filter based on date
        raster_ymd = raster_name.split("-doy")[0].split("_")[-5: -3]  ###This gets the dates out of the raster_name
        if min(raster_ymd) > date_start and max(raster_ymd) < date_end: ## Apply filter
            src_raster = gdal.Open(raster_name) ##Get the actual raster
            new_raster_name = target_directory + target_names + raster_ymd[0] +".tif"
            
            ##Apply bbox and save in target location
            gdal.Translate(new_raster_name, src_raster, projWin = bbox)
            
            ## Disconnect from file
            src_raster = None
            print(new_raster_name) ## Print file name to confirm operation successful
            
        

#---------------------------------------------------------------



##############################################################
########## 2. Data processing Functions ######################
##############################################################

### Data processing function list
### 2.1 reproject_raster: wrapper function for rasterio reprojection
### 2.2 change_raster_res: wrapper for changing resolution with rasterio
### 2.3 set_raster_boundbox: wrapper for re-setting the bounding box with gdal

# 2.1 reproject_raster ---------------------------------------

def reproject_raster (new_crs, source_raster, dst_raster, delete_source = True):
    '''
    This function takes a geotiff raster (with metadata include coordinate projection) and turns out a geotiff raster with updated projection and a check that the new file projection matches the desired target.
    The function also has the option to do source deletion (e.g. for DM purposes)

    Args:
        new_crs (str): New coordinate system to which the raster is to be projected to.
        source_raster (str): path to the geotiff with relevant metadata that will be reprojected
        dst_raster (str): path and filename into which new (re-projected) raster will be saved
        delete_source (bool): determines whether source raster is deleted following function execution

    Resturns:
        str: string confirming that the new geotiff has the expected projection system

    Assumptions
    1. Input data is a geotiff with a header readable by rasterio
    2. Rasterio is working (function tested with rasterio 1.3.10)
    3. Function tested on Python 3.10.12
    4. Numpy is working (function tested with numpy 1.24.3)

    Usage example:
    >>> gdgtm.reproject_raster(new_crs = "ESRI:54028", 
    >>>                        source_raster = '/home/pete/Downloads/chesla_temp.tif',
    >>>                        dst_raster = '/home/pete/Downloads/chesla_transformed.tif')
    "Transform successful"

    '''
    
    #Get dependencies loaded
    import os
    import numpy as np
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling

    dst_crs = new_crs #Set the new crs
        
    ##Get source meta, calculate the transform, upgrade arguments.
    with rasterio.open(source_raster) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        
        ##Generate reprojected raster
        with rasterio.open(dst_raster, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)
    
    ##Delete source raster
    
    
    ##Test that the new raster is correct crs
    with rasterio.open(dst_raster) as dst:
        check = dst.crs == new_crs
        if check:
            return_string = "Reprojection successful"
        else:
            return_string = "Reprojection not successful: target crs is " + new_crs + ", but the transform returned " + dst.crs

    ##Delete source if required:
    if delete_source and return_string == "Reprojection successful":  ## For the delete to work the string in the second part of this condition has to match the successful return string
        os.remove(source_raster)
        
    return print(return_string)
    

# 2.2 change_raster_res  ---------------------------------------
def change_raster_res (target_res, source_raster, dst_raster, delete_source = True):
    
    '''
    The objective of this function is to load a raster from a geotiff, resample it to a set resolution,
    save it to a new file, and optionally delete the source raster.
    
    Args:
        target_res (float): Target resolution in units relevant to the crs     
        source_raster (str): Path to the original raster documents
        dst_raster (str): Path to the file that will hold the re-resolved raster
        delete_source (bool): toggles whether the source raster is to be deleted at the end of the operation
        
    Returns:
        str: string confirming that the new raster has the desired number of pixels (height and width)
        
    Assumptions:
    1. The source_raster is a geotiff.
    2. os and rasterio are installed and working (function tested using rasterio 1.3.10)
    3. numpy is working (function tested using numpy 1.24.3)
    4. Function tested using Python 3.10.12
    5. WARNING: Assumes that the new target resolution is provided within the CRS units
    
    Usage example:
    >>> gdgtm.change_raster_res(target_res = 500,
    >>>                         source_raster = "/home/pete/Downloads/chesla_transformed.tif",
    >>>                         dst_raster = "/home/pete/Downloads/chesla_rescaled.tif")
    "Resolution change successful: new pixel size matches target"
        
    
    '''
    
    ## Get the dependencies
    import os
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    
    ## Do the transform - this is calculating all the infor necessary for the res change
    with rasterio.open (source_raster) as src:
        ## Get dst_crs (same as source - we are not re-projecting here!!!)
        dst_crs = src.crs # Can be skipped - kept for legibility four lines below :)
        
        ## Calculate the transform matrix that will be used to resample
        transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds, resolution = target_res)
        
        #Create reprojected raster and update meta
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform, 
            'width': width,
            'height': height
        })
        
    
        with rasterio.open(dst_raster, 'w', **kwargs) as dst:
            # Reproject bands
            for i in range(1, src.count+1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest
                )
    
    with rasterio.open(dst_raster) as dst:
        dst_dims = [abs(dst.transform[0]), abs(dst.transform[4])]
        check = dst_dims == [abs(target_res), abs(target_res)]
        if check:
             return_string = "Resolution change successful: new pixel size matches target"
        else:
             return_string = "Resolution not successful: target pixel size is: " + target_res + ", but the actual new pixel size is: " + dst.transform[0] + " by " + abs(dst.transform[4])
    
    ##Delete source if required:
    if delete_source and return_string == "Resolution change successful: new pixel size matches target":  ## For the delete to work the string in the second part of this condition has to match the successful return string
        os.remove(source_raster)
    
    return print(return_string)



# 2.3 set_raster_boundbox --------------------------------------
def set_raster_boundbox (target_bb, source_raster, dst_raster, delete_source = True):
    
    '''
    This function loads a geotiff raster, fits it to a new bounding box, saves it as a geotiff file.
    Optionally it deletes the source raster.
    
    Args:
        target_bb (list): list of four numbers defining the target for the new BB (Order: L, B, R, T). 
        source_raster (str): Path to the original raster documents
        dst_raster (str): Path to the file that will hold the re-resolved raster
        delete_source (bool): toggles whether the source raster is to be deleted at the end of the operation
        
    Returns:
        str: string confirming that the new BB corners match the target spec.
        
    Assumptions:
    1. The source_raster is a geotiff.
    2. os, GDAL, and rasterio are installed and working (function tested using GDAL 3.4.1 and rasterio 1.3.10)
    3. numpy is working (function tested using numpy 1.24.3)
    4. Function tested using Python 3.10.12
    
    Usage example:
    >>> new_bb = [556400, 5238900, 566200, 5254900]
    >>> gdgtm.set_raster_boundbox(target_bb = new_bb,
    >>>                           source_raster = "/home/pete/Downloads/chelsa_rescaled_2000.tif",
    >>>                           dst_raster = "/home/pete/Downloads/chelsa_new_bb.tif")
    "New bounding box implemented successfully: all dimensions match"
    
    '''
    
    ##Imports:
    import os
    import rasterio
    from osgeo import gdal
    
    ## Load the raster
    input_raster = gdal.Open(source_raster)
    
    ## Set the bound box (LBRT = xmin, ymin, xmax, ymax)
    xmin = target_bb[0]; ymin = target_bb[1]; xmax = target_bb[2]; ymax = target_bb[3]
    
    ## Get input raster projection and geotransform
    gdal.Translate(dst_raster, input_raster, projWin = [xmin, ymax, xmax, ymin])
    
    ## QC the output
    with rasterio.open(dst_raster) as dst:  #will crash if ouput does no exist.
        dst_bounds = dst.bounds
        bound_error_x = abs((dst_bounds[0] - target_bb[0]) / (dst_bounds[2] - dst_bounds[0]))
        bound_error_y = abs((dst_bounds[1] - target_bb[1]) / (dst_bounds[3] - dst_bounds[1]))
        
        if max(bound_error_x, bound_error_y) < 0.01:
            return_string = "Setting new bounding box successful: errors relative to target < 0.01"
        else:
            return_string = "Setting new bounding box not successful: errors relative to target > 0.01"
        

    ##Delete source if required:
    if delete_source and return_string == "Setting new bounding box successful: errors relative to target < 0.01":  ## For the delete to work the string in the second part of this condition has to match the successful return string
        os.remove(source_raster)
    
    return print(return_string)



#-------------------------------------------------------------



##############################################################
########## 3. Data alignment and validation Functions ########
##############################################################

### Data alignment and validation function list
### 3.1 align_raster: wrapper function for GDAL align raster
### 3.2 validate_raster_alignment: executes checks whether two rasters are truly aligned (coords, pixels, etc.)
### 3.3 align_validate_raster: take a raw and align it, while running the check underneath. Includes automatic re-projection if necessary


# 3.1 align_raster -------------------------------------------

#3.2 validate_raster_alignment -------------------------------

#3.2 align_validate_raster -----------------------------------



