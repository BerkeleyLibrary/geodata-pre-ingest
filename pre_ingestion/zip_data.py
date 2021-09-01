#!/usr/bin/python
import os
import sys
import re
import zipfile
from shutil import copyfile
from geo_helper import GeoHelper
import par

class ZipData(object):

	def __init__(self,zip_from_batch,zip_to_path,zip_name,geo_ext_list=None):
		self.zip_from_batch = zip_from_batch
		self.zip_to_path = zip_to_path #  destinaiton no need batch name
		self.geo_ext_list = geo_ext_list
		self.zip_name = zip_name


	def _zip_geofile(self,geofile_path,func):
		def ark_path(ark):
			pathName = os.path.join(self.zip_to_path,ark)
			if not os.path.exists(pathName):
				os.makedirs(pathName)
			return pathName

		ark = GeoHelper.ark_from_arkfile(geofile_path)
		if ark:
			os.chdir(geofile_path)
			zipfile_name = os.path.join(ark_path(ark),self.zip_name)

			with zipfile.ZipFile(zipfile_name,'w',zipfile.ZIP_DEFLATED) as zf:
				for root, dirs, files in os.walk(geofile_path):
					for file in files:
						original_file = os.path.join(root,file)
						dest_file = func(file,ark)
						if dest_file:
							zf.write(original_file,dest_file)

		else:
			txt = par.ARK_NOT_ASSIGNED
			GeoHelper.arcgis_message(txt.format(geofile_path))


	def zip_all_geofiles(self,func):
		for root, dirs, files in os.walk(self.zip_from_batch):
			for dir in dirs:
				geofile_path = os.path.join(root,dir)
				self._zip_geofile(geofile_path,func)


	def map_zipfiles(self):
		def fun_dest_mapfile_name(file,ark):
			map_zipfile_name = None
			def file_ext(file):
				ext = os.path.splitext(file)[1].strip().lower()
				if ext == ".ovr":
					ext = ".tif.ovr"
				return ext

			ext = file_ext(file)
			if ext in self.geo_ext_list:
				map_zipfile_name = "{0}{1}".format(ark,ext)
			return map_zipfile_name

		self.zip_all_geofiles(fun_dest_mapfile_name)


	def download_zipfiles(self):
		def fun_dest_datafile_name(file,ark=None):
			data_zipfile_name = None
			if not file.count("_arkark") == 2:
				data_zipfile_name = file
			return data_zipfile_name

		self.zip_all_geofiles(fun_dest_datafile_name)
