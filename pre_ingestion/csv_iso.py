#!/usr/bin/python
import os
import xml.etree.ElementTree as ET
from shutil import copyfile
import re
import traceback
import par
from geo_helper import GeoHelper
if os.name == "nt":
    import arcpy

# In work directory: this if for writing to a single geofile
# 1. Copy eariiso xml file to a backup file
# 2. Create an ESRI ISO with slim ESRI ISO and export metadata from GeoFile to this ESRI ISO file: mostly techincal, lineage matadata etc.  - It requires to export to the original ESRI ISO XML file (.tif.xml, .shp.xml)
# 3. Copyt the ESRI ISO metadata file from 2. to  "_temp.tif.xml" or "_temp.shp.xml"
# 4. Wrote both main csv and responsible csv information to the temp file in #3
# 5. Tranform the temp file to iso19139 metadata through arcpy
# 6. Save one iso19139 file to work - iso19139 directory with subdirectory (ark name)
# 7. Save one iso19139 file to the ource geofile directory - required by Susan
# 8. Copy the backed-up ESRI ISO xml from 1) to the original ESRI ISO file ".tif.xml" or ".shp.xml"
# 9. Remove the temp ESRI ISO xml file: "_temp.tif.xml" or "_temp.shp.xml"
# 10.New workflow to ESRI ISO: 1) save resposilbe party with role "006", "010" to './dataIdInfo/idCitation/citRespParty'
                  #2) other roles related responsilbe parties to  './dataIdInfo/idPoC'

