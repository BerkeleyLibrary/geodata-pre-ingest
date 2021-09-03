
from datetime import datetime



CSV_HEADER_COMMON = ["format_s","arkid","filename"]

# Not very column in CSV has a valuefron ESRI ISO metadata
# Elements in below array are ordered as it is in the main csv file;
# These columns are extracrted from ESRI ISO XML
# "_s" - single value column
CSV_HEADER_TRANSFORM = [
         "title_s",
         "alternativeTitle",
         "description",
         "language",
         "subject",
         "date_s",
         "spatialSubject",
         "collectionTitle",
         "rights_general",
         "rights_legal",
         "rights_security",
         "modified_date_dt",
         "topicISO",
         "keyword",
         "temporalCoverage"]

CSV_HEADER_EMPTY = [
         "resourceClass",
         "resourceType",
         "solrYear_s",
         "dateRange_drsim",
         "relation",
         "isPartOf",
         "source",
         "isVersionOf",
         "replaces",
         "isReplacedBy",
         "rightsHolder",
         "license",
         "accessRights_s",
         "suppressed_b",
         "georeferenced_b"]

# mapping between csv header and geoblacklight elements
CSV_HEADER_COLUMNS = {
            "format_s": "dct_format_s",
            "title_s" : "dct_title_s",
            "alternativeTitle" : "dct_alternative_sm",
            "description" : "dct_description_sm",
            "language" : "dct_language_sm",
            "subject" : "dct_subject_sm",
            "topicISO" : "dcat_theme_sm",
            "keyword" : "dcat_keyword_sm",
            "temporalCoverage" : "dct_temporal_sm",
            "date_s" : "dct_issued_s",
            "solrYear_s" : "gbl_indexYear_i",
            "dateRange_drsim" : "gbl_dateRange_drsim",
            "relation" : "dct_relation_sm",
            "spatialSubject" : "dct_spatial_sm",
            "collectionTitle" : "pcdm_memberOf_sm",
            "isPartOf" : "dct_isPartOf_sm",
            "source" : "dct_source_sm",
            "isVersionOf" : "dct_isVersionOf_sm",
            "replaces" : "dct_replaces_sm",
            "isReplacedBy" : "dct_isReplacedBy_sm",
            "license" : "dct_license_sm",
            "accessRights_s" : "dct_accessRights_s",
            "modified_date_dt" : "gbl_mdModified_dt",
            "resourceClass" : "gbl_resourceClass_sm",
            "suppressed_b" : "gbl_suppressed_b",
            "georeferenced_b" : "gbl_georeferenced_b"
            }
# all columns in main header
# CSV_HEADER_COLUMNS = {
#             "format_s": "dct_format_s",
#             "title_s" : "dct_title_s",
#             "alternativeTitle" : "dct_alternative_sm",
#             "description" : "dct_description_sm",
#             "language" : "dct_language_sm",
#             # "originator" : "dct_creator_sm",  - from responsible parties
#             # "publisher" : "dct_publisher_sm", - from responsible parties
#             "subject" : "dct_subject_sm",
#             "topicISO" : "dcat_theme_sm",
#             "keyword" : "dcat_keyword_sm",
#             "temporalCoverage" : "dct_temporal_sm",
#             "date_s" : "dct_issued_s",
#             "solrYear_s" : "gbl_indexYear_i",
#             "dateRange_drsim" : "gbl_dateRange_drsim",
#             "relation" : "dct_relation_sm",
#             "spatialSubject" : "dct_spatial_sm",
#             "collectionTitle" : "pcdm_memberOf_sm",
#             "isPartOf" : "dct_isPartOf_sm",
#             "source" : "dct_source_sm",
#             "isVersionOf" : "dct_isVersionOf_sm",
#             "replaces" : "dct_replaces_sm",
#             "isReplacedBy" : "dct_isReplacedBy_sm",
#             # "rights" : "dct_rights_sm",  - from CSV_HEADER_COLUMNS_RIGHTS
#             # "rightsHolder" : "dct_rightsHolder_sm",  - from responsible parties
#             "license" : "dct_license_sm",
#             "accessRights_s" : "dct_accessRights_s",
#             "modified_date_dt" : "gbl_mdModified_dt",
#             "resourceClass" : "gbl_resourceClass_sm",
#             "suppressed_b" : "gbl_suppressed_b",
#             "georeferenced_b" : "gbl_georeferenced_b"
#             }

