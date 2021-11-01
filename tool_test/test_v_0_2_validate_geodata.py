import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import validate_geodata,geo_helper
dirname = os.path.dirname(__file__).replace("test","test_data")


def main():
    try:
        original_source_path = os.path.join(dirname,"vector_data","vector_original_source")
        # exts = [".tif",".aux",".tfw"]
        # exts = [".tif",".aux",".tfw",".tif.xml",".tif.ovr"]
        exts = [".cpg",
                ".dbf",
                ".prj",
                ".dbf",
                ".sbn",
                ".sbx",
                ".shp",
                ".shp.xml",
                ".shx"]
        geo_ext = ".shp"
        v_geodata = validate_geodata.ValidateGeodata(original_source_path,exts,geo_ext)
        v_geodata.validate()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)




if __name__ == '__main__':
    main()
