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
### Fuction takes on inputs: chesla parameter (has to be CMIP5 standard short name)
### extent (of the area to be covered: four decimals defining the area in EPSG:4326 - WGS 84)
### start_date and end_date (in "yyyy-mm-dd" format)
### write_location: where do we want the file to be
### Function assumes:
### 1. Rchelsa, lubridate, and terra R packages are installed
### 2. Necessary package imports have been executed:
# import os
# import rpy2.robjects as robjects
# import rpy2.rinterface as rinterface
# from rpy2.robjects.packages import importr
### 3. R version 4.1+ is installed


def get_chelsa_data (parameter, extent, start_date, end_date, write_location):
    
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

def reproject_raster (new_crs, source_raster, dst_raster):
    #Get dependencies loaded
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
                
    ##Test that the new raster is correct crs
    with rasterio.open(dst_raster) as dst:
        check = dst.crs == new_crs
        if check:
            return print("Transform succesful")
        else:
            return_string = "target crs is " + new_crs + ", but the transform returned " + dst.crs
            raise Exception(return_string)
                
    

#---------------------------------------------------------------



##############################################################
########## 3. Data validation Functions ######################
##############################################################








