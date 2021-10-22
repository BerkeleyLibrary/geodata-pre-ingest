#!/usr/bin/python

import os
import sys
import csv
from shutil import copyfile
from geo_helper import GeoHelper
import par
if os.name == "nt":
    import arcpy


class CsvIsoCollection(object):
    def __init__(self,csv_files):
        self.csv_files = csv_files
        self.resp_parties_from_csv = []
        self._populate_responsibleparty_csv()


    def csv_collection(self):
        def correct_isotipic(raw,header):  # 001$002;  excel display "001" as "1"
            isotopic = raw[header].strip()
            if len(isotopic) > 0:
                ls = isotopic.split("$")
                raw[header] = "$".join([l.strip().zfill(3) for l in ls])

        def correct_isotipics(raw):
            correct_isotipic(raw,"topicISO")
            correct_isotipic(raw,"topicISO_o")

        def all_csv_objs():
            _csv_objs = []
            with open(self.csv_files[0], 'r') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for main_csv_raw in csv_reader:
                    correct_isotipics(main_csv_raw)
                    csv_obj = self._csv_obj(main_csv_raw)
                    _csv_objs.append(csv_obj)

            return _csv_objs

        return all_csv_objs()

    def _csv_obj(self,main_csv_raw):
        def respible_party_raws_on_ark():
            main_csv_arkid = main_csv_raw["arkid"].strip()
            return [raw  for raw in self.resp_parties_from_csv if main_csv_arkid == raw["arkid"].strip()]

        responsible_party_raws = respible_party_raws_on_ark()

        def resp_party_name(raw):
            organization = raw["organization"].strip()
            individual = raw["individual"].strip()
            if len(individual) > 0: return individual
            if len(organization) > 0: return organization
            return None

        def resp_party_names(role_code):
            names = []
            for raw in responsible_party_raws:
                if raw["role"].strip() == role_code:
                    resp_name = resp_party_name(raw)
                    if resp_name: names.append(resp_name)
            return names if len(names) > 0 else None

        def populate_csv_obj():
            csv_obj = CSVContainer()
            csv_obj.__dict__["_main_csv_raw"] = main_csv_raw
            csv_obj.__dict__["_resp_parties_raws"] = responsible_party_raws
            csv_obj.__dict__["_publishers"] = resp_party_names("010")
            csv_obj.__dict__["_originators"] = resp_party_names("006")
            csv_obj.__dict__["_owners"] = resp_party_names("003")
            return csv_obj

        return populate_csv_obj()


    def _populate_responsibleparty_csv(self):
        def populate_role(raw): # prepare for writting to ESRI ISO
            val = raw["role"].strip()
            raw["role"] = val.zfill(3)

        with open(self.csv_files[1], 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for raw in csv_reader:
                populate_role(raw)
                self.resp_parties_from_csv.append(raw)


class CSVContainer(object):
    def __init__(self):
        pass


    
