import io
import re
import os
import serial
import logging
from subprocess import Popen, PIPE
from decorators import format_h1, EntryExit
import paramiko

_set_def_val = lambda x, y: y if x is None else x

class Command(object):
    def __init__(self, name=None, timeout=None, error_hint=None, success_hint=None):

        self.name = _set_def_val(name, '')
        self.output = ''
        self.error = ''
        self.status = True
        self.timeout = _set_def_val(timeout, 1)
        self.error_hint = _set_def_val(error_hint, ["not found", "error", "failed"])
        self.success_hint = _set_def_val(success_hint, [])

    def to_list(self):
        cmd_list = re.split('[;]', self.name)
        cmd_list = [cmd + ';' for cmd in cmd_list]

        return cmd_list

    def check_output(self, keywords):
        for key in keywords:
            if key in self.output:
                return True

        return False

    def is_error(self, keywords=None):
        return self.check_output(_set_def_val(keywords, self.error_hint))

    def is_success(self, keywords=None):
        return self.check_output(_set_def_val(keywords, self.success_hint))

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
        self.output_filter = []

    def set_output_filter(self, filter_list=None):
        self.output_filter = _set_def_val(filter_list, [])

    @EntryExit
    def send_command(self, cmd, timeout=None, error_hints=None, success_hints=None, filter_output=True):
        self.logger.debug("%s: send_command() Cmd: %s Timeout: %s err_hint: %s" % (self.name, str(cmd), str(timeout), str(error_hints)))
        self.command = Command(cmd, timeout, error_hints, success_hints)

        return self.command.output, self.command.status

    @EntryExit
    def filter_output(self, output=None, filter_list=None):
        self.logger.debug("Stripping output %s\n" % self(self.command.output))

        output = _set_def_val(output, self.command.output)
        filter_list = _set_def_val(filter_list, self.output_filter)

        newout = []

        for entry in output:
            valid = True
            for bentry in filter_list:
                if bentry in entry:
                    valid = False
            if valid:
                newout.append(entry)

        return newout

    @EntryExit
    def print_output(self):
        self.logger.debug("%s print_output()" % (self.name))
        self.logger.info("%s" % self.command)

    @EntryExit
    def check_output(self, hints=None):
        self.logger.debug("%s check_output() hints:%s" % (self.name, str(hints)))
        return self.command.check_output(hints)

    @EntryExit
    def close(self):
        self.logger.debug("%s close()" % (self.name))

    def __str__(self):
        return self.name

