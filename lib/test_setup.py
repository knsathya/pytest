import os
import logging
from terminal import AdbTerminal, SerialTerminal, ShellTerminal, SSHTerminal
from config_parser import ConfigParse
from decorators import format_h1

class Device(object):
    def __init__(self, name="dev", terminal_list={}, default_terminal=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.name = name
        self.terminal_list = {}
        self.current_terminal = None
        self.default_terminal = None
        for type, terminal_cfg in terminal_list.iteritems():
            index = 0
            if type == 'serial':
                for count, params in terminal_cfg.iteritems():
                    terminal = SerialTerminal(port=params['name'], baud=params['baudrate'], parity=params['parity'],
                                              stopbits=params['stopbit'], bytesize=params['bytesize'],
                                              hfc=params['hfc'], sfc=params['sfc'], timeout=params['timeout'])
                    terminal_name = type + '-' + str(index)
                    self.terminal_list[terminal_name] = terminal
                    index = index + 1
            elif type == 'usb-adb':
                for count, params in terminal_cfg.iteritems():
                    terminal = AdbTerminal(device=params['name'])
                    terminal_name = type + '-' + str(index)
                    self.terminal_list[terminal_name] = terminal
                    index = index + 1
            elif type == 'shell':
                for count, params in terminal_cfg.iteritems():
                    terminal = ShellTerminal(name=params['name'])
                    terminal_name = type + '-' + str(index)
                    self.terminal_list[terminal_name] = terminal
                    index = index + 1
            elif type == 'ssh':
                for count, params in terminal_cfg.iteritems():
                    terminal = SSHTerminal(device=params['name'])
                    terminal_name = type + '-' + str(index)
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

    def send_command(self, cmd, timeout=1, error_hints=["not found", "error", "failed"], success_hints=[], channel_name=""):
        self.current_terminal = self._get_terminal(channel_name)
        if self.current_terminal is None:
            self.logger.error("Invalid terminal : %s\n", channel_name)

        return self.current_terminal.send_command(cmd, timeout, error_hints, success_hints)

    def print_output(self):
        return self.current_terminal.print_output()

    def check_output(self, hints):
        return self.current_terminal.check_output(hints)

    def __str__(self):
        return format_h1("Device Info") + "\nName: %s\n" % self.name + "Default Terminal: %s\n" % self.default_terminal +\
               "Current Terminal: %s\n" % self.current_terminal + "Terminal List: %s\n" % str(self.terminal_list.keys()) +\
               format_h1()

class TestSetup(object):

    def __init__(self, setup_cfg, setup_spec, setup_user='', logger=None):
        self.logger = logger or logging.getLogger(__name__)

        self.cfg = ConfigParse(setup_cfg, setup_spec, setup_user, logger).get_cfg()

        params = self.cfg['host']

        self.host = Device(name=params['name'], terminal_list=params['terminal'],
                           default_terminal=params['default_terminal'], logger=logger)

        params = self.cfg['remote']

        self.remote = Device(name=params['name'], terminal_list=params['terminal'],
                             default_terminal=params['default_terminal'], logger=logger)


if __name__ =="__main__":
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    setup =  TestSetup('./config-defaults/gpmrb-base-test-setup.ini', './config-specs/test-setup-spec.ini', logger=logger)

    print setup.cfg

    print setup.host
    print setup.remote

    print setup.remote.send_command('cat /proc/version')