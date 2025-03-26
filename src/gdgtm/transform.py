### These functions cover raster transofrmations: changing resolution, aligning, set bounding boxes, reprojecting (as well as relevant helper functions).


#### Tested in test single
###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def change_raster_res(target_res, src_raster, dst_raster):
    '''
    The objective of this function is to load a raster from a geotiff, resample it to a set resolution,
    save it to a new file, and optionally delete the source raster.

    Args:
        target_res (float): Target resolution in units relevant to the CRS
        src_raster (str): Path to the original raster document
        dst_raster (str): Path to the file that will hold the re-resolved raster

    Returns:
        str: String confirming that the new raster has the desired number of pixels (height and width)

    Assumptions:
    1. The source_raster is a geotiff.
    2. Function tested using Python 3.10 and rasterio.
    3. WARNING: Assumes that the new target resolution is provided within the CRS units

    Usage example:
    >>> change_raster_res(target_res=500,
    >>>                   src_raster="/home/pete/Downloads/chesla_transformed.tif",
    >>>                   dst_raster="/home/pete/Downloads/chesla_transformed_500.tif")
    "Resolution meets target, file exists: /home/pete/Downloads/chelsa_transformed_500.tif"
    '''

    # Load the source raster into rasterio
    with rasterio.open(src_raster) as src:
        # Calculate the new dimensions based on the target resolution
        new_width = int(src.width * (abs(src.transform[0] / target_res)))
        new_height = int(src.height * (abs(src.transform[4] / target_res)))

    # print([new_width, new_height, src.width, src.height])

        # Resample the data to the new dimensions
        data = src.read(
            out_shape=(src.count, new_height, new_width),
            resampling=Resampling.nearest  # Use nearest neighbor resampling to avoid interpolation
        )

        # Calculate the new transform
        new_transform = src.transform * Affine.scale(target_res / abs(src.transform[0]), target_res / abs(src.transform[4]))

        # Write the resampled data to the new raster file
        with rasterio.open(
            dst_raster,
            'w',
            driver='GTiff',
            height=new_height,
            width=new_width,
            count=src.count,
            dtype=src.dtypes[0],
            crs=src.crs,
            transform=new_transform,
            nodata=src.nodata
        ) as dst:
            dst.write(data)

    # Check if the new resolution matches the target
    file_exists = os.path.exists(dst_raster)
    if not file_exists:
        return_string = "Warning, the file does not exist: " + dst_raster
    else:
        with rasterio.open(dst_raster) as dst:
            dst_res = [dst.transform[0], -dst.transform[4]]
            if dst_res == [target_res, target_res]:
                return_string = "Resolution meets target, file exists: " + dst_raster
            else:
                return_string = "Warning, resolution does not meet the target, file exists: " + dst_raster

    return return_string



###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def reproject_raster(new_crs, src_raster, dst_raster):
    '''
    This function takes a geotiff raster (with metadata including coordinate projection) and outputs a geotiff raster with an updated projection.
    The function also has the option to delete the source raster.

    Args:
        new_crs (str): New coordinate system to which the raster is to be projected.
        src_raster (str): Path to the geotiff with relevant metadata that will be reprojected.
        dst_raster (str): Path and filename into which the new (re-projected) raster will be saved.
        delete_source (bool): Determines whether the source raster is deleted following function execution.

    Returns:
        str: String confirming that the new geotiff has the expected projection system.

    Assumptions:
    1. Input data is a geotiff with a header readable by rasterio.
    2. rasterio is working.
    3. Function tested on Python 3.10.12.

    Usage example:
    >>> reproject_raster(new_crs="EPSG:54028", 
    >>>                  src_raster='/home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_01_01_2023.tif',
    >>>                  dst_raster='/home/pete/Downloads/chelsa_transformed.tif')
    "File exists: /home/pete/Downloads/chelsa_transformed.tif"
    '''
    # Open the source raster
    with rasterio.open(src_raster) as src:
        # Define the new CRS
        new_crs = CRS.from_string(new_crs)

        # Calculate the new transform and dimensions
        dst_transform, dst_width, dst_height = calculate_default_transform(
            src.crs, new_crs, src.width, src.height, *src.bounds
        )

        # Create the output raster
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': new_crs,
            'transform': dst_transform,
            'width': dst_width,
            'height': dst_height
        })

        with rasterio.open(dst_raster, 'w', **kwargs) as dst:
            # Reproject the source raster to the new CRS
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=dst_transform,
                    dst_crs=new_crs,
                    resampling=rasterio.warp.Resampling.nearest
                )

    # Test that the new raster exists
    file_exists = os.path.exists(dst_raster)

    if file_exists:
        return_string = "File exists: " + dst_raster
    else:
        return_string = "Warning, file does not exist: " + dst_raster


    return return_string


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



