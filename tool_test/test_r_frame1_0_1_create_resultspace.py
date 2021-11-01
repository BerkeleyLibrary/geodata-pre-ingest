#!/usr/bin/python
import os
import sys
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import geo_helper, par
dirname = os.path.dirname(__file__).replace("test","test_data")

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
        process_path = os.path.join(dirname,"raster_data","raster_frame")
        _mk_dir(process_path)
        print process_path
        mk_sub_dirs(process_path,par.PROCESS_SUB_DIRECTORY)

        process_result_path = os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[0])
        _mk_dir(process_result_path)
        mk_sub_dirs(process_result_path,par.RESULT_DIRECTORY)

        # Create final result directories
        final_result_path = os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[1])
        _mk_dir(final_result_path)

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)

if __name__ == '__main__':
    main()
