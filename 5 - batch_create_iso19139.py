import os
import xml.etree.ElementTree as ET
from typing import List
import logging
import csv
from datetime import datetime
from pathlib import Path
from arcpy import metadata as md
from shutil import copyfile


################################################################################################
#                             1. functions                                                    #
################################################################################################
def create_iso19139_files():
    resp_dic = csv_dic(resp_csv_arkid_filepath)
    with open(main_csv_arkid_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            if row.get("gbl_resourceClass_sm").lower() != "collections":
                arkid = row.get("arkid")
                if not arkid:
                    text = f"Please check the main csv file: missing arkid in {row.get('geofile')}"
                    log_raise_error(text)
                resp_rows = [
                    resp_row for resp_row in resp_dic if arkid == resp_row["arkid"]
                ]

                geofile_path = correlated_filepath(row.get("geofile"))
                geofile = GeoFile(geofile_path, logging)
                geofile.create_iso19139_file(row, resp_rows)


def correlated_filepath(geofile_path):
    if not source_batch_directory_path in geofile_path:
        text = f"File '{geofile_path}' listed in main csv is not located in source batch directory: '{source_batch_directory_path}'"
        log_raise_error(text)

    filepath = geofile_path.replace(
        source_batch_directory_path, projected_batch_directory_path
    )
    if Path(filepath).is_file():
        return filepath
    else:
        text = f"File {filepath} does not exist"
        log_raise_error(text)


def csv_dic(csv_filepath):
    lines = (line for line in open(csv_filepath, "r", encoding="utf-8"))
    rows = (line.strip().split(",") for line in lines)
    header = next(rows)
    return [dict(zip(header, row)) for row in rows]


def log_raise_error(text):
    logging.info(text)
    raise ValueError(text)


################################################################################################
#                             2. class  - initial metadata from *.tif.xml or *.shp.xml         #
################################################################################################
class GeoFile(object):
    def __init__(self, geofile_path, logging):
        self.logging = logging
        self.geofile_path = geofile_path
        self.basename = os.path.splitext(self.geofile_path)[0]
        self.tempfile_path = self._extended_filepath("_temp.xml")
        self.iso19139_path = self._extended_filepath("_iso19139.xml")

    # 1. copy esri xml file(*.shp.xml or *.tif.xml file) to tempfile
    # 2. update above temp metadata xml file with metadata information from main csv and resp csv files
    # 3. import the temp metadata xml file to the geofile
    # 4. export an ISO19139 xml metdata from above geofile
    def create_iso19139_file(self, main_row, resp_row):
        self._copy_tempfile()
        self._write_tempfile(main_row, resp_row)
        self._import_tempfile()
        self._transform_iso19139()
        self.logging.info(f"{self.geofile_path} - iso19139.xml created")

    def _copy_tempfile(self):
        esri_xml = f"{self.geofile_path}.xml"
        if not os.path.isfile(esri_xml):
            print(f"warning: {esri_xml} not found")
            raise FileNotFoundError

        copyfile(esri_xml, self.tempfile_path)

    def _remove_tempfile(self):
        if Path(self.tempfile_path).is_file():
            os.remove(self.tempfile_path)

    def _extended_filepath(self, text):
        base = os.path.splitext(self.geofile_path)[0]
        return f"{base}{text}"

    def _write_tempfile(self, main_row, resp_row):
        try:
            transformer = RowTransformer(
                self.tempfile_path, main_row, resp_row, self.logging
            )
            transformer()
        except Exception as ex:
            self._log_raise_error("Could not write metadata to", ex)

    def _export_tempfile(self):
        try:
            item_md = md.Metadata(self.basename)
            item_md.saveAsXML(self.tempfile_path, "EXACT_COPY")
        except Exception as ex:
            self._log_raise_error("Could not export tempfile to", ex)

    def _import_tempfile(self):
        try:
            item_md = md.Metadata(self.basename)
            item_md.importMetadata(self.tempfile_path, "ARCGIS_METADATA")
            item_md.save()
        except Exception as ex:
            self._log_raise_error("Could not import tempfile to", ex)

    def _transform_iso19139(self):
        try:
            item_md = md.Metadata(self.basename)
            item_md.exportMetadata(self.iso19139_path, "ISO19139")
        except Exception as ex:
            self._log_raise_error("Could not transform iso19139 to", ex)

    def _log_raise_error(self, text, ex):
        msg = f"{text} {self.geofile_path}"
        self.logging.info(f"{msg} - {ex}")
        raise ValueError(msg)


class RowTransformer(object):
    transform_main_headers = []
    resp_headers = []
    right_headers = ["rights_general", "rights_legal", "rights_security"]
    main_elements = {}
    resp_elements = {}

    def __init__(self, tempfile, main_row, resp_rows, logging):
        self.logging = logging
        self.tempfile = tempfile
        self.tree = ET.parse(self.tempfile)
        self.root = self.tree.getroot()
        self.main_row = main_row
        self.resp_rows = resp_rows

    def __call__(self):
        self._transform_main()
        self._transform_resp()
        self._add_ucb_distributor()
        self.tree.write(self.tempfile)

    def _transform_main(self) -> None:
        def remove_nodes(parent, child_name):
            nodes = parent.findall(child_name)
            for node in nodes:
                parent.remove(node)

        def add_key_node(parent, child_name, grandchild_name, val):
            if child_name == "tpCat":
                child = ET.SubElement(parent, child_name)
                grandchild = ET.SubElement(child, grandchild_name)
                grandchild.set("value", val)
            else:
                child = ET.SubElement(parent, child_name, attrib={"xmlns": ""})
                grandchild = ET.SubElement(child, grandchild_name)
                grandchild.text = val

        # Elements under tag "dataIdInfo"
        # example mapping path: "dataIdInfo/tempKeys/keyword" => dataIdInfo/child/grandchild
        def add_keys(path, val):
            tags = path.split("/")
            child = tags[1]
            grandchild = tags[2]
            dataInInfo = self.root.find("dataIdInfo")
            remove_nodes(dataInInfo, child)

            sub_values = [txt.strip() for txt in val.split("$")]
            for sub_val in sub_values:
                if sub_val:
                    add_key_node(dataInInfo, child, grandchild, sub_val)

        # all paths defined in elements start from root,
        # each element in a path is identical
        def ensure_nodes(path):
            elements = path.split("/")
            parent = self.root
            for e in elements:
                parent = self._add_element(parent, e)

        def add_node(path, val, add_to_attribute):
            ensure_nodes(path)
            element = self.root.find(f"./{path}")
            if add_to_attribute:
                element.set("value", val)
            else:
                element.text = val

        def update_metadata(header, val) -> None:
            hash = self.main_elements[header]
            path = hash["path"]
            if "Keys" in path:
                add_keys(path, val)
            else:
                val = val.replace("$", ";")
                add_to_attribute = True if "attribute" in hash else False
                # Geoblacklight allow multiple values, ISO19139 only allows a single value
                add_node(path, val, add_to_attribute)

        # All rights are written under "dataIdInfo/resConst" node
        def update_metadata_rights(rights):
            def right_tag(header):
                hash = self.main_elements[header]
                path = hash["path"]
                tags = path.split("/")
                return tags[2]

            child = "resConst"
            dataInInfo = self.root.find("dataIdInfo")
            # dataInIfo element should have been created during main_csv transformation
            # if not created, user needs check main csv file
            if dataInInfo:
                remove_nodes(dataInInfo, child)
                resConst_node = ET.SubElement(dataInInfo, child)
                for key, value in rights.items():
                    right_node = ET.SubElement(resConst_node, right_tag(key))
                    useLimit_node = ET.SubElement(right_node, "useLimit")
                    useLimit_node.text = value
            else:  # add main csv validation befefore removing this code
                print("Please check main_csv file, it may have no metadata content")

        # not every header has a related header_o
        def main_col_val(header):
            val = self.main_row.get(header)

            def issued_date():
                clr_val = val.replace('"', "")
                ls = clr_val.split("-")
                date_str = clr_val
                if len(ls) == 2:
                    date_str = f"ls[0]-ls[1]-01"
                if len(ls) == 1:
                    date_str = f"ls[0]-01-01"
                return f"{date_str}T00:00:00"

            if val and header.startswith("dct_issued_s"):
                return issued_date()
            return val

        def element_val(header):
            val = main_col_val(header)
            val_o = main_col_val(f"{header}_o")
            return val_o if val_o and (not val) else val

        def transform_main_headers():
            for header in self.transform_main_headers:
                val = element_val(header).strip()
                if val:
                    update_metadata(header, val)

        def transform_rights_headers():
            rights = {}
            for header in self.right_headers:
                val = element_val(header).strip()
                if val:
                    rights[header] = val
            if rights:
                update_metadata_rights(rights)

        def transform():
            transform_main_headers()
            transform_rights_headers()

        transform()

    def _transform_resp(self):
        def remove_old_responsible_parties():
            resp_parties = self.root.findall("./dataIdInfo/idCitation/citRespParty")
            for resp in resp_parties:
                idCitation = self.root.find("./dataIdInfo/idCitation")
                idCitation.remove(resp)

        def remove_old_idPoCs():
            idPoCs = self.root.findall("./dataIdInfo/idPoC")
            if idPoCs:
                dataIdInfo = self.root.find("./dataIdInfo")
                for idPoC in idPoCs:
                    dataIdInfo.remove(idPoC)

        def add_resps(rows):
            for row in rows:
                role = row["role"].strip().zfill(3)
                if role == "010" or role == "006":
                    self._add_resp(row, "./dataIdInfo/idCitation", "citRespParty")
                else:
                    self._add_resp(row, "./dataIdInfo", "idPoC")

        def transform():
            remove_old_responsible_parties()
            remove_old_idPoCs()
            add_resps(self.resp_rows)

        transform()

    def _add_element(self, parent, child_name, attrib=None):
        child = parent.find(child_name)
        if child is None:
            if attrib:
                child = ET.SubElement(parent, child_name, attrib=attrib)
            else:
                child = ET.SubElement(parent, child_name)
        return child

    def _add_resp(self, resp_row, parent_path, tag):
        def get_name():
            i_name = resp_row.get("individual")
            o_name = resp_row.get("organization")
            role = resp_row.get("role").strip().zfill(3)
            if i_name and role == "006":
                return i_name
            return o_name

        def col_val(col_name):
            if col_name == "organization":
                return get_name()
            else:
                return resp_row[col_name].strip()

        def add_sub_node(parent, child_node_name, col_name):
            val = col_val(col_name)
            if val:
                child = self._add_element(parent, child_node_name)
                child.text = val

        def add_siblings(parent, node_names):
            for name in node_names:
                val = resp_row[name].strip()
                if val:
                    child_node_name = self.resp_elements[name]["path"].split("/")[-1]
                    child = self._add_element(parent, child_node_name)
                    child.text = val

        respParty_parent = self.root.find(parent_path)

        if respParty_parent:
            respParty_node = ET.SubElement(respParty_parent, tag, attrib={"xmlns": ""})
            add_sub_node(respParty_node, "rpOrgName", "organization")
            add_sub_node(respParty_node, "rpIndName", "contact_name")
            add_sub_node(respParty_node, "rpPosName", "position")

            rpCntInfo = self._add_element(
                respParty_node, "rpCntInfo", attrib={"xmlns": ""}
            )
            add_siblings(rpCntInfo, ["email", "hours", "instruction"])

            cntAddress = self._add_element(
                rpCntInfo, "cntAddress", attrib={"addressType": ""}
            )
            add_siblings(cntAddress, ["address", "city", "zip", "country"])

            cntPhone = self._add_element(rpCntInfo, "cntPhone")
            add_siblings(cntPhone, ["phone_no", "fax_no"])

            role = self._add_element(respParty_node, "role")
            clr_role = resp_row["role"].strip().zfill(3)
            roleCd = ET.SubElement(role, "RoleCd", attrib={"value": clr_role})
        else:
            self.logging.info(f"File- {self.tempfile} has no responsible party ")

    def _add_ucb_distributor(self):
        def add_sub_node(parent, child_node_name, val):
            if val:
                child = self._add_element(parent, child_node_name)
                child.text = val

        distInfo = self._add_element(self.root, "distInfo", attrib={"xmlns": ""})
        distributor = self._add_element(distInfo, "distributor", attrib={"xmlns": ""})
        distorCont = self._add_element(distributor, "distorCont", attrib={"xmlns": ""})

        add_sub_node(distorCont, "rpOrgName", "UC Berkeley Library")

        rpCntInfo = self._add_element(distorCont, "rpCntInfo")
        cntPhone = self._add_element(rpCntInfo, "cntPhone")
        voiceNum = self._add_element(cntPhone, "voiceNum", attrib={"tddtty": ""})
        voiceNum.text = "(510) 642-2997****"

        cntAddress = self._add_element(
            rpCntInfo, "cntAddress", attrib={"addressType": ""}
        )
        add_sub_node(cntAddress, "delPoint", "50 McCone Hall")
        add_sub_node(cntAddress, "city", "Berkeley")
        add_sub_node(cntAddress, "adminArea", "CA")
        add_sub_node(cntAddress, "postCode", "94720")
        add_sub_node(cntAddress, "country", "USA")
        add_sub_node(cntAddress, "eMailAdd", "eart@library.berkeley.edu")

        add_sub_node(distorCont, "editorSave", "True")
        add_sub_node(distorCont, "displayName", "UC Berkeley Library")

        role = self._add_element(distorCont, "role")
        RoleCd = self._add_element(role, "RoleCd")
        RoleCd.set("value", "005")


################################################################################################
#                    2.      constant variables                                                #
################################################################################################

TRANSFORM_MAIN_HEADERS = [
    "dct_title_s",
    "dct_alternative_sm",
    "summary",
    "dct_description_sm",
    "dct_language_sm",
    "dct_subject_sm",
    "dct_issued_s",
    "dct_spatial_sm",
    "pcdm_memberOf_sm",
    "gbl_mdModified_dt",
    "dcat_theme_sm",
    "dcat_keyword_sm",
    "dct_temporal_sm",
]

# 1) Keys are headers of main CSV file
# 2) If an attribute "path" value include "keys", the element has multiple occurrences in ISO19139
MAIN_ELEMENTS = {
    "dct_title_s": {"path": "dataIdInfo/idCitation/resTitle", "type": "string"},
    "dct_alternative_sm": {
        "path": "dataIdInfo/idCitation/resAltTitle",
        "type": "string",
    },
    "summary": {"path": "dataIdInfo/idPurp", "type": "string"},
    "dct_description_sm": {"path": "dataIdInfo/idAbs", "type": "string", "html": True},
    "dct_language_sm": {"path": "dataIdInfo/dataLang/languageCode", "type": "string"},
    "dct_subject_sm": {"path": "dataIdInfo/themeKeys/keyword", "type": "string"},
    "dct_issued_s": {"path": "dataIdInfo/idCitation/date/pubDate", "type": "string"},
    "dct_spatial_sm": {"path": "dataIdInfo/placeKeys/keyword", "type": "string"},
    "rights_general": {
        "path": "dataIdInfo/resConst/Consts/useLimit",
        "html": True,
        "type": "string",
    },
    "rights_legal": {
        "path": "dataIdInfo/resConst/LegConsts/useLimit",
        "type": "string",
    },
    "rights_security": {
        "path": "dataIdInfo/resConst/SecConsts/useLimit",
        "type": "string",
    },
    "gbl_mdModified_dt": {"path": "Esri/ModDate", "type": "date"},
    "dcat_theme_sm": {
        "path": "dataIdInfo/tpCat/TopicCatCd",
        "attribute": True,
        "type": "string",
    },
    "dcat_keyword_sm": {"path": "dataIdInfo/searchKeys/keyword", "type": "string"},
    "dct_temporal_sm": {"path": "dataIdInfo/tempKeys/keyword", "type": "string"},
    "pcdm_memberOf_sm": {"path": "dataIdInfo/idCitation/collTitle", "type": "string"},
}

RESP_HEADERS = [
    "arkid",
    "geofile",
    "from",
    "individual",
    "role",
    "contact_name",
    "position",
    "organization",
    "contact_info",
    "email",
    "address_type",
    "address",
    "city",
    "state",
    "zip",
    "country",
    "phone_no",
    "fax_no",
    "hours",
    "instruction",
]

RESP_ELEMENTS = {
    "contact_name": {"path": "rpIndName", "type": "string"},
    "position": {"path": "rpPosName", "type": "string"},
    "organization": {"path": "rpOrgName", "type": "string"},
    "contact_info": {"path": "rpCntInfo", "type": "string"},
    "email": {"path": "rpCntInfo/cntAddress/eMailAdd", "type": "string"},
    "address_type": {
        "path": "rpCntInfo/cntAddress",
        "type": "attribute",
        "key": "addressType",
        "values": [("postal", "postal"), ("physical", "physical"), ("both", "both")],
    },
    "address": {"path": "rpCntInfo/cntAddress/delPoint", "type": "string"},
    "city": {"path": "rpCntInfo/cntAddress/city", "type": "string"},
    "state": {"path": "rpCntInfo/cntAddress/adminArea", "type": "string"},
    "zip": {"path": "rpCntInfo/cntAddress/postCode", "type": "string"},
    "country": {"path": "rpCntInfo/cntAddress/country", "type": "string"},
    "phone_no": {"path": "rpCntInfo/voiceNum", "type": "string"},
    "fax_no": {"path": "rpCntInfo/faxNum", "type": "string"},
    "hours": {"path": "rpCntInfo/cntHours", "type": "string"},
    "instruction": {"path": "rpCntInfo/cntInstr", "type": "string"},
}

# initial csv infomation to class variables
RowTransformer.resp_headers = RESP_HEADERS
RowTransformer.resp_elements = RESP_ELEMENTS
RowTransformer.transform_main_headers = TRANSFORM_MAIN_HEADERS
RowTransformer.main_elements = MAIN_ELEMENTS

################################################################################################
#                                 3. set up                                                    #
################################################################################################

# 1. setup log file path
logfile = r"C:\process_data\log\process.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 2. source batch directory
source_batch_directory_path = r"C:\process_data\source_batch"


# 3. Projected batch directory path
projected_batch_directory_path = r"C:\process_data\source_batch_projected"

# 4. please provide main csv and resp csv files here, check csv files in script "4 - check_csv_files.py", before running this script:
main_csv_arkid_filepath = r"C:\process_data\csv_files_arkid\main_arkid.csv"
resp_csv_arkid_filepath = r"C:\process_data\csv_files_arkid\resp_arkid.csv"


################################################################################################
#                    4. Create an ISO19139.xml file for each  geofile                               #
################################################################################################
def output(msg):
    logging.info(msg)
    print(msg)


def verify_setup(file_paths, directory_paths):
    verified = True
    for file_path in file_paths:
        if not Path(file_path).is_file():
            print(f"{file_path} does not exit.")
            verified = False

    for directory_path in directory_paths:
        if not Path(directory_path).is_dir():
            print(f"{directory_path} does not exit.")
            verified = False
    return verified


script_name = "5 - batch_create_iso19139.py"
output(f"***starting  {script_name}")

if verify_setup(
    [main_csv_arkid_filepath, resp_csv_arkid_filepath],
    [source_batch_directory_path, projected_batch_directory_path],
):
    # 1. Get a geofile name from main csv file
    # 2. Find the geofile in projected directory
    # 3. Create an iso19139 xml file for each geofile found in 2
    create_iso19139_files()
    output(f"***completed {script_name}")
