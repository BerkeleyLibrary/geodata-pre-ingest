#!/usr/bin/python
import os
import xml.etree.ElementTree as ET
import csv
import re
import traceback
import par
import datetime
from geo_helper import GeoHelper
if os.name == "nt":
	import arcpy


# 1  Metadata element value is in string format
# 2. Most metadata values are extracted from ESRI ISO file - shp.xml, or tif.xml
# 3. A single geofile matadata - Read metadata from ESRI ISO file, save to an object
# 4. Object attribute names are derived from keys(csv headers) in par.transform_elements
# 5. arkid from assigned ark to geofile
# 6. One ESRI ISO file may have multiple Responsible Parties. They are from two different sources: 1) ./dataIdInfo/idCitation/citRespParty; 2) ./dataIdInfo/idPoC

class ArcGisIso(object):
	def __init__(self,arcgis_isofile):
		self.arcgis_isofile = arcgis_isofile
		self.root = self._root()
		self.ark = self._ark()
		self.filename = self._geofile_name()
		self.main_csv_metadata = self._main_csv_metadata()
		self.all_responsible_parties = self._responsible_party_csv_metadata()

	def _root(self):
		tree = ET.parse(self.arcgis_isofile)
		return tree.getroot()


	def _fun_txt(self):
		return lambda element: element.text.strip()


	def _fun_val(self):
		return lambda element: element.get('value').strip()


	### Values for csv file###
	def _ark(self):
		esriiso_dir = os.path.dirname(self.arcgis_isofile)  # work directory
		_ark = GeoHelper.ark_from_arkfile(esriiso_dir)
		return _ark


	# '/geodata_pre_ingest/test_raster/raster_workspace/Angola_restricted/024/024.tif.xml
	# =>  /geodata_pre_ingest/test_raster/raster_workspace/Angola_restricted/024/024.tif
	def _geofile_name(self):
		return self.arcgis_isofile.strip()[:-4]


	#### main csv data ######
	def _collection_title(self):
		# tag_info is consistent with tag_info from par.transform_elements
		first_tag_info = {"path": "dataIdInfo/idCitation/collTitle"}
		second_tag_info = {"path": "dataIdInfo/aggrInfo/aggrDSName/resTitle"}
		second_code_tag_info = {"path": "dataIdInfo/aggrInfo/assocType/AscTypeCd",
								"attribute": True}

		def collection_title_first():
			return self._element_value(first_tag_info,self.root)

		def collection_title_second():
			val = ""
			code_val = self._element_value(second_code_tag_info,self.root)
			if code_val == "002": val =  self._element_value(second_tag_info,self.root)
			return val

		txt  = collection_title_first()
		if  len(txt) == 0: txt = collection_title_second()
		return txt


	def _temporalCoverage(self):
		txt = ""
		# sequence of these paths must be kept
		tag_infos = [
					{"path": "dataIdInfo/tempKeys/keyword"},
					{"path": "dataIdInfo/dataExt/tempEle/TempExtent/exTemp/TM_Period"},
					{"path": "dataIdInfo/dataExt/tempEle/TempExtent/exTemp/TM_Instant"}
				]
		for tag_info in tag_infos:
			txt = self._element_value(tag_info,self.root)
			if len(txt) > 0: return txt
		return txt

	def _modified_date_dt(self):
		return  datetime.datetime.today().strftime('%Y%m%d')


	def _element_value(self,tag_info,parent_node):

		def has_attribute(name):
			return tag_info.has_key(name) and tag_info[name]

		def is_node_leaf(node):
			return len(list(node)) == 0

		def node_value(node):
			clr_html = has_attribute("html")
			from_attribute = has_attribute("attribute")
			fun = self._fun_val() if from_attribute else self._fun_txt()

			txt = ""
			if node is not None and is_node_leaf(node):
				txt = fun(node)
				if clr_html:
					txt = GeoHelper.clr_html_tags(txt)
			return txt.strip()

		def val():
			content_str = ""
			path = tag_info["path"]
			nodes = parent_node.findall(path)
			if len(nodes) > 0:
				for node in nodes:
					txt = node_value(node)
					if len(txt) > 0:
						content_str += "{0}$".format(txt.encode("utf-8"))

			clr_content = content_str.rstrip("$").strip()
			return clr_content.strip().decode('utf-8')

		return val()


	def _main_csv_metadata(self):

		geom = {"polyline":"Line data",
				"polygon" : "Polygon data",
				"point": "Point data"
				}

		def get_geom_type():
			desc = arcpy.Describe(self.filename)
			geoType = desc.shapeType.lower()
			return geom[geoType]

		obj = MetadataContainer() #xml element defined in dictionary
		for header,tag_info in par.transform_elements.iteritems():
			element_value = self._element_value(tag_info,self.root)
			obj.__dict__["_{0}_o".format(header)] = element_value

		# Update these special elements with new values
		obj.__dict__["_{0}_o".format("collectionTitle")] = self._collection_title()
		obj.__dict__["_{0}_o".format("temporalCoverage")] = self._temporalCoverage()
		obj.__dict__["_{0}_o".format("modified_date_dt")] = self._modified_date_dt()
		if os.name == "nt":
			obj.__dict__["_{0}_o".format("resourceType")] = get_geom_type()
		return obj


	#### responsible party csv data ######
	# To ensure a geofile has at least one "006" and one "010" roles in repsponsible parties
	def _add_default_publisher_originator(self,objs_cititation_idPoC):
		resp_objs = []

		def has_no_role(role_code):
			for resp in objs_cititation_idPoC:
				if resp.__dict__["_role"] == role_code:
					return False
			return 	True

		def default_responsible_party_to_obj(role_code):
			obj = MetadataContainer()
			dic = par.responsibleparty_elements
			for header,v in dic.iteritems():
				obj.__dict__["_{0}".format(header)] = ""
			obj.__dict__["_individual"] = ""
			obj.__dict__["_from"] = "--"
			obj.__dict__["_role"] = role_code
			return obj

		def add_publisher_originator(role_code):
			if has_no_role(role_code):
				obj = default_responsible_party_to_obj(role_code)
				resp_objs.append(obj)

		add_publisher_originator("006")
		add_publisher_originator("010")

		return resp_objs


	def _responsible_parties_objs(self,path):
		def responsible_party_obj(node):
			obj = None
			role = node.find('./role/RoleCd').get('value')
			if role:
				obj = MetadataContainer()
				for header,tag_info in par.responsibleparty_elements.iteritems():
					element_value = self._element_value(tag_info,node)
					obj.__dict__["_{0}".format(header)] = element_value
				obj.__dict__["_role"] = role.strip()
				obj.__dict__["_from"] = path
				obj.__dict__["_individual"] = ""
			return obj

		def responsible_party_objs():
			resp_objs = []
			nodes = self.root.findall(path)
			if nodes:
				for node in nodes:
					resp_obj = responsible_party_obj(node)
					if resp_obj: resp_objs.append(resp_obj)
			return resp_objs

		return responsible_party_objs()


	def _responsible_party_csv_metadata(self):
		objs = []
		objs_cititation  = self._responsible_parties_objs('./dataIdInfo/idCitation/citRespParty')
		objs.extend(objs_cititation)

		objs_idPoC =  self._responsible_parties_objs('./dataIdInfo/idPoC')
		objs.extend(objs_idPoC)

		objs_default = self._add_default_publisher_originator(objs) # if existed "006", "010" from both sources
		objs.extend(objs_default)

		return objs


class MetadataContainer(object):
    def __init__(self):
        pass
