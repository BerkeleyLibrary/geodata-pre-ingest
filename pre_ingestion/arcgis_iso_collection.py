#!/usr/bin/python
import os
import sys
import re
import xml.etree.ElementTree as ET
from shutil import copyfile
from arcgis_iso  import ArcGisIso
from geo_helper import GeoHelper
import par
if os.name == "nt":
    import arcpy


# 1) Workflow allows user to use ArcCatalog to input/add/update metadata. - Descriptive metadata from ArcCatalog are saved in the original ESRIISO metadata.
# 2) Use original original ESRI ISO - ".tif.xml" or ".shp.xml" from work directory,
# 3) If no orignal ESRI ISO existing, create one by copying the slim ESRIISO xml to work directory
# 4) TODO: if needed, add FGDC metadata case

class ArcGisIsoCollection(object):
    def __init__(self,workspace_batch_path,geo_ext):
        self.workspace_batch_path = workspace_batch_path
        self.geo_ext = geo_ext


    def all_arcgisiso(self):
        esriiso_slim = os.path.join(os.path.dirname(__file__),"metadata_template","ESRI_ISO_slim.xml")  # template xml file with minium metadata

        def _esriiso_file(file):
            return "{0}.xml".format(file)

        def _is_geofile(file):
            return GeoHelper.has_extention(file,self.geo_ext)

        ls = []
        for root, dirs, files in os.walk(self.workspace_batch_path):
            for file in files:
                if _is_geofile(file):
                    geofile = os.path.join(root,file)
                    esriiso_file = _esriiso_file(geofile)

                    if not os.path.isfile(esriiso_file):
                        copyfile(esriiso_slim,esriiso_file)

                    esriiso = ArcGisIso(esriiso_file)
                    ls.append(esriiso)

        if len(ls) == 0:
            GeoHelper.arcgis_message("No GeoFiles in {0}".format(self.workspace_batch_path))
        return ls


   # leave this here, if we need consider FGDC transforming in future
    #def _prepare_esriiso_file_old(self,geofile):
    #     esriiso_file = self._esriiso_file(geofile)
    #
    #     def is_file():
    #         return os.path.isfile(esriiso_file)
    #
    #     def is_esriiso():
    #         path = "./Esri"
    #         return self._has_node(esriiso_file,path)
    #     #
    #     # def is_slim_esriiso():
    #     #     path = "./Esri/DataProperties"
    #     #     return not self._has_node(esriiso_file,path)
    #     #
    #     # def need_add_esriiso():
    #     #     return  (not is_file()) or (is_file() and is_esriiso() and is_slim_esriiso())
    #
    #     def need_fgdc_transform(): # if it is not ESRI, it is FGDC, convert it to ESIR ISO
    #         return is_file() and (not is_esriiso())
    #
    #
    #     if not is_file():
    #         self._create_esriiso(geofile,esriiso_file)
    #
    #     if need_fgdc_transform():
    #         self._transform_fgdc_to_esriiso(geofile) # if it is not ESRI, it is FGDC, convert it to ESIR ISO
    #         GeoHelper.arcgis_message(par.NOT_ESRI_ISO.format(esriiso_file))
