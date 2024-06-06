### Functions allowing to get data from Chelsa: https://chelsa-climate.org/


### List of functions----------------------------------------------------------

## 1 get_chelsa_daily
## 2 get_chelsa_bio_19812010_data
## 3 get_chelsa_clim_19812010_data


# 1 get_chelsa_daily ----------------------------------------------------------

def get_chelsa_daily (parameter, bbox, interval, dst_path, dst_name):
    """
    This function gets a cropped raster from Chelsa (https://chelsa-climate.org/), saves it as a .tiff to designated folder, checks that the .tiff exists, and prints a confirmation to the console.

    Args:
        parameter (str): The name of the variable used by Chelsa to find the intended data (has to be CMIP5 standard short name - specifies what climate varia is desired, see https://chelsa-climate.org/wp-admin/download-page/CHELSA_tech_specification_V2.pdf for possible varias).
        bbox (tuple): a tuple of four floats defining the area covered (WNES)
        interval (tuple): a yyyy-mm-dd formatted string determining the start date (position 0) and end date (position 1)
        target_directory (str): location to which the downloaded .tiff is written
        dst_name (str): First part of the file name

    Returns:
        str: string confirming that the intended .tiff indeed exists in the target location

    Assumptions:
    1. The provided interval is covered by Chelsa data.
    2. The parameter name is correct.
    3. os and GDAL are working (function tested using GDAL 3.4.1)
    4. datetime and dateutil are working (function tested using versions 5.5 and 2.8.2)
    4. Function tested using Python 3.10.12

    Usage example:
    >>> get_chelsa_data(parameter = "tas", 
    >>>                 bbox = (7.3, 47.2, 7.5, 47.0), 
    >>>                 interval = ("2023-01-01", "2023-01-05"), 
    >>>                 dst_path = '/home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/',
    >>>                 dst_name = "chelsa_tas_"
    >>>                )
    File exists: /home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_01_01_2023.tif
    File exists: /home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_02_01_2023.tif
    File exists: /home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_03_01_2023.tif
    File exists: /home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_04_01_2023.tif
    File exists: /home/pete/Documents/tests_and_vals/gdgtm/01_get_functions/chelsa_tas_05_01_2023.tif

    """
    
    ## Import the relevant Python and R packages with names corresponding to those used in the current function
    import os
    from osgeo import gdal
    from datetime import datetime
    from dateutil.rrule import rrule, DAILY ## Note that this has to be imported exactly this way for the function to work

    ## Create a list of dates from the interval
    start_date = datetime.strptime(interval[0], "%Y-%m-%d")
    end_date = datetime.strptime(interval[1], "%Y-%m-%d")
    dates = [dt.strftime("%d_%m_%Y") for dt in rrule(freq = DAILY, dtstart = start_date, until = end_date)]

    ## Transform dates into target_urls
    core_url = "https://os.unil.cloud.switch.ch/chelsa02/chelsa/global/daily/" + parameter + "/YEAR/CHELSA_"+ parameter + "_DATE_V.2.1.tif"
    target_urls = []

    for date in dates:
        year = date[6:10]
        target_url = core_url.replace("YEAR", year)
        target_url = target_url.replace("DATE", date)
        target_urls.append(target_url)
        
    ## Use GDAL to download the rasters and enforce the desired bounding box
    ## First initialize list for filename QC check:
    return_strings = []

    for i in range(len(dates)):
        dst_raster = dst_path + dst_name + dates[i] + ".tif"
        url_to_get = target_urls[i]
    
        ##Get raster from URL and apply the bounding box
        src_raster = gdal.Open(url_to_get)
        gdal.Translate(dst_raster, src_raster, projWin = bbox)
        src_raster = None ## Close connection
    
        if os.path.isfile(dst_raster):
            return_strings.append("File exists: " + dst_raster)
        else:
            return_strings.append("Warning, file does NOT exist: " + dst_raster)

    return return_strings


# 2 get_chelsa_bio_19812010_data ----------------------------------------------
def get_chelsa_bio_19812010_data (parameter, bbox, dst_raster):
    '''
    This function retrieves 1980 - 2010 BIOCLIM+ data from the Chelsa S3 bucket (https://envicloud.wsl.ch/#/?prefix=chelsa%2Fchelsa_V2%2F).
    The function can be modified to point at a broader range of sources by changing the base_url and adjusting URL construction(indicated below)
    
    **Agrs:**
        - parameter (str): specifies which parameter is being sought. Needs to be exactly one of the paramter names specified in: https://chelsa-climate.org/bioclim/
        - bbox (tuple): specifies the bounding box of the saved raster. Include edges in the following order: WNES in degrees relative to WGS84
        - dst_raster (str): path and filename to the raster destination
        
    **Returns:**
        - str: confirmation that file exists
        
    **Assumptions:**
    1. Function tested using GDAL 3.4.1
    2. Function tested using Python 3.10.12
    3. The downloaded file is a GeoTIFF

    **Usage:**
    >>> extent = (5.7663, 47.9163, 10.5532, 45.6755)
    >>> get_chelsa_bio_19812010_data("swe", bbox = extent, dst_raster = "/home/pete/Downloads/chesla_bio_test.tif")
    File exists: /home/pete/Downloads/chesla_bio_test.tif
      
    '''
    
    from osgeo import gdal
    import os
    
    ## Construct URL - Modify here to point at other parts of the CHELSA S3 bucket
    base_url = "https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V2/GLOBAL/climatologies/1981-2010/bio/CHELSA_"
    url_tail = "_1981-2010_V.2.1.tif"
    url_to_get = base_url + parameter + url_tail
    
    ##Get raster from URL and apply the bounding box
    src_raster = gdal.Open(url_to_get)
    gdal.Translate(dst_raster, src_raster, projWin = bbox)
    
    if os.path.exists(dst_raster):
        return_string = "File exists: " + dst_raster
    else:
        return_string = "File does not exist: " + dst_raster
    
    
    ##Disconnect from file
    src_raster = None
    
    return print(return_string)