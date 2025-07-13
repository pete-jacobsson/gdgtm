### These functions cover the management of raster data
import seaborn as sns
import rasterio
from rasterio.enums import Resampling
from rasterio.plot import reshape_as_image
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt

###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def convert_gtif_to_nparray (src_path, height, width, convert_no_data=False):
    """
    This function takes a single-layer GeoTIFF source file and converts it into an np.array.
    Optionally converts no data values to np.nan.
    Also validates that the GeoTIFF has values within the expected ranges.
    
    Parameters:
        src_path (str): Path to the input GeoTIFF file.
        height (int): Expected height of the image.
        width (int): Expected width of the image.
        convert_no_data (bool): Whether to convert no data values to np.nan.

    Returns:
        np.ndarray: The image data as a NumPy array.
    """

    with rasterio.open(src_path) as src:
        # print(f"Height/Width passed from function: {height}, {width}")
        if int(src.height) != height or int(src.width) != width:
            raise Exception(f"unexpected_dims: height = {int(src.height)}, width = {int(src.width)}")
        
        data = src.read(
            out_shape=(src.count, int(src.height), int(src.width)),
            resampling=Resampling.bilinear
        )
        
        # Get the no data value from the metadata
        no_data_value = src.nodata

        if no_data_value is not None:
            # If convert_no_data is True, replace no data values with np.nan
            if convert_no_data:
                data = np.where(data == no_data_value, np.nan, data)
        
        # Check if all values are between 0 and 1
        # if not np.all(np.isnan(data) | (data > -0.01) & (data < 1.01)): ##TO DO: once success run completed, re-do the prep and ensure Zizka data also all in 0 - 1
        #     raise ValueError(f"{src_path} contains values outside the range [0, 1]")

        
        # # Clip values to [0, 1] range and convert to float16  #### TODO: bring this out to a different function
        # data = np.clip(data, 0, 1).astype(np.float16)

        # # Reorganize the shape to (height, width, channels)
        data = np.transpose(data, (1, 2, 0))
        
    return data



### TO RE_IMPLEMENT
# ###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# def convert_gtif_to_jpg(input_path, output_path):
#     """
#     Convert a single GeoTIFF file to a JPG image.
    
#     :param input_path: Path to the input GeoTIFF file
#     :param output_path: Path to save the output JPG file
#     """
#     try:
#         with rasterio.open(input_path) as src:
#             data = src.read()
#             image_data = reshape_as_image(data)
#             # image_data = np.clip(image_data, 0, 1) 
#             # image_data = (image_data * 255.0).astype(np.uint8)
            
#             if image_data.shape[2] == 3:
#                 img = Image.fromarray(image_data, 'RGB')
#             elif image_data.shape[2] == 1:
#                 img = Image.fromarray(image_data[:,:,0], 'L')
#             else:
#                 raise ValueError("Unsupported number of bands")
            
#             img.save(output_path, 'JPEG', quality=85)
        
#         print(f"Successfully converted {input_path} to {output_path}")
    
#     except Exception as e:
#         print(f"An error occurred processing {input_path}: {str(e)}")


# ###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# def process_dir_to_jpg(input_folder, output_folder):
#     """
#     Process all GeoTIFF files in the input folder and save JPGs to the output folder.
    
#     :param input_folder: Path to the folder containing GeoTIFF files
#     :param output_folder: Path to the folder where JPG files will be saved
#     """
#     # Create output folder if it doesn't exist
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
    
#     # Process each file in the input folder
#     for filename in os.listdir(input_folder):
#         if filename.lower().endswith(('.tif', '.tiff')):
#             input_path = os.path.join(input_folder, filename)
#             output_filename = os.path.splitext(filename)[0] + '.jpg'
#             output_path = os.path.join(output_folder, output_filename)
#             geotiff_to_jpg(input_path, output_path)


###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_raster_with_colorbar(raster_path, title=None, cmap='viridis'):
    """
    Plots a raster with a color bar using seaborn and rasterio.
    
    Parameters:
    raster_path (str): Path to the raster file
    title (str, optional): Title for the plot
    cmap (str, optional): Colormap to use for the plot (default is 'viridis')
    """
    
    # Open the raster file
    with rasterio.open(raster_path) as src:
        # Read the first band
        raster_data = src.read(1)
        
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot the raster using seaborn's heatmap
        sns.heatmap(raster_data, cmap=cmap, ax=ax, cbar=True, cbar_kws={'label': 'Value'})
        
        # Remove x and y ticks
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Set title if provided
        if title:
            ax.set_title(title, fontsize=16)
        
        # Add some padding to the plot
        plt.tight_layout()
        
        # Show the plot
        plt.show()

# Example usage
# raster_path = "path/to/your/raster.tif"
# plot_raster_with_colorbar(raster_path, title="My Raster Plot", cmap="YlOrRd")



