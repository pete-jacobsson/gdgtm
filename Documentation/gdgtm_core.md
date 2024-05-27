<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<tbody>
<tr class="odd">
<td> <br />
 <br />
<strong>gdgtm_core</strong></td>
<td style="text-align: right;"><a href=".">index</a><br />
<a href="file:/home/pete/Documents/GitHub/gdgtm/src/gdgtm/gdgtm_core.py">/home/pete/Documents/GitHub/gdgtm/src/gdgtm/gdgtm_core.py</a></td>
</tr>
</tbody>
</table>

`### Functions forming the core workflow of the gdgtm package.`

   
**Functions**

`      `

 

<span id="-change_raster_res">**change\_raster\_res**</span>(target\_res, source\_raster, dst\_raster, delete\_source=True)  
`The objective of this function is to load a raster from a geotiff, resample it to a set resolution, save it to a new file, and optionally delete the source raster.   Args:     target_res (float): Target resolution in units relevant to the crs          source_raster (str): Path to the original raster documents     dst_raster (str): Path to the file that will hold the re-resolved raster     delete_source (bool): toggles whether the source raster is to be deleted at the end of the operation      Returns:     str: string confirming that the new raster has the desired number of pixels (height and width)      Assumptions: 1. The source_raster is a geotiff. 2. os and rasterio are installed and working (function tested using rasterio 1.3.10) 3. numpy is working (function tested using numpy 1.24.3) 4. Function tested using Python 3.10.12   Usage example: >>> gdgtm.change_raster_res(target_res = 500, >>>                         source_raster = "/home/pete/Downloads/chesla_transformed.tif", >>>                         dst_raster = "/home/pete/Downloads/chesla_rescaled.tif") "Resolution change successful: new pixel size matches target"`

<!-- -->

<span id="-get_chelsa_data">**get\_chelsa\_data**</span>(parameter, extent, start\_date, end\_date, write\_location)  
`This function gets a cropped raster from Chelsa (https://chelsa-climate.org/), saves it as a .tiff to designated folder, checks that the .tiff exists, and prints a confirmation to the console.   Args:     parameter (str): The name of the variable used by Chelsa to find the intended data (has to be CMIP5 standard short name - specifies what climate varia is desired).     extent (list): a list of four decimals defining the grid square covered.      start_date (str): a yyyy-mm-dd formatted string determining the start date for Chelsa data     end_date (str): a yyyy-mm-dd formatted string determining the end date for Chelsa data     write_location (str): location to which the downloaded .tiff is written   Returns:     str: string confirming that the intended .tiff indeed exists in the target location   Assumptions: 1. Rchelsa, lubridate, and terra R packages are installed (function tested using versions 1.0.1, 1.9.3, and 1.7.71 respectively) 2. os and rpy2 Python modules are working (function tested using rpy 3.5.16) 3. R version 4.1+ has been installed (function tested using R 4.1.2) 4. Python 3 (function tested using Python 3.10.12)   Usage example: >>> parameter = "tas" >>> extent = [7.3, 7.5, 47.0, 47.2] >>> start_date = "2023-1-1" >>> end_date = "2023-2-2" >>> get_chelsa_data(parameter, extent, start_date, end_date, write_location = '/home/pete/Downloads/chesla_temp.tif') "Target .tiff exists"`

<!-- -->

<span id="-get_cognames_from_stac_coll_static">**get\_cognames\_from\_stac\_coll\_static**</span>(static\_coll\_link)  
`This function produces a list of names of cog (cloud optimized geotiffs) files from a STAC collection.   Args:     static_coll_link (str): link to a static STAC collection      Returns:     list: list of cog names as strings      Assumptions: 1. Link points at an actual STAC static collection. 2. pystac is installed ( function tested using pystac 1.10.1). 3. Python installation includes the re module. 4. Function tested using Python 3.10.12 5. Function version for gdgtm version 0.1.0 is only tested against Open Land Map urls   Usage example: >>> test = gdgtm.get_cognames_fom_stac_coll_static("https://s3.eu-central-1.wasabisys.com/stac/openlandmap/wilderness_li2022.human.footprint/collection.json") >>> print(test[0]) https://s3.openlandmap.org/arco/wilderness_li2022.human.footprint_p_1km_s_20000101_20001231_go_epsg.4326_v16022022.tif`

<!-- -->

