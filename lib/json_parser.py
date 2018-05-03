import json
import os
from jsonschema import validators, validate, Draft4Validator
from jsonmerge import merge

class JSONParser(object):

    def _extend_with_default(self, validator_class):
        validate_properties = validator_class.VALIDATORS["properties"]

        def set_defaults(validator, properties, instance, schema):
            for property_, subschema in properties.items():
                if "default" in subschema and not isinstance(instance, list):
                    instance.setdefault(property_, subschema["default"])

            for error in validate_properties(
                    validator, properties, instance, schema,
            ):
                yield error

        return validators.extend(
            validator_class, {"properties": set_defaults},
        )

    def _get_json_data(self, json_in):

        data = ""
        status = False

        if type(json_in) == str:
            if os.path.exists(os.path.abspath(json_in)):
                with open(json_in) as data_file:
                    data = json.load(data_file)
                    status = True
        elif type(json_in) == dict:
            data = json_in
            status = True

        return data, status

    def __init__(self, schema, cfg, merge_list=[], extend_defaults=False, sub_env=False, opt_env=[]):

        data, status = self._get_json_data(schema)
        if status is False:
            raise IOError("%s file not found\n" % schema)

        self.schema = data

        data, status = self._get_json_data(cfg)
        if status is False:
            raise IOError("%s file not found\n" % cfg)

        for entry in merge_list:
            mergedata, status = self._get_json_data(entry)
            if status is False:
                raise IOError("%s invalid merge files\n" % mergedata)

            result = merge(data, mergedata)

            data = result

        #validate(data, self.schema, resolver=resolver)

        if extend_defaults is True:
            FillDefaultValidatingDraft4Validator = self._extend_with_default(Draft4Validator)
            FillDefaultValidatingDraft4Validator(self.schema).validate(data)
        else:
            validate(data, self.schema)


        self.data = data


if __name__ == '__main__':

    obj = JSONParser(schema='../config-spec/device-schema.json', cfg='../config/drgn410c-device.json', extend_defaults=True)

    print json.dumps(obj.data, indent=4, sort_keys=True)