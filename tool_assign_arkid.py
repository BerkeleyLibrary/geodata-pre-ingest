
import arcpy
# from lib import common_helper
# from lib import workspace_directory
# from lib import assign_arkid
# from lib import constants
import common_helper
import workspace_directory
import assign_arkid
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
        val0 = constants.no_prcess_path_selected
        val1 = val0
        val2 = val0
        if (workspace_directory.source_batch_directory_path is not None):
            csv_files_directory_path = workspace_directory.csv_files_directory_path
            val0 = fr"{csv_files_directory_path}\main.csv"
            val1 = fr"{csv_files_directory_path}\resp.csv"     
            val2 = workspace_directory.csv_files_arkid_directory_path   
        parameters[0].value = val0
        parameters[1].value = val1
        parameters[2].value = val2
        return

    def execute(self, parameters, messages):
        common_helper.call_run('assign_arkid')
        return
