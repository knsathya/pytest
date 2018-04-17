import os
import sys
import logging
from decorators import format_h1, EntryExit

class TestHandlers(object):
    def __init__(self, setup, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("TestHandlers init()")
        self.setup = setup

    @EntryExit
    def print_result(self, id, params, output, status):
        self.logger.info(format_h1("%s test results" % str(id)))
        self.logger.info("Test ID: %s" % id)
        self.logger.info("Test type: %s" % params['type'])
        self.logger.info("Test name: %s" % params['name'])
        self.logger.info("Test status: %s" % ("passed" if status else "failed"))
        self.logger.debug("Expected result: %s" % params['cmd_expected_result'])
        self.logger.debug("Actual result: %s" % output)
        self.logger.info(''.join(['=' for i in range(1, 100)]))

    @EntryExit
    def _execute_cmd(self, host, remote, cmd_str, cmd_timeout, error_hints, success_hints):
        output, status = "Invalid command", False
        if cmd_str.startswith('host:'):
            cmd = cmd_str[5:]
            output, status = host.send_command(cmd, cmd_timeout, error_hints, success_hints)
        elif cmd_str.startswith('remote:'):
            cmd = cmd_str[7:]
            output, status = remote.send_command(cmd, cmd_timeout, error_hints, success_hints)

        if status is False:
            self.logger.error("Command %s Failed" % cmd_str)
            self.logger.error(''.join(['*' for i in range(1, 100)]))
            self.logger.error("Actual result: %s" % output)
            self.logger.error(''.join(['*' for i in range(1, 100)]))

        return output, status

    @EntryExit
    def execute_cmd_list(self, host, remote, cmd_list, timeout, error_hints, success_hints):
        output, status = "Invalid command", False

        for cmd_str in cmd_list:
            output, status = self._execute_cmd( host, remote, cmd_str, timeout, error_hints, success_hints)
            if status is False:
                break

        return output, status

    @EntryExit
    def execute_test(self, host, remote, id, params):
        output, status = "Invalid command", False
        get_cmd_params = lambda x, i: params[x][i] if i < len(params[x]) else params['default_' + x]

        for index, cmd_str in enumerate(params['cmd_list']):
            timeout = get_cmd_params('cmd_timeout', index)
            error_hints = get_cmd_params('cmd_error_hint', index).split('|')
            success_hints = get_cmd_params('cmd_expected_result', index).split('|')

            output, status = self._execute_cmd(host, remote, cmd_str, timeout, error_hints, success_hints)
            if status is False:
                break

        self.print_result(id, params, output, status)

        return output, status


