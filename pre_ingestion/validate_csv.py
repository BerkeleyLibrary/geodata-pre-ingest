#!/usr/bin/python
import os
import sys
import csv
import json
from geo_helper import GeoHelper
import par

if os.name == "nt":
    from jsonschema import validate
    import jsonschema

# Not just validating CSV
class ValidateCSV(object):
    def __init__(self,process_path):
        self.csv_files = GeoHelper.dest_csv_files_updated(process_path)
        self.process_path = process_path
        self.arkids = self.arkids()

    def arkids(self):
        arks = []
        with open(self.csv_files[0], 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for main_csv_raw in csv_reader:
                arkid = main_csv_raw["arkid"].strip()
                if len(arkid) == 0:
                    GeoHelper.arcgis_message(" A line in '{0}' has no arkid".format(self.csv_files[0]))
                else:
                    arks.append(arkid)
        return arks

    def check_default_codes(self,arkid,column_val,code_list,header):
        messages = []
        if len(column_val) > 0:
            vals = [txt.strip() for txt in column_val.split("$")]
            for val in vals:
                if not int(val) in code_list:
                    warning_msg = "{0} - column '{1}' has incorrect code value -- '{2}' ".format(arkid,header,val)
                    messages.append(warning_msg)
        return messages


    def validate_main_csv_file(self):
        messages = []

        # main csv - 1. make sure columns with header in par.CSV_REQUIRED_HEADERS have values, mandatory metadata elementes
        def check_required_elements(raw):
            required_headers = par.CSV_REQUIRED_HEADERS
            for header in required_headers:
                val = GeoHelper.metadata_from_csv(header,raw)
                if not GeoHelper.isNotNullorEmpty(val):
                    arkid = raw["arkid"].strip()
                    warning_msg = "{0} - '{1}': missing required value ".format(arkid,header)
                    messages.append(warning_msg)

        # main csv - 2. To avoid typo in accessright element
        def check_accessright(raw):
            arkid = raw["arkid"].strip()
            rights = ["public","private"]
            right = raw["accessRights_s"].strip().lower()
            if len(right) > 0 and (not right in rights):
                warning_msg = "{0} - '{1}' value should not be '{2}'.".format(arkid,"accessRights_s",right)
                messages.append(warning_msg)

        # main csv - 3. Make sure input correct topicis code
        def check_topiciso(raw):
            codes = range(1,20)
            arkid = raw["arkid"].strip()
            column_val = raw["topicISO"].strip()
            column_val_o = raw["topicISO_o"].strip()

            warning_msgs = self.check_default_codes(arkid,column_val,codes,"topicISO")
            warning_msgs_o = self.check_default_codes(arkid,column_val_o,codes,"topicISO_o")
            warning_msgs.extend(warning_msgs_o)
            if len(warning_msgs)>0:
                messages.extend(warning_msgs)

        # main csv - 4. Make sure Geofile work directory is the same as in main csv file. A user may move the updated CSV files around
        def check_geofile(raw):
            geofile = raw["filename"]
            geopath = GeoHelper.geo_path_from_CSV_geofile(geofile)
            workpath = GeoHelper.work_path(self.process_path)

            correct_geofile = False
            if geopath == workpath:
                if os.path.isfile(geofile):
                    correct_geofile = True
                else:
                    messages.append("**** Missing Geofile - {0}".format(geofile))
            else:
                messages.append("*** Work Directory is different! From CSV file - {0}; Actual work directory - {1}".format(geopath,workpath))
            return correct_geofile


        # def check_sourcetype(raw):
        #     warning_msgs = self.check_default_codes(raw,par.resourceType,"resourceType")


        def validate_all():
            with open(self.csv_files[0],'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for raw in csv_reader:  # should we check ISOTopic ?
                    check_geofile(raw)
                    check_required_elements(raw)
                    check_topiciso(raw)
                    check_accessright(raw)
                    # check_sourcetype(raw)
                return messages

        return validate_all()


    def validate_resp_update_csv_file(self):
        resp_msg = []
        arkids = []
        arkids_with_publisher = []
        arkids_with_originator = []

        def ark_category(arkid,role):
            if arkid not in arkids:
                arkids.append(arkid)
            if role == "010":
                arkids_with_publisher.append(arkid)
            if role == "006":
                arkids_with_originator.append(arkid)

        # resp_csv - 1. only role 006 can have "individual value"
        def only_role_006_has_individual(arkid,role,individual):
            if len(individual) > 0 and role <> "006":
                msg = par.INCORRECT_ROLE_FOR_INDIVIDUAL.format(arkid,role)
                resp_msg.append(msg)

        def ensure_006_010_have_value(arkid,role,individual,organization):
            invlid_originator_value = (role == "006") and len(individual) == 0  and len(organization) == 0
            invlid_publisher_value = (role == "010") and len(organization) == 0
            if invlid_originator_value or invlid_publisher_value:
                msg = par.EMPTY_ROLE.format(arkid,role)
                resp_msg.append(msg)

        def check_missing_roles(role_msg,role_arks):
            messeges = []
            if len(role_arks) > 0:
                for arkid in arkids:
                    if not arkid in role_arks:
                        msg = par.MISSING_ROLE.format(arkid,role_msg)
                        messeges.append(msg)
            return messeges

        # resp_csv - 3. Each arkid (geofile) may have multiple lines in responsible table, but each Geofile(arkid) should at least have a publisher and a originator
        def ensure_required_roles_existed():
            msgs1 = check_missing_roles("Publisher (010)",arkids_with_publisher)
            resp_msg.extend(msgs1)

            msgs2 = check_missing_roles("Originator (006)",arkids_with_originator)
            resp_msg.extend(msgs2)

        # resp_csv - 4. Make sure input correct role code
        def ensure_correct_role_code(arkid,role_val):
            codes = range(1,12)
            msg = self.check_default_codes(arkid,role_val,codes,"role")
            if len(msg)>0:
                resp_msg.extend(msg)

        def validate_all():
            responsible_part_csvfile = self.csv_files[1]
            with open(responsible_part_csvfile, 'r') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for raw in csv_reader:
                    arkid = raw["arkid"].strip()
                    role = raw["role"].strip().zfill(3)
                    individual = raw["individual"].strip()
                    organization = raw["organization"].strip()

                    ark_category(arkid,role)
                    ensure_correct_role_code(arkid,role)
                    only_role_006_has_individual(arkid,role,individual)
                    ensure_006_010_have_value(arkid,role,individual,organization)
            ensure_required_roles_existed()

            return resp_msg

        return validate_all()


    def updated_csv_files_valid(self):
        msg_list = self.validate_main_csv_file()
        msg_list_2 =  self.validate_resp_update_csv_file()
        msg_list.extend(msg_list_2)

        if len(msg_list) > 0:
            GeoHelper.arcgis_message(self.csv_files[0])
            GeoHelper._print_files_txt(msg_list,par.MISSING_CVS_VALUES)
            return False
        else:
            GeoHelper.arcgis_message(par.PASS_CSV_VALIDATION)
            return True


    def updated_csv_files_existed(self):
        existed = True
        if len(self.csv_files) <> 2:
            base
            GeoHelper.arcgis_message("Missing updated CSV file in directory '{0}'".format(updated_csv_files_path))
            existed = False
        return existed


    #### Not CSV file - other validations ####

    def files_existed(self,dir,name):
        def full_path_file(dir,arkid,name):
            return os.path.join(dir,arkid,name) # "iso19139.xml"

        missing_files = []
        for arkid in self.arkids:
            file = full_path_file(dir,arkid,name)
            if not os.path.isfile(file):
                missing_files.append(file)
                GeoHelper.arcgis_message("*** Directory '{0}' missing file - '{1}'".format(dir,file))

        return len(missing_files) == 0

    # 1. Check ISO19139 files
    def iso19139_files_existed(self):
        dir = GeoHelper.iso19139_path(self.process_path)
        return self.files_existed(dir,"iso19139.xml")

    # 2. Check geoblacklight files
    def geoblacklight_files_existed(self):
        dir = GeoHelper.geoblacklight_path(self.process_path)
        return self.files_existed(dir,"geoblacklight.json")

    def files_existed_to_zip(self,is_source_file):
        def new_file(old_file):
            if os.name == "nt":
                return old_file.replace("\\Work\\","\\Source\\")
            else:
                return old_file.replace("/Work/","/Source/")

        missing_files = []
        with open(self.csv_files[0], 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for main_csv_raw in csv_reader:
                file = main_csv_raw["filename"].strip()
                the_file = new_file(file) if is_source_file else file
                if not os.path.isfile(the_file):
                    missing_files.append(the_file)
                    GeoHelper.arcgis_message("*** Missing file - '{0}'".format(the_file))

        return len(missing_files) == 0

    # 3. check work files ready for map.zp
    def work_files_existed(self):
        return self.files_existed_to_zip(False)

    # 4. check source files ready for download  data.zip
    def source_files_existed(self):
        return self.files_existed_to_zip(True)

    # 5. check download zip files existing for merrritt
    def data_zip_files_existed(self):
        dir = GeoHelper.data_download_path(self.process_path)
        return self.files_existed(dir,"data.zip")


    ### Geoblacklight JSON veridation ###
    def ardvark_validation(self):
        schema_path = os.path.join(os.path.dirname(__file__),"validation")
        ardvark_schema = os.path.join(schema_path,"GeoblacklightTransform.json")

        def validation(file):
            isvalid = False
            schema = ""
            data = ""

            with open(ardvark_schema,'r') as s:
                schema = s.read()
            with open(file,'r') as d:
                data = d.read()

            try:
                v = jsonschema.Draft4Validator(json.loads(schema))
                for error in sorted(v.iter_errors(json.loads(data)), key=str):
                    errorMessage = error.message.replace("u\'","\'")
                    msg = "* " + errorMessage
                    if len(error.path) > 0:
                        msg = "* " + error.path[0] + ': ' + errorMessage
                    GeoHelper.arcgis_message(msg)

            except jsonschema.ValidationError as e:
                msg = "^^ Geoblackschema error when validating {0} : error --  {1}".format(file,e.message)
                GeoHelper.arcgis_message(msg)
            except:
                GeoHelper.arcgis_message("^^ ardvark_validation error -- {0}".format(e.message))

        def validation_all():
            geoblacklight_dir = GeoHelper.geoblacklight_path(self.process_path)
            for root, dirs, files in os.walk(geoblacklight_dir):
                for file in files:
                    json_file = os.path.join(root,file)

                    ext = os.path.splitext(json_file)[1].lower()
                    if ext == ".json":
                        if os.name == "nt":
                            validation(json_file)

        validation_all()