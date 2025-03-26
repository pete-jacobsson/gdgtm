# gdgtm (Geospatial Data Getting Transforming and Managing)

## Package overview
This package is about simplifying repetitive spatial data management actions. Its success is defined by whether it can allow someone with limited knowledge of spatial data processing packages or GIS software to batch-process simple transformations from a code-based interface with Python.

For example, if you a Neural Networks kind of person and you have an idea for a project that involves reprojecting, clipping, or aligning a whole bunch of different rasters, you might find this package useful (these guys told me they did: https://www.biorxiv.org/content/10.1101/2025.01.31.635975v1.full).

Underneath the hood the package consists of a set of rasterio wrappers for common problems, using functional Python throughout. While I see advantages in moving towards an OOP approach, I find a functional approach more logical in this kind of context (though this might change).

I chose rasterio because it is easier to install in Python environments than GDAL is (at least in my exxperience from June 2024). Of course, this is not an issue if you're using Conda, but a) not everyone likes Conda and b) your HPC Cluster Sysadmin might have reasons for deep dislike of Conda.

The package is built around a process-based approach, where you can "inject" your data at any stage:
* Getting Geospatial data from online resources (*note: this functionality needs to be re-instated after the move from a GDAL base: see CHANGELOG*)
* Setting up a target blank covering the bit of the map that you want covered in the projection you need, with the datatype necessary for your project
* Aligning your geospatial data to that target blank

If you are interested in an example project, check out the sample_pipeline.py, which uses development versions of the functions herein to produce rasters underpinning some Neural Network research in an upcoming paper.

If you want to know more, check out the demo and the Documentation folder.

Last, if you would like to know the extent of the testing, see the tests notebook.


## Installation

=======
pip install "git+https://github.com/pete-jacobsson/gdgtm" 


### Package was developed and tested using the following:
* Python 3.10.12
* datetime 5.5
* dateutil 2.8.2
* Numpy 1.24.3
* rasterio 1.3.10
* pystac 1.10.1
* pandas 2.0.3

The .toml is configured to import these versions of the packages or higher.

## Structure
The package is built around the following modules:
- auto_workflow
- get
- transform
- manage

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
