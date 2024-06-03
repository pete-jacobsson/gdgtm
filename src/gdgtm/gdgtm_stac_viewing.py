### Functions for interacting with STAC objects


# summarize_stac() ------------------------------------------------------------

def summarize_stac (catalog_url):
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



