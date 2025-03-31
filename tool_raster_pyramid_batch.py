import arcpy
import workspace_directory
import common_helper
import constants

class CreateRasterPyramidTool(object):
    def __init__(self):
        self.label = "1 .2 - Run to create raster pyramid for projected raster GeoTIFF files"
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
        val = constants.no_prcess_path_selected
        if (workspace_directory.projected_batch_directory_path is not None):
            val = workspace_directory.projected_batch_directory_path            
        parameters[0].value = val
        
        return

    def execute(self, parameters, messages):
        common_helper.call_run_tool('raster_pyramid_batch')
        return