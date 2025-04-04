
import arcpy
import common_helper
import workspace_directory
import constants

class SourceBatchCheckTool(object):
    def __init__(self):
        self.label = "1 .0 - Run to verify source data"

    def getParameterInfo(self):
        from_source_path_param = arcpy.Parameter(
            displayName="Source batch directory",
            name="From Directory",
            datatype="GPString",
            direction="Output"
        )    
        
        
        return [ from_source_path_param]

    def updateParameters(self, parameters):
        val0 = constants.no_prcess_path_selected
        if (workspace_directory.projected_batch_directory_path is not None):
            val0= workspace_directory.source_batch_directory_path      
        
        common_helper.assign_parameters(parameters, [val0])
        return

    def execute(self, parameters, messages):
        common_helper.call_run_tool('source_batch_check')
        return

    
