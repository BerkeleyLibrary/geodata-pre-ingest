import arcpy
import os
from pathlib import Path
import common_helper
import workspace_directory

class SourceBatch(object):
    def __init__(self):
       
        self.source_dir = workspace_directory.source_batch_directory_path
        self.all_file_paths = self._file_paths("")
        self._geo_init()

    def check_files(self):
        self._check_missed_files()
        self._check_exceptional_files()

    def prepare(self, referenced_filepath):
        def is_projected(file_path):
            if Path(file_path).is_file():
                sr_name = arcpy.Describe(file_path).spatialReference.name
                return sr_name == "GCS_WGS_1984"
            return False

        def projection(geofile_path, prj_geofile_path):
            if self.geo_type == "shp":
                self.vector_projection(geofile_path, prj_geofile_path)
            else:
                self.raster_projection(
                    geofile_path, prj_geofile_path, referenced_filepath
                )

        for geofile_path in self.geofile_paths:
            name = os.path.basename(geofile_path)
            prj_geofile_path = os.path.join(workspace_directory.projected_batch_directory_path, name)
            if is_projected(prj_geofile_path):
                continue
            projection(geofile_path, prj_geofile_path)

    def _geo_init(self):
        shapefile_paths = self._file_paths(".shp")
        tiffile_paths = self._file_paths(".tif")
        if not shapefile_paths and not tiffile_paths:
            common_helper.output(f"No shapefiles or raster files found in {self.source_dir}.", 2)
            raise ValueError(
                "Directory should include either shapefiles or raster files"
            )

        if shapefile_paths and tiffile_paths:
            common_helper.output(f"Mixing shapefiles and raster files found in {self.source_dir}.")
            raise ValueError(
                "Both shapefiles and raster files found. Directory should include either shapefiles or raster files."
            )

        if shapefile_paths:
            self.geofile_paths = shapefile_paths
            self.geo_type = "shp"
        else:
            self.geofile_paths = tiffile_paths
            self.geo_type = "tif"

    def _expected_exts(self):
        if self.geo_type is None:
            raise NotImplementedError
        DEFAULT_VECTOR_EXTS = [
            ".cpg",
            ".dbf",
            ".prj",
            ".sbn",
            ".sbx",
            ".shp",
            ".shp.xml",
            ".shx",
        ]
        DEFAULT_RASTER_EXTS = [".tif", ".aux", ".tfw", ".tif.xml", ".tif.ovr"]
        return DEFAULT_VECTOR_EXTS if self.geo_type == "shp" else DEFAULT_RASTER_EXTS

    def _check_missed_files(self):
        paths = []
        expected_exts = self._expected_exts()
        for geofile_path in self.geofile_paths:
            paths.extend(
                self._missed_file_paths_from_geofile(geofile_path, expected_exts)
            )
        self._logger("Missing files:", paths)

    def _check_exceptional_files(self):
        def stem_and_basename():
            stems = [Path(geofile_path).stem for geofile_path in self.geofile_paths]
            basenames = [
                os.path.basename(geofile_path) for geofile_path in self.geofile_paths
            ]
            return stems + basenames

        paths = []
        geo_stems = stem_and_basename()
        for file_path in self.all_file_paths:
            # abc.shp.xml
            stem = Path(file_path).stem
            if stem not in geo_stems:
                paths.append(file_path)
        self._logger("Exceptional files:", paths)

    def _logger(self, summary, list):
        if len(list) > 0:
            common_helper.output(f"{summary}", 1)
            for l in list:
                common_helper.output(f"{l}", 1)

    def _missed_file_paths_from_geofile(self, geofile, expected_exts):
        paths = []
        base = os.path.splitext(geofile)[0]
        for ext in expected_exts:
            expected_file_path = f"{base}{ext}"
            if expected_file_path not in self.all_file_paths:
                paths.append(expected_file_path)
        return paths

    def _file_paths(self, ext):
        paths = []
        for file in os.listdir(self.source_dir):
            if file.endswith(ext):
                file_path = os.path.join(self.source_dir, file)
                if os.path.isfile(file_path):
                    paths.append(file_path)
        return paths

    def vector_projection(self, from_filepath, to_filepath):
        try:
            wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
            sr = arcpy.SpatialReference()
            sr.loadFromString(wkt)
            arcpy.Project_management(from_filepath, to_filepath, sr)
        except Exception as ex:
            common_helper.output(f"{from_filepath} - {ex}")

    def raster_projection(self, from_filepath, to_filepath, referenced_filepath):
        try:
            sr = arcpy.Describe(referenced_filepath).spatialReference
            arcpy.ProjectRaster_management(from_filepath, to_filepath, sr)
        except Exception as ex:
            common_helper.output(f"{from_filepath} - {ex}")


# Default geofile extensions
# Add or remove extenstions in below lists based on requirements
DEFAULT_RASTER_EXTS = [".tif", ".aux", ".tfw", ".tif.xml", ".tif.ovr"]
DEFAULT_VECTOR_EXTS = [
    ".cpg",
    ".dbf",
    ".prj",
    ".sbn",
    ".sbx",
    ".shp",
    ".shp.xml",
    ".shx"
]
  
def run_tool():
    # A GeoTIFF projected file
    geotif_referenced_filepath = (
        r"C:\pre-ingestion-config\projected_raster\5048_1_reproject4326.tif"
    )
    common_helper.verify_workspace_and_files([geotif_referenced_filepath])
    
    source_batch = SourceBatch()
    source_batch.check_files() # todo: move this to other tool
    source_batch.prepare(geotif_referenced_filepath)