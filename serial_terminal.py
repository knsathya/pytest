import serial
import io
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.ERROR)

class SerialTerminal(object):
    def __init__(self, port="/dev/ttyUSB0", baud=115200, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, timeout=4):
        logger.debug("Using serial port %s baudarate %d" % (port, baud))
        self.name = port
        self.serial = serial.Serial(port=port, baudrate=baud, parity=parity, bytesize=bytesize, stopbits=stopbits, timeout=timeout)
        self.cmd =""
        self.output = "None"
        self.cmd_status = True

    def send_cmd(self, cmd, error_str=["not found", "error", "failed"]):
        cmd_status = True
        self.cmd = cmd + "\r"
        self.serial.flushOutput()
        self.serial.flushInput()
        self.serial.write(self.cmd)
        self.serial.flush()
        self.output = self.serial.readlines()

        for error in error_str:
            if any(error in s for s in error_str):
                self.cmd_status = False
                break

        return self.cmd_status

    def print_output(self, skip_cmd=False, skip_last=False):
        output = self.output
        output = output[1:] if skip_cmd is True else output
        output = output[:-1] if skip_last is True else output
        for out in output:
            print out

    def check_output(self, keyword):
        if any(keyword in s for s in self.output):
            return True

        return False

    def close(self):
        self.serial.close()

if __name__ == "__main__":
    terminal = SerialTerminal(port="/dev/ttyUSB4")

    terminal.send_cmd("lsusb", )
    terminal.print_output()

    terminal.close()
