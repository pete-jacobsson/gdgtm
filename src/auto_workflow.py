import numpy as np
import rasterio
from rasterio.errors import RasterioIOError
import warnings
from rasterio.errors import NotGeoreferencedWarning
import rasterio
from rasterio.transform import Affine
import gdgtm


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



###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    {'/home/pete/Documents/tests_and_vals/gdgtm_dev_copy/down_aligned.tif': {'dimension_match': True, 'projection_match': True, 'pixel_count_match': True, 'geotransform_match': True}}
         
    '''
    
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
