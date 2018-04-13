import os
from configobj import ConfigObj,flatten_errors
from configobj.validate import Validator
import logging

class ConfigParse(object):

    def _validate(self, obj):
        validator = Validator()
        results = obj.validate(validator)
        if results != True:
            for (section_list, key, _) in flatten_errors(obj, results):
                if key is not None:
                    raise Exception(
                        'The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list)))
                else:
                    raise Exception('The following section was missing:%s ' % ', '.join(section_list))


    def _config_check(self, cfg):
        if not os.path.exists(cfg):
            raise IOError("File %s does not exists" % cfg)

        return True

    def __init__(self, cfg,  cfg_spec, usr_cfg='', logger=None):
        self.logger = logger or logging.getLogger(__name__)

        self._config_check(cfg)
        self._config_check(cfg_spec)

        cfgobj = ConfigObj(cfg)

        if os.path.exists(usr_cfg):
            cfgobj.merge(usr_cfg)

        self.cfg = ConfigObj(cfgobj, configspec=cfg_spec)
        self._validate(self.cfg)

    def get_cfg(self):
        return self.cfg
