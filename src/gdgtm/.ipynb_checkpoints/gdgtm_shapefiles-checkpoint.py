### Functions for transforming shapefiles into rasters

###############################################################################
##################### GENERAL WORKFLOW ########################################
###############################################################################

# This set of functions is intended for transforming multi-poly shapefiles into rasters
# General workflow is as follows:
# 1. Crop shapefile
# 2. Set up "template" raster
# 3. Break up the cropped shape file into individual files for each poly line
# 4. Add the data from the individual poly lines into the template raster
# 5. Remove all the temp files

## List of functions and relationship to workflow steps:
# 1. bound_shape (crops shapefiles - WF step 1)
# 2. rasterize_shapefile_base (creates the "template" raster - WF step 2)
# 3. break_polys (creates shapefiles for each layer - WF step 3)
# 4. add_polys_to_raster (adds data from individual polys to template raster - WF step 4)
# 5. rasterize_shapefile (wrapper to execute the workflow and delete temp files - WF steps 1 - 5)


###############################################################################
#############################  Functions  #####################################
###############################################################################

# 1 bound_shape ---------------------------------------------------------------
def bound_shape (src_shape, dst_shape, target_bbox):
    '''
    This function set a new bounding box on a shape file.

    **Args:**
        - src_shape (str): path to the original file
        - dst_shape (str): path to the target file
        - target_bbox (tuple): provided in the WNES convention, standard to gdgtm.

    **Returns:**
        - bool: confirmation that the destination file exists

    **Assumptions:**
    1. Input file is an ESRI shapefile
    2. ogr is working (tested using GDAL version 3.4.1)
    3. Function tested using Python 3.10.12

    **Usage:**
    >>> new_bbox = (6.7663, 47.9163, 10.5532, 45.6755)
    >>> test = bound_shape("/home/pete/Downloads/sample_shapefile.shp", "/home/pete/Downloads/sample_shapefile_bound.shp", target_bbox = new_bbox)
    >>> print(test)
    True
    '''
    from osgeo import ogr
    import os
    
    ## Reformat the target_bbox to WSEN convention of ogr
    target_bbox = (target_bbox[0], target_bbox[3], target_bbox[2], target_bbox[1])

    ## Open the input shapefile
    src_ds = ogr.Open(src_shape)
    src_lyr = src_ds.GetLayer()

    # Create a new data source and layer with the desired bounding box
    dst_driver = ogr.GetDriverByName('ESRI Shapefile')
    dst_ds = dst_driver.CreateDataSource(dst_shape)
    dst_lyr = dst_ds.CreateLayer('', src_lyr.GetSpatialRef(), geom_type=src_lyr.GetLayerDefn().GetGeomType())

    # Copy features from input layer to output layer if they intersect with the new bounding box
    for feat in src_lyr:
        geom = feat.GetGeometryRef()
        if geom.Intersects(ogr.CreateGeometryFromWkt(f'POLYGON(({target_bbox[0]} {target_bbox[1]}, {target_bbox[2]} {target_bbox[1]}, {target_bbox[2]} {target_bbox[3]}, {target_bbox[0]} {target_bbox[3]}, {target_bbox[0]} {target_bbox[1]}))')):
            dst_lyr.CreateFeature(feat)
    
    src_ds = None
    dst_ds = None

    return os.path.exists(dst_shape)




