import os
import sys
from geo_helper import GeoHelper
from check_projection import CheckProjection

def main():
    try:
        original_source_path = sys.argv[1]
        geo_ext = '.tif'

        check_projection = CheckProjection(original_source_path,geo_ext)
        check_projection.excute()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)

if __name__ == '__main__':
    main()
