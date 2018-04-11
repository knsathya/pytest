import os
import logging
from terminal import AdbTerminal, SerialTerminal, ShellTerminal, SSHTerminal

class Device(object):
    def __init__(self, name="dev", terminal_list={}, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.name = name
        self.terminal = {'serial':[], 'usb-adb':[], 'shell':[], 'ssh':[]}
        for type, terminal_cfg in terminal_list.iteritems():
            if type == 'serial':
                for count, params in terminal_cfg.iteritems():
                    terminal = SerialTerminal(port=params['name'], baud=params['baudrate'], parity=params['parity'],
                                              stopbits=params['stopbit'], bytesize=params['bytesize'],
                                              hfc=params['hfc'], sfc=params['sfc'], timeout=params['timeout'])
                    self.terminal[type].append(terminal)

            elif type == 'usb-adb':
                for count, params in terminal_cfg.iteritems():
                    terminal = AdbTerminal(name=params['name'])
                    self.terminal[type].append(terminal)
            elif type == 'shell':
                for count, params in terminal_cfg.iteritems():
                    terminal = ShellTerminal(name=params['name'])
                    self.terminal[type].append(terminal)
            elif type == 'ssh':
                for count, params in terminal_cfg.iteritems():
                    terminal = SSHTerminal(name=params['name'])
                    self.terminal[type].append(terminal)

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