# Combine three below three columns to "dct_rights_sm" in Geoblacklight
CSV_HEADER_COLUMNS_RIGHTS = [ "rights_general","rights_legal","rights_security",]


CSV_HEADER_RESPONSIBLE_PARTY = [ "from",
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
         "instruction"]

UCB_RESPONSIBLE_PARTY = {
    "organization":"UC Berkeley Library",
    "email":"eart@library.berkeley.edu",
    "address_Type":"Both",
    "address": "50 McCone Hall",
    "city":"Berkeley",
    "state": "CA",
    "zip":"94720-6000",
    "country":"UNITED STATES"
}

G_SM = [
             "alternativeTitle" ,
             "description" ,
             "language" ,
             "subject" ,
             "topicISO" ,
             "keyword" ,
             "temporalCoverage" ,
             "relation" ,
             "spatialSubject",
             "collectionTitle",
             "isPartOf" ,
             "source" ,
             "isVersionOf" ,
             "replaces" ,
             "isReplacedBy" ,
             "license" ,
             "resourceClass"
]

PROCESS_SUB_DIRECTORY = ["Results","Source","Work"]
RESULT_DIRECTORY_PARENTS =  ["precessed_result","final_result"]
RESULT_DIRECTORY = ["GeoFiles for Downloading","GeoFiles for Geoserver(Projected)","Geoblacklight Json Files","The CSV File","ISO19139 Metadata Files","Updated CSV Files"]

PREFIX = "berkeley-"
INSTITUTION = "Berkeley"
GEOBLACKLGITH_VERSION = "v2"

HOSTS = {
          "geoserver_host":"geoservices.lib.berkeley.edu",
          "ISO139": "\"http://www.isotc211.org/schemas/2005/gmd/\":\"https://spatial.lib.berkeley.edu/metadata/",
          "download": "\"http://schema.org/downloadUrl\":\"https://spatial.lib.berkeley.edu/public/",
          "wfs":"\"http://www.opengis.net/def/serviceType/ogc/wfs\":\"https://geoservices.lib.berkeley.edu/geoserver/wfs\",",
          "wms":"\"http://www.opengis.net/def/serviceType/ogc/wms\":\"https://geoservices.lib.berkeley.edu/geoserver/wms\","
        }

HOSTS_SECURE = {
              	"geoserver_host":"geoservices-secure.lib.berkeley.edu",
                "ISO139": "\"http://www.isotc211.org/schemas/2005/gmd/\":\"https://spatial.lib.berkeley.edu/metadata/",
              	"download": "\"http://schema.org/downloadUrl\":\"https://spatial.lib.berkeley.edu/UCB/",
                "wfs":"\"http://www.opengis.net/def/serviceType/ogc/wfs\":\"https://geoservices-secure.lib.berkeley.edu/geoserver/wfs\",",
              	"wms":"\"http://www.opengis.net/def/serviceType/ogc/wms\":\"https://geoservices-secure.lib.berkeley.edu/geoserver/wms\","
        }


############# Messages for ArcCatalog ######

WARNING_ARK_MAPFILE_NUMBER_DIFFERENT = "**** Arks ({0}), work directory geofiles ({1}), source directory geofiles ({2}), Please make sure that the numbers of geofiles and arks are the same. ****"

ARKS_HAVE_BEEN_ASSIGNED = "**** Have Ark ids been already assigned ? ****"

ARKS_HAVE_BEEN_RE_ASSIGNED = "**** Arks have been re-assinged! ****"

SUCCESSFUL_ASSINGED_ARKS = "Successfully assigned {0} ark ids !"

NOT_SINGLE_MAP_FILES = "**** Directory {0} has less or more than one Map files ****"

INCORRECT_PROJECTION = "**** {0} - projection is incorrect ***"

PROJECT_SUCCEEDED = "**** {0} - is projected."

