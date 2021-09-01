#!/usr/bin/python
import os
import sys
from geo_helper import GeoHelper
import par
if os.name == "nt":
    import arcpy


class ValidateGeodata(object):
    def __init__(self,path,exts,geo_ext):
        self.path = path
        self.geo_ext = geo_ext
        self.exts = exts
        self.files_from_path = GeoHelper.files(self.path)
        self.geofiles_from_path = GeoHelper.geofiles(self.path,self.geo_ext)

    def _missing_files_with_ext(self,ext):
        ls = []
        for geofile in self.geofiles_from_path:
            expected_file = self._new_file(geofile,ext)
            if not expected_file in self.files_from_path:
                ls.append(expected_file)
        return ls

    def validate(self):
        try:
            missing_files = []
            abnormal_files = [f for f in self.files_from_path if not self._is_arkfile(f)]

            def find_missing_files(geofile):
                for ext in self.exts:
                    missing_files_with_ext = self._missing_files_with_ext(ext)
                    if len(missing_files_with_ext) > 0 : missing_files.extend(missing_files_with_ext)


            def find_abnormal_files(geofile):
                geofile_without_ext = os.path.splitext(geofile)[0]
                for f in self.files_from_path:
                    file_without_ext = os.path.splitext(f)[0]
                    if (geofile_without_ext == file_without_ext) or (file_without_ext == geofile) : # tif.xml; tif.ovr
                        abnormal_files.remove(f) # remote the file which belong to GeoTIFF or shapefile

            # start from geofile
            for geofile in self.geofiles_from_path:
                find_missing_files(geofile)
                find_abnormal_files(geofile)

            self._print_files_txt(missing_files,par.MISSING_FILES)
            self._print_files_txt(abnormal_files,par.ABNORMAL_FILES)

            if self.geo_ext == '.tif':
                files_need_pyrimid = self._missing_files_with_ext(".tif.ovr")
                self._print_files_txt(files_need_pyrimid,par.PYRIMID_NEEDED)

            return True
        except Exception, e:
            return False

    def add_pyrimids(self):

        files_need_pyrimid = self._missing_files_with_ext(".tif.ovr")
        geo_files = []
        for pyrimid_file in files_need_pyrimid:
            geofile = os.path.splitext(pyrimid_file)[0]  # pyrimid_file = "c;/a/b.tif.ovr"
            geo_files.append(geofile)
            if os.name == "nt":
                pylevel = "7"
                skipfirst = "NONE"
                resample = "NEAREST"
                compress = "Default"
                quality = "70"
                skipexist = "SKIP_EXISTING"
                arcpy.BuildPyramids_management(geofile, pylevel, skipfirst, resample, compress, quality, skipexist)
        self._print_files_txt(geo_files,par.PYRIMID_ADDED)




    def _is_arkfile(self,file):
        return file.strip().endswith("_arkark.txt")

    def _new_file(self,geofile,ext):
        geofile_without_ext = os.path.splitext(geofile.strip())[0] # remove ".tif" or ".shp"
        return "{0}{1}".format(geofile_without_ext,ext)

    def _print_files_txt(self,ls,pre_txt):
        if len(ls) > 0:
            txt = pre_txt + "\n"
            i = 1
            for l in ls:
                txt += "{0}) {1}; \n".format(str(i),l)
                i += 1
            GeoHelper.arcgis_message(txt)
