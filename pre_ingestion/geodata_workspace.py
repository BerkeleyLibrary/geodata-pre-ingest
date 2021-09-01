#!/usr/bin/python
import os
import sys
from shutil import copyfile, copytree, rmtree
from geo_helper import GeoHelper
import par
if os.name == "nt":
    import arcpy


class GeodataWorkspace(object):
    def __init__(self,original_source_path,process_path,geo_ext):
        self.original_batch_path = original_source_path
        self.process_path = process_path

        self.all_files_in_original_batch_path = GeoHelper.files(self.original_batch_path)
        self.unqualified_files = [ f  for f in self.all_files_in_original_batch_path]
        self.geofiles = GeoHelper.geofiles(self.original_batch_path,geo_ext)

        self.geo_ext = geo_ext


    # all files of a geofile has the same basename: eg. 20.tif, 20.aux,20.tif.xml etc.
    def files_in_geofile(self,geofile):
        ls = []
        geofile_base = os.path.splitext(geofile)[0] # "test_raster/raster_source/Angola_restricted/020.tif" => "test_raster/raster_source/Angola_restricted/020"

        def file_base(file): # some file may have multip ".", such as "20.tif.xml", so cannot use os.path.splitext
            ls = file.split(".")
            return ls[0]

        def add_file(f):
            base = file_base(f)
            if base == geofile_base:
                ls.append(f)

        for f in self.all_files_in_original_batch_path:  # add file the same basename a geofile, such as "test_raster/raster_source/Angola_restricted/020"
            add_file(f)

        return ls


    def move_batch(self):
        process_path = self.process_path
        workspace_batch_path = GeoHelper.work_path(process_path)
        source_batch_path = GeoHelper.source_path(process_path)

        def vector_projection(geofile,prj_geofile):
            try:
                #GeoHelper.rm_file(prj_geofile)
                wkt =  'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
                sr = arcpy.SpatialReference()
                sr.loadFromString(wkt)
                arcpy.Project_management(geofile,prj_geofile,sr)
                GeoHelper.arcgis_message(par.PROJECT_SUCCEEDED.format(geofile))
            except:
                GeoHelper.arcgis_message(par.PROJECT_FAILED.format(geofile))

        def empty_subpath(subpath):
            if(subpath == '/' or subpath == "\\"): return
            else:
                for root, dirs, files in os.walk(subpath,topdown=False):
                    for name in files:
                        # print "file - " + os.path.join(root, name)
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        # print "dir +" + os.path.join(root, name)
                        os.rmdir(os.path.join(root, name))

        # get geofile basename for creating a folder to move related files of a geofile to this folder:  eg. 20.tif => 20
        def sub_path(geofile,batch_path):
            geofile_basename = os.path.basename(geofile)
            geofile_batch_name = os.path.splitext(geofile_basename)[0]
            return os.path.join(batch_path,geofile_batch_name)

        def make_dest_subpaths(batch_path):
            for geofile in self.geofiles:
                subpath = sub_path(geofile,batch_path)
                if os.path.exists(subpath):
                    empty_subpath(subpath)  # os.rmtree will lock the folder, cannot do projection, change to use empty_subpath: remove all files under work or source directories
                else:
                    os.makedirs(subpath)

        def copy_geofile_to_work(geofile):
            geofile_path = sub_path(geofile,workspace_batch_path)
            for f in self.files_in_geofile(geofile):
                f_basename = os.path.basename(f)
                dest_file_name = os.path.join(geofile_path,f_basename)
                copyfile(f,dest_file_name)

        # for vector data
        def proj_geofile_to_work(geofile):
            dest_geofile_path = sub_path(geofile,workspace_batch_path)
            f_basename = os.path.basename(geofile)
            dest_file_name = os.path.join(dest_geofile_path,f_basename)
            vector_projection(geofile,dest_file_name)

        def copy_geofile_to_source(geofile):
            geofile_path = sub_path(geofile,source_batch_path)
            for f in self.files_in_geofile(geofile):
                f_basename = os.path.basename(f)
                dest_file_name = os.path.join(geofile_path,f_basename)
                copyfile(f,dest_file_name)
                self.unqualified_files.remove(f)

        def ensure_dest_subpaths():
            make_dest_subpaths(workspace_batch_path)
            make_dest_subpaths(source_batch_path)

        def copy_to_dest_subpaths():
            for geofile in self.geofiles:
                copy_geofile_to_work(geofile)
                copy_geofile_to_source(geofile)

        def copy_and_proj_dest_subpaths():
            for geofile in self.geofiles:
                proj_geofile_to_work(geofile)
                copy_geofile_to_source(geofile)

        def move_files():
            ensure_dest_subpaths()
            if os.name == "nt" and self.geo_ext.lower() == ".shp":
                copy_and_proj_dest_subpaths()
            else:
                copy_to_dest_subpaths()

            if os.name == "nt":
                arcpy.RefreshCatalog(workspace_batch_path)
                arcpy.RefreshCatalog(source_batch_path)

        move_files()

    def excute(self):
        self.move_batch()
        GeoHelper._print_files_txt(self.unqualified_files,par.FILES_NOT_MOVED)
