#!/usr/bin/python
import os
import sys
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import zip_data,geo_helper,par,validate_csv
dirname = os.path.dirname(__file__).replace("test","test_data")

def main():
    try:
        geo_ext_list = [".tif",".aux",".tfw",'.prj']
        process_path = os.path.join(dirname,"raster_data","raster_output")
        valid_updated_csv = validate_csv.ValidateCSV(process_path)

        if valid_updated_csv.work_files_existed():
            workspace_batch_path = geo_helper.GeoHelper.work_path(process_path)
            projected_map_path = geo_helper.GeoHelper.map_download_path(process_path)

            z_data = zip_data.ZipData(workspace_batch_path,projected_map_path,"map.zip",geo_ext_list)
            z_data.map_zipfiles()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)


if __name__ == '__main__':
    main()
