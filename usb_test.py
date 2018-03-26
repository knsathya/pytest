from terminal import LocalTerminal, AdbTerminal, SerialTerminal
import logging
from config_parser import TestConfigParser

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.ERROR)

class USBTest(object):
    def __init__(self, cfg):
        self.cfg_parser = TestConfigParser('usb-config.ini')
        self.cfg = self.cfg_parser.cfg

        if self.cfg.remote_terminal.type == 'serial':
            terminal = self.cfg.serial
            self.terminal = SerialTerminal(terminal.name, terminal.baudrate, terminal.parity,
                                           terminal.bytesize, terminal.stopbit, terminal.hfc,
                                           terminal.sfc, int(terminal.timeout))

    def do_test_1(self):
        test_params = self.cfg.test_1
        logger.debug("Executing %s" % test_params.name)
        output, status  = self.terminal.send_command(test_params.remote_cmd)
        print self.terminal.print_output()



if __name__ == "__main__":
    logger.debug("Start USB testing")
    testobj = USBTest('usb-config.ini')
    testobj.do_test_1()