PROJECT_FAILED = "**** Cannot project shapefile '{0}'."

FAILED_TO_ASSIGN_ARKS = "Failed to assign ark ids !"

ARK_NOT_ASSIGNED = "*** No ark assigned yet: {0} ***"

MISSING_FILES = "*** Missing Files: "

ABNORMAL_FILES = "*** Files do not belong to any GeoTIFF/Shapefile: "

PYRIMID_ADDED = "*** Pyrimid added to these GeoTIFFs: "

PYRIMID_NEEDED = "*** Pyrimid needed for these GeoTIFFs: "

FGDC_TO_ISO = "*** {0} - is in FGDC standard, it has been transfered to ESRI ISO. "

NOT_ESRI_ISO = "*** {0} -  A metadata file detected, but it is not in ESRI ISO METADATA STANDARd, PLEASE CHECK. "

NO_ESRIISO_XML = "***  No ESRIISO metadata file: {0} "

New_ESRIIO_XML = "*** New ESRIISO metedata file created: {0}"

SAVE_TO_CSV = "***  CSV files exported: {0}."

OLD_ARK_FILES_REMOVED = "*** Old Ark files are removed: "

MISSING_CVS_VALUES = '*** Found some invalid metadata values in the CSV file'

INCORRECT_ROLE_FOR_INDIVIDUAL = 'Line {2}: {0} - In ResponsibleParty CSV file, role "{1}" should not have individual. Only role 6 could have individual'

MISSING_ROLE =  'Line {2}: Responsible party, {0} - missing "{1}" role'

EMPTY_ROLE =  'Line {2}:  arkid - {0}: Requred role {1} has no value'

PASS_PROJECTION_VALIDATION = "*** All projections are valid ***"

PASS_CSV_VALIDATION = "*** The updated CSV files are valid ***"

FILES_NOT_MOVED = "*** Files not moved to work batch - name not good,please check, or move manually."

# keys are CSV headers of responsible party csv file
responsibleparty_elements = {
    "contact_name": {
        "path": "rpIndName",
        "type": "string"},

    "position": {
        "path": "rpPosName",
        "type": "string"},

    "organization": {
        "path": "rpOrgName",
        "type": "string"},


    "contact_info": {
        "path": "rpCntInfo",
        "type": "string"},

    "email": {
        "path": "rpCntInfo/cntAddress/eMailAdd",
        "type": "string"},

    "address_type": {
        "path": "rpCntInfo/cntAddress",
        "type": "attribute",
        "key": "addressType",
        "values": [("postal", "postal"),
                   ("physical", "physical"),
                   ("both", "both")]},

    "address": {
        "path": "rpCntInfo/cntAddress/delPoint",
        "type": "string"
        },

    "city": {
        "path": "rpCntInfo/cntAddress/city",
        "type": "string"},

    "state": {
        "path": "rpCntInfo/cntAddress/adminArea",
        "type": "string"},

    "zip": {
        "path": "rpCntInfo/cntAddress/postCode",
        "type": "string"},

    "country": {
        "path": "rpCntInfo/cntAddress/country",
        "type": "string"},

    "phone_no": {
        "path": "rpCntInfo/voiceNum",
        "type": "string"},

    "fax_no": {
        "path": "rpCntInfo/faxNum",
        "type": "string"},

    "hours": {
        "path": "rpCntInfo/cntHours",
        "type": "string"},

    "instruction": {
        "path": "rpCntInfo/cntInstr",
        "type": "string"}

	}

