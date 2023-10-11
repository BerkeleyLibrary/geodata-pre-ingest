import arcpy
from arcpy import metadata as md
import os
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
import csv
import re
from datetime import date, datetime
from typing import List


################################################################################################
#                             1. class                                                         #
################################################################################################


class BatchExportCsv(object):
    def __init__(self, workspace_dir, results_dir, logging):
        self.logging = logging
        self.workspace_dir = workspace_dir
        self.geofile_paths = self._geofile_paths()
        self.results_dir = results_dir

    def main_csv(self):
        file = self._filename("main")
        rows = [
            GeoFile(geofile_path, self.logging).main_row()
            for geofile_path in self.geofile_paths
        ]
        self._write_csv(file, GeoFile.main_headers, rows)

    def resp_csv(self):
        file = self._filename("resp")
        rows = []
        for geofile_path in self.geofile_paths:
            resp_rows = GeoFile(geofile_path, self.logging).resp_rows()
            rows.extend(resp_rows)
        self._write_csv(file, GeoFile.resp_headers, rows)

    def _geofile_paths(self):
        shapefile_paths = self._file_paths("shp")
        tiffile_paths = self._file_paths("tif")

        if not shapefile_paths and not tiffile_paths:
            self.logging.info(
                f"No shapefiles or raster files found in {self.workspace_dir}!"
            )
            return []

        if shapefile_paths and tiffile_paths:
            self.logging.info(
                f"Mixing shapefiles and raster files found in {self.workspace_dir}."
            )
            raise ValueError(
                "Both shapefiles and raster files found. Directory should include either shapefiles or raster files."
            )

        return shapefile_paths if shapefile_paths else tiffile_paths

    def _write_csv(self, file, header, rows):
        new_headers = ["\uFEFF他们 (für)"]
        new_headers.extend(header)
        with open(file, "w", newline="", encoding="utf-8") as csvfile:
            csvWriter = csv.writer(csvfile)
            csvWriter.writerow([h for h in new_headers])
            for row in rows:
                new_row = [""]
                new_row.extend([col if col else "" for col in row])
                csvWriter.writerow(new_row)

    def _filename(self, prefix):
        name = f"{prefix}.csv"
        return os.path.join(self.results_dir, name)

    def _file_paths(self, ext) -> List:
        return [
            os.path.join(dirpath, filename)
            for dirpath, dirs, filenames in os.walk(self.workspace_dir)
            for filename in filenames
            if filename.endswith(ext)
        ]


