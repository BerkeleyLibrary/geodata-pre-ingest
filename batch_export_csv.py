import arcpy
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
        raws = [GeoFile(geofile_path).main_row() for geofile_path in self.geofile_paths]
        self._write_csv(file, GeoFile.main_headers, raws)

    def resp_csv(self):
        file = self._filename(self.dir, "resp")
        rows = []
        for geofile_path in self.geofile_paths:
            resp_rows = GeoFile(geofile_path).resp_rows()
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

    def _write_csv(self, file, header, raws):
        with open(file, "w") as csvfile:
            csvWriter = csv.writer(csvfile)
            csvWriter.writerow([h for h in header])
            for raw in raws:
                csvWriter.writerow([col if col else "" for col in raw])

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

    def __init__(self, geofile):
        self.geofile = geofile
        self.root = self._root()

    def main_row(self):
        if not self.root:
            return [""] * 52

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
        xml_file = f"{self.geofile}.xml"
        if Path(xml_file).is_file():
            tree = ET.parse(xml_file)
            return tree.getroot()

        return None

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
    "title_s_o",
    "title_s",
    "alternativeTitle_o",
    "alternativeTitle",
    "date_s_o",
    "date_s",
    "summary_o",
    "summary",
    "description_o",
    "description",
    "topicISO_o",
    "topicISO",
    "subject_o",
    "subject",
    "keyword_o",
    "keyword",
    "spatialSubject_o",
    "spatialSubject",
    "temporalCoverage_o",
    "temporalCoverage",
    "solrYear",
    "dateRange_drsim",
    "language_o",
    "language",
    "resourceClass",
    "resourceType_o",
    "resourceType",
    "collectionTitle_o",
    "collectionTitle",
    "relation",
    "isPartOf",
    "isMemberOf",
    "source",
    "isVersionOf",
    "replaces",
    "isReplacedBy",
    "accessRights_s",
    "rights_general_o",
    "rights_general",
    "rights_legal_o",
    "rights_legal",
    "rights_security_o",
    "rights_security",
    "rightsHolder",
    "license",
    "suppressed_b",
    "georeferenced_b",
    "modified_date_dt_o",
    "modified_date_dt",
]


# 1) Keys are used as CSV headers of the main CSV file, header sequence is from CSV_HEADER_TRANSFORM
# 2) Elements with "key_path":True are supposed to have multiple occurrences in ISO19139
main_elements = {
    "title_s": {"path": "dataIdInfo/idCitation/resTitle", "type": "string"},
    "alternativeTitle": {"path": "dataIdInfo/idCitation/resAltTitle", "type": "string"},
    "summary": {"path": "dataIdInfo/idPurp", "type": "string"},
    "description": {"path": "dataIdInfo/idAbs", "type": "string", "html": True},
    "language": {
        "path": "dataIdInfo/dataLang/languageCode",
        "attribute": True,
        "type": "string",
    },
    "subject": {
        "path": "dataIdInfo/themeKeys/keyword",
        "key_path": True,
        "type": "string",
    },
    "date_s": {"path": "dataIdInfo/idCitation/date/pubDate", "type": "string"},
    "spatialSubject": {
        "path": "dataIdInfo/placeKeys/keyword",
        "key_path": True,
        "type": "string",
    },
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
    "modified_date_dt": {
        "path": "Esri/ModDate",
        "type": "date",
        "default": date.today().strftime("%Y%m%d"),
    },
    "topicISO": {
        "path": "dataIdInfo/tpCat/TopicCatCd",
        "attribute": True,
        "key_path": True,
        "type": "string",
    },
    "keyword": {
        "path": "dataIdInfo/searchKeys/keyword",
        "key_path": True,
        "type": "string",
    },
    "temporalCoverage": {
        "path": "dataIdInfo/tempKeys/keyword",
        "key_path": True,
        "type": "string",
    },
    "collectionTitle": {"path": "dataIdInfo/idCitation/collTitle", "type": "string"},
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

# Log file
logfile = r"D:/Log/shpfile_projection.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 1. please update directory information here
workspace_directory = r"D:/test1/tijuana_workspace"

# 2. please update directory information here
output_directory = r"D:/results"


################################################################################################
#                                4. Run options                                                #
################################################################################################
logging.info(f"*** starting 'batch_export_csv'")

batch = BatchExportCsv(workspace_directory, output_directory, logging)
batch.main_csv()
batch.resp_csv()

logging.info(f"*** end 'batch_export_csv'")
