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

        if valid_updated_csv.work_files_existed():
            work_batch_path = GeoHelper.work_path(process_path)
            output_mapdata_path = GeoHelper.map_download_path(process_path)

            geo_ext_list = [".tif",".aux",".tfw",".prj",".tif.ovr"]

            zip_data = ZipData(work_batch_path,output_mapdata_path,"map.zip",geo_ext_list)
            zip_data.map_zipfiles()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)


if __name__ == '__main__':
    main()