def create_location_map(
    square_basename: str,
    coordinates_df: pd.DataFrame,
    global_landmask_path: str,
    output_path: str,
    square_pixel_size: int = 128,
    frame_to_square_ratio: int = 10,
    crop_to_square_ratio: int = 75,
    square_color: tuple = (128, 0, 0, 255),  # Maroon, fully opaque
    frame_color: str = "steelblue",
) -> bool:
    """Generates and saves a location map image for a given square.

    This function uses rasterio to open the geospatial landmask, converts it
    to a standard image format, and then uses PIL to draw the location of the
    square and a larger context frame before cropping and saving the final map.

    Args:
        square_basename (str): The basename of the square, e.g., "square_1".
        coordinates_df (pd.DataFrame): DataFrame from coord_log.csv.
        global_landmask_path (str): Path to the large landmask GeoTIFF file.
        output_path (str): The full path where the generated map will be saved.
        square_pixel_size (int): The dimension of the square in pixels.
        frame_to_square_ratio (int): Multiplier for square size for context frame.
        crop_to_square_ratio (int): Multiplier for square size for the crop area.
        square_color (tuple): RGBA color for the square's rectangle.
        frame_color (str): Color name for the context frame.

    Returns:
        bool: True if the map was created successfully, False otherwise.
    """
    # --- 1. Validate inputs and find coordinates (same as before) ---
    if not os.path.exists(global_landmask_path):
        print(f"  Error: Global landmask not found at {global_landmask_path}")
        return False

    try:
        square_num_match = re.search(r"\d+", square_basename)
        if not square_num_match:
            raise ValueError(
                f"Could not extract square number from '{square_basename}'"
            )
        square_num = int(square_num_match.group(0))

        coords_row = coordinates_df[coordinates_df["draw"] == square_num]
        if coords_row.empty:
            raise ValueError(f"Coordinates for draw number {square_num} not found.")
        pixel_coords = tuple(coords_row[["x_pixel", "y_pixel"]].iloc[0].values)
    except (ValueError, IndexError) as e:
        print(f"  Error finding coordinates for '{square_basename}': {e}")
        return False

    # --- 2. Open with rasterio and convert to a PIL-compatible format ---
    try:
        with rasterio.open(global_landmask_path) as src:
            # Scale a single band to 0-255 uint8 for display
            def scale_to_uint8(band_data, nodata_val):
                # Handle nodata values by masking them before scaling
                if nodata_val is not None:
                    band_data = np.ma.masked_equal(band_data, nodata_val).filled(0)

                min_val, max_val = np.min(band_data), np.max(band_data)
                if max_val == min_val:
                    return np.zeros_like(band_data, dtype=np.uint8)

                # Perform a linear stretch to 0-255
                scaled_data = 255.0 * (band_data - min_val) / (max_val - min_val)
                return scaled_data.astype(np.uint8)

            # Check number of bands to decide between RGB and grayscale
            if src.count >= 3:
                # Read first 3 bands for an RGB image and scale each
                r = scale_to_uint8(src.read(1), src.nodata)
                g = scale_to_uint8(src.read(2), src.nodata)
                b = scale_to_uint8(src.read(3), src.nodata)
                # Stack bands into an (H, W, 3) array
                rgb_array = np.stack([r, g, b], axis=-1)
                landmask_img = IMAGE_PROCESSING_LIB.fromarray(rgb_array, "RGB")
            else:
                # Read the first band for a grayscale image
                gray_array = scale_to_uint8(src.read(1), src.nodata)
                landmask_img = IMAGE_PROCESSING_LIB.fromarray(gray_array, "L")

        # --- 3. Proceed with drawing logic on the created PIL image ---
        # Ensure the image is in a mode that supports color drawing
        if landmask_img.mode not in ["RGB", "RGBA"]:
            landmask_img = landmask_img.convert("RGBA")
        draw = ImageDraw.Draw(landmask_img)

        # The rest of the drawing, cropping, and saving logic remains the same
        x0, y0 = int(pixel_coords[0]), int(pixel_coords[1])
        x1, y1 = x0 + square_pixel_size, y0 + square_pixel_size
        draw.rectangle([x0, y0, x1, y1], fill=square_color)

        img_width, img_height = landmask_img.size
        crop_size = crop_to_square_ratio * square_pixel_size

        if (img_width > crop_size) or (img_height > crop_size):
            frame_size = frame_to_square_ratio * square_pixel_size
            frame_x0 = max(0, x0 - (frame_size - square_pixel_size) // 2)
            frame_y0 = max(0, y0 - (frame_size - square_pixel_size) // 2)
            frame_x1 = min(img_width, frame_x0 + frame_size)
            frame_y1 = min(img_height, frame_y0 + frame_size)
            draw.rectangle(
                [frame_x0, frame_y0, frame_x1, frame_y1], outline=frame_color, width=5
            )

            center_x, center_y = (x0 + x1) // 2, (y0 + y1) // 2
            left = max(0, center_x - crop_size // 2)
            upper = max(0, center_y - crop_size // 2)
            right = min(img_width, left + crop_size)
            lower = min(img_height, upper + crop_size)

            if right - left < crop_size:
                left = max(0, right - crop_size)
            if lower - upper < crop_size:
                upper = max(0, lower - crop_size)

            final_image = landmask_img.crop((left, upper, right, lower))
        else:
            final_image = landmask_img

        # os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_image.save(output_path, quality=95)
        print(f"  Location map for '{square_basename}' saved to: {output_path}")
        return True

    except Exception as e:
        print(f"  An error occurred during image processing: {e}")
        return False
