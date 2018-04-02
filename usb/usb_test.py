import logging
from configobj import ConfigObj,flatten_errors
from validate import Validator
from lib.terminal import SerialTerminal, AdbTerminal, LocalTerminal
from lib.test_libs import TestLib

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

        self.host = self.create_terminal(self.setupobj[host_keys[0]][host_keys[1]][host_keys[2]])
        self.dut = self.create_terminal(self.setupobj[dut_keys[0]][dut_keys[1]][dut_keys[2]])

        self.testlib = testlib

    def exec_tests(self):
        print self.testobj
        for id, params in self.testobj.iteritems():
            getattr(self.testlib, params['handler'])(self.host, self.dut, id, params)


if __name__ == "__main__":
    logger.debug("Start USB testing")
    testlib = TestLib()
    testobj = TestConfig('setup.ini', 'setup-spec.ini', 'test-config.ini', 'test-config-spec.ini', testlib)
    testobj.exec_tests()
