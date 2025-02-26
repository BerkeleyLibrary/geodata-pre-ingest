import arcpy
import os
import logging
from typing import List
from pathlib import Path
from datetime import datetime
import workspace_directory
import raster_pyramid_batch


class CreateRasterPyramidTool(object):
    def __init__(self):
        self.label = "1 .2 - Create raster pyramid for projected raster GeoTIFF files"
        self.title = "This is a title"
        
    def getParameterInfo(self):
        projected_path_param = arcpy.Parameter(
            displayName="Create Pyramids for GeoTIFF files in this directory",
            name="To Directory",
            datatype="GPString",
            direction="Output"

        )
        
        return [projected_path_param]

    def updateParameters(self, parameters):
        val = "Please select a geodata batch in tool 0. 0 - Select a processing batch"
        if (workspace_directory.projected_batch_directory_path is not None):
            val = workspace_directory.projected_batch_directory_path            
        parameters[0].value = val
        
        return

    def execute(self, parameters, messages):
        projected_batch_directory_path = workspace_directory.projected_batch_directory_path
        if raster_pyramid_batch.verify_setup(
            [],
            [projected_batch_directory_path],
        ):
            raster_pyramid_batch.add_pyramid_to_geotif_files()
            # output(f"***completed {script_name}")
