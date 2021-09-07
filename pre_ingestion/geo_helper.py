#!/usr/bin/env python
import os
import sys
import re
import json
import shutil
import datetime
import xml.dom.minidom
import csv
import par
if os.name == "nt":
    import arcpy

class GeoHelper:

    # def __init__(self):
    #     pass

    @staticmethod
    def json_data(file):
        json_data = None
        with open(file,'r') as f:
            json_data = json.load(f)
        return json_data

    @staticmethod
    def arcgis_message(txt):
        os_name = os.name
        if os_name == "posix":
            print txt
        if os_name == "nt":
            arcpy.AddMessage(txt)

    @staticmethod
    def path_split(path):
        ls = path.split("/")
        if os.name == "nt":
            ls = path.split("\\")
        return ls

    @staticmethod
    def path_join(ls):
        new_path = "/".join(ls)
        if os.name == "nt":
            new_path = "\\".join(ls)
        return new_path

    @staticmethod
    def geo_path_from_CSV_geofile(geofile):
        geofile_basepath = os.path.split(geofile)[0]
        ls = GeoHelper.path_split(geofile_basepath)[:-1] # remove the directory name of a geofile "/vector_data/vector_export/Work/1950prj_county" => ""/vector_data/vector_export/Work"
        new_path = GeoHelper.path_join(ls)
        return new_path

    #######################################################################

    @staticmethod
    def batchname(path):   # eg. c://original/Angola_restricted
        return GeoHelper.path_split(path)[-1]
        # return path.split("\\")[-1]  # Windows

    @staticmethod
    def filename_no_extention(file):
        return os.path.basename(file)

    @staticmethod
    def arkfilename(mapfile,ext,arkid):
        digit = len(ext)
        basename = mapfile.strip()[:-digit]
        return "{0}_{1}_{2}_{3}.txt".format(basename,"arkark",arkid,"arkark")

    @staticmethod
    def line(file):
        pattern = "arkark_(.*?)_arkark"
        patterns = re.search(pattern, file)

        if patterns:
            return patterns.group(1)
        return patterns

    @staticmethod
    def arkfile(dest_path):
        afile = None
        for root, dirs, files in os.walk(dest_path):
            for file in files:
                if file.endswith("arkark.txt"):
                    afile = os.path.join(root,file)
        return afile

    @staticmethod
    def ark_from_arkfile(dest_path):
        ark = None
        arkfile = GeoHelper.arkfile(dest_path)
        if arkfile:
            ark = GeoHelper.line(arkfile)
        return ark

    @staticmethod
    def _dest_batch_path(dest_path,original_batch_path):
        batchname = GeoHelper.batchname(original_batch_path)
        return os.path.join(dest_path,batchname)

    @staticmethod
    def mkdir(path,sub_path):
        pathName = os.path.join(path,sub_path)
        if not os.path.exists(pathName):
            os.makedirs(pathName)

    @staticmethod
    def not_ark_file(filename): # add arkid to the arkid txt file
        return False if filename.strip().endswith(".txt") else True

    @staticmethod
    def geofiles(pathname,ext):
        geofiles = [os.path.join(dirpath,filename) for dirpath, dirs, filenames in os.walk(pathname) for filename in filenames if filename.endswith(ext)]
        return geofiles

    @staticmethod
    def files(pathname):
        files = [os.path.join(dirpath,filename) for dirpath, dirs, filenames in os.walk(pathname) for filename in filenames]
        return files

    @staticmethod
    def clr_html_tags(txt):
        tags = re.compile('<.*?>')
        return re.sub(tags, '', txt)

    @staticmethod
    def has_extention(file,ext):
        return file.endswith(ext)

    @staticmethod
    def files_with_extention(srcdir,ext):
        ls = []
        for root, dirs,files in os.walk(srcdir):
            for file in files:
                if GeoHelper.has_extention(file,ext):
                    ls.append(file)
        return ls

    @staticmethod
    def _space(ls,num):
        for n in range(num):
            ls.append("")

    @staticmethod
    def rm_file(fname):
        if os.path.isfile(fname):
            os.remove(fname)

    @staticmethod
    def empty_subpath(subpath):
        if(subpath == '/' or subpath == "\\"): return
        else:
            for root, dirs, files in os.walk(subpath,topdown=False):
                for name in files:
                    if not name == ".keep":
                        # print "file - " + os.path.join(root, name)
                        os.remove(os.path.join(root, name))
                for name in dirs:
                    # print "dir +" + os.path.join(root, name)
                    os.rmdir(os.path.join(root, name))

    @staticmethod
    def esriiso_file(geofile):
        return "{0}.xml".format(geofile)

    @staticmethod
    def _print_files_txt(ls,pre_txt):
        if len(ls) > 0:
            txt = pre_txt + "\n"
            i = 1
            for l in ls:
                txt += "{0}) {1}; \n".format(str(i),l)
                i += 1
            GeoHelper.arcgis_message(txt)

    @staticmethod
    def isNotNullorEmpty(s):
        return (s and s.strip())

    @staticmethod
    def clr_file(file):
	if os.path.isfile(file):
		f = open(file, 'w')
		f.close()

    @staticmethod
    def datetime(str):
        return datetime.datetime.strptime(str,"%Y%m%d").strftime("%Y-%m-%d")
        # return datetime.datetime.strptime(str,"%m%d%Y").strftime("%m-%d-%Y")

    @staticmethod
    def beautify_file(f_file,t_file):
        file = open(f_file, 'r')
        xml_string = file.read()
        file.close()

        parsed_xml = xml.dom.minidom.parseString(xml_string)
        # print xml_string
        pretty_xml_as_string = parsed_xml.toprettyxml().encode('utf-8')

        file = open(t_file, 'w')
        file.write(pretty_xml_as_string)
        file.close()
        os.remove(f_file)

    @staticmethod
    def responsibleParty_csv_update_header():
        header = []
        header.extend(par.CSV_HEADER_RESPONSIBLE_PARTY[:2])
        header.extend(par.CSV_HEADER_COMMON)
        header.extend(par.CSV_HEADER_RESPONSIBLE_PARTY[2:])
        return header

    @staticmethod
    def responsibleParty_csv_original_header():
        header = []
        header.extend(par.CSV_HEADER_RESPONSIBLE_PARTY[:1])
        header.extend(par.CSV_HEADER_COMMON)
        header.extend(par.CSV_HEADER_RESPONSIBLE_PARTY[2:])
        return header

    @staticmethod
    def main_csv_header():

        def double_header(ls):
            out_ls = []
            for l in ls:
                out_ls.append("{0}_o".format(l))
                out_ls.append(l)
            return out_ls

        header = []
        header.extend(par.CSV_HEADER_COMMON)
        transformed_metadata_header = double_header(par.CSV_HEADER_TRANSFORM)
        header.extend(transformed_metadata_header)
        header.extend(par.CSV_HEADER_EMPTY)
        return header

    @staticmethod
    def dest_csv_files(process_path):
        batchname = GeoHelper.batchname(process_path)
        filename = "{0}_ORIGINAL.csv".format(batchname)
        fourth_filename = "{0}_UPDATE.csv".format(batchname)

        second_filename = "{0}_responsible_parties_UPDATE.csv".format(batchname)
        third_filename = "{0}_responsible_parties_ORIGINAL.csv".format(batchname)

        dest_path = GeoHelper.csv_path(process_path)
        return [os.path.join(dest_path,filename),os.path.join(dest_path,second_filename),os.path.join(dest_path,third_filename),os.path.join(dest_path,fourth_filename)]

    @staticmethod
    def dest_csv_files_updated(process_path):
        files = []

        def add_file(name):
            dest_path = GeoHelper.csv_path_updated(process_path)
            file = os.path.join(dest_path,name)
            # if os.path.isfile(file):
            files.append(file)

        batchname = GeoHelper.batchname(process_path)
        main_filename = "{0}_UPDATE.csv".format(batchname)
        resp_filename = "{0}_responsible_parties_UPDATE.csv".format(batchname)
        add_file(main_filename)
        add_file(resp_filename)

        return files


    @staticmethod
    def final_result_path(process_path):
        return os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[1])

    @staticmethod
    def processing_result_path(process_path):
        return os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[0])

    @staticmethod
    def source_path(process_path):
        return os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[1])

    @staticmethod
    def work_path(process_path):
        return os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[2])

    @staticmethod
    def data_download_path(process_path):
        return os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[0],par.RESULT_DIRECTORY[0])

    @staticmethod
    def map_download_path(process_path):
        return os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[0],par.RESULT_DIRECTORY[1])

    @staticmethod
    def geoblacklight_path(process_path):
        return os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[0],par.RESULT_DIRECTORY[2])

    @staticmethod
    def csv_path(process_path):
        return os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[0],par.RESULT_DIRECTORY[3])

    @staticmethod
    def csv_path_updated(process_path):
        return os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[0],par.RESULT_DIRECTORY[5])

    @staticmethod
    def iso19139_path(process_path):
        return os.path.join(process_path,par.PROCESS_SUB_DIRECTORY[0],par.RESULT_DIRECTORY_PARENTS[0],par.RESULT_DIRECTORY[4])

    @staticmethod
    def csv_file(process_path):
        batchname = GeoHelper.batchname(process_path)
        file_name =  "{0}.csv".format(batchname)
        return os.path.join(GeoHelper.csv_path(process_path),file_name)

    @staticmethod
    def has_files(path):
        return len(os.listdir(path)) > 0

    @staticmethod
    def metadata_from_csv(header,raw): # string
        val = raw[header].strip()

        def has_original_column(header):
            return (header in par.CSV_HEADER_TRANSFORM)

        def val_from_original(header):
            val = ""
            if has_original_column(header): # some elements in csv files have no original elements
                header_o = "{0}_o".format(header)
                val = raw[header_o].strip()
            return val

        if len(val) == 0:
            val = val_from_original(header)

        return val

    @staticmethod
    def update_main_csv_file(export_work,temp_file,main_file): # unittest method
        GeoHelper.rm_file(main_file)

        raws = []
        header = []
        with open(temp_file, 'r') as tempfile:
            csv_reader = csv.DictReader(tempfile)
            raws = [raw for raw in csv_reader]
            header = csv_reader.fieldnames

        with open(main_file, 'wb') as main_file:
            csv_writer = csv.writer(main_file)
            csv_writer.writerow(header)
            for raw in raws:
                raw["filename"] = os.path.join(export_work,raw["filename"])
                vals = [raw[h] for h in header]
                csv_writer.writerow(vals)
