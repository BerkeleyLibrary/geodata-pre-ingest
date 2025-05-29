import source_batch
import common_helper

def run_tool():  
    # A GeoTIFF projected file
    geotif_referenced_filepath = (
        r"C:\pre-ingestion-config\projected_raster\5048_1_reproject4326.tif"
    )
    common_helper.verify_workspace_and_files([geotif_referenced_filepath])
    source_batch.projection_transform(geotif_referenced_filepath)