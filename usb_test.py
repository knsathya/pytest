import serial_terminal
import logging
from ConfigParser import SafeConfigParser

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.ERROR)

class USBTest(object):
    def __init__(self, cfg):
        self.parser = SafeConfigParser()
        self.parser.read('platform.config')
        self.use_serial = self.parser.get("terminal", "serial")
        self.use_adb = self.parser.get("terminal", "adb")
        if self.use_serial:

    def test_1(self):
        self.parser.get("test_1")

if __name__ == "__main__":
    logger.debug("Start USB testing")
