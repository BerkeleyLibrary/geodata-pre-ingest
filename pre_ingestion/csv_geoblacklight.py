#!/usr/bin/python
import os
import xml.etree.ElementTree as ET
import csv
import par
import json
from datetime import datetime
from geo_helper import GeoHelper
if os.name == "nt":
    import arcpy


# Geoblacklight metadata from:
# 1) CSV
# 2) Default values
# 3) Drived from arkid
# 4) Extracted from iso19139
# 5) From obj - gotten from reponsible party csv file
# 6) Todo: add multiple resource download after geoblacklight v4

class CsvGeoblacklight(object):
    def __init__(self,raw_obj,process_path):
        self.raw_obj = raw_obj
        self.main_csv_raw = raw_obj.__dict__["_main_csv_raw"]

        self.arkid = self.main_csv_raw["arkid"].strip()
        self.geofile = self.main_csv_raw["filename"].strip()
        self.process_path = process_path


    def create_geoblacklight_file(self):
        def geoblacklight_file():
            geoblacklight_dir = GeoHelper.geoblacklight_path(self.process_path)
            path = os.path.join(geoblacklight_dir,self.arkid)
            if not os.path.exists(path):
                os.makedirs(path)
            return os.path.join(path,"geoblacklight.json")

        def save_pretty():
            json_data = {}
            self._add_from_csv(json_data)
            self._add_from_raw_obj(json_data)
            self._add_from_default(json_data)
            self._add_from_arkid(json_data)
            if os.name == "nt":
                self._add_from_iso19139(json_data)

            with (open(geoblacklight_file,"w+")) as geo_json:
                geo_json.write(json.dumps(json_data,sort_keys=True,indent=4,separators=(',',':'))) #pretty print

        geoblacklight_file = geoblacklight_file()
        save_pretty()


    def _add_from_raw_obj(self,json_data): # from updated reponsible party csv, previous workflow is from ISO19139
        originators = self.raw_obj.__dict__["_originators"]
        publishers = self.raw_obj.__dict__["_publishers"]
        owners = self.raw_obj.__dict__["_owners"]

        if originators: json_data['dct_creator_sm'] = originators  # originator, publisher cannot be empty
        if publishers: json_data['dct_publisher_sm'] = publishers
        if owners :json_data['dct_rightsHolder_sm'] = owners


    def _add_from_csv(self,json_data):
        def has_original_column(header):
            return (header in par.CSV_HEADER_TRANSFORM)

        def is_multiple_values(header):
            return header in par.G_SM

        def need_captilize(header):  # only elements in from csv file needs capitlizsed
            HEADER_UPCASE = ["spatialSubject","subject"]
            return (header in HEADER_UPCASE)

        def d_sub_str(val): # val = "04072021"
            return GeoHelper.datetime(val.strip())

        def d_time(val):  # val = "04072021"
            return d_sub_str(val) + "T23:34:35.206Z"

        def isoTopics(val):
            codes = val.split("$")
            topics = [par.isoTopic[code] for code in codes]
            return "$".join(topics)

        def corrected_original_val(header):
            val = ""
            if has_original_column(header): # some elements in csv files have no original elements
                header_o = "{0}_o".format(header)
                val = self.main_csv_raw[header_o].strip()
                if len(val) > 0:
                    if header_o == "modified_date_dt_o" : val = d_time(val)  # only use original modified date for geoblacklight
                    if header_o == "topicISO_o": val = isoTopics(val)

            return val

        def corrected_current_val(header):
            val = self.main_csv_raw[header].strip()
            if len(val) > 0:
                if header == "date_s": val = d_sub_str(val)
                if header == "topicISO": val = isoTopics(val)
            return val

        def val_from_csv(header): # string
            val = corrected_current_val(header)
            if len(val) == 0:
                val = corrected_original_val(header)
            return val

        def captilize_str(str):
        	noCapWords = ["and", "is", "it", "or","if"]
        	words = [w.capitalize() if (w not in noCapWords) and (w[0].isalpha()) else w  for w in str.split()]
        	return " ".join(words)

        def captilize_arr(arr):
            new_arr = [captilize_str(w) for w in arr]
            return new_arr

        def format_metadata(header,column_val):
            val = column_val
            if is_multiple_values(header):
                val = column_val.split("$")
                need_captilized = need_captilize(header)
                if need_captilized:
                    val = captilize_arr(val)
            # else: # no this case for now
            #     if need_captilized:
            #         val = captilize_str(val)
            return val

        def add_rights(): # conslidate multiple columns of rights to one
            all_ls = []
            for h in par.CSV_HEADER_COLUMNS_RIGHTS:
                right = val_from_csv(h)
                if len(right) > 0:
                    ls = right.split("$")
                    all_ls.extend(ls)
            if len(all_ls)  > 0:
                json_data["dct_rights_sm"] = all_ls

        def add_metadata():
            for header,element_name in par.CSV_HEADER_COLUMNS.iteritems():
                column_val = val_from_csv(header)
                if len(column_val) > 0:
                    meta_value = format_metadata(header,column_val)
                    json_data[element_name] = meta_value

        add_metadata()
        add_rights()


    def _add_from_default(self,json_data):
        json_data["schema_provider_s"] = par.INSTITUTION
        json_data["gbl_mdVersion_s"]   = par.GEOBLACKLGITH_VERSION


    def _add_from_arkid(self,json_data):
        def ref_hosts():
            hosts = par.HOSTS
            hosts_secure = par.HOSTS_SECURE
            access = self.main_csv_raw["accessRights_s"].strip().lower()
            return   hosts if access == "public" else hosts_secure

        def dc_references(arkid): # TODO: add multiple download from csv later
            hosts = ref_hosts()
            id = "{0}{1}".format(par.PREFIX,arkid)
            iso_139_ext = "/iso19139.xml\","
            iso_139_xml = hosts["ISO139"] + id + iso_139_ext
            ref = "{" + hosts["wfs"] + hosts["wms"] + iso_139_xml + hosts["download"] + id + "/data.zip\"}"
            return ref.strip()

        arkid = self.arkid.strip()
        json_data['id'] = "{0}{1}".format(par.PREFIX,arkid)
        json_data['gbl_wxsIdentifier_s'] = arkid
        json_data['dct_identifier_sm'] = "http://spatial.lib.berkeley.edu/viewpublic/{0}{1}".format(par.PREFIX,arkid)
        json_data['dct_references_s'] = dc_references(arkid)


    def _add_from_iso19139(self,json_data):
        def iso19139_file():
            iso19139_dir = GeoHelper.iso19139_path(self.process_path)
            path = os.path.join(iso19139_dir,self.arkid)
            return os.path.join(path,"iso19139.xml")

        iso_19139 =iso19139_file()
        tree =  ET.parse(iso_19139)
        root = tree.getroot()
        self._geoblacklight_boundary(root,json_data)


    # From ISO19139
    def _geoblacklight_boundary(self,root,json_data):
        parent_path = "./{0}identificationInfo/{0}MD_DataIdentification/{0}extent/{0}EX_Extent/{0}geographicElement/{0}EX_GeographicBoundingBox".format("{http://www.isotc211.org/2005/gmd}")
        east_path = "./{0}eastBoundLongitude/{1}Decimal".format("{http://www.isotc211.org/2005/gmd}","{http://www.isotc211.org/2005/gco}")
        north_path = "./{0}northBoundLatitude/{1}Decimal".format("{http://www.isotc211.org/2005/gmd}","{http://www.isotc211.org/2005/gco}")
        south_path = "./{0}southBoundLatitude/{1}Decimal".format("{http://www.isotc211.org/2005/gmd}","{http://www.isotc211.org/2005/gco}")
        west_path = "./{0}westBoundLongitude/{1}Decimal".format("{http://www.isotc211.org/2005/gmd}","{http://www.isotc211.org/2005/gco}")

        parent_node = root.find(parent_path)
        if not parent_node is None:
            E = parent_node.find(east_path).text
            N = parent_node.find(north_path).text
            S = parent_node.find(south_path).text
            W = parent_node.find(west_path).text

            env = "ENVELOPE({0},{1},{2},{3})".format(W,E,N,S)
            json_data["locn_geometry"] = env
        else:
            GeoHelper.arcgis_message("{0} - {1}: No boundary found .".format(self.geofile,self.arkid))
