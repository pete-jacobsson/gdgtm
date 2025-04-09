### NOTE: this functionality is still GDAL-dependent (old versions of the package) and hence commented out



# # 2 download_raster -----------------------------------------------------------
# def download_raster (raster_link, dst_raster, bbox = None):
#     '''
#     The function downloads a raster and sets a bounding box

#     **Args:**
#         - raster_link (str): a link to a raster to be downloaded
#         - bbox (tuple): a WNES set of coordinates defining the downloaded raster bounding box

#     **Returns:**
#         - dict: confirmation that dst_raster exists

#     **Assumptions:**
#         - raster_link points to a valid raster links
#         - Function developed and tested using GDAL version 3.6.2 and Python 3.10.12

#     *Usage:*
#     >>>    download_raster("https://s3.openlandmap.org/arco/wilderness_li2022.human.footprint_p_1km_s_20000101_20001231_go_epsg.4326_v16022022.tif", 
#     >>>                    "/home/pete/Documents/tests_and_vals/gdgtm_dev_copy/down_raster.tif", 
#     >>>                     bbox = (4, 48, 9, 44))
#     {'dst_raster exists': True}
#     '''
#     from osgeo import gdal
#     import os

#     # Check if the file in question really is a GeoTIFF
#     is_geotiff = check_if_geotiff(raster_link)
#     if not list(is_geotiff.values())[0]:
#         raise TypeError(f"{is_geotiff}")

#     # Load the raster
#     src_raster = gdal.Open(raster_link)

#     if bbox is None:
#         gdal.Translate(dst_raster, src_raster) ##Save to dst
#     else:
#         gdal.Translate(dst_raster, src_raster, projWin = bbox) ## Apply bbox and save to dst

#     src_raster = None ## Disconnect from raster
#     return {"dst_raster exists": os.path.exists(dst_raster)}