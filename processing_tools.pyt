from tool_create_workspace import CreateWorkspaceTool
from tool_select_workspace import SelectWorkspaceTool
from tool_source_batch_projection_transform import SourceBatchProjectionTransformTool
from tool_raster_pyramid_batch import CreateRasterPyramidTool
from tool_batch_export_csv import BatchExportCsvTool
from tool_assign_arkid import AssignArkidTool
from tool_check_csv_files import CheckCsvFilesTool
from tool_batch_create_iso19139 import BatchCreateIso19139Tool
from tool_batch_create_geoblacklight import BatchCreateGeoblacklightTool
from tool_create_ingestion_files import CreateIngestionFilesTool
from tool_validate_ingestion_files import ValidateIngestionFilesTool
from tool_rename_and_copy_files import RenameAndCopyFilesTool
from tool_source_batch_check import SourceBatchCheckTool

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GeoblacklightToolbox"
        self.alias = "geoblacklight_toolbox"    
        self.tools = [RenameAndCopyFilesTool,
                      CreateWorkspaceTool,
                      SelectWorkspaceTool, 
                      SourceBatchProjectionTransformTool, 
                      CreateRasterPyramidTool, 
                      BatchExportCsvTool,
                      AssignArkidTool, 
                      CheckCsvFilesTool,
                      BatchCreateIso19139Tool,
                      BatchCreateGeoblacklightTool,
                      CreateIngestionFilesTool,
                      ValidateIngestionFilesTool,
                      SourceBatchCheckTool]
