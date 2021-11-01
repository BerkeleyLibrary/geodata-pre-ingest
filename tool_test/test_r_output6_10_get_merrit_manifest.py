#!/usr/bin/python
import os
import sys
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import merritt,geo_helper,par,validate_csv
dirname = os.path.dirname(__file__).replace("test","test_data")

def main():
    try:
        process_path = os.path.join(dirname,"raster_data","raster_output")
        valid_updated_csv = validate_csv.ValidateCSV(process_path)

        if valid_updated_csv.geoblacklight_files_existed():
            if valid_updated_csv.data_zip_files_existed():
                final_result_dir =  geo_helper.GeoHelper.final_result_path(process_path)

                merritt_collection = merritt.Merrit(process_path,final_result_dir)
                merritt_collection.save_merritt_to_file()  # save final result directory

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)



if __name__ == '__main__':
    main()
