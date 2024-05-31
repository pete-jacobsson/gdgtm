<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<tbody>
<tr class="odd">
<td> <br />
 <br />
<strong>gdgtm_merge_mosaic</strong></td>
<td style="text-align: right;"><a href=".">index</a><br />
<a href="file:/home/pete/Documents/GitHub/gdgtm/src/gdgtm/gdgtm_merge_mosaic.py">/home/pete/Documents/GitHub/gdgtm/src/gdgtm/gdgtm_merge_mosaic.py</a></td>
</tr>
</tbody>
</table>

`### Functions for raster merging and mosaics`

   
**Functions**

`      `

 

<span id="-merge_rasters">**merge\_rasters**</span>(raster\_1, raster\_2, dst\_raster, delete\_source=True)  
`This function merges two rasters, combining them into a single raster with two bands.   **Args:**     - raster_1 (str): link to the location of the first of the two rasters to merge     - raster_2 (str): link to the location of the second raster to merge     - dst_raster (str): path and file name of the destination file     - delete_source (bool): toggles whether the function deletes the source rasters      **Returns:**     - str: indication whether the bound counts match between the source and the destination      **Assumptions:** 1. The two rasters share the same projection and dimensions 2. Both rasters are GeoTIFFs 4. Function tested using GDAL 4.3.1 and Python 3.10.12   **Usage:** >>> merge_rasters(raster_1 = "/home/pete/Documents/tests_and_vals/gdgtm/06_mosaic_merge_prep/olm_humfoot_switz_raw_west_20010101.tif",  >>>               raster_2 = "/home/pete/Documents/tests_and_vals/gdgtm/06_mosaic_merge_prep/olm_humfoot_switz_raw_west_20020101.tif", >>>               dst_raster = "/home/pete/Documents/tests_and_vals/gdgtm/07_mosaic_merge_out/olm_humfoot_switz_raw_west_merge_2001_2002.tif")   "Both source and destination contain 2 bands total."`

<!-- -->

<span id="-mosaic_rasters">**mosaic\_rasters**</span>(raster\_1, raster\_2, dst\_raster, delete\_source=True)  
`This function takes two raster and mosaics them into a single raster   **Args:**     - raster_1 (str): link to the location of the first of the two rasters to mosaic     - raster_2 (str): link to the location of the second raster to mosaic     - dst_raster (str): path and file name of the destination file     - delete_source (bool): toggles whether the function deletes the source rasters      **Returns:**     - str: indication whether the dst_raster exists      **Assumptions:** 1. Both rasters are GeoTIFFs 2. Both rasters are same projection 3. Both rasters have the same bands 4. Function tested using GDAL 4.3.1 and Python 3.10.12   **Usage:** >>> mosaic_rasters(raster_1 = "/home/pete/Documents/tests_and_vals/gdgtm/06_mosaic_merge_prep/olm_humfoot_switz_raw_west_20010101.tif", >>>                raster_2 = "/home/pete/Documents/tests_and_vals/gdgtm/06_mosaic_merge_prep/olm_humfoot_switz_raw_east_20010101.tif", >>>                dst_raster = "/home/pete/Documents/tests_and_vals/gdgtm/07_mosaic_merge_out/olm_humfoot_switz_raw_whole_20010101.tif")   "/home/pete/Documents/tests_and_vals/gdgtm/07_mosaic_merge_out/olm_humfoot_switz_raw_whole_20010101.tif exists"`