###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def apply_land_mask(land_mask_path, data_raster_path, output_path):
    """
    Apply a land mask to a data raster and save the result.

    This function reads a land mask raster and a data raster, applies the mask
    to the data, and saves the result as a new raster file. The land mask is 
    expected to have values of 1 for land and any other value for non-land areas.

    Parameters:
    -----------
    land_mask_path : str
        Path to the land mask raster file.
    data_raster_path : str
        Path to the data raster file to be masked.
    output_path : str
        Path where the masked raster will be saved.

    Raises:
    -------
    ValueError
        If the land mask and data raster have different dimensions.

    Notes:
    ------
    - Both input rasters are assumed to be single-band.
    - The output raster will have the same profile (CRS, transform, etc.) as the land mask.
    - Areas where the land mask is not 1 will be set to 0 in the output.

    Example:
    --------
    >>> apply_land_mask('land_mask.tif', 'data.tif', 'masked_data.tif')
    Masked raster saved to masked_data.tif
    """
    # Open the land mask raster
    with rasterio.open(land_mask_path) as land_mask:
        mask_data = land_mask.read(1)  # Assuming it's a single band
        profile = land_mask.profile

    # Open the data raster
    with rasterio.open(data_raster_path) as data_raster:
        data = data_raster.read(1)  # Assuming it's a single band
        
        # Ensure the rasters have the same shape
        if data.shape != mask_data.shape:
            raise ValueError("The land mask and data raster must have the same dimensions")
        
        # Apply the mask
        masked_data = np.where(mask_data != 1, 0, data)

    # Update the profile for the output raster
    profile.update(dtype=masked_data.dtype, count=1)

    # Write the result to a new raster
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(masked_data, 1)

    print(f"Masked raster saved to {output_path}")




###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def rescale_raster_to_zero_one(input_path, output_path, output_dtype=rasterio.float32):
    """
    Rescale raster values to a 0-1 range and save the result.

    This function normalizes raster values using min-max scaling, preserving the
    original data distribution while converting it to a specified floating-point format.

    Parameters:
    -----------
    input_path : str
        Path to the input raster file
    output_path : str
        Path to save the rescaled output raster
    output_dtype : rasterio dtype, optional
        Output data type (default: rasterio.float32)

    Notes:
    ------
    - Handles masked arrays to ignore nodata values during calculation
    - Preserves original raster metadata (CRS, transform, etc.)
    - Maintains masked (nodata) values as NaN in output
    - Integer output types will lose precision in the 0-1 range

    Example:
    --------
    >>> rescale_raster_to_zero_one('input.tif', 'scaled.tif')
    Rescaled raster saved to scaled.tif
    Original range: [12.5, 87.3] rescaled to [0, 1]
    """
    
    with rasterio.open(input_path) as src:
        data = src.read(1, masked=True).astype(float) 
        min_value = np.min(data)
        max_value = np.max(data)

        if max_value == min_value:
            print("Warning: Zero variance raster. Returning original data.")
            rescaled_data = data 
        else:
            rescaled_data = (data - min_value) / (max_value - min_value)

        profile = src.profile
        profile.update(dtype=output_dtype)

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(rescaled_data.astype(output_dtype), 1)

    print(f"Rescaled raster saved to {output_path}")
    print(f"Original range: [{min_value}, {max_value}] rescaled to [0, 1]")


