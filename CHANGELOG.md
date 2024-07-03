## Versions 0.0.1 - 0.0.4 (Closed)
- Developing function to downlaod data from Chelsa
- Developing the core pipeline up to post-reprojecting application of a Bounding Box

## Version 0.1 (current)
- 0.1.0: implemented two functions: download of cog names from STAC collection and downloading cogs from OLM (in test)

## Version 0.2 (skipped)
- 0.2.0: implement raster mosaics (moved to 0.4.0)
- 0.2.1: implement raster aligning (moved to 0.3.0)

## Version 0.3 (current)
- 0.3.0: implemented align_validate_raster

## Version 0.4 (current)
- 0.4.0: implemented raster mosaics and raster merging

## Version 0.5 (current)
- 0.5.0: Add summarize_stac
- 0.5.1: Fix issue 2: getting OLM function to work with non-timestamped data
- 0.5.2: Standardize bbox inputs (make GDAL compatible)
- 0.5.3: Added Python-only Chelsa get functions, aiming at 1980-2010 BIOCLIM+
- 0.5.4: Changed the get_chelsa_data to get_chelsa_daily (including change of underpinning dependencies from Rchelsa to GDAL)
- 0.5.5: Changed rasterio dependencies to GDAL

## Version 0.6 (test)
- 0.6.1 Module re-organization, including function renaming
- 0.6.2 rasterize_shape
- 0.6.3 numpyify_raster + general clean-up


## Version 0.7 (planned)
- 0.7.0: Add automated workflow to a blank raster

