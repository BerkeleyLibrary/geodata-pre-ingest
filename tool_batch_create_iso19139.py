
import arcpy
import common_helper
import workspace_directory
import constants

class BatchCreateIso19139Tool(object):
    def __init__(self):
        self.label = "5 - Run to create ISO19139 xml files for the batch"

    def getParameterInfo(self):
        source_batch_directory_path_param = arcpy.Parameter(
            displayName="The source batch directory",
            name="Source Batch Directory",
            datatype="GPString",
            direction="Output"
        )    
        projected_batch_directory_path = arcpy.Parameter(
            displayName="The projected batch directory",
            name="Projected Batch Directory",
            datatype="GPString",
            direction="Output"

        )
        main_csv_arkid_filepath_param = arcpy.Parameter(
            displayName="Main csv file",
            name="From main csv file",
            datatype="GPString",
            direction="Output"
        )    
        resp_csv_arkid_filepath_param = arcpy.Parameter(
            displayName="Responsible csv file",
            name="From responsible csv file",
            datatype="GPString",
            direction="Output"
        )    
        
        return [ source_batch_directory_path_param, projected_batch_directory_path, main_csv_arkid_filepath_param, resp_csv_arkid_filepath_param]

    def updateParameters(self, parameters):
        val0 = val1 = val2 = val3 = constants.no_prcess_path_selected
        if (workspace_directory.source_batch_directory_path is not None):
            val0 = workspace_directory.source_batch_directory_path
            val1 = workspace_directory.projected_batch_directory_path  
            val2 = common_helper.csv_filepath('main', True)
            val3 = common_helper.csv_filepath('resp', True)
        
        common_helper.assign_parameters(parameters, [val0, val1, val2, val3])
        return

    def execute(self, parameters, messages):
        common_helper.call_run_tool('batch_create_iso19139')
        return
  
