import arcpy
from arcpy import metadata as md
import os
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
import csv
import re
from datetime import date
from typing import List


################################################################################################
#                             1. class                                                         #
################################################################################################


class BatchExportCsv(object):
    def __init__(self, workspace_dir, results_dir, logging):
        self.logging = logging
        self.workspace_dir = workspace_dir
        self.geofile_paths = self._geofile_paths()
        self.dir = results_dir

    def main_csv(self):
        file = self._filename(self.dir, "main")
        rows = [
            GeoFile(geofile_path, self.logging).main_row()
            for geofile_path in self.geofile_paths
        ]
        self._write_csv(file, GeoFile.main_headers, rows)

    def resp_csv(self):
        file = self._filename(self.dir, "resp")
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

    def _filename(self, dir, prefix):
        basename = os.path.basename(self.workspace_dir)
        name = f"{prefix}_{basename}.csv"
        return os.path.join(dir, name)

    ## common methods to be moved
    def _file_paths(self, ext) -> List:
        return [
            os.path.join(dirpath, filename)
            for dirpath, dirs, filenames in os.walk(self.workspace_dir)
            for filename in filenames
            if filename.endswith(ext)
        ]

    ## common functions end


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
            self._main_column(header.strip()[:-2]) if header.endswith("_o") else ""
            for header in self.main_headers
        ]
        self._update_row(row, self.main_headers, "geofile", self.geofile)

        return row

    def resp_rows(self):
        rows = []
        citation_rows = self._resp_rows_from_path(
            "./dataIdInfo/idCitation/citRespParty"
        )
        rows.extend(citation_rows)

        idpoc_rows = self._resp_rows_from_path("./dataIdInfo/idPoC")
        rows.extend(idpoc_rows)

        self._add_defalut_role("010", rows)
        self._add_defalut_role("006", rows)

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

    # TODO: make functions the same format
    def _main_column(self, tag):
        tag_functions = {
            "collectionTitle": self._collection_title,
            "temporalCoverage": self._temporalCoverage,
            "resourceType": self._resource_type,
            "modified_date_dt": self._modified_date_dt,
        }
        fun = tag_functions.get(tag, None)
        if fun:
            return fun()
        else:
            val = self._tag_value(tag).strip()
            if tag == "topicISO":  # check import later
                val = val.strip("0")
            return val

    def _tag_value(self, tag):
        keys = self.main_elements.keys()
        if tag in keys:
            dic = self.main_elements[tag]
            from_attribute = dic.get("attribute")
            path = dic.get("path")
            return self._field_value(path, from_attribute)

        return ""

    def _node_value(self, node, from_attribute):
        tags = re.compile("<.*?>")
        if node is not None and len(list(node)) == 0:  # leaf node
            txt = node.get("value") if from_attribute else node.text
            if txt:
                return re.sub(tags, "", txt.strip())

        return ""

    def _field_value(self, path, from_attribute, parent_node=None):
        if parent_node is None:
            parent_node = self.root

        content = ""
        nodes = parent_node.findall(path)
        for node in nodes:
            value = self._node_value(node, from_attribute)
            if len(value) > 0:
                content += f"{value}$"

        return content.strip().rstrip("$").strip()

    def _collection_title(self):
        coll_title = self._field_value("dataIdInfo/idCitation/collTitle", False)
        if coll_title:
            return coll_title

        code = self._field_value("dataIdInfo/aggrInfo/assocType/AscTypeCd", True)
        if code == "002":
            res_title = self._field_value(
                "dataIdInfo/aggrInfo/aggrDSName/resTitle", False
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

        for xpath in xpaths:
            txt = self._field_value(xpath, False)
            if len(txt) > 0:
                return txt

        return ""

    def _modified_date_dt(self):
        return date.today().strftime("%Y%m%d")

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

    def _resp_tag_value(self, name, node):
        path_info_dic = self.resp_elements[name]
        path = path_info_dic.get("path")
        return self._field_value(path, False, node)

    def _resp_row(self, node):
        role = node.find("./role/RoleCd").get("value")
        if role:
            keys = self.resp_elements.keys()
            row = [
                self._resp_tag_value(name, node) if name in keys else ""
                for name in self.resp_headers
            ]
            self._update_row(row, self.resp_headers, "role", role)
            self._update_row(row, self.resp_headers, "geofile", self.geofile)
            return row

        return None

    def _update_row(self, row, headers, header_name, value):
        index = headers.index(header_name)
        row[index] = value

    def _resp_rows_from_path(self, path):
        nodes = self.root.findall(path)
        if nodes:
            rows = [self._resp_row(node) for node in nodes]
            return [row for row in rows if row is not None]

        return []

    #### responsible party csv data ######
    # To ensure a geofile has at least one "006" and one "010" roles in repsponsible parties
    def _add_defalut_role(self, role_code, rows):
        index = self.resp_headers.index("role")
        role_codes = [row[index] for row in rows]
        if role_code not in role_codes:
            new_row = [""] * 18
            self._update_row(new_row, self.resp_headers, "role", role_code)
            self._update_row(new_row, self.resp_headers, "geofile", self.geofile)
            rows.append(new_row)

    def doc_name(self):
        pass


################################################################################################
#                             2. constant variables                                                        #
################################################################################################
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
    "pcdm_memberOf_sm_o",
    "pcdm_memberOf_sm",
    "dct_relation_sm",
    "dct_isPartOf_sm",
    "isMemberOf",
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
logfile = r"Y:\GeoBlacklight\testing\Log\vector_2023-08-22.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 2. Please provide source data directory path here
source_batch_path = r"Y:\GeoBlacklight\testing\test_vector_source_2023-08"

# 3. please provide result directory path - a place to save main csv and resp csv files:
#   attention: Please do not use the original batch directory path or projected directory path
#              Suggest to provide a specific directory path for result files
output_directory = r"Y:\GeoBlacklight\testing\test_vector_csv_2023-08"


################################################################################################
#                                4. Run options                                                #
################################################################################################
def output(msg):
    logging.info(msg)
    print(msg)


output(f"*** starting 'batch_export_csv'")

batch = BatchExportCsv(source_batch_path, output_directory, logging)
batch.main_csv()
batch.resp_csv()

output(f"*** end 'batch_export_csv'")
