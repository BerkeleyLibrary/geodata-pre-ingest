#!/usr/bin/python
import os
import shutil
import par
from geo_helper import GeoHelper
from  geodata_workspace  import GeodataWorkspace
if os.name == "nt":
    import arcpy

def mk_sub_dirs(path,subs):
    for sub in subs:
        sub_path = os.path.join(path,sub)
        if not os.path.exists(sub_path):
            os.makedirs(sub_path)
def _mk_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    try:

        process_path = sys.argv[1]
        mk_sub_dirs(process_path,par.PROCESS_SUB_DIRECTORY)

        process_result_path = os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[0])
        _mk_dir(process_result_path)
        mk_sub_dirs(process_result_path,par.RESULT_DIRECTORY)

        # Create final result directories
        final_result_path = os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[1])
        _mk_dir(final_result_path)
        #  refresh folder
        if os.name == "nt":
            arcpy.RefreshCatalog(process_result_path)
    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)

if __name__ == '__main__':
    main()
