
import arcpy
import common_helper
import workspace_directory
import constants

class ValidateIngestionFilesTool(object):
    def __init__(self):
        self.label = "7 - Run to validate result files"

    def getParameterInfo(self):
        result_directory_path_param = arcpy.Parameter(
            displayName="The result directory",
            name="Result Directory",
            datatype="GPString",
            direction="Output"
        )    
        
        return [result_directory_path_param]

    def updateParameters(self, parameters):
        val0 =  constants.no_prcess_path_selected
        if (workspace_directory.source_batch_directory_path is not None):
          val0 = workspace_directory.results_directory_path
       
        parameters[0].value = val0
        return

    def execute(self, parameters, messages):
        common_helper.call_run_tool('validate_ingestion_files')
        return
  