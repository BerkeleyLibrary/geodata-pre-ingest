
import arcpy
import common_helper
import workspace_directory
import constants


class AssignArkidTool(object):
    def __init__(self):
        self.label = "3 - Run to assign arkids to main and responsible CSV files"

    def getParameterInfo(self):
        from_main_csv_path_param = arcpy.Parameter(
            displayName="From main csv file",
            name="From main csv file",
            datatype="GPString",
            direction="Output"
        )    
        from_responsible_csv_path_param = arcpy.Parameter(
            displayName="From responsible csv file",
            name="From responsible csv file",
            datatype="GPString",
            direction="Output"
        )    
        to_csv_path_param = arcpy.Parameter(
            displayName="To this directory:(new main csv file and resp csv file with arkid assigned)",
            name="To Directory",
            datatype="GPString",
            direction="Output"

        )
        
        return [ from_main_csv_path_param, from_responsible_csv_path_param, to_csv_path_param]

    def updateParameters(self, parameters):
        val0 = val1 = val2 = constants.no_prcess_path_selected
        if (workspace_directory.source_batch_directory_path is not None):    
            val0 = common_helper.csv_filepath('main')
            val1 = common_helper.csv_filepath('resp')
            val2 = workspace_directory.csv_files_arkid_directory_path   
        common_helper.assign_parameters(parameters, [val0, val1, val2])
        return

    def execute(self, parameters, messages):
        common_helper.call_run_tool('assign_arkid')
        return
