# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
from shutil import copyfile, rmtree
from tool_create_workspace import CreateWorkspaceTool
from tool_select_workspace import SelectWorkspaceTool
from tool_prepare_batch import PrepareBatchTool
from tool_raster_pyramid_batch import CreateRasterPyramidTool
from tool_batch_export_csv import BatchExportCsvTool
from tool_assign_arkid import AssignArkidTool
from tool_check_csv_files import CheckCsvFilesTool
from tool_batch_create_iso19139 import BatchCreateIso19139Tool

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GeoblacklightToolbox"
        self.alias = "geoblacklight_toolbox"    
        self.tools = [CreateWorkspaceTool,
                      SelectWorkspaceTool, 
                      PrepareBatchTool, 
                      CreateRasterPyramidTool, 
                      BatchExportCsvTool,
                      AssignArkidTool, 
                      CheckCsvFilesTool,
                      BatchCreateIso19139Tool]
