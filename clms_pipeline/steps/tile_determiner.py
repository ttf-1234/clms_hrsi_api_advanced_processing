import os
import requests
import zipfile
import glob
import geopandas as gpd
import rasterio
import shapely.geometry

class TileDeterminer:
    def __init__(self, config):
        self.config = config

    def determine_tiles(self):
        print("Determining Sentinel-2 tiles for each reference raster...")
        url = "https://sentiwiki.copernicus.eu/__attachments/1692737/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.zip?inst-v=7e368646-a179-477f-af62-26dcc645dd8a"
        base_dir = os.path.dirname(self.config.__file__) if hasattr(self.config, "__file__") else os.getcwd()
        destination_path = os.path.join(base_dir, "data/tile_system/S2_tile_info.zip")
        unziped_path = os.path.join(base_dir, "data/tile_system/")
        os.makedirs(unziped_path, exist_ok=True)

        # Download and unzip tile system shapefile if not already existing
        if os.path.exists(unziped_path) and os.listdir(unziped_path):
            print("File already exists, skipping downloading and unzipping!")
        else:
            response = requests.get(url)
            with open(destination_path, "wb") as f:
                f.write(response.content)
            if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
                print("S2 tile system shapefile in .zip format was successfully downloaded!\n")
                with zipfile.ZipFile(destination_path, 'r') as zip_ref:
                    zip_ref.extractall(unziped_path)
                os.remove(destination_path)
                print("Tile system information file downloaded and unzipped!\n")
            else:
                print("Download failed or zip file is empty!")
                return

        kml_files = glob.glob(os.path.join(unziped_path, "*.kml"))
        if not kml_files:
            print("No KML file found in the directory!")
            return
        else:
            s2_tile_system = gpd.read_file(kml_files[0])
            print("KML file loaded into Python!")
            print("KML CRS:", s2_tile_system.crs)

        for raster_entry in self.config.reference_rasters:
            AOI_path = os.path.join(self.config.reference_raster_dir, raster_entry["name"])
            raster_name = os.path.splitext(os.path.basename(AOI_path))[0]
            result_path = os.path.abspath(os.path.join(base_dir, 'data/tile_system/', f"relevant_tiles_{raster_name}.txt"))

            if not os.path.exists(AOI_path):
                print(f"Reference raster file not found: {AOI_path}")
                continue

            with rasterio.open(AOI_path, "r") as src:
                if src.crs is not None:
                    bounds = src.bounds
                    aoi_geom = shapely.geometry.box(bounds.left, bounds.bottom, bounds.right, bounds.top)
                    aoi_gdf = gpd.GeoDataFrame({'geometry': [aoi_geom]}, crs=src.crs)
                else:
                    print("The reference raster does not have a CRS defined. Using config CRS:", raster_entry["crs"])
                    bounds = src.bounds
                    aoi_geom = shapely.geometry.box(bounds.left, bounds.bottom, bounds.right, bounds.top)
                    aoi_gdf = gpd.GeoDataFrame({'geometry': [aoi_geom]}, crs=raster_entry["crs"])

            aoi_gdf = aoi_gdf.to_crs(s2_tile_system.crs)
            intersecting_tiles = s2_tile_system[s2_tile_system.intersects(aoi_gdf.geometry.iloc[0])]

            if not intersecting_tiles.empty:
                with open(result_path, 'w') as f:
                    for tile in intersecting_tiles['Name']:
                        f.write(f"{tile}\n")
                print(f"Intersecting tiles written to {result_path}")
                print("Determined tiles for raster:", AOI_path)
                for tile in intersecting_tiles['Name']:
                    print(f"  {tile}")
            else:
                print(f"No intersecting tiles found for raster: {AOI_path}")
