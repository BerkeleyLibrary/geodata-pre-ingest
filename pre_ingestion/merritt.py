#!/usr/bin/python
import os
import sys
import json
from geo_helper import GeoHelper
import par
import hashlib

class Merrit(object):
    def __init__(self,process_path,final_result_dir):
        self.process_path = process_path
        self.final_result_dir = final_result_dir

    # geoblacklight json files under result to get all arks
    def _content(self):
        content = ""
        geoblacklight_dir =  GeoHelper.geoblacklight_path(self.process_path)

        for root, dirs, files in os.walk(geoblacklight_dir):
            for dir in dirs: # here dir is ark
                if GeoHelper.isNotNullorEmpty(dir):
                    ark_merrit = ArkMerritt(dir,self.process_path)
                    content  += ark_merrit.row()
        return content

    def save_merritt_to_file(self):
        merritt_file = os.path.join(self.final_result_dir,"merritt.txt")
        header =  "fileUrl | hashAlgorithm | hashValue | fileSize | fileName | primaryIdentifier | creator | title | date"  + os.linesep
    	with open(merritt_file, 'wb') as f:
            f.write(header)
            content = self._content()
            f.write(content)


class ArkMerritt(object):
    def __init__(self,ark,process_path):
        self.ark = ark
        self.process_path = process_path
        self.json_data = self._geobacklight_json_data()
        self.download_data_zip_file = self._download_data_zip_file()

    def row(self):
        _row = "{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}".format(
                                self.file_url(),
                                "MD5",
                                self.hashValue(),
                                self.fileSize(),
                                "Data.zip",
                                self.primary_identifer(),
                                self.creator(),
                                self.title(),
                                self.date()
                                ) +  os.linesep

        return _row

    def _download_data_zip_file(self):
        download_path = GeoHelper.data_download_path(self.process_path)
        return os.path.join(download_path,self.ark,"data.zip")

    def _geobacklight_json_data(self):
        geoblacklight_dir =  GeoHelper.geoblacklight_path(self.process_path)
        geoblackligh_file =  os.path.join(geoblacklight_dir,self.ark, "geoblacklight.json")

    	json_data = None
    	with open(geoblackligh_file ,'r') as f:
    		json_data = json.load(f)
    	return json_data

    def file_url(self):
        access_right = self.json_data["dct_accessRights_s"]
        download_host = "https://spatial.lib.berkeley.edu/public" if access_right.lower()  == "public" else "https://spatial.lib.berkeley.edu/UCB"
        return  "{0}/berkeley-{1}/data.zip".format(download_host,self.ark)

    def hashValue(self):
        md5 = ""
        with open(self.download_data_zip_file,'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        return md5

    def fileSize(self):
        size = os.path.getsize(self.download_data_zip_file)
        return str(size)

    def primary_identifer(self):
        return "ark:/28722/{0}".format(self.ark)

    def creator(self):
        str = ""
        ls = self.json_data["dct_creator_sm"]
        if ls:
            str = ",".join(ls)
        return self._rm_pipe(str)

    def title(self):
        _title =  "{0} {1}".format(self.json_data["dct_title_s"],self.primary_identifer())
        return self._rm_pipe(_title)

    def date(self):
        return self.json_data["gbl_mdModified_dt"].strip()[:10]

    def _rm_pipe(self,str):
        return str.replace("|","_")