class ShellTerminal(Terminal):
    def __init__(self, name='HOST-SHELL', logger=None):
        super(ShellTerminal, self).__init__(name, logger)

    def send_command(self,  cmd, timeout=1, error_hints=None, success_hints=None, filter_output=True):
        super(ShellTerminal, self).send_command(cmd, timeout, error_hints, success_hints, filter_output)

        proc = Popen(self.command.to_list(), shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        self.command.output, self.command.error = proc.communicate('through stdin to stdout')
        self.command.update_status()

        return self.command.output, self.command.status

class AdbTerminal(ShellTerminal):
    def __init__(self, device="USB-ADB", logger=None):
        super(AdbTerminal, self).__init__(device, logger)

    def send_command(self,  cmd, timeout=1, error_hints=None, success_hints=None, filter_output=True):
        cmd = "adb shell " + cmd
        return super(AdbTerminal, self).send_command(cmd, timeout, error_hints, success_hints, filter_output)

class SSHTerminal(paramiko.SSHClient, Terminal):
    def __init__(self, hostname=None, port=None, username=None, password=None,
                 pkey=None, key_filename=None, logger=None):

        Terminal.__init__(self, hostname, logger)

        paramiko.SSHClient.__init__(self)

        self.load_system_host_keys()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.connect(hostname=hostname, port=port, username=username, password=password, pkey=pkey,
                     key_filename=key_filename)

    def send_command(self,  cmd, timeout=1, error_hints=None, success_hints=None, filter_output=True):

        stdin, stdout, stderr = self.exec_command(cmd)
        self.command.output = stdout.read()
        self.command.update_status()

        return self.command.output, self.command.status

    def close(self):
        self.logger.debug("%s close()" % (self.name))

        super(SSHTerminal, self).close()

class SerialTerminal(serial.Serial, Terminal):
    def __init__(self, port="/dev/ttyUSB0", baud=115200, parity="None", bytesize=8, stopbits=1, hfc=False, sfc=False, timeout=1, logger=None):
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

    def send_command(self, cmd, timeout=-1, error_hints=None, success_hints=None, filter_output=True):
        super(SerialTerminal, self).send_command(cmd, timeout, error_hints, success_hints)

        self.command.name = "\r" + self.command.name + "\r"

        self.flushOutput()
        self.flushInput()
        self.write(self.command.name)
        self.flush()

        tmp_timeout = self.timeout
        if self.command.timeout != -1:
            self.timeout = self.command.timeout

        output = map(lambda it: it.strip('\r'), self.readlines())

        if filter_output is True:
            output = self.filter_output()

        self.command.output = ''.join(output)

        self.timeout = tmp_timeout

        self.command.update_status()

        return self.command.output, self.command.status

class Device(object):
    def __init__(self, name="dev", terminal_list={}, default_terminal=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.name = name
        self.terminal_list = {}
        self.current_terminal = None
        self.default_terminal = None
        for type, terminal_cfg in terminal_list.iteritems():
            index = 0
            terminal = None
            terminal_name = ""
            if type == 'serial':
                for count, params in terminal_cfg.iteritems():
                    terminal = SerialTerminal(port=params['name'], baud=params['baudrate'], parity=params['parity'],
                                              stopbits=params['stopbit'], bytesize=params['bytesize'],
                                              hfc=params['hfc'], sfc=params['sfc'], timeout=params['timeout'])
            elif type == 'usb-adb':
                for count, params in terminal_cfg.iteritems():
                    terminal = AdbTerminal(device=params['name'])
            elif type == 'shell':
                for count, params in terminal_cfg.iteritems():
                    terminal = ShellTerminal(name=params['name'])
            elif type == 'ssh':
                for count, params in terminal_cfg.iteritems():
                    terminal = SSHTerminal(device=params['name'])

            if terminal is not None:
                if len(params['filter_output']) > 0:
                    terminal.set_output_filter(params['filter_output'])
                terminal_name = type + ':' + str(index)
                self.terminal_list[terminal_name] = terminal
                index = index + 1

        if default_terminal is not None and default_terminal in self.terminal_list.keys():
            self.default_terminal = self.terminal_list[default_terminal]

    def _get_terminal(self, channel_name):
        if channel_name in self.terminal_list.keys():
            return self.terminal_list[channel_name]

        if self.default_terminal is not None:
            return self.default_terminal

        if len(self.terminal_list.keys()) > 0:
            return self.terminal_list.values()[0]

        return None

    def _cmd_params(self, cmd_str, default_channel):
        cmd = ''
        channel_name = default_channel

        if ':=' in cmd_str:
            cmd = cmd_str[cmd_str.index(':=') + 2:]
            channel_name = cmd_str[0:cmd_str.index(':=')]

        return cmd, channel_name

    def _exec_cmd(self, cmd, timeout, error_hints, success_hints, default_channel):

        output, status = self.current_terminal.send_command(cmd, timeout, error_hints, success_hints)

        if status is False:
            self.logger.error("Command %s Failed" % cmd)
            self.logger.error(''.join(['*' for i in range(1, 100)]))
            self.logger.error("Actual result: %s" % output)
            self.logger.error(''.join(['*' for i in range(1, 100)]))

        return output, status

    @EntryExit
    def send_command(self, cmds, timeout=1, error_hints=["not found", "error", "failed"], success_hints=[], channel_name=""):
        output, status = "Invalid command", False

        if type(cmds) is list:
            for cmd_str in cmds:
                cmd, channel = self._cmd_params(cmd_str, channel_name)
                self.current_terminal = self._get_terminal(channel)
                if self.current_terminal is None:
                    self.logger.error("Invalid terminal : %s\n", channel_name)
                output, status = self._exec_cmd(cmd, timeout, error_hints, success_hints)
                if status is False:
                    break
        elif type(cmds) is str:
            cmd, channel = self._cmd_params(cmds, channel_name)
            self.current_terminal = self._get_terminal(channel)
            if self.current_terminal is None:
                self.logger.error("Invalid terminal : %s\n", channel_name)
            output, status = self._exec_cmd(cmd, timeout, error_hints, success_hints)

        return output, status

    def print_output(self):
        return self.current_terminal.print_output()

    def check_output(self, hints):
        return self.current_terminal.check_output(hints)

    def __str__(self):
        return format_h1("Device Info") + "\nName: %s\n" % self.name + "Default Terminal: %s\n" % self.default_terminal +\
               "Current Terminal: %s\n" % self.current_terminal + "Terminal List: %s\n" % str(self.terminal_list.keys()) +\
               format_h1()

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(message)s')
    logger.setLevel(logging.INFO)
    #terminal = SSHTerminal(hostname="192.168.1.103", username='root', port=22)
    #print terminal.send_command('ls')
    terminal = SerialTerminal(port="/dev/ttyUSB0")
    #terminal = AdbTerminal(device="sathya")
    terminal.send_command("ls /bin", timeout=1, strip_output=['root@linaro-alip:~#'])
    terminal.print_output()