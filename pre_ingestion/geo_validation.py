import os
import re
import json
from jsonschema import validate
import jsonschema
from geo_helper import GeoHelper



class GeoValidation(object):
    def __init__(self,jsonFile,jsonSchema):
        self.jsonFile = jsonFile
        self.jsonSchema = jsonSchema

    def isValidGeoJson(self):
        schema = ""
        data = ""

        with (open(self.jsonSchema)) as s:
            schema = s.read()
        with (open(self.jsonFile)) as d:
            data = d.read()

        try:
            v = jsonschema.Draft4Validator(json.loads(schema))
            num = 0
            for error in sorted(v.iter_errors(json.loads(data)), key=str):
                num += 1
                errorMessage = error.message.replace("u\'","\'")
                msg = ""
                if len(error.path) > 0:
                    msg = "* " + error.path[0] + ': ' + errorMessage
                else:
                    msg =  "* " + errorMessage
                if (len(msg)>0):
                    error_msg = "'{0}'' is invalid: {1}".format(self.jsonFile,";".join(msg))
                    GeoHelper.arcgis_message(error_msg)
            return (True if num == 0 else False)

        except jsonschema.ValidationError as e:
            msg = ("^^ Geoblackschema error when validating {0} : error --  " + e.message).format(self.jsonFile)
            GeoHelper.arcgis_message(msg)
            return False
        except:
            msg = "exception in validating {0}".format(self.jsonFile)
            GeoHelper.arcgis_message(msg)
            return False
