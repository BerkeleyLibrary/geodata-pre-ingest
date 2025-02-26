
import arcpy
import os
import logging
from pathlib import Path
from datetime import datetime
from shutil import copyfile, rmtree
import common_helper
import workspace_directory
import prepare_batch
import logger

class PrepareBatchTool(object):
    def __init__(self):
        self.label = "1 .1 - prepare_batch"
        self.description = "1 .1 - prepare_batch - desc"

    def getParameterInfo(self):
        from_source_path_param = arcpy.Parameter(
            displayName="Projected from below source batch directory",
            name="From Directory",
            datatype="GPString",
            direction="Output"
        )    
        to_projected_path_param = arcpy.Parameter(
            displayName="To this directory",
            name="To Directory",
            datatype="GPString",
            direction="Output"

        )
        
        return [ from_source_path_param, to_projected_path_param]

    def updateParameters(self, parameters):
        val = "Please select a geodata batch in tool 0. 0 - Select a processing batch"
        val1 = val
        val2 = val
        if (workspace_directory.projected_batch_directory_path is not None):
            val1 = workspace_directory.source_batch_directory_path
            val2 = workspace_directory.projected_batch_directory_path            
        parameters[0].value = val1
        parameters[1].value = val2
        return

    def execute(self, parameters, messages):
        source_batch_directory_path = workspace_directory.source_batch_directory_path
        projected_batch_directory_path = workspace_directory.projected_batch_directory_path

        # A GeoTIFF projected file
        geotif_referenced_filepath = (
            r"C:\pre-ingestion-config\projected_raster\5048_1_reproject4326.tif"
        )

        if common_helper.verify_setup(
            [geotif_referenced_filepath],
            [source_batch_directory_path, projected_batch_directory_path],
        ):
            source_batch = prepare_batch.SourceBatch(source_batch_directory_path, logging)
            source_batch.check_files()
            source_batch.prepare(projected_batch_directory_path, geotif_referenced_filepath)
        script_name = "1 .1 - prepare_batch.py"
        # arcpy.AddMessage(f"***completed1 {script_name}")
        a = f"***completed11111 {script_name}"
        logger.output(a)
        return

    
