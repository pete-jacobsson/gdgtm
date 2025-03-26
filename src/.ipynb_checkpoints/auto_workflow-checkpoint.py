###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
### Functions for setting the bounding box based on NW corner coordinates #####
###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_nearest_pixel(dataset, lon, lat):
    # Convert geographic coordinates to pixel coordinates
    py, px = dataset.index(lon, lat)
    return int(px), int(py)

def extract_window(dataset, px, py, width=128, height=128):
    # Create a window object
    window = Window(px, py, width, height)
    
    # Read the data within the window
    return dataset.read(window=window)

def check_window_values(data, threshold=0.5):
    return np.any(data > threshold)


def random_square_from_raster(raster_width, raster_height, seed=None):
    # Set the random seed
    rng = np.random.default_rng(seed)
    
    # Ensure the raster is large enough
    if raster_width < 128 or raster_height < 128:
        raise ValueError("Raster dimensions must be at least 128x128")
    
    # Generate random top-left corner coordinates
    x_max = raster_width - 128
    y_max = raster_height - 128
    x = rng.integers(0, x_max + 1)
    y = rng.integers(0, y_max + 1)
    
    return x, y + 128



###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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



###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def check_if_geotiff (file_path):
    '''
    This function checks if a given file is a geotiff

    **Args:**
        - file_path (str): path (including filename) to the raster to be tested. Can be local or URL.

    **Returns:**
        - dict: Indication of point of failure and whether file is a GeoTIFF

    **Assumptions:**
        1. Function developed and tested using Python 3.10.14 and rasterio 1.4.3 working under conda 24.4.0 virtual environment.

    **Usage:**
    >>>    test = check_if_geotiff("https://s3.openlandmap.org/arco/bulkdens.fineearth_usda.4a1h_m_250m_b0cm_19500101_20171231_go_epsg.4326_v0.2.tif")
    >>>    print(test)
    {"File is GeoTIFF": True}

    >>>    test = check_if_geotiff("/home/pete/Documents/tests_and_vals/gdgtm_dev_copy/lol_cat.tif")
    >>>    print(test)
    {"src.crs": False}
    '''
    import rasterio
    from rasterio.errors import RasterioIOError
    import warnings
    from rasterio.errors import NotGeoreferencedWarning

    warnings.filterwarnings("ignore", category=NotGeoreferencedWarning) ### Suppress warnings
    
    try:
        with rasterio.open(file_path) as src:
            # Check if file opened successfully
            if src is None:
                return {"rasterio.open": False}

            # Check projection
            if src.crs is None:
                return {"src.crs": False}

            # Check if file has a valid transform
            if src.transform == rasterio.transform.Affine(1, 0, 0, 0, 1, 0):
                return {"src.transform": False}

        return {"File is GeoTIFF": True}

    except RasterioIOError as e:
        return {"RasterioIOError": str(e)}
    except Exception as e:
        return {str(type(e).__name__): str(e)}



###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def set_up_blank (bbox, proj, pixel_size, dst_raster, dtype = "uint16"):
    '''
    This function takes a projection and a bbox, and sets up a blank geotiff 
    raster to those specifications using rasterio.

    **Args:**
        - bbox (tuple): WNES bbox (west, north, east, south)
        - proj (str): authority:code formatted projection (e.g., "EPSG:4326")
        - pixel_size (float): pixel edge length in projection units
        - dst_raster (str): output file path
        - dtype (str): data type used. Note that this will propagate in automated workflows.

    **Returns:**
        - list: [CRS string, transform coefficients list]

    **Usage:**
    >>> bbox = (5, 47, 8, 45)  # West, North, East, South
    >>> proj = "EPSG:4326"
    >>> pixel_size = 0.01
    >>> output = set_up_blank(bbox, proj, pixel_size, "blank.tif")
    >>> print(output)
    ['EPSG:4326', [0.01, 0.0, 5.0, 0.0, -0.01, 47.0, 0.0, 0.0, 1.0]] 
    '''
    import numpy as np
    import rasterio
    from rasterio.transform import Affine
    
    west, north, east, south = bbox
        
    # Calculate raster dimensions
    width = int((east - west) / pixel_size)
    height = int((north - south) / pixel_size)
    
    # Create affine transform matrix
    transform = Affine(pixel_size, 0, west,
                       0, -pixel_size, north)
    
    # Define raster profile
    profile = {
        'driver': 'GTiff',
        'width': width,
        'height': height,
        'count': 1,
        'dtype': dtype,
        'crs': rasterio.crs.CRS.from_string(proj),
        'transform': transform,
        'nodata': 1,
        'tiled': True,         # Enable tiling for large rasters
        'compress': 'lzw'      # Add lossless compression
    }
    print(profile)
    
    # Create blank raster with zeros
    with rasterio.open(dst_raster, 'w', **profile) as dst:
        dst.write(np.zeros((height, width), dtype=dtype), 1)
    
    return [proj, list(transform.to_gdal()) + [0.0, 0.0, 1.0]]