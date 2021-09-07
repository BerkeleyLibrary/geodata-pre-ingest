#!/usr/bin/python
import os
import sys
from geo_helper import GeoHelper
import par
if os.name == "nt":
    import arcpy


class CheckProjection(object):
    def __init__(self,path,geo_ext):
        self.path = path
        self.geofiles = GeoHelper.geofiles(path,geo_ext)

    def excute(self):
        missing_projecction_files = self.files_missing_projection()
        if len(missing_projecction_files) == 0:
            GeoHelper.arcgis_message(par.PASS_PROJECTION_VALIDATION)

    def files_missing_projection(self):
        files = []

        gcs = "GCS_WGS_1984"
        txt = "Check projections: \n"

        def checkGeoTIFF(geofile):
            desc = arcpy.Describe(geofile)
            spatialRef = desc.spatialReference
            coordsys_name = spatialRef.Name

            if coordsys_name <> gcs:
                files.append(geofile)
                GeoHelper.arcgis_message(par.INCORRECT_PROJECTION.format(geofile))

        for geofile in self.geofiles:
            checkGeoTIFF(geofile)

        return files
