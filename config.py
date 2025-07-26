import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

##### Path of the reference raster #####
reference_raster_path = os.path.join(BASE_DIR, "data/reference_raster/dem_rofental_100.asc")
reference_raster_crs = "EPSG:32632"
tile_txt_path = os.path.join(BASE_DIR, "data/tile_system/relevant_tiles.txt")

##### CLMS credentials #####
clms_username = "xxx"
clms_password = "xxx"

##### CLMS product ID #####
clms_query_type = "query_and_download"  # Options: "query", "download", "query_and_download"
# ALLOWED_PRODUCTS = ["FSC", "PSA", "SWS", "WDS", "GFSC"]
clms_product=["FSC","PSA"]

##### Period #####
start_date = "2023-01-01T00:00:00Z"
end_date = "2023-01-15T23:59:59Z"

##### Output path for downloaded data #####
output_path_original = os.path.join(BASE_DIR, "data/clms_data/original/")
output_path_processed = os.path.join(BASE_DIR, "data/clms_data/processed/")

##### Further processing #####
mosaic_output = True
reclassify = False
crop_resample = True
filter_cc = True
cc_threshold = 0.2
