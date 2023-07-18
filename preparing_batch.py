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
        self.geofile_paths = []
        self.geo_type = None
        self._geo_init()
        self.expected_exts = self._expected_exts()

    def checkup(self):
        paths = self._missed_file_paths()
        self._logger("Missing files:", paths)
        paths = self._unclaimed_file_paths()
        self._logger("Unclaimed files:", paths)

    def _geo_init(self):
        shapefile_paths = self._file_paths("shp")
        tiffile_paths = self._file_paths("tif")
        shp_num = len(shapefile_paths)
        tif_num = len(tiffile_paths)
        if shp_num > 0 and tif_num > 0:
            self.logging.info(
                "Can not run with mixing shapefiles and raster files in the same directory!"
            )
            raise NotImplementedError
        if shp_num == 0 and tif_num == 0:
            self.logging.info(
                "No shapefiles or raster files found in the source directory!"
            )
            raise NotImplementedError
        if shp_num > 0:
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
        for geofile_path in self.geofile_paths:
            paths.extend(self._missed_file_paths_from_geofile(geofile_path))
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

    def _missed_file_paths_from_geofile(self, geofile) -> List:
        paths = []
        base = os.path.splitext(geofile)[0]
        for ext in self.expected_exts:
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


################################################################################################
#                                 2. set up                                                    #
################################################################################################
# Source data directory
source_batch_path = "D:\small_test\Vector_sample_fake"

# Log file
logfile = "D:\Log\shpfile_projection.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s - %(levelname)s",
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

# 3. Raster grid


logging.info(f"***'batch_preparing' finished.")
