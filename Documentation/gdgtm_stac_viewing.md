<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<tbody>
<tr class="odd">
<td> <br />
 <br />
<strong>gdgtm_stac_viewing</strong></td>
<td style="text-align: right;"><a href=".">index</a><br />
<a href="file:/home/pete/Documents/GitHub/gdgtm/src/gdgtm/gdgtm_stac_viewing.py">/home/pete/Documents/GitHub/gdgtm/src/gdgtm/gdgtm_stac_viewing.py</a></td>
</tr>
</tbody>
</table>

`### Functions for interacting with STAC objects`

   
**Functions**

`      `

 

<span id="-summarize_stac">**summarize\_stac**</span>(catalog\_url)  
`This function produces a pandas table that can be used to get a better idea of collections present in a STAC catalog   **Args:**     - catalog_url (str): link to the catalog.json      **Returns:**     - DataFrame: a data frame containing information on:         1. Order of a collection in a catalog         2. STAC ID of the collection         3. Title         4. Keywords         5. Description         6. Spatial bounding box (W, S, E, N order)         7. Temporal extent covered by the data set         8. Link to the collection.json file   Assumptions: 1. The URL target is a STAC 1.0+ catalog.json 2. Pandas and pystac are available and running (tested using versions 2.0.3 and 1.10.1 respectively) 3. Function tested using Python 3.10.12   Usage: >>> summarize_stac("http://s3.eu-central-1.wasabisys.com/stac/openlandmap/catalog.json")`
