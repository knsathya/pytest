import serial
import io
import logging
from subprocess import Popen, PIPE
import os
import re

class Command(object):
    def __init__(self, name='', timeout=0, error_hint=[], success_hint=[]):
        self.name = name
        self.output = ''
        self.error = ''
        self.status = True
        self.timeout = timeout
        self.error_hint = error_hint
        self.success_hint = success_hint

    def to_list(self):
        cmd_list = re.split('[;]', self.name)
        cmd_list = [cmd + ';' for cmd in cmd_list]

        return cmd_list

    def check_output(self, keywords):
        for key in keywords:
            if key in self.output:
                return True

        return False

    def is_error(self, keywords=[]):
        keywords =  self.error_hint if len(keywords) == 0 else keywords
        return self.check_output(keywords)


    def is_success(self, keywords=[]):
        keywords =  self.success_hint if len(keywords) == 0 else keywords
        return self.check_output(keywords)

    def update_status(self):
        self.status = True

        if self.is_error():
            self.status = False
            return

        if self.is_success():
            self.status = True
            return

    def __str__(self):
        return "Command:%s Status:%s Output:%s" % (self.name.strip(), str(self.status), self.output)

class Terminal(object):
    def __init__(self, name, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.name = name
        self.command = Command()

    def send_command(self, cmd, timeout=0, error_hints=["not found", "error", "failed"], success_hints=[]):
        self.logger.debug("%s: send_command() Cmd: %s Timeout: %d err_hint: %s" % (self.name, cmd, timeout, str(error_hints)))
        self.command = Command(cmd, timeout, error_hints, success_hints)

        return self.command.output, self.command.status

    def print_output(self):
        self.logger.debug("%s print_output()" % (self.name))
        self.logger.info("%s" % self.command)

    def check_output(self, hints):
        self.logger.debug("%s check_output() hints:%s" % (self.name, str(hints)))
        return self.command.check_output(hints)

    def close(self):
        self.logger.debug("%s close()" % (self.name))

class ShellTerminal(Terminal):
    def __init__(self, name='HOST-SHELL', logger=None):
        super(ShellTerminal, self).__init__(name, logger)

    def send_command(self,  cmd, timeout=0, error_hints=["not found", "error", "failed"], success_hints=[]):
        super(ShellTerminal, self).send_command(cmd, timeout, error_hints, success_hints)

        proc = Popen(self.command.to_list(), shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        self.command.output, self.command.error = proc.communicate('through stdin to stdout')
        self.command.update_status()

        return self.command.output, self.command.status

class AdbTerminal(ShellTerminal):
    def __init__(self, device="USB-ADB", logger=None):
        super(AdbTerminal, self).__init__(device, logger)

    def send_command(self,  cmd, timeout=0, error_hints=["not found", "error", "failed"], success_hints=[]):
        cmd = "adb shell " + cmd
        return super(AdbTerminal, self).send_command(cmd, timeout, error_hints, success_hints)

class SerialTerminal(serial.Serial, Terminal):
    def __init__(self, port="/dev/ttyUSB0", baud=115200, parity="None", bytesize=8, stopbits=1, hfc=False, sfc=False, timeout=2, logger=None):
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

        if stopbits == '1.5':
            stopbits = serial.STOPBITS_ONE_POINT_FIVE
        elif stopbits == '2':
            stopbits = serial.STOPBITS_TWO
        else:
            stopbits = serial.STOPBITS_ONE

        Terminal.__init__(self, port, logger)

        serial.Serial.__init__(self, port=port, baudrate=int(baud), parity=parity, bytesize=bytesize, stopbits=stopbits, xonxoff=sfc, rtscts=hfc, timeout=timeout)

        self.logger.debug("Using serial port %s baudarate %s parity %s bytesize %d stopbits %s hfc %d sfc %d timeout %d" %
                     (port, baud, parity, bytesize, stopbits, hfc, sfc, timeout))

    def send_command(self, cmd, timeout=-1, error_hints=["not found", "error", "failed"], success_hints=[]):
        super(SerialTerminal, self).send_command(cmd, timeout, error_hints, success_hints)

        self.command.name = "\r" + self.command.name + "\r"

        self.flushOutput()
        self.flushInput()
        self.write(self.command.name)
        self.flush()

        tmp_timeout = self.timeout
        if self.command.timeout != -1:
            self.timeout = self.command.timeout

        self.command.output = ''.join(map(lambda it: it.strip('\r'), self.readlines()))

        self.timeout = tmp_timeout

        self.command.update_status()

        return self.command.output, self.command.status


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(message)s')
    logger.setLevel(logging.INFO)
    terminal = SerialTerminal(port="/dev/ttyUSB4")
    #terminal = AdbTerminal(device="sathya")
    terminal.send_command("ls")
    terminal.print_output()
    #terminal.close()
    #signer = sign_m2crypto.M2CryptoSigner(os.path.expanduser('~/.android/adbkey'))
    #device = adb_commands.AdbCommands.ConnectDevice(rsa_keys=[signer])
    #print device.Shell('lspci -k')