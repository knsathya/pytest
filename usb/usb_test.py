import os
import logging
import logging.config
import yaml
from lib.test_handlers import TestHandlers
from lib.test_managers import TestManager

def setup_logging(default_path, default_level=logging.INFO, env_key='LOG_CFG'):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    return logging.getLogger(__name__)

class USBTestHandlers(TestHandlers):
    def configfs_disable_gadget(self, host, remote, id, params):
        cmd_list = []
        if params['os_type'] == 'Android':
            cmd_list.append('remote:stop adbd')
        cmd_list.append('remote:echo "" > /config/usb_gadget/g1/UDC')

        return self.execute_cmd_list(host, dut, cmd_list, params['default_cmd_timeout'], params['default_cmd_expected_result'], params['default_cmd_error_hint'].split('|'))

    def configfs_add_gadget(self, host, remote, id, params):
        cmd_list = ['remote:echo 0xa4a0 > /config/usb_gadget/g1/idProduct',
                    'remote:echo 0x0525 > /config/usb_gadget/g1/idVendor',
                    'remote:rm /config/usb_gadget/g1/configs/b.1/f1',
                    'remote:ln -s /config/usb_gadget/g1/functions/SourceSink.1 /config/usb_gadget/g1/configs/b.1/f1']

        return self.execute_cmd_list(host, remote, cmd_list, params['default_cmd_timeout'],
                                     params['default_cmd_expected_result'].split('|'),
                                     params['default_cmd_error_hint'].split('|'))

    def enable_gadget(self, host, remote, id, params):
        cmd_list = ['remote:echo ' + params['device_controller'] + ' > /config/usb_gadget/g1/UDC']
        if params['os_type'] == 'Android':
            cmd_list.append('remote:start adbd')

        return self.execute_cmd_list(host, remote, cmd_list, params['default_cmd_timeout'],
                                     params['default_cmd_expected_result'].split('|'),
                                     params['default_cmd_error_hint'].split('|'))

if __name__ == "__main__":
    #logger.debug("Start USB testing")
    #logger = logging.getLogger(__name__)
    #logging.basicConfig(format='%(message)s')
    #logger.setLevel(logging.DEBUG)
    logger = setup_logging('usb-log.yaml')
    testhandlers = USBTestHandlers()
    testobj = TestManager(os.path.join(os.getcwd(), 'gpmrb-test-setup.ini'),
                         os.path.join(os.getcwd(), '../lib/test-setup-defaults.ini'),
                         os.path.join(os.getcwd(), 'usb-test-default.ini'),
                         os.path.join(os.getcwd(), '../lib/test-config-defaults.ini'),
                        testhandlers, logger=logger)
    testobj.exec_tests(0)
