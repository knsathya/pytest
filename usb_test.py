from terminal import LocalTerminal, AdbTerminal, SerialTerminal
import logging
from config_parser import TestConfigParser

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)

class USBTest(object):
    def __init__(self, cfg):
        self.cfg_parser = TestConfigParser('usb-config.ini')
        self.cfg = self.cfg_parser.cfg

        if self.cfg.remote_terminal.type == 'serial':
            terminal = self.cfg.serial
            self.terminal = SerialTerminal(terminal.name, terminal.baudrate, terminal.parity,
                                           terminal.bytesize, terminal.stopbit, terminal.hfc,
                                           terminal.sfc, int(terminal.timeout))
        elif self.cfg.remote_terminal.type == 'adb':
            terminal = self.cfg.adb
            self.terminal = AdbTerminal(terminal.name)
        elif self.cfg.remote_terminal.type == 'local':
            terminal = self.cfg.local
            self.terminal = LocalTerminal(terminal.name)

    def print_test_result(self, id, params, status):
        print "\nTest ID: %s" % id
        print "Test type: %s" % params.type
        print "Test name: %s" % params.name
        print "Test status: %s" % "passed" if status else "failed"
        if status is False:
            print "Expected result: %s" % params.remote_expected_result
            print "Actual result: %s" % self.terminal.command_output


    def do_test_1(self):
        test_params = self.cfg.test_1
        self.terminal.send_command(test_params.remote_cmd)
        status = self.terminal.check_output(test_params.remote_expected_result)
        self.print_test_result("test_1", test_params, status)

    def do_test_2(self):
        test_params = self.cfg.test_2
        self.terminal.send_command(test_params.remote_cmd)
        status = self.terminal.check_output(test_params.remote_expected_result)
        self.print_test_result("test_2", test_params, status)

if __name__ == "__main__":
    logger.debug("Start USB testing")
    testobj = USBTest('usb-config.ini')
    testobj.do_test_1()
    testobj.do_test_2()