class GeoFile(object):
    main_headers = []
    main_elements = {}
    resp_headers = []
    resp_elements = {}

    def __init__(self, geofile, logging):
        self.geofile = geofile
        self.root = self._root()
        self.logging = logging

    def main_row(self):
        row = [
            self.column_from_main_elements(header) if header.endswith("_o") else ""
            for header in self.main_headers
        ]
        self._update_main_col(row, "geofile", self.geofile)
        self._update_main_col(row, "gbl_resourceType_sm_o", self._resource_type())
        self._update_main_col(row, "dct_format_s_o", self._format())
        return row

    def resp_rows(self):
        rows = []
        citation_rows = self._resp_rows_from_path(
            "./dataIdInfo/idCitation/citRespParty"
        )
        rows.extend(citation_rows)

        idpoc_rows = self._resp_rows_from_path("./dataIdInfo/idPoC")
        rows.extend(idpoc_rows)

        self._add_rows_with_defalut_roles(rows)

        return rows

    def _root(self):
        xml_filepath = f"{self.geofile}.xml"
        if not Path(xml_filepath).is_file():
            self._export_xml_file(xml_filepath)
        tree = ET.parse(xml_filepath)
        return tree.getroot()

    def _export_xml_file(self, xml_filepath):
        try:
            basename = os.path.splitext(self.geofile)[0]
            item_md = md.Metadata(basename)
            item_md.saveAsXML(xml_filepath, "EXACT_COPY")
        except Exception as ex:
            msg = f"Could not export to xml file from {self.geofile}"
            self.logging.info(f"{msg} - {ex}")
            raise ValueError(msg)

    def column_from_main_elements(self, header):
        tag = header.strip()[:-2]
        keys = self.main_elements.keys()
        if not tag in keys:
            return ""

        tag_functions = {
            "pcdm_memberOf_sm": self._collection_title,
            "dct_temporal_sm": self._temporalCoverage,
            "gbl_mdModified_dt": self._modified_date_dt,
        }
        fun = tag_functions.get(tag, None)
        if fun:
            return fun()
        else:
            val = self._tag_value(tag).strip()
            if tag == "dcat_theme_sm":
                val = val.strip("0")
            return val

    def _tag_value(self, tag):
        dic = self.main_elements[tag]
        path = dic.get("path")
        from_attribute = dic.get("attribute")
        removal_dollar_sign = True if tag.endswith("m") else False

        hash = {
            "from_attribute": from_attribute,
            "removal_dollar_sign": removal_dollar_sign,
        }
        value = self._field_value(path, hash)
        if tag == "dcat_theme_sm":
            return value.strip("0")
        if tag == "dct_issued_s":
            return self._issued_date(value)

        return value

    def _issued_date(self, val):
        try:
            if val:
                datetime_obj = datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")
                return f'"{datetime_obj.strftime("%Y-%m-%d")}"'
            else:
                return ""
        except ValueError:
            return ""

    def _node_value(self, node, from_attribute):
        tags = re.compile("<.*?>")
        if node is not None and len(list(node)) == 0:  # leaf node
            txt = node.get("value") if from_attribute else node.text
            if txt:
                return re.sub(tags, "", txt.strip())

        return ""

    def _field_value(self, path, hash, parent_node=None):
        if parent_node is None:
            parent_node = self.root

        content = ""
        nodes = parent_node.findall(path)
        for node in nodes:
            value = self._node_value(node, hash.get("from_attribute"))
            if len(value) > 0:
                if hash.get("removal_dollar_sign"):
                    value = self.rm_dollar_sign(value)
                content += f"{value}$"

        return content.strip().rstrip("$").strip()

    def _collection_title(self):
        hash = {"from_attribute": False, "removal_dollar_sign": True}
        coll_title = self._field_value("dataIdInfo/idCitation/collTitle", hash)
        if coll_title:
            return coll_title

        hash = {"from_attribute": True, "removal_dollar_sign": True}
        code = self._field_value("dataIdInfo/aggrInfo/assocType/AscTypeCd", hash)

        if code == "002":
            hash = {"from_attribute": False, "removal_dollar_sign": True}
            res_title = self._field_value(
                "dataIdInfo/aggrInfo/aggrDSName/resTitle", hash
            )
            if res_title:
                return res_title

        return ""

    def _temporalCoverage(self):
        xpaths = [
            "dataIdInfo/tempKeys/keyword",
            "dataIdInfo/dataExt/tempEle/TempExtent/exTemp/TM_Period",
            "dataIdInfo/dataExt/tempEle/TempExtent/exTemp/TM_Instant",
        ]
        hash = {"from_attribute": False, "removal_dollar_sign": True}
        for xpath in xpaths:
            txt = self._field_value(xpath, hash)
            if len(txt) > 0:
                return txt

        return ""

    def _modified_date_dt(self):
        return date.today().strftime("%Y-%m-%dT%H:%M:%SZ")

    def _resource_type(self):
        desc = arcpy.Describe(self.geofile)
        data_type = desc.dataType
        if data_type == "RasterDataset":
            return "Raster data"

        if data_type == "ShapeFile":
            shape_mapping = {
                "polyline": "Line data",
                "polygon": "Polygon data",
                "point": "Point data",
            }
            shape = desc.shapeType.lower()
            return shape_mapping.get(shape, "")
        return ""

    def _format(self):
        desc = arcpy.Describe(self.geofile)
        data_type = desc.dataType
        if data_type == "RasterDataset":
            return "GeoTIFF"
        if data_type == "ShapeFile":
            return "Shapefile"
        return ""

    def _resp_tag_value(self, name, node):
        path_info_dic = self.resp_elements[name]
        path = path_info_dic.get("path")
        hash = {"from_attribute": False, "removal_dollar_sign": False}
        return self._field_value(path, hash, node)

    def _resp_row(self, node):
        role = node.find("./role/RoleCd").get("value")
        if role:
            keys = self.resp_elements.keys()
            row = [
                self._resp_tag_value(name, node) if name in keys else ""
                for name in self.resp_headers
            ]
            self._update_resp_col(row, "geofile", self.geofile)
            self._update_resp_col(row, "role", role)
            return row

        return None

    def _update_main_col(self, row, header_name, value):
        index = self.main_headers.index(header_name)
        row[index] = value

    def _update_resp_col(self, row, header_name, value):
        index = self.resp_headers.index(header_name)
        row[index] = value

    def _resp_rows_from_path(self, path):
        nodes = self.root.findall(path)
        if nodes:
            rows = [self._resp_row(node) for node in nodes]
            return [row for row in rows if row is not None]

        return []

    #### responsible party csv data ######
    # To ensure a geofile has at least one "006" and one "010" roles in repsponsible parties
    def _add_rows_with_defalut_roles(self, rows):
        defalut_role_codes = ["010", "006"]
        identical_row_codes = self._codes(rows, "role")
        for code in defalut_role_codes:
            if code not in identical_row_codes:
                rows.append(self._add_role(code))

    def _add_role(self, code):
        new_row = ["" for header in self.resp_headers]
        self._update_resp_col(new_row, "role", code)
        self._update_resp_col(new_row, "geofile", self.geofile)
        return new_row

    def _codes(self, rows, name):
        index = self.resp_headers.index(name)
        codes = [row[index] for row in rows]
        code_set = set(codes)
        return list(code_set)

    def rm_dollar_sign(self, str):
        return str.replace("$", "_")


