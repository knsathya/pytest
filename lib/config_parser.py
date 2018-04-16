import os
from configobj import ConfigObj,flatten_errors
from configobj.validate import Validator
import logging
import re

def _sub_env(section, key, env_opt=None, logger=None):
    logger = logger or logging.getLogger(__name__)

    def lookup(match):

        logger.info("Found match")
        logger.info(match.groups())

        key = match.group(2)

        if key in env_opt.keys():
            return env_opt[key]

        return match.group(1)

    pattern = re.compile(r'(\${(\w+)})')
    logger.info(section[key])
    if type(section[key]) == list:
        for index, opt in enumerate(section[key]):
            replaced = pattern.sub(lookup, opt)
            if replaced is not None:
                section[key][index] = replaced
    else:
        replaced = pattern.sub(lookup, section[key])
        if replaced is not None:
            section[key] = replaced

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


    def __init__(self, cfg,  cfg_spec, usr_cfg='', os_env=False, opt_env=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)

        self.logger.debug("cfg = %s" % cfg)
        self.logger.debug("cfg_spec = %s" % cfg_spec)
        self.logger.debug("usr_cfg = %s" % usr_cfg)

        self._config_check(cfg)
        self._config_check(cfg_spec)

        cfgobj = ConfigObj(cfg)

        if opt_env is not None:
            cfgobj.walk(_sub_env, env_opt=opt_env, logger=logger)

        self.logger.info(cfgobj)

        if os_env is True:
            cfgobj.walk(_sub_env, env_opt=os.environ, logger=logger)

        if os.path.exists(usr_cfg):
            cfgobj.merge(usr_cfg)

        self.cfg = ConfigObj(cfgobj, configspec=cfg_spec)
        self._validate(self.cfg)

    def get_cfg(self):
        return self.cfg
