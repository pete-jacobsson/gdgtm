# gdgtm (Geospatial Data Getting Transforming and Managing)

## Project overviews
The purpose of the project is to wrap a set of extant Python utilities to streamline geospatial data downloads and processing (reprojection, bound setting and mosaicing), to allow easier pipeline construction for downstream processing.

The package is built in Python, with calls to R code as relevant.

## Installation
Ubuntu: pip install git+https://github.com/pete-jacobsson/gdgtm

Full lists of dependencies for individual functions are provided in the Documentation files


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
