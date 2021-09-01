#!/usr/bin/python
import os
import sys
import shutil
from validate_csv import ValidateCSV
from geo_helper import GeoHelper

def main():
    try:
        process_path = sys.argv[1]
        dest_csv_files_updated = GeoHelper.dest_csv_files_updated(process_path)
        validate_csv = ValidateCSV(process_path)
        validated = validate_csv.updated_csv_files_valid()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)



if __name__ == '__main__':
    main()