# 2 rasterize_shapefile_base --------------------------------------------------
def rasterize_shapefile_base (src_shape, dst_raster, target_xres):
    '''
    This function takes on a shapefile and transforms it into a background raster using GDAL

    **Args:**
        - src_shape (str): path to the source shapefile
        - dst_raster (str): path to the destination raster
        - target_xres (int): determines the number of pixels along the x-axis of the target raster (therefore setting the desired pixel size and resolution).

    **Returns:**
        - bool: confirmation that target file exists

    **Assumptions:**
        - GDAL and ogr are working (function tested using version 3.4.1).
        - src_shape points to a genuine shape file
        - Function tested on Python 3.10.12


    **Usage:**
    >>> test = rasterize_shapefile("home/pete/Downloads/sample_shapefile.shp", "home/pete/Downloads/sample_shapefile_rasterized.tif")
    >>> print(test)
    True
    
    '''
    from osgeo import gdal, ogr
    import os
    
    ## Load the shapefile
    src_shp = ogr.Open(src_shape)
    layer = src_shp.GetLayer()

    ## Get extent and projection
    extent = layer.GetExtent()
    projection = layer.GetSpatialRef()
    
    ## Set the pixel size
    pixel_size = float((extent[1] - extent[0]) / target_xres)

    ## Set up the Geotransform:
    dst_geot = (extent[0], pixel_size, 0, extent[3], 0, -pixel_size)

    ##Determine target raster resolution:
    x_res = int((extent[1] - extent[0]) / pixel_size)
    y_res = int((extent[3] - extent[2]) / pixel_size)

    ##Set up the destination raster
    dst_ds = gdal.GetDriverByName("GTiff").Create(dst_raster, x_res, y_res, 1, gdal.GDT_Byte)
    dst_ds.SetGeoTransform(dst_geot)
    dst_ds.SetProjection(projection.ExportToWkt())

    # Rasterize the shapefile layer
    gdal.RasterizeLayer(dst_ds, [1], layer, burn_values=[1])
    
    ## Close connections
    dst_ds.FlushCache()
    dst_ds = None
    src_shp = None

    return os.path.exists(dst_raster)



# 3 break_polys ---------------------------------------------------------------
def break_polys (src_shape, temp_folder):
    '''
    This function takes on a shapefile and breaks it down into individual polygons for downstream addition to a raster.

    **Args:""
        - src_shape (str): location of the source shape file
        - temp_folder (str): folder where the resulting shape files will be stored

    **Returns:**
        None

    **Assumptions:**
    1. Input file is an ESRI shapefile
    2. ogr is working (tested using GDAL version 3.4.1)
    3. Function tested using Python 3.10.12
    4. temp_folder exists

    **Usage:**
    >>> break_polys("/home/pete/Downloads/sample_shapefile.shp", "/home/pete/Downloads/temp_shp_folder/")
    '''
    
    from osgeo import ogr

    src_ds = ogr.Open(src_shape)
    src_lyr = src_ds.GetLayer()

    ##Get driver for setting up the output files
    output_driver = ogr.GetDriverByName('ESRI Shapefile')

    for feat in src_lyr:
        geom = feat.GetGeometryRef()

        ## Create new data source and layer for this polygon
        output_ds = output_driver.CreateDataSource(temp_folder + f"polygon{feat.GetFID()}.shp")
        output_lyr = output_ds.CreateLayer('polygon', geom.GetSpatialReference(), ogr.wkbPolygon)

        ## Create a new feature with the polygon geometry
        output_feat = ogr.Feature(output_lyr.GetLayerDefn())
        output_feat.SetGeometry(geom)

        ## Add the feature to the new layer
        output_lyr.CreateFeature(output_feat)

        ## Close the data source
        output_feat = None
        output_ds = None
    


# 4 add_polys_to_raster -------------------------------------------------------
def add_polys_to_raster (poly_folder, dst_raster):
    '''
    This function adds data from individual polygons to a raster. 

    **Args:**
        - poly_folder (str): path to the folder containing the shapefiles for the individual layers.
        - dst_raster (str): path to an extant destination raster.

    **Retruns:**
        None

    **Assumptions:**
    1. Polygon shapefiles exist in the poly_folder and the dst_raster exists
    2. ogr and GDAL are working (tested using GDAL version 3.4.1)
    3. Function tested using Python 3.10.12
    
    **Usage:**
    >>> add_polys_to_raster("/home/pete/Downloads/temp_shp_folder/", "/home/pete/Downloads/sample_rasterized_background.tif")
    '''
    from osgeo import gdal, ogr
    import os

    ## Open the raster into which we want to sink the vectors
    dst_ds = gdal.Open(dst_raster, gdal.GA_Update)
    dst_band = dst_ds.GetRasterBand(1)

    ## Fish out the shapefiles from the poly folder
    poly_names = os.listdir(poly_folder)
    poly_paths = []
    for name in poly_names: 
        if ".shp" in name:
            poly_paths.append(poly_folder + name)

    # Now proceed to add the polys to the raster.
    burn_value = 1
    for poly in poly_paths:
        vector_ds = ogr.Open(poly) #Open the vector
        vector_layer = vector_ds.GetLayer()

        gdal.RasterizeLayer(dst_ds, [1], vector_layer, burn_values = [burn_value])
        dst_band.FlushCache() ##Makes sure operations are stacked onto the file on the disk and not kept in memory.
        burn_value += 1
        vector_ds = None #clear memory
        


