# gdgtm (Geospatial Data Getting Transforming and Managing)

## Project overviews
The purpose of the project is to wrap a set of extant Python utilities to streamline geospatial data downloads and processing (reprojection, bound setting and mosaicing), to allow easier pipeline construction for downstream processing. The main point is to simplify the process of acquiring raster data from online sources and building a straightforward pipeline for their processing and standardization ahead of downstream analysis. As of version 0.6 of the package the get functions are written for OpenLandMap STAC (https://stac.openlandmap.org/) and Chelsa (https://chelsa-climate.org/).

The core workflow of this package is:
1. Get a raster from an online source
2. Process it to the desired projection, resolution and bounding box - this is the **Master GeoTIFF**
3. Get further rasters (**complementary rasters**) and align those to the Master

The result is a collection of GeoTIFF files that is standardized in terms of projection, bounding box, resolution, and exact pixel location.

The package is built in Python, with almost all functions being in reality GDAL wrappers designed to simplify the workflow and reduce number of lines of code required to do a project.


## Installation
### Ubuntu with pre-installed GDAL 
pip install "git+https://github.com/pete-jacobsson/gdgtm"

### Virtual environments
For set-up in venv, the key challenge is installing GDAL (the effective GIS engine underneath all of the gdgtm functions. Unfortunately, pip cannot install GDAL easily, making it difficult to set up virtual environments through the usual means. However, Conda can install GDAL easily, making it possible to set up a virtual environment across all three major platforms.

1. set up virtual environment: conda create -n gdgtm python =3.10
2. Activate the virtual environment: conda activate my_env
3. Intsall GDAL: conda install gdal
4. pip install matplotlib
5. pip install "git+https://github.com/pete-jacobsson/gdgtm"


### Package was developed and tested using the following:
* Python 3.10.12
* datetime 5.5
* dateutil 2.8.2
* GDAL 3.4.1
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
