#!/usr/bin/python
import os
import sys
import shutil


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import geo_helper,par,validate_csv
dirname = os.path.dirname(__file__).replace("test","test_data")


# test: validate csv file:  has this in output:  3) s7mh53 - 'resourceType': incorrect value -- 'app tool' ;

def main():
    try:
        process_path = os.path.join(dirname,"vector_data","vector_export")
        # dest_csv_files_updated = geo_helper.GeoHelper.dest_csv_files_updated(process_path)

        v_csv = validate_csv.ValidateCSV(process_path)
        validated = v_csv.updated_csv_files_valid()
        # v_csv.ardvark_validation()


    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)

if __name__ == '__main__':
    main()