# 5 rasterize_shapefile -------------------------------------------------------
def rasterize_shapefile (src_shape, dst_raster, target_bbox, target_xres, dst_shape = "temp_shape.shp", poly_folder = "temp_folder"):
    '''
    This is the wrapper function for transforming ESRI shapefiles into .tiff rasters. It works by: 
    1) cropping the original shapefiles; 
    2) making a "template raster" from the cropped shape file; 
    3) Breaking down the cropped shape file into its individual polygons
    4) Adding the polygons onto the "template raster".

    **Args:**
        - src_shape (str): path (inluding name) of the shapefile to be transformed.
        - dst_raster (str): location of the raster to which layers will get added.
        - target_bbox (tuple): a WNES tuple containing the boundaries onto which the src_shape is to be cropped.
        - target_xres (int): amount of pixels along the x axis desired on the final raster.
        - dst_shape (str): path to the temporary file used for storing the cropped shapefile
        - poly_folder (str): path to the folder used to store all the indivudal shapefile layers.

    **Returns:**
        - str: confirmation that the dst raster exists

    **Assumptions:**
        1 GDAL and ogr are working (function tested using 3.4.1)
        2 Original shapefile is a geo-references ESRI .shp
        3 Tested using Python 3.10.12

    **Usage:**
    >>> new_bbox = (6.7663, 47.9163, 10.5532, 45.6755)
    >>> test = rasterize_shapefile ("/home/pete/Downloads/sample_shapefile.shp", 
    >>>                             "/home/pete/Downloads/sample_shape_rasterized.tif", 
    >>>                             target_bbox = new_bbox, 
    >>>                             target_xres = 2000)
    "File exists: /home/pete/Downloads/sample_shape_rasterized.tif"
    
    '''
    from osgeo import gdal, ogr
    import os

    ##Crop original shapefile
    try: 
        bound_shape(src_shape, dst_shape, target_bbox = new_bbox)
    except Exception as e:
        print(f"Error creating {dst_shape}: {e}")

    ##Create the "template" raster
    ##!!!!From here on after work only with dst_shape!!!!
    try:
        rasterize_shapefile_base(dst_shape, dst_raster, target_xres = target_xres)
    except Exception as e:
        print(f"Error creating {dst_raster}: {e}")

    ##Set up temp folder, if not existing yet
    if not os.path.exists(poly_folder):
        os.mkdir(poly_folder)

    ##Break up the shapefile into its indivudal polygons
    try:
        break_polys(dst_shape, poly_folder + "/")  ## The "/" added to the poly_folder string is necessary for python to know that we're dealing with a folder here
    except Exception as e:
        print(f"Error decomposing {dst_shape} into polygons: {e}")
        
    ##Now add those individual polygons to the template raster
    try:
        add_polys_to_raster(poly_folder + "/", dst_raster)
    except Exception as e:
        print(f"Error adding polys to {dst_raster}: {e}")

    
    ##Remove temp files
    
    try:
        ## Cropped shape
        os.remove(dst_shape)
        os.remove(dst_shape[:-3] + "prj")
        os.remove(dst_shape[:-3] + "shx")
        os.remove(dst_shape[:-3] + "dbf")

        ## Temp shape files and folder
        for filename in os.listdir(poly_folder + "/"):
            file_path = os.path.join(poly_folder + "/", filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing {file_path}: {e}")
            
        os.rmdir(poly_folder)
    except Exception as e:
        print(f"Failed to remove temp files: {e}")
    
    ## Check that the target file exists
    if os.path.exists(dst_raster):
        return "File exists: " + dst_raster
    else:
        return "Warning, file does not exist: " + dst_raster
    