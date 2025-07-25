"""
Summary:
--------
This script downloads the Sentinel-2 tile system shapefile (if not already present), extracts it, and determines which Sentinel-2 tiles intersect with the area of interest (AOI) defined by your reference raster.  
The names of the intersecting tiles are written to a text file for use in further processing.

Source of tile system: https://sentiwiki.copernicus.eu/__attachments/1692737/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.zip?inst-v=7e368646-a179-477f-af62-26dcc645dd8a

Code with comments:
-------------------
"""

##### Packages #####
import requests         # For downloading files from the internet
import zipfile          # For extracting zip files
import sys
sys.path.append('../')
import os               # For file and directory operations
import glob             # For finding files by pattern
import geopandas as gpd # For working with geospatial vector data
import rasterio         # For working with raster data
import shapely.geometry # For geometric operations
import config           # Project configuration

##### I/O paths and URLs #####
url = "https://sentiwiki.copernicus.eu/__attachments/1692737/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.zip?inst-v=7e368646-a179-477f-af62-26dcc645dd8a"
destination_path = "./../data/tile_system/S2_tile_info.zip"
unziped_path = "./../data/tile_system/"
AOI_path = config.reference_raster_path
result_path = config.tile_txt_path

##### Download and unzip tile system shapefile if not already existing #####
if os.path.exists(unziped_path) and os.listdir(unziped_path):
    print("File already exists, skipping downloading and unzipping!")
else:
    # Download the tile system zip file
    response = requests.get(url)
    with open(destination_path, "wb") as f:
        f.write(response.content)
    # Check if download was successful
    if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
        print("S2 tile system shapefile in .zip format was successfully downloaded!\n")
        # Extract the zip file
        with zipfile.ZipFile(destination_path, 'r') as zip_ref:
            zip_ref.extractall(unziped_path)
        os.remove(destination_path)
        print("Tile system information file downloaded and unzipped!\n")
    else:
        print("Download failed or zip file is empty!")
        exit(1)

##### Read tile system shapefile #####
kml_files = glob.glob(os.path.join(unziped_path, "*.kml"))
if not kml_files:
    print("No KML file found in the directory!")
    exit(1)
else:
    # Load the KML file as a GeoDataFrame
    s2_tile_system = gpd.read_file(kml_files[0])
    print("KML file loaded into Python!")
    print("KML CRS:", s2_tile_system.crs)

##### Read reference raster and turn into box #####
if not os.path.exists(AOI_path):
    print(f"Reference raster file not found: {AOI_path}")
    exit(1)

with rasterio.open(AOI_path, "r+") as src:
    # If the raster has no CRS, set it from config
    if src.crs is None:
        print("The reference raster does not have a CRS defined.")
        src.crs = config.reference_raster_crs
    # Get the bounding box of the raster as a shapely geometry
    bounds = src.bounds
    aoi_geom = shapely.geometry.box(bounds.left, bounds.bottom, bounds.right, bounds.top)
    aoi_gdf = gpd.GeoDataFrame({'geometry': [aoi_geom]}, crs=src.crs)

##### Find intersecting tiles #####
# Reproject AOI to tile system CRS if needed
aoi_gdf = aoi_gdf.to_crs(s2_tile_system.crs)
# Find all tiles that intersect with the AOI
intersecting_tiles = s2_tile_system[s2_tile_system.intersects(aoi_gdf.geometry.iloc[0])]

##### Write intersecting tiles to file #####
if not intersecting_tiles.empty:
    with open(result_path, 'w') as f:
        for tile in intersecting_tiles['Name']:
            f.write(f"{tile}\n")
    print(f"Intersecting tiles written to {result_path}")
    print("Determined tiles:")
    for tile in intersecting_tiles['Name']:
        print(f"  {tile}")
else:
    print("No intersecting tiles found.")

