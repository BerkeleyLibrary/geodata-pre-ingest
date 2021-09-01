#!/usr/bin/python
import os
import sys
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import zip_data,geo_helper,par,validate_csv
dirname = os.path.dirname(__file__).replace("test","test_data")

# package map files from source data
def main():
    try:
        process_path = os.path.join(dirname,"raster_data","raster_export")
        valid_updated_csv = validate_csv.ValidateCSV(process_path)

        if valid_updated_csv.source_files_existed():
            sourcedata_batch_path = geo_helper.GeoHelper.source_path(process_path)
            data_download_path = geo_helper.GeoHelper.data_download_path(process_path)

            z_data = zip_data.ZipData(sourcedata_batch_path,data_download_path,"data.zip")
            z_data.download_zipfiles()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)


if __name__ == '__main__':
    main()
