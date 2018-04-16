import os
import itertools as it
import re
import logging
from lib.config_parser import ConfigParse
from lib.device import Device
import collections

config_env = {'CONFIG_DIR' : os.path.join(os.getcwd(), 'config'),
          'CONFIG_SPEC_DIR' : os.path.join(os.getcwd(), 'config-spec')}


def dict_merge(*args):
    results = {}

    for arg in args:
        if type(arg) is dict:
            results.update(arg)

    return results


def flatten_dict(d):
    def expand(key, value):
        if isinstance(value, dict):
            return [ (key + '.' + k, v) for k, v in flatten_dict(value).items() ]
        else:
            return [ (key, value) ]

    items = [ item for k, v in d.items() for item in expand(k, v) ]

    results = dict(items)

    return dict(items)

class TestSetup(object):

    def __init__(self, setup_cfg, setup_spec, setup_user='', logger=None):
        self.logger = logger or logging.getLogger(__name__)

        fenv_opt = flatten_dict(config_env)

        self.cfg = ConfigParse(setup_cfg, setup_spec, setup_user, os_env=True, opt_env=flatten_dict(config_env), logger=logger).get_cfg()

        #logger.info(self.cfg)

        params = self.cfg['test']['platform-env']

        self.plat_env = ConfigParse(params['base_cfg'], params['spec_cfg'], params['usr_cfg'], os_env=True, logger=logger).get_cfg()

        #logger.info(self.plat_env)

        params = self.cfg['test']['test-dm-config']

        self.test_obj = {}

        for dm_name, test_params  in params.iteritems():
            #env_opt = dict_merge(flatten_dict(self.plat_env.dict()) , flatten_dict(os.environ))
            #plat_env_copy = self.plat_env.copy()
            #fenv_opt = flatten_dict(plat_env_copy, os_env=False)
            #print flatten_json(self.plat_env, os_env=False)
            #logger.info(flatten_dict(self.plat_env))
            #logger.info(dict_merge(flatten_dict(self.plat_env) , flatten_dict(os.environ)))
            #logger.info(flatten_dict(self.plat_env.dict()))
            test_obj = ConfigParse(test_params['base_cfg'], test_params['spec_cfg'], test_params['usr_cfg'],
                                   os_env=True, opt_env=flatten_dict(self.plat_env.dict()), logger=logger).get_cfg()
            #logger.info(test_obj)

        '''

        params = self.cfg['host']

        self.host = Device(name=params['name'], terminal_list=params['terminal'],
                           default_terminal=params['default_terminal'], logger=logger)

        params = self.cfg['remote']

        self.remote = Device(name=params['name'], terminal_list=params['terminal'],
                             default_terminal=params['default_terminal'], logger=logger)

        params = self.cfg['test']['platform-env']

        self.env = ConfigParse(params['base_cfg'], params['spec_cfg'], params['usr_cfg'], logger).get_cfg()

        '''


if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(message)s')
    logger.setLevel(logging.DEBUG)

    print os.getcwd()

    testobj = TestSetup(os.path.join(os.getcwd(), 'config', 'drgn410c-base-test-setup.ini'), os.path.join(os.getcwd(), 'config-spec', 'test-setup-spec.ini'), logger=logger)