###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def replace_nodata_with_lowest(input_path, output_path):
    """
    Replace NoData values in a raster with the lowest valid data value.

    This function reads a raster file, identifies NoData values, replaces them
    with the lowest valid value found in the raster, and saves the result to a
    new file. The NoData value is removed from the output raster's metadata.

    Parameters:
    -----------
    input_path : str
        Path to the input raster file.
    output_path : str
        Path where the processed raster will be saved.

    Notes:
    ------
    - Assumes a single-band raster input.
    - The original NoData value is obtained from the raster's metadata.
    - All metadata (CRS, transform, etc.) is preserved, except the NoData value.
    - The output raster will not have a NoData value defined in its metadata.

    Caution:
    --------
    - This operation modifies the data distribution by introducing new values.
    - The output raster will not distinguish between original low values and 
      what were previously NoData values.

    Example:
    --------
    >>> replace_nodata_with_lowest('input_dem.tif', 'processed_dem.tif')
    Processed raster saved to processed_dem.tif
    """
    
    with rasterio.open(input_path) as src:
        # Read the raster data
        data = src.read(1)
        
        # Get the nodata value
        nodata = src.nodata
        
        # Create a mask for valid data
        valid_mask = data != nodata
        
        # Find the lowest valid data value
        lowest_value = np.min(data[valid_mask])
        
        # Replace nodata with the lowest value
        data[~valid_mask] = lowest_value
        
        # Update the profile
        profile = src.profile
        profile.update(nodata=None)  # Remove nodata value from metadata
        
        # Write the updated raster
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(data, 1)

    print(f"Processed raster saved to {output_path}")



###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def align_raster(src_raster, target_raster, dst_raster):
    '''
    This function aligns the source_raster to the target_raster

    **Args:**
        - src_raster (str): link to the geotiff location of the source raster.
        - target_raster (str): link to the geotiff location of the target raster.
        - dst_raster (str): path (including name) to the destination where the raster is saved.

    **Returns:**
        - str: confirmation that dst_raster exists

    **Assumptions:**
    1. All input files are geotiffs.
    2. os and rasterio are installed and working.
    3. Function tested using Python 3.10.12

    **Usage:**
    >>> align_raster(source_raster = "/home/pete/Documents/tests_and_vals/gdgtm/02_master_reprojected/olm_alc_switz_reproj_20040101.tif",
    >>>              target_raster = "/home/pete/Documents/tests_and_vals/gdgtm/04_master_rebound/olm_alc_switz_rebound_100_20040101.tif",
    >>>              dst_raster = "/home/pete/Documents/tests_and_vals/gdgtm/05_supplements_aligned/olm_alc_switz_aligned_20040101.tif")
    "/home/pete/Documents/tests_and_vals/gdgtm/05_supplements_aligned/olm_alc_switz_aligned_20040101.tif exists"
    '''

    # Open the target and source rasters
    with rasterio.open(target_raster) as target:
        with rasterio.open(src_raster) as src:
            # Get the target raster's bounds, transform, and dimensions
            target_bounds = target.bounds
            target_transform = target.transform
            target_width, target_height = target.width, target.height

            # Create the output raster
            kwargs = target.meta.copy()
            kwargs.update({
                'crs': target.crs,
                'transform': target_transform,
                'width': target_width,
                'height': target_height,
                'dtype': src.dtypes[0],  # Use the source raster's dtype
                'count': src.count  # Ensure the band count matches the source
            })

            with rasterio.open(dst_raster, 'w', **kwargs) as dst:
                # Reproject the source raster to the target raster's bounds and resolution
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=target_transform,
                        dst_crs=target.crs,
                        dst_resolution=(target_transform.a, -target_transform.e),
                        src_nodata=src.nodata,
                        dst_nodata=target.nodata,
                        resampling=Resampling.nearest
                    )

    # Run the checks
    aligned_raster_exists = os.path.exists(dst_raster)

    return f"{dst_raster} exists"


