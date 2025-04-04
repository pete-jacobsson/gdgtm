# gdgtm (Geospatial Data Getting Transforming and Managing)

## Project overview
The purpose of this package is to simplify getting, transforming and managing geospatial data within programmatic workflows. What we want to achieve here is a platform that will allow, in relatively few lines of code, to bulk process sizeable volumes of geospatial data for downstream analysis, quickly.

Hence, if you want to run a machine learning project based on a collection of a hundred rasters downlaoded from different sources, but first need to align those rasters, you might find gdgtm helpful.

To get an overview of the functuionality see the test script, 

## Installation






### Package was developed and tested using the following:
* Python 3.10.12
* datetime 5.5
* dateutil 2.8.2
* GDAL 3.6.2 ### NOTE: failing to work for Shapefiles
* Numpy 1.24.3
* rasterio 1.3.10
* pystac 1.10.1
* pandas 2.0.3
* datetime 5.5
* dateutil 2.8.2
The .toml is configured to import these versions of the packages or higher.

## Structure
The package is built around the following modules:
- gdgtm_core: covers functions for transforming and aligning rasters.
- gdgtm_chelsa_gets: functions for getting data from https://chelsa-climate.org/
- gdgtm_stac_gets: functions for interacting with STAC objects (static and open only).
- gdgtm_merge_mosaic: functions for mosaicing rasters and for merging multiple rasters into a single multi-layer raster.
- gdgtm_numpys: functions for converting GeoTiffs into numpy arrays (2D only).
- gdgtm_shapefiles: functions for converting ESRI .shp files into GeoTiffs.

Specific usage examples provided in the documentation and the demo.


## Supported Data Formats
gdgtm has only been tested for geotif (.tif) format.

## Testing
gdgtm functions are built in Jupyter with explicit tests built into the process.
Beyond in-development testing, all functions in the "main" branch will have been run through the test script, including failure tests.

## License
MIT License

## Sources of test shapefiles

The package includes three shapefiles used in functionality testing, and which will also be part of the demo. Their sources are as follows:

- STRUCTHELV_LINE_AUX.shp and STRUCTHELV_POLYGON_MAIN.shp have been obtained from https://www.swisstopo.admin.ch/en/special-geological-maps-vector (Collection 128 Structural Map of the Helvetic Zone of the swiss Alps, including Vorarlberg (Austria) and Haute Savoie (France)) under the following terms: https://shop.swisstopo.admin.ch/en/free-geodata
- gadm41_CHE_3.shp has been obtained from: https://gadm.org/download_country.html under the following terms: https://gadm.org/license.html


## Contact
Pete Jacobsson (pt.jacobsson@gmail.com)
