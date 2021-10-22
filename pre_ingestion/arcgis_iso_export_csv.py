#!/usr/bin/python
import os
import sys
import csv
from arcgis_iso import ArcGisIso,MetadataContainer
from geo_helper import GeoHelper
import par
if os.name == "nt":
    import arcpy


# 1) Writing main metadata from arcgis_iso_collection to main csv files, saved as *_UPDATED,*_ORIGINAL csv files
# 2) Writing responsible party metadata from arcgis_iso_collection to responsible party csv files, saved in *_UPDATED,*_ORIGINAL csv files

class ExportCsv(object):

    def __init__(self,arcGisIso_list,dest_csv_files,geo_ext):
        self.geo_ext = geo_ext
        self.arcGisIso_list = arcGisIso_list
        self.dest_csv_files = dest_csv_files


    def _format(self):
        format = ""
        if self.geo_ext.lower() == ".tif": format = "GeoTIFF"
        elif self.geo_ext.lower() == ".shp": format = "Shape File"
        return format


    def _add_common_metadata(self,ls,arcgisiso):
        ls.append(self._format())
        ls.append(arcgisiso.ark)
        ls.append(arcgisiso.filename)

    def _add_bom(self,ls,full_path_filename):
        filename = os.path.basename(full_path_filename)
        ls.append(filename)

    def _main_csv_raw(self,arcgisiso):
        metadata_obj = arcgisiso.main_csv_metadata
        ls = []

        def column_val(name):
            val = ""
            if name.endswith("_o"):
                val = metadata_obj.__dict__["_{0}".format(name)]
            return val

        def add_transformed_metadata():
            for name in par.CSV_ORDERED_HEADERS:
                val = column_val(name)
                ls.append(val)

        self._add_bom(ls,arcgisiso.filename)
        self._add_common_metadata(ls,arcgisiso)
        add_transformed_metadata()
        return ls

    # One arcgisiso obj has multiple responsible parties
    def _responsible_party_update_raw(self,arcgisiso,resp_obj):
        ls = []

        def column_val(key):
            txt = ""
            attr_key = "_{0}".format(key)
            if attr_key in resp_obj.__dict__:
                txt = resp_obj.__dict__[attr_key]
            return txt

        def add_extra_columns():
            ls.append(resp_obj.__dict__["_from"])
            ls.append(resp_obj.__dict__["_individual"])

        def add_transformed_metadata():
            for name in par.CSV_HEADER_RESPONSIBLE_PARTY[2:]: # Use the list to ensure the order, python dictionary cannot garentee the order of items
                val = column_val(name)
                ls.append(val)

        self._add_bom(ls,arcgisiso.filename)
        add_extra_columns()
        self._add_common_metadata(ls,arcgisiso)
        add_transformed_metadata()
        return ls


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
            header.extend(par.CSV_BOM)
            header.extend(par.CSV_HEADER_COMMON)
            header.extend(par.CSV_ORDERED_HEADERS)

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
