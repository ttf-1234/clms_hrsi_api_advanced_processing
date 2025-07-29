# CLMSConfig class definition for pipeline configuration
class CLMSConfig:
    def __init__(self, reference_rasters, clms_username, clms_password, **kwargs):
        self.reference_rasters = reference_rasters
        self.clms_username = clms_username
        self.clms_password = clms_password
        for k, v in kwargs.items():
            setattr(self, k, v)

# Example configuration for CLMS pipeline
config = CLMSConfig(
    reference_rasters=[
        {"name": "dem_rofental_100.asc", "crs": "EPSG:32632"},
        {"name": "dem_guadalfeo_100.asc", "crs": "EPSG:32630"},
        # Add more as needed
    ],
    reference_raster_dir="data/reference_raster/",
    clms_username="xx",
    clms_password="xx",
    clms_query_type="query_and_download",  # Options: "query", "download", "query_and_download"
    clms_product=["FSC"],  # ALLOWED_PRODUCTS = ["FSC", "PSA", "SWS", "WDS", "GFSC"]
    start_date="2023-07-01T00:00:00Z",
    end_date="2023-07-02T23:59:59Z",
    output_path_original="data/clms_data/original/",
    output_path_processed="data/clms_data/processed/",
    mosaic_output=True,
    reclassify=True,
    crop_resample=True,
    filter_cc=False,
    cc_threshold=0.2,
)
