#!/usr/bin/python
import os
import sys
import csv
from arcgis_iso import ArcGisIso,MetadataContainer
from geo_helper import GeoHelper
import par
if os.name == "nt":
    import arcpy

# Note:
# 1) Writing main metadata from arcgis_iso_collection to main csv file, saved in *_UPDATED,*_ORIGINAL csv files
# 2) Writing responsible party metadata from arcgis_iso_collection to the responsible file, saved in *_UPDATED,*_ORIGINAL csv files

class ExportCsv(object):

    def __init__(self,arcGisIso_list,dest_csv_files,geo_ext):
        self.geo_ext = geo_ext
        self.arcGisIso_list = arcGisIso_list
        self.dest_csv_files = dest_csv_files
        self.main_csv_tranform_header_double = self._double_header(par.CSV_HEADER_TRANSFORM)  # add header_o column for main csv

    def _format(self):
        format = ""
        if self.geo_ext.lower() == ".tif": format = "GeoTIFF"
        elif self.geo_ext.lower() == ".shp": format = "Shape File"
        return format

    def _double_header(self,ls):
        out_ls = []
        for l in ls:
            out_ls.append("{0}_o".format(l))
            out_ls.append(l)
        return out_ls

    def _attr_value(self,metadata_obj,key):
        txt = ""
        attr_key = "_{0}".format(key)
        if attr_key in metadata_obj.__dict__:
            txt = metadata_obj.__dict__[attr_key]
        return txt

    def _add_common_metadata(self,ls,arcgisiso):
        ls.append(self._format())
        ls.append(arcgisiso.ark)
        ls.append(arcgisiso.filename)

    def _main_csv_raw(self,arcgisiso):
        metadata_obj = arcgisiso.main_csv_metadata
        ls = []

        def add_transformed_metadata():
            for name in self.main_csv_tranform_header_double:  # python dictionary cannot grarentee the order of items,we have to use the list for ordering items - make sure written in order
                val = self._attr_value(metadata_obj,name)
                ls.append(val)

        self._add_common_metadata(ls,arcgisiso)
        add_transformed_metadata()
        GeoHelper._space(ls,15)
        return ls

    # one arcgisiso obj has multiple responsible parties
    def _res_raw(self,arcgisiso,resp_obj,update_individual):  #  responsible_party = None: when emapty ESRI ISO generated
        ls = []

        def add_from_column():
            ls.append(resp_obj.__dict__["_from"]) # default value for ""update?
            if update_individual:
                ls.append(resp_obj.__dict__["_individual"])

        def add_transformed_metadata():
            for name in par.CSV_HEADER_RESPONSIBLE_PARTY[2:]: #   # python dictionary cannot grarentee the order of items
                # val = self._attr_value(resp_obj,"{0}_o".format(name))
                val = self._attr_value(resp_obj,name)  # use the same name as defined in par.CSV_HEADER_RESPONSIBLE_PARTY: only role has two columns: role_o, role
                ls.append(val)

        add_from_column()
        self._add_common_metadata(ls,arcgisiso)
        add_transformed_metadata()
        return ls

    def _responsible_party_update_raw(self,arcgisiso,resp_obj):
        return self._res_raw(arcgisiso,resp_obj,True)

    def _responsible_party_original_raw(self,arcgisiso,resp_obj):
        return self._res_raw(arcgisiso,resp_obj,False)

    def _write_csv(self,file,header,raws):
        with open(file, 'wb') as csvfile:
            csvWriter = csv.writer(csvfile)
            csvWriter.writerow([h.encode("utf-8") for h in header])
            for raw in raws:
                # print str(raw["_modified_date_dt"])
                csvWriter.writerow([v.encode("utf-8") if v else "" for v in raw])

    def write_to_main_csv(self):
        header = []
        raws = []

        def get_main_csv_header_with_o():
            header.extend(par.CSV_HEADER_COMMON)
            header.extend(self.main_csv_tranform_header_double)
            header.extend(par.CSV_HEADER_EMPTY)

        def get_raws():
            for arcGisIso in self.arcGisIso_list:
                raw = self._main_csv_raw(arcGisIso)
                raws.append(raw)

        get_main_csv_header_with_o()
        get_raws()
        self._write_csv(self.dest_csv_files[0],header,raws)
        self._write_csv(self.dest_csv_files[3],header,raws)


    def write_responsible_party_csvs(self):
        header_update = GeoHelper.responsibleParty_csv_update_header()
        resp_parties_raws = []

        def get_raws():
            for arcGisIso in self.arcGisIso_list:
                responsible_parties = arcGisIso.all_responsible_parties
                for res in responsible_parties:
                    raw = self._responsible_party_update_raw(arcGisIso,res)
                    resp_parties_raws.append(raw)

        get_raws()
        self._write_csv(self.dest_csv_files[1],header_update,resp_parties_raws)
        self._write_csv(self.dest_csv_files[2],header_update,resp_parties_raws)

    def export_csv_files(self):
        self.write_to_main_csv()
        self.write_responsible_party_csvs()

        csv_files = "; ".join(self.dest_csv_files)
        GeoHelper.arcgis_message(par.SAVE_TO_CSV.format(csv_files))