# ESRI ISO metadata element information:
# 1) used as mapping for storing ESRI ISO metadata to object bfore exporting to CSV;
# 2) used as mapping for storing csv columns to object before transforming to ESRI ISO
# 3) key will be the same as CSV_HEADER_TRANSFORM. Since dictionary in python cannot keep the order, key sequence of CSV_HEADER_TRANSFORM will be the order of headers of the main CSV file
# 4) only elements with "key_path":True will have multiple elements in ISO19139
transform_elements = {

    "title_s": {
        "path": "dataIdInfo/idCitation/resTitle",
        "type": "string"},

    "alternativeTitle": {
        "path": "dataIdInfo/idCitation/resAltTitle",
        "type": "string"},

    "description": {
        "path": "dataIdInfo/idAbs",
        "type": "string",
        "html": True},

    "language": {
        "path": "dataIdInfo/dataLang/languageCode",
        "attribute": True,
        "type": "string"},

    "subject": {
        "path": "dataIdInfo/themeKeys/keyword",
        "key_path":True,
        "type": "string"},

    "date_s": {
        "path": "dataIdInfo/idCitation/date/pubDate",
        "type": "string"},

    "spatialSubject": {
        "path": "dataIdInfo/placeKeys/keyword",
        "key_path": True,
        "type": "string"},

    "rights_general": {
        "path": "dataIdInfo/resConst/Consts/useLimit",
        "html": True,
        "type": "string"},

    "rights_legal": {
        "path": "dataIdInfo/resConst/LegConsts/useLimit",
        "type": "string"},

    "rights_security": {
        "path": "dataIdInfo/resConst/SecConsts/useLimit",
        "type": "string"},

    "modified_date_dt": {
        "path": "Esri/ModDate",
        "type": "date",
        "default": datetime.today().strftime('%Y%m%d')},

    "topicISO": {
        "path": "dataIdInfo/tpCat/TopicCatCd",
        "attribute": True,
        "key_path": True,
        "type": "string"},

    "keyword": {
        "path": "dataIdInfo/searchKeys/keyword",
        "key_path": True,
        "type": "string"
        },


    "temporalCoverage": {
        "path": "dataIdInfo/tempKeys/keyword",
        "key_path": True,
        "type": "string"},

    "collectionTitle": {
        "path":'dataIdInfo/idCitation/collTitle',
        "type": "string"
        }

    }


# required elements - header names
CSV_REQUIRED_HEADERS = ["title_s","solrYear_s","accessRights_s","modified_date_dt"]

resourceType = [
        "LiDAR",
        "Line data",
        "Mesh data",
        "Multi-spectral data",
        "Oblique photographs",
        "Point cloud data",
        "Point data",
        "Polygon data",
        "Raster data",
        "Satellite imagery",
        "Table data",
        "Aerial photographs",
        "Aerial views",
        "Aeronautical charts",
        "Armillary spheres",
        "Astronautical charts",
        "Astronomical models",
        "Atlases",
        "Bathymetric maps",
        "Block diagrams",
        "Bottle-charts",
        "Cadastral maps",
        "Cartographic materials",
        "Cartographic materials for people with visual disabilities",
        "Celestial charts",
        "Celestial globes",
        "Census data",
        "Children's atlases",
        "Children's maps",
        "Comparative maps",
        "Composite atlases",
        "Digital elevation models",
        "Digital maps",
        "Early maps",
        "Ephemerides",
        "Ethnographic maps",
        "Fire insurance maps",
        "Flow maps",
        "Gazetteers",
        "Geological cross-sections",
        "Geological maps",
        "Globes",
        "Gores (Maps)",
        "Gravity anomaly maps",
        "Index maps",
        "Linguistic atlases",
        "Loran charts",
        "Manuscript maps",
        "Mappae mundi",
        "Mental maps",
        "Meteorological charts",
        "Military maps",
        "Mine maps",
        "Miniature maps",
        "Nautical charts",
        "Outline maps",
        "Photogrammetric maps",
        "Photomaps",
        "Physical maps",
        "Pictorial maps",
        "Plotting charts",
        "Portolan charts",
        "Quadrangle maps",
        "Relief models",
        "Remote-sensing maps",
        "Road maps",
        "Statistical maps",
        "Stick charts",
        "Strip maps",
        "Thematic maps",
        "Topographic maps",
        "Tourist maps",
        "Upside-down maps",
        "Wall maps",
        "World atlases",
        "World maps",
        "Worm's-eye views",
        "Zoning maps"
]

isoTopic = {
            "001":"Farming",
            "002":"Biota",
            "003":"Boundaries",
            "004":"Climatology, Meteorology and Atmosphere",
            "005":"Economy",
            "006":"Elevation",
            "007":"Environment",
            "008":"Geoscientific Information",
            "009":"Health",
            "010":"Imagery and Base Maps",
            "011":"Intelligence and Military",
            "012":"Inland Waters",
            "013":"Location",
            "014":"Oceans",
            "015":"Planning and Cadastral",
            "016":"Society",
            "017":"Structure",
            "018":"Transportation",
            "019":"Utilities and Communication"
            }
