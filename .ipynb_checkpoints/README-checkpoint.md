# gdgtm (Geospatial Data Getting Transforming and Managing)

## Project overviews
The purpose of the project is to wrap a set of extant Python utilities to streamline geospatial data downloads and processing (reprojection, bound setting and mosaicing), to allow easier pipeline construction for downstream processing. The main point is to simplify the process of acquiring raster data from online sources and building a straightforward pipeline for their processing and standardization ahead of downstream analysis. As of version 0.5 of the package the get functions are written for OpenLandMap STAC (https://stac.openlandmap.org/) and Chelsa (https://chelsa-climate.org/).

The core workflow of this package is:
1. Get a raster from an online source
2. Process it to the desired projection, resolution and bounding box - this is the **Master GeoTIFF**
3. Get further rasters (**complementary rasters**) and align those to the Master

The result is a collection of GeoTIFF files that is standardized in terms of projection, bounding box, resolution, and exact pixel location.

The package is built in Python, with almost all functions being in reality GDAL wrappers designed to simplify the workflow and reduce number of lines of code required to do a project.


## Installation
Ubuntu: pip install "git+https://github.com/pete-jacobsson/gdgtm"

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
The module is built around two main sub-modules:
- gdgtm_core: covers functions for getting and transforming the data
- gdgtm_manager: covers functions for automating DM tasks and initiating core functions

Specific usage examples provided in the documentation.


## Supported Data Formats
gdgtm has only been tested for geotif (.tif) format.

## Testing
gdgtm are built in Jupyter with explicit tests built into the process.
The functions are then copied into the gdgtm repo and tested from re-build against original tests

## License
MIT License

## Contact
Pete Jacobsson (pt.jacobsson@gmail.com)