<span id="-get_cogs_from_olm">**get\_cogs\_from\_olm**</span>(cognames, target\_directory, target\_names, bbox=(-180, 180, 180, -180), date\_start='00010101', date\_end='99991231')  
`The function uses a list of OpenLandMap cog locations to download a set of rasters bound in space and time   Args:     cognames (list): list of names of geotiffs in the OLM S3 bucket associated with the STAC collection of interest     target_directory (str): directory to which the files will be saved     target_names (str): the convention name for the files to be downlaoded     bbox (tupple): a tupple of floats indicating the WGS84 (EPSG:4326) coordinates of the bounding box used to crop the rasters downloaded. Defaults to entire grid (-180, 180, 180, -180)     date_start (str): date before which the data are ignored. Needs to be provided in the yyyymmdd format. Defaults to 01JAN0001.     date_end (str): date after which the data are ignored. Needs to be provided in the yyyymmdd format. Defaults to 31DEC9999.   returns:     str: names of downloaded files in the target_directory     Downloaded geotiff files named in the target_names_orig_file_date format in the target_directory      Assumptions:     cognames point to an OLM S3 bucket and OLM data     All incmong raster refer to data points happenning between 01JAN0001 and 31DEC9999.     GDAL is available (function tested using GDAL 3.4.1)   Usage: >>> bbox = (5.7663, 47.9163, 10.5532, 45.6755) >>> >>> gdgtm.get_cogs_from_olm(cognames = test,  >>>                         target_directory = "/home/pete/Downloads/",  >>>                         target_names = "olm_humfoot_switz_raw_", >>>                         bbox = bbox, >>>                         date_start = "20000601", >>>                         date_end = "20050101" >>>                        )   /home/pete/Downloads/olm_humfoot_switz_raw_20010101.tif /home/pete/Downloads/olm_humfoot_switz_raw_20020101.tif /home/pete/Downloads/olm_humfoot_switz_raw_20030101.tif /home/pete/Downloads/olm_humfoot_switz_raw_20040101.tif`

<!-- -->

<span id="-reproject_raster">**reproject\_raster**</span>(new\_crs, source\_raster, dst\_raster, delete\_source=True)  
`This function takes a geotiff raster (with metadata include coordinate projection) and turns out a geotiff raster with updated projection and a check that the new file projection matches the desired target. The function also has the option to do source deletion (e.g. for DM purposes)   Args:     new_crs (str): New coordinate system to which the raster is to be projected to.     source_raster (str): path to the geotiff with relevant metadata that will be reprojected     dst_raster (str): path and filename into which new (re-projected) raster will be saved     delete_source (bool): determines whether source raster is deleted following function execution   Resturns:     str: string confirming that the new geotiff has the expected projection system   Assumptions 1. Input data is a geotiff with a header readable by rasterio 2. Rasterio is working (function tested with rasterio 1.3.10) 3. Function tested on Python 3.10.12 4. Numpy is working (function tested with numpy 1.24.3)   Usage example: >>> gdgtm.reproject_raster(new_crs = "ESRI:54028",  >>>                        source_raster = '/home/pete/Downloads/chesla_temp.tif', >>>                        dst_raster = '/home/pete/Downloads/chesla_transformed.tif') "Transform successful"`

<!-- -->

<span id="-set_raster_boundbox">**set\_raster\_boundbox**</span>(target\_bb, source\_raster, dst\_raster, delete\_source=True)  
`This function loads a geotiff raster, fits it to a new bounding box, saves it as a geotiff file. Optionally it deletes the source raster.   Args:     target_bb (list): list of four numbers defining the target for the new BB (Order: L, B, R, T).      source_raster (str): Path to the original raster documents     dst_raster (str): Path to the file that will hold the re-resolved raster     delete_source (bool): toggles whether the source raster is to be deleted at the end of the operation      Returns:     str: string confirming that the new BB corners match the target spec.      Assumptions: 1. The source_raster is a geotiff. 2. os, GDAL, and rasterio are installed and working (function tested using GDAL 3.4.1 and rasterio 1.3.10) 3. numpy is working (function tested using numpy 1.24.3) 4. Function tested using Python 3.10.12   Usage example: >>> new_bb = [556400, 5238900, 566200, 5254900] >>> gdgtm.set_raster_boundbox(target_bb = new_bb, >>>                           source_raster = "/home/pete/Downloads/chelsa_rescaled_2000.tif", >>>                           dst_raster = "/home/pete/Downloads/chelsa_new_bb.tif") "New bounding box implemented successfully: all dimensions match"`
