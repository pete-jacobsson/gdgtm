### These functions cover raster transofrmations: changing resolution, aligning, set bounding boxes, reprojecting (as well as relevant helper functions).


### Function set-up~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def set_raster_boundbox(target_bbox, src_raster, dst_raster = None):
    '''
    This function loads a geotiff raster, fits it to a new bounding box, saves it as a geotiff file.
    The function tests if the new bounds are in excess of the new bounds and if so amaneds the new bounds.
    
    Args:
        target_bbox (list): Four numbers defining the target for the new BB (Order: WNES). 
        src_raster (str): Path to the original raster documents
        dst_raster (str): Path to the file that will hold the re-resolved raster
        
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
    "File exists: /home/pete/Downloads/chelsa_transformed_500_cropped.tif"
    
    '''
    
    
    with rasterio.open(src_raster) as src:
        # Get the bounds of the source raster
        src_bounds = src.bounds

        target_bbox[0] = max(target_bbox[0], src_bounds.left)
        target_bbox[1] = min(target_bbox[1], src_bounds.top)
        target_bbox[2] = min(target_bbox[2], src_bounds.right)
        target_bbox[3] = max(target_bbox[3], src_bounds.bottom)
        
        
        # Define the bounding box in geographic coordinates
        west = target_bbox[0]
        south = target_bbox[3]
        east = target_bbox[2]
        north = target_bbox[1]
    
        # Create the window from bounds
        window = from_bounds(west, south, east, north, transform=src.transform)
    
        # Read the data within the window
        data = src.read(1, window=window)
    
        # Get the affine transform for the window
        transform = src.window_transform(window)
    
        # Optionally, you can update the profile for the cropped data
        profile = src.profile.copy()
        profile['transform'] = transform
        profile['width'] = window.width
        profile['height'] = window.height
    
        # show(data)
    
        # Save the cropped data
        with rasterio.open(dst_raster, 'w', **profile) as dst:
            dst.write(data, 1)  

        ### TODO: Implement a check

        return f"{src_raster} now set to bounding box {target_bbox}"
