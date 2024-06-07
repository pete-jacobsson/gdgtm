# gdgtm (Geospatial Data Getting Transforming and Managing)

## Project overviews
The purpose of the project is to wrap a set of extant Python utilities to streamline geospatial data downloads and processing (reprojection, bound setting and mosaicing), to allow easier pipeline construction for downstream processing. The main point is to simplify the process of acquiring raster data from online sources and building a straightforward pipeline for their processing and standardization ahead of downstream analysis. As of version 0.5 of the package the get functions are written for OpenLandMap STAC (https://stac.openlandmap.org/) and Chelsa (https://chelsa-climate.org/).

At its core the functions herein are wrappers for **GDAL**: https://gdal.org/index.html

The core workflow of this package is: **To be amended in future version by working from a blank template GeoTiff**
1. Get a raster from an online source
2. Process it to the desired projection, resolution and bounding box - this is the **Master GeoTIFF**
3. Get further rasters (**complementary rasters**) and align those to the Master

The result is a collection of GeoTIFF files that is standardized in terms of projection, bounding box, resolution, and exact pixel location.

The package is built in Python, with almost all functions being in reality GDAL wrappers designed to simplify the workflow and reduce number of lines of code required to do a project.


## Installation
If installing to root in **Ubuntu** use: pip install "git+https://github.com/pete-jacobsson/gdgtm"

*Otherwise*:
The key challenge is getting GDAL up and running: pip install gdal does not work. 
This is easiest achieved through conda:

conda create -n my_env python=3.10  ###Set up a Python 3.10 conda venv

conda activate my_env ### Activate the venv

conda install gdal ### Install GDAL

pip install matplotlib ### Will cause some errors to come up

pip install "git+https://github.com/pete-jacobsson/gdgtm" ### Will cause some errors to come up

### Using jupyter from the conda environment
*To do this you will need to install Jupyter on your conda local environment*:

conda activate myenv (if not active)

conda install -c conda-forge jupyterlab  ### This was tested using Jupyter lab. In principle Jupyter notebook should work as well.

conda install ipykernel

*Next add the environment as a Jupyter Kernel*:

python -m ipykernel install --user --name=myenv --display-name "Python (myenv)"

*Open Jupyter lab*:

jupyter lab







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
The module is built around two main sub-modules: **INVALID**
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
