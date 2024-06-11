### Functions for viewing and interacting with STAC objects: https://stacspec.org/en/


### List of functions----------------------------------------------------------

## 1 summarize_statitc_stac
## 2 get_cognames_static_stac
## 3 get_olm_cogs


# 1 summarize_static_stac------------------------------------------------------
def summarize_static_stac (catalog_url):
    '''
    This function produces a pandas table that can be used to get a better idea of collections present in a STAC catalog
    
    **Args:**
        - catalog_url (str): link to the catalog.json
        
    **Returns:**
        - DataFrame: a data frame containing information on:
            1. Order of a collection in a catalog
            2. STAC ID of the collection
            3. Title
            4. Keywords
            5. Description
            6. Spatial bounding box (W, S, E, N order)
            7. Temporal extent covered by the data set
            8. Link to the collection.json file
    
    Assumptions:
    1. The URL target is a STAC 1.0+ catalog.json
    2. Pandas and pystac are available and running (tested using versions 2.0.3 and 1.10.1 respectively)
    3. Function tested using Python 3.10.12
    
    Usage:
    >>> summarize_stac("http://s3.eu-central-1.wasabisys.com/stac/openlandmap/catalog.json")
    
    '''

    ## Load dependencies
    import pandas as pd
    import pystac
    import re
    
    ## Create a catalog object and the list of children
    cat = pystac.Catalog.from_file(catalog_url)
    cat_children = cat.get_children()
    
    
    ## Create the records placeholder and set the regex pattern
    cat_records = []
    coll_self_pattern = "collection.json"
    seq_num = 0
        
    ## For loop through the catalog and update the cat_records
    for child in cat_children:
        entry = seq_num
        stac_id = child.id
        title = child.title
        keywords = child.keywords
        description = child.description
        spatial_extent = child.extent.spatial.bboxes[0]
        temp_extent =  child.extent.temporal.intervals[0]
    
        coll_links = child.links
        for link in coll_links:
            if link.rel == "self" and re.search(coll_self_pattern, link.href): ## This checks that only the collection itself and assorted link are added.
                coll_href = link.href
    
        record = [entry, stac_id, title, keywords, description, spatial_extent, temp_extent, coll_href]
        cat_records.append(record)
        seq_num += 1
    
    ## Convert to a Pandas DF
    cat_records = pd.DataFrame(cat_records, columns = ["entry_no", "stac_id", "title", "keywords", "description", 
                                                       "spatial_extent", "temp_extent", "coll_href"])
    
    return cat_records



# 2 get_cognames_static_stac --------------------------------------------------
def get_cognames_static_stac (static_coll_link):
    '''
    This function produces a list of names of cog (cloud optimized geotiffs) files from a STAC collection.
    
    Args:
        static_coll_link (str): link to a static STAC collection
        
    Returns:
        list: list of cog names as strings
        
    Assumptions:
    1. Link points at an actual STAC static collection.
    2. pystac is installed ( function tested using pystac 1.10.1).
    3. Python installation includes the re module.
    4. Function tested using Python 3.10.12
    5. Function version for gdgtm version 0.1.0 is only tested against Open Land Map urls
    
    Usage example:
    >>> test = gdgtm.get_cognames_static_stac("https://s3.eu-central-1.wasabisys.com/stac/openlandmap/wilderness_li2022.human.footprint/collection.json")
    >>> print(test[0])
    https://s3.openlandmap.org/arco/wilderness_li2022.human.footprint_p_1km_s_20000101_20001231_go_epsg.4326_v16022022.tif
    
    '''
    ## Import dependencies
    import pystac
    import re
    
    ## Set up empty list
    geotiff_names = []
    
    ## Get collection items
    collection = pystac.read_file(static_coll_link)
    collection_items = collection.get_all_items()
    
    ## Iterate over collection items to the asset level. Then in the asset level determine if something is a geotiff
    for item in collection_items:
        for asset_key in item.assets:
            asset = item.assets[asset_key]
            if re.search("geotiff", asset.media_type):   # Using regex, as the actual media_type string contains much more various data
                geotiff_names.append(asset.href) # asset.href is the link to the actual geotiff
                
    return geotiff_names


# 3 get_olm_cogs --------------------------------------------------------------
def get_olm_cogs (cognames, target_directory, target_names, bbox = (-180, 180, 180, -180), interval = None):
    '''
    The function uses a list of OpenLandMap cog locations to download a set of rasters bound in space and time
    
    Args:
        cognames (list): list of names of geotiffs in the OLM S3 bucket associated with the STAC collection of interest
        target_directory (str): directory to which the files will be saved
        target_names (str): the convention name for the files to be downlaoded
        bbox (tupple): a tupple of floats indicating the WGS84 (EPSG:4326) coordinates of the bounding box used to crop the rasters downloaded. Defaults to entire grid (-180, 180, 180, -180)
        interval (tupple or None): dates outside which rasters will be ignored. Needs to be provided in the yyyymmdd format. Defaults to 01JAN0001.
            
    returns:
        str: names of downloaded files in the target_directory
        Downloaded geotiff files named in the target_names_orig_file_date format in the target_directory
        
    Assumptions:
        cognames point to an OLM S3 bucket and OLM data
        All incmong raster refer to data points happenning between 01JAN0001 and 31DEC9999.
        GDAL is available (function tested using GDAL 3.4.1)
    
    Usage:
    >>> bbox = (5.7663, 47.9163, 10.5532, 45.6755)
    >>>
    >>> get_cogs_from_olm(cognames = test, 
    >>>                   target_directory = "/home/pete/Downloads/", 
    >>>                   target_names = "olm_humfoot_switz_raw_",
    >>>                   bbox = bbox,
    >>>                   interval = ("20000601", "20050101")

    
    /home/pete/Downloads/olm_humfoot_switz_raw_20010101.tif
    /home/pete/Downloads/olm_humfoot_switz_raw_20020101.tif
    /home/pete/Downloads/olm_humfoot_switz_raw_20030101.tif
    /home/pete/Downloads/olm_humfoot_switz_raw_20040101.tif
    
    '''
    ## Import GDAL
    from osgeo import gdal

    ## Ensure that cognames are a list: if only single cogname was provided into the function it turns to a string, breaking down the next step.
    if type(cognames) != list:
        cognames = [cognames]
    
    ## Loop getting the rasters
    for raster_name in cognames:
        ###This gets the dates out of the raster_name
        raster_ymd = raster_name.split("-doy")[0].split("_")[-5: -3]
        if type(interval) is tuple:
            ## Filter based on date - if date out of range, no action taken
            if min(raster_ymd) > interval[0] and max(raster_ymd) < interval[1]: ## Apply filter
                src_raster = gdal.Open(raster_name) ##Get the actual raster
                new_raster_name = target_directory + target_names + raster_ymd[0] + ".tif"
                ##Apply bbox and save in target location
                gdal.Translate(new_raster_name, src_raster, projWin = bbox)
                print(new_raster_name) ## Print file name to confirm operation successful
                
        else:
            ## If no interval is set:
            src_raster = gdal.Open(raster_name) ##Get the actual raster
            new_raster_name = target_directory + target_names + raster_ymd + ".tif"
            ##Apply bbox and save in target location
            gdal.Translate(new_raster_name, src_raster, projWin = bbox)
            print(new_raster_name) ## Print file name to confirm operation successful
            
       
            
        ## Disconnect from file
        src_raster = None