# gdgtm (Geospatial Data Getting Transforming and Managing)

## Project overviews
The purpose of the project is to wrap a set of extant Python utilities to streamline geospatial data downloads and processing (reprojection, bound setting and mosaicing), to allow easier pipeline construction for downstream processing.

The package is built in Python, with calls to R code as relevant.

## Installation
Ubuntu: pip install "git+https://github.com/pete-jacobsson/gdgtm"

### Package was developed and tested using the following:
* Python 3.10.12
* GDAL 3.4.1
* Numpy 1.24.3
* rasterio 1.3.10
* pystac 1.10.1
* pandas 2.0.3
* rpy2 3.5.16
The .toml is configured to import these versions of the packages or higher.


One function, get_chelsa_data, uses R components (gdgtm versions < 0.6). The package was tested in the following configuration:
* R 4.1.2
* Rchelsa 1.0.1
* lubridate 1.9.3
* terra 1.7.71
* 


## Usage
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