raster_exts = [".tif",".aux",".tfw",".prj",".tif.ovr"]
vector_exts = [".cpg",
        ".dbf",
        ".prj",
        ".dbf"
        ".sbn",
        ".sbx",
        ".shp",
        ".shp.xml",
        ".shx"]

# not used in code, for future reference
# geoblacklight_rolecodes = ["006","010"]
# other_rolecodes = ["001","002","003","004","005","007","008","009","011"]
# ISO 19139 role codes
# ("resource provider", "001"),
#                    ("custodian", "002"),
#                    ("owner", "003"),
#                    ("user", "004"),
#                    ("distributer", "005"),
#                    ("originator", "006"),
#                    ("point of contact", "007"),
#                    ("principal investigator", "008"),
#                    ("processor", "009"),
#                    ("publisher", "010"),
#                    ("author", "011")]

# transform_elements = {
#
#     "title_s": { #1
#         "path": "dataIdInfo/idCitation/resTitle",
#         "type": "string"},
#
#     "alternativeTitle": { #2
#         "path": "dataIdInfo/idCitation/resAltTitle",
#         "type": "string"},
#
#     "description": { #3
#         "path": "dataIdInfo/idAbs",
#         "type": "string"},
#
#     "language": { #4
#         "path": "dataIdInfo/dataLang/languageCode",
#         "attribute": True,
#         "type": "string"},
#     # 5 - originator
#     # 6 - Publisher
#     "subject": { #7
#         "path": "dataIdInfo/themeKeys/keyword",
#         "type": "string"},
#
#     "date_s": { #8
#         "path": "dataIdInfo/idCitation/date/pubDate",
#         "type": "string"},
#
#     "spatialSubject": { # 9
#         "path": "dataIdInfo/placeKeys/keyword",
#         "type": "string"},
#
#    # 10 -collectionTitle
#     # "collectionTitle_1": {  # complicated
#     #     "path": "./dataIdInfo/idCitation/collTitle",   # different attributes
#     #     "type": "string"},
#     #
#     # "collectionTitle_2": {  # complicated
#     #     "path": "./dataIdInfo/idCitation/collTitle",   # different attributes
#     #     "type": "string"},
#
#     "rights_general": { # 11
#         "path": "dataIdInfo/resConst/Consts/useLimit",
#         "type": "string"},  # how to mapping to geoblacklight schema?
#
#     "rights_legal": { # 12
#         "path": "dataIdInfo/resConst/LegConsts",
#         "type": "string"},  # how to mapping to geoblacklight schema?
#
#     "rights_security": { # 13
#         "path": "dataIdInfo/resConst/SecConsts",
#         "type": "string"},  # how to mapping to geoblacklight schema?
#
#     "modified_date_dt": { # 14
#         "path": "Esri/ModDate",
#         "type": "date"},
#
#     # Q: will this a list?
#     "topicISO": { # 15
#         "path": "dataIdInfo/TopicCatCd", # Q: from value?
#         "type": "string"},
#
#     "keyword": { # 16
#         "path": "dataIdInfo/searchKeys/keyword",
#         "type": "string"
#         },
#
#     # Q: what will be other two type of path data look like
#     "temporalCoverage": { # 17
#         # "path": "dataIdInfo/tempKeys/keyword;dataIdInfo/dataExt/tempEle/TempExtent/exTemp/TM_Period;dataIdInfo/dataExt/tempEle/TempExtent/exTemp/TM_Instant",
#         "path": "dataIdInfo/tempKeys/keyword",
#         "type": "string"}
#
#
#     }

#  Look for value in "/dataIdInfo/tempKeys/keyword", if found take the value; if not found, then check value in "/dataIdInfo/dataExt/tempEle/TempExtent/exTemp/TM_Period" and "/dataIdInfo/dataExt/tempEle/TempExtent/exTemp/TM_Instant"
