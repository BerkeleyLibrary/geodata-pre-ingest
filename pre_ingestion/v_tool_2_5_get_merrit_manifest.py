#!/usr/bin/python
import os
import sys
import shutil
from merritt import Merrit
from geo_helper import GeoHelper
from validate_csv import ValidateCSV

def main():
    try:

        process_path = sys.argv[1]
        valid_updated_csv = ValidateCSV(process_path)

        if valid_updated_csv.geoblacklight_files_existed():
            if valid_updated_csv.data_zip_files_existed():
                final_result_path =  GeoHelper.final_result_path(process_path)

                merritt_collection = Merrit(process_path,final_result_path)
                merritt_collection.save_merritt_to_file()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)



if __name__ == '__main__':
    main()
