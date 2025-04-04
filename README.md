# gdgtm (Geospatial Data Getting Transforming and Managing)

## Project overview
The purpose of this package is to simplify getting, transforming and managing geospatial data within programmatic workflows. What we want to achieve here is a platform that will allow, in relatively few lines of code, to bulk process sizeable volumes of geospatial data for downstream analysis, quickly.

Hence, if you want to run a machine learning project based on a collection of a hundred rasters downlaoded from different sources, but first need to align those rasters, you might find gdgtm helpful.

To get an overview of the functuionality see the test script and the Documentation.


## Package build
The package is compiled using the .toml process:
python -m build

Building the deocs:
chmod +x generate_docs.sh
./build_docs.sh


## Installation
You can install it from github (requires GIT):
pip install "git+https://github.com/pete-jacobsson/gdgtm"


## Package was developed and tested using the following:
The .toml is configured to import these versions of the packages or higher:

- numpy 1.24.3
- pillow 10.3.0
- rasterio 1.3.10
- seaborn 0.13.2
- matplotlib 3.8.2


## Supported Data Formats
gdgtm has only been tested for geotif (.tif) format.

## Testing
gdgtm functions are built in Jupyter with explicit tests built into the process.
Beyond in-development testing, all functions in the "main" branch will have been run through the test script, including failure tests.

## License
MIT License

## Contact
Pete Jacobsson (pt.jacobsson@gmail.com)
