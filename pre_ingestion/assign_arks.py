#!/usr/bin/python
import os
import sys
import par
from shutil import copyfile
from geo_helper import GeoHelper



# 1. Make sure no Ark file existing in both WORK and SOURCE directories before allocating ark ids
# 2. Make sure the number of arkids in arks.txt are the same as the numbers of GeoFiles in both WORK and SOURCE directories
# 3. Susan required: once ark assinged, cannot be assigned again from tool
# 4. To re-assiging arks, a user will remove all ark files located under the subdirectory of GeoFiles in both WORK and SOURCE directories.  ark file ,such as "026/026_arkark_a7r971_arkark.txt"

class AssignArks(object):

    def __init__(self,process_path,txt_file,ext):
        self._arks = self._arks(txt_file)
        self.ext = ext

        self.workpath = GeoHelper.work_path(process_path)
        self.sourcepath = GeoHelper.source_path(process_path)

        self.geofiles_from_workpath = GeoHelper.geofiles(self.workpath,ext)
        self.geofiles_from_sourcepath = GeoHelper.geofiles(self.sourcepath,ext)


    def _arks(self,txtfile):
        def layerid(line): #ark:/28722/s7r971
            return line.split('/')[2].strip()

        ark_list = []
        with open(txtfile,'r') as f:
    		x = f.readlines()
    		ark_list =[layerid(line) for num,line in enumerate(x) if len(line.strip()) > 0]
        return ark_list


    def _need_ark(self):
        need_ark = True
        files_from_both_paths = GeoHelper.files(self.workpath) + GeoHelper.files(self.sourcepath)
        for file in files_from_both_paths:
            if file.strip().endswith("_arkark.txt"):
                need_ark  = False
                GeoHelper.arcgis_message("*** Found an arkid file existed - {0}.".format(file))
                GeoHelper.arcgis_message(par.ARKS_HAVE_BEEN_ASSIGNED)
                break
        return need_ark


    def _assign_arks(self):
        def new_path(work_arkfile):
            if os.name == "nt":
                return os.path.dirname(work_arkfile).replace("\\Work\\","\\Source\\")
            else:
                return os.path.dirname(work_arkfile).replace("/Work/","/Source/")

        def equal_numbers():
            num_arks = len(self._arks)
            num_source_geofiles = len(self.geofiles_from_sourcepath)
            num_work_geofiles = len(self.geofiles_from_workpath)
            if (num_source_geofiles == num_arks) and (num_work_geofiles == num_arks):
                return True
            else:
                GeoHelper.arcgis_message(par.WARNING_ARK_MAPFILE_NUMBER_DIFFERENT.format(num_arks,num_work_geofiles,num_source_geofiles))
                return False

        def save_to_work(filename,ark,geofile):
            ln = "ark:/28722/{0}\t{1}".format(ark,geofile)
            with open(filename,'w') as f:
                f.write(ln)

        def copy_to_source(work_arkfile):
            arkfile_basename = os.path.basename(work_arkfile)
            source_dir = new_path(work_arkfile)
            source_arkfile = os.path.join(source_dir,arkfile_basename)
            copyfile(work_arkfile,source_arkfile)

        def assign():
            if equal_numbers():
                i = 0
                for ark in self._arks:
                    work_geofile = self.geofiles_from_workpath[i]
                    work_arkfile = GeoHelper.arkfilename(work_geofile,self.ext,ark)
                    save_to_work(work_arkfile,ark,work_geofile) # save work directory geofile info in the ark file
                    copy_to_source(work_arkfile)
                    i += 1
                if i > 0: GeoHelper.arcgis_message(par.SUCCESSFUL_ASSINGED_ARKS.format(str(i)))

        assign()


    def excute(self):
        if self._need_ark():
            self._assign_arks()
