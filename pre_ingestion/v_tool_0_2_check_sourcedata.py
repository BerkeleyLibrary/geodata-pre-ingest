import os
import sys
from geo_helper import GeoHelper
from validate_geodata import ValidateGeodata
import par

def main():
    try:
        original_source_path = sys.argv[1]
        # original_source_path = GeoHelper.original_source_path(process_path)

        if GeoHelper.has_files(original_source_path) > 0:

            # exts = [".tif",".aux",".tfw",".tif.xml",".tif.ovr"]
            exts = [".cpg",
            		".dbf",
            		".prj",
                    ".dbf"
            		".sbn",
            		".sbx",
            		".shp",
            		".shp.xml",
            		".shx"]
            # exts = [".tif",".aux",".tfw"]
            geo_ext = '.shp'

            validate_geodata = ValidateGeodata(original_source_path,exts,geo_ext)
            validate_geodata.validate()
        else:
            GeoHelper.arcgis_message("***Attention***: No source data in directory {0}".format(original_source_path))

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)


if __name__ == '__main__':
    main()
