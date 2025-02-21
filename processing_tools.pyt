# -*- coding: utf-8 -*-

import arcpy
import os
import logging
from pathlib import Path
from datetime import datetime
from shutil import copyfile, rmtree
import workspace_directory
import common_helper
import prepare_batch


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GeoblacklightToolbox"
        self.alias = "geoblacklight_toolbox"    
        self.tools = [DefineWorkspaceTool, PrepareBatchTool]

class DefineWorkspaceTool:
    def __init__(self):
        self.label = "0. 0 - Select a processing batch"
        self.description = "0.0 - "

    def getParameterInfo(self):
        input_param = arcpy.Parameter(
            displayName="Geobalcklight data processing directory",
            name="Input Processing Pirectory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
       
        return [input_param]
   
    def execute(self, parameters, messages):
        # common_helper.batch_directory = parameters[0].valueAsText
        workspace_directory.source_batch_directory_path = parameters[0].valueAsText
        parent_path = os.path.dirname(parameters[0].valueAsText)
        workspace_directory.projected_batch_directory_path = fr"{parent_path}\source_batch_projected"

        return

   

class PrepareBatchTool:
    def __init__(self):
        self.label = "1 .1 - prepare_batch"
        self.description = "1 .1 - prepare_batch - desc"

    def getParameterInfo(self):
        """Define the tool parameters."""
        output_param = arcpy.Parameter(
            displayName="Projected to Directory",
            name="Projected to Directory",
            datatype="GPString",
            direction="Output"

        )
        
        # arcpy.SetParameterAsText(output_param, 'result')
        return [output_param]

    def updateParameters(self, parameters):
        val = "Please select a geodata batch in tool 0. 0 - Select a processing batch" if (workspace_directory.projected_batch_directory_path is None) else  workspace_directory.projected_batch_directory_path
        parameters[0].value = val
        return
     

    def execute(self, parameters, messages):
        arcpy.AddMessage("!!- starting preparing data!!!.")
        logfile = r"C:\process_data\log\process.log"
        logging.basicConfig(
            filename=logfile,
            level=logging.INFO,
            format="%(message)s - %(asctime)s - %(funcName)s - %(levelname)s",
        )

        # input_fc = parameters[0].valueAsText
        # output_fc = parameters[1].valueAsText

        # source_batch_directory_path =  common_helper.batch_directory
        source_batch_directory_path = workspace_directory.source_batch_directory_path
        # 3. Please provide projected data directory path
        # parent_path = os.path.dirname(source_batch_directory_path)
        # projected_batch_directory_path = fr"{parent_path}\source_batch_projected"
        projected_batch_directory_path = workspace_directory.projected_batch_directory_path

       

        arcpy.AddMessage(projected_batch_directory_path)

        # 4. A GeoTIFF projected file
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
        arcpy.AddMessage(f"***completed {script_name}")
        return

    
