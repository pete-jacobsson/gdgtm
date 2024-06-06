### Functions for converting rasters into numpy arrays

## 1 numpyify_raster - converts a GeoTiff into an in-memory np.array. NOTE: In the current gdgtm version single band rasters only.
## 2 save_numpd_raster - uses numpyify_raster to create an array and then saves it into a textfile, alongside the geo-metadata.

# 1 numpify_raster ------------------------------------------------------------
def numpyify_raster (src_raster):
    '''
    This function takes on a GeoTIFF and converts it into a numpy array. 
    At the moment the function is restricted to working with single-band rasters.
    
    **Args:**
        - src_raster (str): path to the source raster

    **Returns:**
        - np.array: raster in np.array form

    **Assumptions:**
    1. Input file is a single band raster
    2. GDAL and numpy are working (function tested using versions 3.4.1 and 1.24.3)
    3. Function tested using Python 3.10.12

    **Usage:**
    >>> test = numpyify_raster("/home/pete/Downloads/sample_shape_rasterized.tif")
    >>> print(test)
    (1030, 2000)
    
    '''
    from osgeo import gdal
    import numpy as np
    import os

    ## Check that file exists
    if not os.path.exists(src_raster):
        return "Warning, src_raster does not exist"
    
    ## Open the raster file
    try:
        src_ds = gdal.Open(src_raster)
    except Exception as e:
        print(f"File {src_raster} cannot be opened by GDAL: {e}")
        
    
    ## Get the raster band
    try:
        raster_band = src_ds.GetRasterBand(1)
    except Exception as e:
        print(f"Cannot get raster band: {e}")

    ## Read the raster data into a NumPy array
    try:
        raster_array = raster_band.ReadAsArray()
    except Exception as e:
        print(f"Cannot read raster band as array: {e}")
        
    ## Close the raster file
    src_ds = None

    if "raster_array" in locals():
        return raster_array
    



# 2 save_numpd_raster ---------------------------------------------------------
def save_numpd_raster (src_raster, dst_txt):
    '''
    The function takes a raster and converts it into a text file consisting of:
    1. a Geo metadata header (line 1)
    2. a numpy array (starting at line 2)

    **Args:**
        - src_raster (str): path to the source raster
        - dst_txt (str): path to the destination text file

    **Returns:**
        - str: a check that the target file exists

    **Assumptions:**
        1. The src_raster is a GeoTIFF
        2. Function tested using: GDAL 3.4.1, numpy 1.24.3 and Python 3.10.12
        3. Function assumes that the shell command gdalinfo will work.

    **Usage:**
    >>> test = save_numpd_raster("/home/pete/Downloads/sample_shape_rasterized.tif", "/home/pete/Downloads/sample_raster_numpd.tif")
    >>> print(test)
    File exists: /home/pete/Downloads/sample_raster_numpd.tif
  
   
    '''
    import subprocess
    import os
    import numpy as np

    ## Check that file exists
    if not os.path.exists(src_raster):
        return "Warning, src_raster does not exist"

    ## Get the metadata -- To keep this contact need to use the shell command gdalinfo
    try: 
        cmd = f"gdalinfo {src_raster}"
        metadata = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        metadata = str(metadata)
      
          
    except Exception as e:
        print(f"Failed to get metadata from {src_raster}: {e}")


    ## Now get the raster in as an np.array:
    try:
        numpd_raster = numpyify_raster(src_raster)
    except Exception as e:
        print(f"Failed to convert {src_raster} to a numpy array: {e}")

    ## Add the array to the .txt file
    np.savetxt(dst_txt, numpd_raster, header = metadata)
        
    if os.path.exists(dst_txt):
        return "File exists: " + dst_txt    