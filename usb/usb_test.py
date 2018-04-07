import os
import logging
from lib.configobj import ConfigObj,flatten_errors
from lib.configobj.validate import Validator
from lib.terminal import SerialTerminal, AdbTerminal, LocalTerminal
from lib.test_handlers import TestLib

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.ERROR)

def config_key_check(configobj, *keys):
    obj = configobj
    for key in keys:
        if key not in obj.keys():
            return False
        else:
            obj = configobj[key]

    return True

def validate_configobj(obj):
    validator = Validator()
    results = obj.validate(validator)
    if results != True:
        for (section_list, key, _) in flatten_errors(obj, results):
            if key is not None:
                raise Exception('The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list)))
            else:
                raise Exception('The following section was missing:%s ' % ', '.join(section_list))


class USBTestLib(TestLib):
    def configfs_disable_gadget(self, host, dut, id, params):
        cmd_list = []
        if params['os_type'] == 'Android':
            cmd_list.append('remote:stop adbd')
        cmd_list.append('remote:echo "" > /config/usb_gadget/g1/UDC')

        return self.execute_cmd_list(host, dut, cmd_list, params['default_cmd_timeout'], params['default_cmd_expected_result'], params['default_cmd_error_hint'].split('|'))

    def configfs_add_gadget(self, host, dut, id, params):
        cmd_list = ['remote:echo 0xa4a0 > /config/usb_gadget/g1/idProduct',
                    'remote:echo 0x0525 > /config/usb_gadget/g1/idVendor',
                    'remote:rm /config/usb_gadget/g1/configs/b.1/f1',
                    'remote:ln -s /config/usb_gadget/g1/functions/SourceSink.1 /config/usb_gadget/g1/configs/b.1/f1']

        return self.execute_cmd_list(host, dut, cmd_list, params['default_cmd_timeout'], params['default_cmd_expected_result'], params['default_cmd_error_hint'].split('|'))

    def enable_gadget(self, host, dut, id, params):
        cmd_list = ['remote:echo ' + params['device_controller'] + ' > /config/usb_gadget/g1/UDC']
        if params['os_type'] == 'Android':
            cmd_list.append('remote:start adbd')

        return self.execute_cmd_list(host, dut, cmd_list, params['default_cmd_timeout'], params['default_cmd_expected_result'], params['default_cmd_error_hint'].split('|'))


class TestConfig(object):

    def create_terminal(self, terminal):
        if terminal['type'] == 'serial':
            return SerialTerminal(port=terminal['name'], baud=terminal['baudrate'],
                                  parity=terminal['parity'], stopbits=terminal['stopbit'],
                                  bytesize=terminal['bytesize'], hfc=terminal['hfc'], sfc=terminal['sfc'],
                                  timeout=terminal['timeout'])
        elif terminal['type'] == 'usb-adb':
            return  AdbTerminal()
        else:
            return LocalTerminal()

    def configure_dut(self):
        self.dut.send_command(self.dut_params['login_cmd'])
        self.dut.send_command(self.dut_params['setup_cmd'])

    def reset_dut(self):
        self.dut.send_command(self.dut_params['reset_cmd'])
        self.dut.send_command(self.dut_params['exit_cmd'])

    def print_test_section(self, test):
        print "Name: %s" % test['name']
        print "Type: %s" % test['type']
        print "Handler: %s" % test['handler']
        print "Local Cmd Timeout: %s" % test['local_cmd_timeout']
        print "Local Cmd: %s" % test['local_cmd']
        print "Remote Cmd Timeout: %s" % test['remote_cmd_timeout']
        print "Remote Cmd: %s" % test['remote_cmd']
        print "Remote Cmd Expected Results: %s" % test['remote_expected_result']

    def __init__(self, setup_cfg, setup_spec, test_cfg, test_spec, testlib):
        logger.debug("Parsing setup config/spec")

        self.setupobj = ConfigObj(setup_cfg, configspec=setup_spec)
        validate_configobj(self.setupobj)

        self.testobj = ConfigObj(test_cfg, configspec=test_spec)
        validate_configobj(self.testobj)

        host_keys = self.setupobj['test']['preffered-host-terminal'].split(':')
        dut_keys = self.setupobj['test']['preffered-dut-terminal'].split(':')


        self.host_params = self.setupobj[host_keys[0]][host_keys[1]][host_keys[2]]
        self.dut_params = self.setupobj[dut_keys[0]][dut_keys[1]][dut_keys[2]]

        self.host = self.create_terminal(self.host_params)
        self.dut = self.create_terminal(self.dut_params)

        self.testlib = testlib

    def exec_tests(self):

        self.configure_dut()

        for id, params in self.testobj.iteritems():
            env = self.setupobj['dut']['env']
            for handler in params['handler']:
                output, status = getattr(self.testlib, handler)(self.host, self.dut, id, dict(params.items() + env.items()))

        #self.reset_dut()

if __name__ == "__main__":
    logger.debug("Start USB testing")
    testlib = USBTestLib()
    testobj = TestConfig('gpmrb-setup.ini',
                         os.path.join(os.getcwd(), '../lib/test-setup-defaults.ini'),
                         'usb-test-config.ini',
                         os.path.join(os.getcwd(), '../lib/test-config-defaults.ini'),
                         testlib)
    testobj.exec_tests()