class CsvIso(object):
    def __init__(self,csv_obj,process_path):
        self.main_csv_raw = csv_obj.__dict__["_main_csv_raw"]
        self.arkid = self.main_csv_raw["arkid"].strip()
        self.geofile = self.main_csv_raw["filename"].strip()
        self.ext = os.path.splitext(self.geofile)[1].strip().lower()
        self.resp_parties_citation_raws = []
        self.resp_parties_idoc_raws = []
        self._seperate_resp_parties(csv_obj.__dict__["_resp_parties_raws"])

        self.process_path = process_path
        self.root = None

    def create_iso19139_file(self):
        # ESRI ISO file names
        ext = self.ext
        esriiso_file = self.geofile.replace(ext,"{0}.xml".format(ext))
        esriiso_backup_file = self.geofile.replace(ext,"_backup{0}.xml".format(ext))
        esriiso_temp_file = self.geofile.replace(ext,"_temp{0}.xml".format(ext))

        # prepare new ESRIISO .tif.xml or .shp.xml  file
        def backup_and_remove_original_esriiso_file():
            if os.path.isfile(esriiso_file):
                copyfile(esriiso_file,esriiso_backup_file)
                GeoHelper.rm_file(esriiso_file)

        # create an ESRI ISO xml from slim ESRI ISO template
        # A full ESIR ISO cannot be generated, a tick is to copy a slim ESRI ISO template, then export metadata of this geofile to to it's own metadata file.  https://desktop.arcgis.com/en/arcmap/10.3/tools/conversion-toolbox/import-metadata.htm
        def create_esriiso_file():
            esriiso_slim = os.path.join(os.path.dirname(__file__),"metadata_template","ESRI_ISO_slim.xml")  # template xml file with minium metadata
            copyfile(esriiso_slim,esriiso_file)

            arcpy.ImportMetadata_conversion(esriiso_file, "FROM_ESRIISO",self.geofile, False)
            GeoHelper.arcgis_message(par.New_ESRIIO_XML.format(esriiso_file))

        def copy_esriiso_to_tempfile():
            if os.path.isfile(esriiso_file):
                copyfile(esriiso_file,esriiso_temp_file)

        # copy to the temp file, prepare for transforming to ISO19139
        def prepare_esriiso_file_to_transform():
            if os.name == "nt":
                backup_and_remove_original_esriiso_file()
                create_esriiso_file()
            copy_esriiso_to_tempfile()

        def recover_original_esriiso():
            if os.path.isfile(esriiso_backup_file):
                copyfile(esriiso_backup_file,esriiso_file)
                GeoHelper.rm_file(esriiso_backup_file)

        def clean_up():
            if os.path.isfile(esriiso_temp_file):
                GeoHelper.rm_file(esriiso_temp_file)

        def esriiso_to_iso19139():
            prepare_esriiso_file_to_transform()
            if os.path.isfile(esriiso_temp_file):
                self._update_csvs_to_esriiso(esriiso_temp_file) # csv is read and written to the tempfile. it is written to geofile in work directory, geofile path is from csv file
                if os.name == "nt":
                    self._transfrom_esriiso_to_iso19139(esriiso_temp_file) # this has to be in arcgis machine
                    recover_original_esriiso()
                    clean_up() # can be commented out for debug in VM
            else:
                GeoHelper.arcgis_message("ESRIISO - '{0}' is missing: Please try: 1) run tool '1. 4 - Exporting Metedata from Woking Directory to The CSV files Directory'; 2) make sure geofile path is correct in updated CSV files.".format(esriiso_temp_file) )


        esriiso_to_iso19139()

    # requirement from Susan: only 010 and 006 got to citation responsible party
    def _seperate_resp_parties(self,raws):
        for raw in raws:
            role = raw["role"].strip()
            if role == "010" or role == "006":
                self.resp_parties_citation_raws.append(raw)
            else:
                self.resp_parties_idoc_raws.append(raw)

    def _update_csvs_to_esriiso(self,tempfile):
        tree =  ET.parse(tempfile)
        root = tree.getroot()
        self.root = root  # delayed loading

        self._populate_main_metadata()
        self._populate_responsible_parties()
        self._add_ucb_distributor()

        tree.write(tempfile)
        # beautiful_temp_file = tempfile.replace(".xml","_a.xml")
        # GeoHelper.beautify_file(tempfile,beautiful_temp_file)


    def _transfrom_esriiso_to_iso19139(self,esritemp_file):
        def geofile_batch_name():
            geofile_basename = os.path.basename(self.geofile)
            return  os.path.splitext(geofile_basename)[0]

        def iso19139_file():
            iso19139_dir =  GeoHelper.iso19139_path(self.process_path)
            path = os.path.join(iso19139_dir,self.arkid)
            if not os.path.exists(path):
                os.makedirs(path)
            return os.path.join(path,"iso19139.xml")

        def transform_ISO19139(iso19139_file):
            GeoHelper.rm_file(iso19139_file) # if a file exists, arcpy cannot to conversion
            arcgis_dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
            translator = os.path.join(arcgis_dir,"Metadata\\Translator\\ArcGIS2ISO19139.xml")
            result = arcpy.ExportMetadata_conversion(esritemp_file,translator,iso19139_file)

        def copy_ISO19139_to_source_dir(iso19139_file):
            source_dir = GeoHelper.source_path(self.process_path)
            batch_name = geofile_batch_name()
            source_dir_geofile_batch = os.path.join(source_dir,batch_name)

            if os.path.isdir(source_dir_geofile_batch):
                source_dir_iso19139 = os.path.join(source_dir_geofile_batch,"{0}_iso19139.xml".format(batch_name))
                copyfile(iso19139_file,source_dir_iso19139)
            else:
                GeoHelper.arcgis_message("Cannot move ISO19139.xml to source directory - {0}, it's missing. ".format(source_dir_geofile_batch), )

        def transform_and_copy():
            the_iso19139_file = iso19139_file()
            transform_ISO19139(the_iso19139_file)  #  this will be in work directory
            copy_ISO19139_to_source_dir(the_iso19139_file)

        transform_and_copy()


    ###################### populate main metadata from csv ###################

    def _populate_main_metadata(self):
        def special_type(dic,a):
            return dic.has_key(a) and dic[a]

        def add_node_value(path,val,add_to_attribute):
            self._ensure_path_nodes_exists(path)
            element = self.root.find("./{0}".format(path))
            if add_to_attribute:
                element.set("value", val)
            else:
                element.text = val

        def add_node(parent_node,child,grandchild,val):
            if child == "tpCat":
                child_node = ET.SubElement(parent_node,child)
                grandchild_node = ET.SubElement(child_node,grandchild)
                grandchild_node.set("value", val)
            else:
                child_node = ET.SubElement(parent_node,child,attrib={"xmlns": ""})
                grandchild_node = ET.SubElement(child_node,grandchild)
                grandchild_node.text = val

        # elements under tag "dataIdInfo"
        def add_node_multiple_values(path,val): # example path: "dataIdInfo/tempKeys/keyword" => dataInfo/child/grandchild
            tags = path.split("/")
            child = tags[1]
            grandchild =  tags[2]
            dataInInfo = self.root.find("dataIdInfo")
            self._remove_elements(dataInInfo,child)

            sub_values = [txt.strip() for txt in val.split("$")]
            for sub_val in sub_values:
                if len(sub_val) > 0:
                    add_node(dataInInfo,child,grandchild,sub_val)

        def update_metadata(header,val):
            dic = par.transform_elements[header]
            path = dic["path"]
            add_to_key = special_type(dic,"key_path")
            add_to_attribute = special_type(dic,"attribute")

            if add_to_key:
                add_node_multiple_values(path,val)
            else:
                val = val.replace("$",";") # Geoblacklight allow multiple values, ISO19139 will be a single value
                add_node_value(path,val,add_to_attribute)

        # all rights are written under "dataIdInfo/resConst" node
        def update_metadata_rights(rights):
            # element_info_dic = par.transform_elements["rights_general"] # "dataIdInfo/resConst/Consts/useLimit",
            def right_tag(header):
                element_info_dic = par.transform_elements[header]
                path = element_info_dic["path"]
                tags = path.split("/")
                return tags[2]

            child = "resConst"
            dataInInfo = self.root.find("dataIdInfo")
            self._remove_elements(dataInInfo,child)
            resConst_node =  ET.SubElement(dataInInfo,child)
            for key, value in rights.items():
                right_node = ET.SubElement(resConst_node,right_tag(key))
                useLimit_node = ET.SubElement(right_node,"useLimit")
                useLimit_node.text = value

        # get value for updating to the temp ESRI ISO xml file - prepare for ISO 19139 transforming
        def final_value(h):
            h_o = "{0}_o".format(h)
            new_val = self.main_csv_raw[h].strip()
            old_val = self.main_csv_raw[h_o].strip()
            return new_val if len(new_val) > 0 else old_val

        def update_csv_to_temp_ESRIISO():
            rights = {} # three different rights
            for h in par.CSV_HEADER_TRANSFORM:
                val = final_value(h) # new workflow: write all back to ESRI ISO
                if len(val) > 0 :
                    if h in par.CSV_HEADER_COLUMNS_RIGHTS:
                        rights[h] = val
                    else:
                        update_metadata(h,val)
            if bool(rights):
                update_metadata_rights(rights)

        update_csv_to_temp_ESRIISO()


    def _remove_elements(self,parent_element,child_name):
        elements = parent_element.findall(child_name)
        for element in elements:
            parent_element.remove(element)


    def _add_element(self,parent_element,child_name,attrib = None):
        child_element = parent_element.find(child_name)
        if child_element is None:
            if attrib:
                child_element = ET.SubElement(parent_element,child_name,attrib = attrib)
            else:
                child_element = ET.SubElement(parent_element,child_name)
        return child_element


    def _ensure_path_nodes_exists(self,path): # all the path defined in header elements start from root, each element on the path is identical
        elements = path.split("/")
        parent = self.root
        for e in elements:
            parent = self._add_element(parent,e)


    def _remove_old_responsible_parties(self):
        resp_parties = self.root.findall('./dataIdInfo/idCitation/citRespParty')
        for resp in resp_parties:
            idCitation = self.root.find('./dataIdInfo/idCitation')
            idCitation.remove(resp)


    def _remove_old_idPoCs(self):
        idPoCs = self.root.findall('./dataIdInfo/idPoC')
        if not idPoCs is None:
            dataIdInfo = self.root.find('./dataIdInfo')
            for idPoC in idPoCs:
                dataIdInfo.remove(idPoC)


    def _populate_responsible_parties(self):
        self._remove_old_responsible_parties()
        self._add_to_citiaton()

        self._remove_old_idPoCs()
        self._add_to_idoc()


    def _add_to_citiaton(self):
        # def update_berkley_info_to(raw):
        #     header_value = par.UCB_RESPONSIBLE_PARTY
        #     for k,v in header_value.iteritems ():
        #         raw[k] = v
        #         raw["role"] = ""

        for raw in self.resp_parties_citation_raws:
            # update_berkley_info_to(raw)
            # self._add_citation_responsible_party(raw)
            self._add_responsible_party(raw,"./dataIdInfo/idCitation","citRespParty")


    def _add_to_idoc(self):
        for raw in self.resp_parties_idoc_raws:
            self._add_responsible_party(raw,'./dataIdInfo','idPoC')


    def _add_responsible_party(self,resp_raw,parent_path,tag):
        def value(name):
            return resp_raw[name].strip()

        def add_sub_node(parent_node,child_node_name,val):
            if len(val.strip()) > 0:
                child_node = self._add_element(parent_node,child_node_name)
                child_node.text = val

        def add_siblings(parent_node,node_names):
            for name in node_names:
                val = value(name)
                if GeoHelper.isNotNullorEmpty(val):
                    child_node_name = par.responsibleparty_elements[name]["path"].split("/")[-1]
                    # print "{0} :: {1}".format(child_node_name,val)
                    add_sub_node(parent_node,child_node_name,val)

        # parent_node = self.root.find('./dataIdInfo')
        respParty_parent_node = self.root.find(parent_path)

        if not respParty_parent_node is None:
            #citRespParty = ET.SubElement(parent_node,"idPoC", attrib={"xmlns": ""})
            respParty_node = ET.SubElement(respParty_parent_node,tag, attrib={"xmlns": ""})

            organization = value("organization")

            add_sub_node(respParty_node,"rpOrgName",organization)

            contact_name = value("contact_name")
            add_sub_node(respParty_node,"rpIndName",contact_name)

            position = value("position")
            add_sub_node(respParty_node,"rpPosName",position)

            rpCntInfo = self._add_element(respParty_node,"rpCntInfo",attrib={"xmlns": ""})
            contact_ls = ["email","hours","instruction"]
            add_siblings(rpCntInfo,contact_ls)

            cntAddress = self._add_element(rpCntInfo,"cntAddress",attrib={"addressType": ""})
            address_ls = ["address","city","zip","country"]
            add_siblings(cntAddress,address_ls)

            cntPhone = self._add_element(rpCntInfo,"cntPhone")
            phone_ls = ["phone_no","fax_no"]
            add_siblings(cntPhone,phone_ls)

            role = self._add_element(respParty_node,"role")
            clr_role = value("role")
            roleCd = ET.SubElement(role, "RoleCd", attrib={"value": clr_role})
        else:
            GeoHelper.arcgis_message("File- {0}: path '{2}',  no responsible party found - {1}".format(self.geofile,self.arkid,parent_path))


    def _add_ucb_distributor(self):
        def add_sub_node(parent_node,child_node_name,val):
            if len(val.strip()) > 0:
                child_node = self._add_element(parent_node,child_node_name)
                child_node.text = val

        distInfo = self._add_element(self.root,"distInfo",attrib={"xmlns": ""})
        distributor = self._add_element(distInfo,"distributor",attrib={"xmlns": ""})
        distorCont = self._add_element(distributor,"distorCont",attrib={"xmlns": ""})

        add_sub_node(distorCont,"rpOrgName","UC Berkeley Library")

        rpCntInfo =  self._add_element(distorCont,"rpCntInfo")

        cntPhone =  self._add_element(rpCntInfo,"cntPhone")
        voiceNum =  self._add_element(cntPhone,"voiceNum", attrib={"tddtty":""})
        voiceNum.text = "(510) 642-2997****"

        cntAddress =  self._add_element(rpCntInfo,"cntAddress",attrib={"addressType": ""})
        add_sub_node(cntAddress,"delPoint","50 McCone Hall")
        add_sub_node(cntAddress,"city","Berkeley")
        add_sub_node(cntAddress,"adminArea","CA")
        add_sub_node(cntAddress,"postCode","94720")
        add_sub_node(cntAddress,"country","USA")
        add_sub_node(cntAddress,"eMailAdd","eart@library.berkeley.edu")

        add_sub_node(distorCont,"editorSave","True")
        add_sub_node(distorCont,"displayName","UC Berkeley Library")

        role = self._add_element(distorCont,"role")
        RoleCd = self._add_element(role,"RoleCd")
        RoleCd.set("value", "005")
