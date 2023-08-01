import arcpy
import os
import logging
from typing import List
from pathlib import Path
from datetime import datetime


################################################################################################
#                             1. class                                                         #
################################################################################################


class SourceBatch(object):
    def __init__(self, source_dir, logging):
        self.logging = logging
        self.source_dir = source_dir
        self.file_paths = self._file_paths("")
        self._geo_init()

    def checkup(self):
        paths = self._missed_file_paths()
        self._logger("Missing files:", paths)
        paths = self._unclaimed_file_paths()
        self._logger("Unclaimed files:", paths)

    def shp_projection(self, workspace):
        if self.geo_type == "tif":
            return
        for file in self.geofile_paths:
            geofile = GeoFile(file)
            geofile.projection(workspace, self.logging)

    def tif_pyramid(self):
        if self.geo_type == "shp":
            return
        for file in self.geofile_paths:
            geofile = GeoFile(file)
            geofile.pyramid(self.logging)

    def _geo_init(self):
        shapefile_paths = self._file_paths("shp")
        tiffile_paths = self._file_paths("tif")
        if not shapefile_paths and not tiffile_paths:
            self.logging.info(
                f"No shapefiles or raster files found in {self.source_dir}."
            )
            raise ValueError(
                "Directory should include either shapefiles or raster files"
            )

        if shapefile_paths and tiffile_paths:
            self.logging.info(
                f"Mixing shapefiles and raster files found in {self.source_dir}."
            )
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
        return DEFAULT_VECTOR_EXTS if self.geo_type == "shp" else DEFAULT_RASTER_EXTS

    def _missed_file_paths(self):
        paths = []
        expected_exts = self._expected_exts()
        for geofile_path in self.geofile_paths:
            paths.extend(
                self._missed_file_paths_from_geofile(geofile_path, expected_exts)
            )
        return paths

    def _unclaimed_file_paths(self):
        paths = []
        geo_stems = [
            Path(geofile_path).stem for geofile_path in self.geofile_paths
        ]  # abc.shp => abc
        for file_path in self.file_paths:
            stem = Path(file_path).stem
            if stem not in geo_stems:
                paths.append(file_path)
        return paths

    def _logger(self, summary, list):
        if len(list) > 0:
            self.logging.info(f"{summary}")
            for l in list:
                self.logging.info(f"{l}")

    def _missed_file_paths_from_geofile(self, geofile, expected_exts) -> List:
        paths = []
        base = os.path.splitext(geofile)[0]
        for ext in expected_exts:
            expected_file_path = f"{base}{ext}"
            if expected_file_path not in self.file_paths:
                paths.append(expected_file_path)
        return paths

    def _file_paths(self, ext) -> List:
        return [
            os.path.join(dirpath, filename)
            for dirpath, dirs, filenames in os.walk(self.source_dir)
            for filename in filenames
            if filename.endswith(ext)
        ]


class GeoFile(object):
    def __init__(self, geofile):
        self.geofile = geofile

    def projection(self, workspace, logging):
        name = os.path.basename(self.geofile)
        prj_file = os.path.join(workspace, name)
        try:
            wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
            sr = arcpy.SpatialReference()
            sr.loadFromString(wkt)
            arcpy.Project_management(self.geofile, prj_file, sr)
        except Exception as ex:
            logging.info(f"{self.geofile} - {ex}")

    def pyramid(self, logging):
        pylevel = "7"
        skipfirst = "NONE"
        resample = "NEAREST"
        compress = "Default"
        quality = "70"
        skipexist = "SKIP_EXISTING"
        try:
            arcpy.BuildPyramids_management(
                self.geofile, pylevel, skipfirst, resample, compress, quality, skipexist
            )
        except Exception as ex:
            logging.info(f"{self.geofile} - {ex}")


################################################################################################
#                                 2. set up                                                    #
################################################################################################
# 1. Please update source data directory here
source_batch_path = r"D:\small_test\Vector_sample_fake"

# 2. Please updare Workspace directory here
workspace_path = r"D:\workspace"

# 3. Plese update Log file
logfile = r"D:\Log\shpfile_projection.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s - %(funcName)s - %(levelname)s",
)

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
    ".shx",
]


################################################################################################
#                                3. Run options                                                #
################################################################################################
logging.info(f"***starting 'batch_preparing'")
source_batch = SourceBatch(source_batch_path, logging)

# options
# 1. Check Source Batch
source_batch.checkup()

# 2. Vector projection
source_batch.shp_projection(workspace_path)

# 3. Raster grid
source_batch.tif_pyramid()


logging.info(f"***'batch_preparing' finished.")
