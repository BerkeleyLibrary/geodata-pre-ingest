#!/usr/bin/python
import os
import sys
from csv_iso  import CsvIso
from csv_geoblacklight import CsvGeoblacklight
from geo_helper import GeoHelper
from csv_iso_collection import CsvIsoCollection
import par


class CsvTransform(object):
    def __init__(self,csv_collection,process_path):
        self.raw_objs = csv_collection
        self.process_path = process_path


    def transform_both(self):
        for  raw_obj in self.raw_objs:
            csv_iso = CsvIso(raw_obj,self.process_path)
            csv_iso.create_iso19139_file()

            csv_Geoblacklight = CsvGeoblacklight(raw_obj,self.process_path)
            csv_Geoblacklight.create_geoblacklight_file()


    def transform_iso19139(self):
        for  raw_obj in self.raw_objs:
            csv_iso = CsvIso(raw_obj,self.process_path)
            csv_iso.create_iso19139_file()


    def transform_geoblacklight(self):
        for  raw_obj in self.raw_objs:
            #print raw_obj.__dict__["_arkid"]
            csv_Geoblacklight = CsvGeoblacklight(raw_obj,self.process_path)
            csv_Geoblacklight.create_geoblacklight_file()