################################################################################################
#                             2. constant variables                                                        #
################################################################################################
ls_gbl_resourceClass_sm = {
    "Collections",
    "Datasets",
    "Imagery",
    "Maps",
    "Web services",
    "Websites",
    "Other",
}

# Main CSV File headers: the order of this array define the order the main CSV file
main_headers = [
    "arkid",
    "geofile",
    "dct_title_s_o",
    "dct_title_s",
    "dct_alternative_sm_o",
    "dct_alternative_sm",
    "dct_issued_s_o",
    "dct_issued_s",
    "summary_o",
    "summary",
    "dct_description_sm_o",
    "dct_description_sm",
    "dcat_theme_sm_o",
    "dcat_theme_sm",
    "dct_subject_sm_o",
    "dct_subject_sm",
    "dcat_keyword_sm_o",
    "dcat_keyword_sm",
    "dct_spatial_sm_o",
    "dct_spatial_sm",
    "dct_temporal_sm_o",
    "dct_temporal_sm",
    "gbl_indexYear_im",
    "gbl_dateRange_drsim",
    "dct_language_sm_o",
    "dct_language_sm",
    "gbl_resourceClass_sm",
    "gbl_resourceType_sm_o",
    "gbl_resourceType_sm",
    "dct_format_s_o",
    "dct_format_s",
    "pcdm_memberOf_sm_o",
    "pcdm_memberOf_sm",
    "dct_relation_sm",
    "dct_isPartOf_sm",
    "dct_source_sm",
    "dct_isVersionOf_sm",
    "dct_replaces_sm",
    "dct_isReplacedBy_sm",
    "dct_accessRights_s",
    "rights_general_o",
    "rights_general",
    "rights_legal_o",
    "rights_legal",
    "rights_security_o",
    "rights_security",
    "rightsHolder",
    "dct_license_sm",
    "gbl_suppressed_b",
    "gbl_georeferenced_b",
    "gbl_mdModified_dt_o",
    "gbl_mdModified_dt",
    "gbl_displayNote_sm",
    "dct_identifier_sm",
    "doc_zipfile_path",
]


# 1) Keys are used as CSV headers of the main CSV file, header sequence is from CSV_HEADER_TRANSFORM
# 2) An element with "keys" in it's path has multiple occurrences in ISO19139
main_elements = {
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

resp_headers = [
    "arkid",
    "geofile",
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

UCB_RESPONSIBLE_PARTY = {
    "organization": "UC Berkeley Library",
    "email": "eart@library.berkeley.edu",
    "address_Type": "Both",
    "address": "50 McCone Hall",
    "city": "Berkeley",
    "state": "CA",
    "zip": "94720-6000",
    "country": "UNITED STATES",
}

resp_elements = {
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


################################################################################################
#                                 3. set up                                                    #
################################################################################################

# initial csv infomation to class variables
GeoFile.resp_headers = resp_headers
GeoFile.resp_elements = resp_elements
GeoFile.main_headers = main_headers
GeoFile.main_elements = main_elements

# 1. Please provide your local log file path
logfile = r"C:\process_data\log\process.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 2. Please provide source data directory path
source_batch_directory_path = r"C:\process_data\source_batch"

# 3. please provide result directory path:
csv_files_directory_path = r"C:\process_data\csv_files"


################################################################################################
#                                4. Run                                                       #
# Example:
# input directory paths:
#      source_batch_directory_path = r"C:\process_data\source_batch"
#      csv_files_directory_path = r"C:\process_data\csv_files"
# output csv files:
#     C:\process_data\csv_files\main.csv
#     C:\process_data\csv_files\resp.csv
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


script_name = "2 - batch_export_csv.py"
output(f"***starting  {script_name}")

if verify_setup([], [source_batch_directory_path, csv_files_directory_path]):
    batch = BatchExportCsv(
        source_batch_directory_path, csv_files_directory_path, logging
    )
    batch.main_csv()
    batch.resp_csv()
    output(f"***completed {script_name}")
