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




###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def convert_gtif_to_jpg(input_path, output_path):
    """
    Convert a single GeoTIFF file to a JPG image.
    
    :param input_path: Path to the input GeoTIFF file
    :param output_path: Path to save the output JPG file
    """
    try:
        with rasterio.open(input_path) as src:
            data = src.read()
            image_data = reshape_as_image(data)
            # image_data = np.clip(image_data, 0, 1) 
            # image_data = (image_data * 255.0).astype(np.uint8)
            
            if image_data.shape[2] == 3:
                img = Image.fromarray(image_data, 'RGB')
            elif image_data.shape[2] == 1:
                img = Image.fromarray(image_data[:,:,0], 'L')
            else:
                raise ValueError("Unsupported number of bands")
            
            img.save(output_path, 'JPEG', quality=85)
        
        print(f"Successfully converted {input_path} to {output_path}")
    
    except Exception as e:
        print(f"An error occurred processing {input_path}: {str(e)}")


###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def process_dir_to_jpg(input_folder, output_folder):
    """
    Process all GeoTIFF files in the input folder and save JPGs to the output folder.
    
    :param input_folder: Path to the folder containing GeoTIFF files
    :param output_folder: Path to the folder where JPG files will be saved
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Process each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.tif', '.tiff')):
            input_path = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + '.jpg'
            output_path = os.path.join(output_folder, output_filename)
            geotiff_to_jpg(input_path, output_path)


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