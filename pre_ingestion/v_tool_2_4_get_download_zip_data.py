#!/usr/bin/python
import os
import shutil
from geo_helper import GeoHelper
from zip_data import ZipData
from validate_csv import ValidateCSV

def main():
    try:

        process_path = sys.argv[1]
        valid_updated_csv = ValidateCSV(process_path)

        if valid_updated_csv.source_files_existed():
            sourcedata_batch_path = GeoHelper.source_path(process_path)
            output_download_path = GeoHelper.data_download_path(process_path)

            zip_data = ZipData(sourcedata_batch_path,output_download_path,"data.zip")
            zip_data.download_zipfiles()  # all files except ark file, such as "020_arkark_s7c11k_arkark.txt"

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)


if __name__ == '__main__':
    main()
