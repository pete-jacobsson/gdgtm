### Functions forming the core workflow of the gdgtm package.



### 1. Data getting functions
### 2. Data processing functions
### 3. Data validation functions


##############################################################
########## 1. Data getting Functions #########################
##############################################################

### Data getting function list
### 1.1 get_chelsa_data: gets data from Chelsa (bound-setting available natively)




#-------------------------------------------------------------
### get_chelsa_data

def get_chelsa_data (parameter, extent, start_date, end_date, write_location):
    """
    This function gets a cropped raster from Chelsa (https://chelsa-climate.org/), saves it as a .tiff to designated folder, checks that the .tiff exists, and prints a confirmation to the console.

    Args:
        parameter (str): The name of the variable used by Chelsa to find the intended data (has to be CMIP5 standard short name - specifies what climate varia is desired).
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
    
#---------------------------------------------------------------



##############################################################
########## 2. Data processing Functions ######################
##############################################################

### Data processing function list
### 2.1 reproject_raster: wrapper function for rasterio reprojection

### The function takes on the target projection, creates a re-projected .tiff
### Function should send a confirm message that it re-projected correctly
### Assumes rasterio and numpy packages are installed on the machine
### Assumes new coord system name is recognized by rasterio
### Assumes the following have been imported:
# import numpy as np
# import rasterio
# from rasterio.warp import calculate_default_transform, reproject, Resampling

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
            return print("Transform successful")
        else:
            return_string = "target crs is " + new_crs + ", but the transform returned " + dst.crs
            raise Exception(return_string)

    ##Delete source if required:
    if delete_source and return_string == "Transform successful":
        os.remove(source_raster)
        
    return return_string
    

#---------------------------------------------------------------



##############################################################
########## 3. Data validation Functions ######################
##############################################################








