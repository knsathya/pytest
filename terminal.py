import serial
import io
import logging
from subprocess import Popen, PIPE


logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.ERROR)

class RemoteTerminal(object):
    def __init__(self, name):
        logger.debug("Remote terminal init")
        self.name = name
        self.terminal = None
        self.command = ""
        self.command_output = "None"
        self.command_status = True

    def open(self):
        logger.debug("Remote terminal open()")

    def send_command(self, cmd, error_str=[]):
        logger.debug("Remote channel send_command()")
        return self.command_output, self.command_status

    def print_output(self, skip_cmd=False, skip_last=False):
        for out in self.command_output:
            print out

    def check_output(self, keyword):
        if any(keyword in s for s in self.command_output):
            return True

        return False

    def close(self):
        logger.debug("Remote terminal close()")

class SerialTerminal(RemoteTerminal):
    def __init__(self, port="/dev/ttyUSB0", baud=115200, parity="None", bytesize=8, stopbits=1, hfc=False, sfc=False, timeout=4):
        super(SerialTerminal, self).__init__(port)

        if parity == "Odd":
            parity = serial.PARITY_ODD
        elif parity == "Even":
            parity = serial.PARITY_EVEN
        else:
            parity = serial.PARITY_NONE

        if bytesize == 7:
            bytesize = serial.SEVENBITS
        elif bytesize == 6:
            bytesize = serial.SIXBITS
        elif bytesize == 5:
            bytesize = serial.FIVEBITS
        else:
            bytesize = serial.EIGHTBITS

        if stopbits == 1.5:
            stopbits = serial.STOPBITS_ONE_POINT_FIVE
        elif stopbits == 2:
            stopbits = serial.STOPBITS_TWO
        else:
            stopbits = serial.STOPBITS_ONE

        self.terminal = serial.Serial(port=port, baudrate=baud, parity=parity, bytesize=bytesize, stopbits=stopbits, xonxoff=sfc, rtscts=hfc, timeout=timeout)

        logger.error("Using serial port %s baudarate %d parity %s bytesize %d stopbits %d hfc %d sfc %d timeout %d" %
                     (port, baud, parity, bytesize, stopbits, hfc, sfc, timeout))

    def send_command(self, cmd, error_str=["not found", "error", "failed"]):
        cmd_status = True
        self.command = cmd + "\r"
        self.terminal.flushOutput()
        self.terminal.flushInput()
        self.terminal.write(self.command)
        self.terminal.flush()
        self.command_output = self.terminal.readlines()

        for error in error_str:
            status = not self.check_output(error)
            if status is False:
                self.command_status = status
                break

        return self.command_output, self.command_status

    def close(self):
        self.terminal.close()
        super(SerialTerminal, self).close()

class LocalTerminal(RemoteTerminal):
    def __init__(self, name="shell"):
        super(LocalTerminal, self).__init__(self, name)
        self.terminal = Popen

    def send_command(self, cmd, error_str=["not found", "error", "failed"]):
        self.command = cmd
        proc = self.terminal(list(self.command), shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        self.command_output, self.command_status = proc.communicate('through stdin to stdout')

        for error in error_str:
            status = not self.check_output(self, error)
            if status is False:
                self.command_status = status
                break

        return self.command_output, self.command_status

class AdbTerminal(LocalTerminal):
    def __init__(self, device=""):
        super(LocalTerminal, self).__init__(self, device)

    def send_command(self, cmd, error_str=[]):
        return super(LocalTerminal, self).send_command(self, "adb shell" + ' ' + cmd, error_str)



if __name__ == "__main__":
    terminal = SerialTerminal(port="/dev/ttyUSB4")

    terminal.send_command("lsusb", )
    terminal.print_output()
    terminal.close()