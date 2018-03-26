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
                                           terminal.sfc, terminal.timeout)

    def test_1(self):
        self.parser.get("test_1")

if __name__ == "__main__":
    logger.debug("Start USB testing")
    USBTest('usb-config.ini')