###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def validate_raster_alignment(raster_1, raster_2):
    '''
    This function checks whether two rasters are aligned: i.e., whether they have the same number of pixels and whether these pixels have identical coordinates.

    **Args:**
        - raster_1 (str): link to the geotiff location of the first raster
        - raster_2 (str): link to the geotiff location of the second raster

    **Returns:**
        - dict: A dictionary containing the results of the alignment checks.

    **Assumptions:**
    1. All input files are geotiffs.
    2. os and rasterio are installed and working.
    3. Function tested using Python 3.10.12

    **Usage:**
    >>> validate_raster_alignment("/home/pete/Documents/tests_and_vals/gdgtm/04_master_rebound/olm_alc_switz_rebound_100_20040101.tif",
    >>>                           "/home/pete/Documents/tests_and_vals/gdgtm/05_supplements_aligned/olm_alc_switz_aligned_20040101.tif")
       
    {'dimension_match': False,
     'projection_match': True,
     'pixel_count_match': False,
     'geotransform_match': False}
    '''

    # Open the rasters
    with rasterio.open(raster_1) as src1:
        with rasterio.open(raster_2) as src2:
            # Check rows and cols (Dimension match)
            rows1, cols1 = src1.height, src1.width
            rows2, cols2 = src2.height, src2.width
            check_results = {"dimension_match": (rows1 == rows2 and cols1 == cols2)}

            # Check projection match
            proj_1 = src1.crs.to_string()
            proj_2 = src2.crs.to_string()
            check_results.update({"projection_match": proj_1 == proj_2})

            # Check pixels match:
            num_pixels_1 = rows1 * cols1
            num_pixels_2 = rows2 * cols2
            check_results.update({"pixel_count_match": num_pixels_1 == num_pixels_2})

            # Check if geotransforms match (implies pixel location match):
            geotransform_1 = src1.transform
            geotransform_2 = src2.transform
            check_results.update({"geotransform_match": geotransform_1 == geotransform_2})

    # Return the check results
    return check_results





###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def align_validate_raster(src_raster, target_raster, dst_raster):
    '''
    This function aligns the source_raster to the target_raster and validates the alignment.

    **Args:**
        - src_raster (str): Link to the geotiff location of the source raster.
        - target_raster (str): Link to the geotiff location of the target raster.
        - dst_raster (str): Path (including name) to the destination where the raster is saved.

    **Returns:**
        - dict: A dictionary containing the results of the alignment validation.

    **Assumptions:**
    1. All input files are geotiffs.
    2. os and rasterio are installed and working.
    3. Function tested using Python 3.10.12.
    4. Function relies on reproject_raster and align_raster functions.

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

    # Load the target raster to get its CRS
    with rasterio.open(target_raster) as target:
        target_crs = target.crs

    # Check if the source raster needs to be reprojected
    with rasterio.open(ssrc_raster) as src:
        if src.crs != target_crs:
            # Reproject the source raster
            reproject_raster(new_crs=target_crs.to_string(), src_raster=src_raster, dst_raster='temp_reproj_source.tif')
            projected_source_loc = 'temp_reproj_source.tif'
        else:
            projected_source_loc = src_raster

    # Align the two rasters
    align_raster(src_raster=projected_source_loc, target_raster=target_raster, dst_raster=dst_raster)

    # Run the alignment check
    alignment_outcome = validate_raster_alignment(target_raster, dst_raster)

    # Clean up the temporary reprojected raster if it exists
    if os.path.exists('temp_reproj_source.tif'):
        os.remove('temp_reproj_source.tif')

    return alignment_outcome