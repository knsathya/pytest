import os
import logging
from lib.config_parser import ConfigParse
from lib.device import Device
import importlib

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

    def _create_device(self, name, params):
        return Device(name=params[name], terminal_list=params[name]['terminal'],
                      default_terminal=params[name]['default_terminal'], logger=logger)

    def get_device(self, name):
        if name == 'host':
            return self.host
        elif name == 'remote':
            return self.remote

    def _parse_cmdstr(self, cmd_str):
        device = cmd_str.split(':')[0]
        cmd = cmd_str.split(':=')[1]
        channel = ''.join(cmd_str.split(':=')[0].split(':')[1:])

        return device, channel, cmd

    def __init__(self, setup_cfg, setup_spec, setup_user='', logger=None):
        self.logger = logger or logging.getLogger(__name__)

        self.cfg = ConfigParse(setup_cfg, setup_spec, setup_user, os_env=True, opt_env=flatten_dict(config_env), logger=logger).get_cfg()

        self.logger.debug(self.cfg)

        params = self.cfg['test']['platform-env']

        self.plat_env = ConfigParse(params['base_cfg'], params['spec_cfg'], params['usr_cfg'], os_env=True, logger=logger).get_cfg()

        self.logger.debug(self.plat_env)

        params = self.cfg['test']['test-dm-config']

        self.test_obj = {}

        for dm_name, test_params  in params.iteritems():
            test_obj = ConfigParse(test_params['base_cfg'], test_params['spec_cfg'], test_params['usr_cfg'],
                                   os_env=True, opt_env=flatten_dict(self.plat_env.dict()), logger=logger).get_cfg()
            self.test_obj[dm_name] = (test_obj, test_params['handler_module'], test_params['handler_class'])

        # Create devices
        self.host = self._create_device('host', self.cfg)
        self.remote = self._create_device('remote', self.cfg)

        self.logger.debug(self.host)
        self.logger.debug(self.remote)

    def exec_test(self, name=None):
        self.logger.debug("Execute %s tests" % "all" if name is None else name)

        for dm, params in self.test_obj.iteritems():
            self.logger.debug("Executing %s tests" % dm)
            test_obj, test_module, handler_class = params
            logger.debug("Loading module: %s class: %s" % (test_module, handler_class))
            handler_obj = getattr(importlib.import_module(test_module), handler_class)(setup=self, logger=self.logger)



if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(message)s')
    logger.setLevel(logging.DEBUG)

    print os.getcwd()

    testobj = TestSetup(os.path.join(os.getcwd(), 'config', 'drgn410c-base-test-setup.ini'), os.path.join(os.getcwd(), 'config-spec', 'test-setup-spec.ini'), logger=logger)
    testobj.exec_test()

