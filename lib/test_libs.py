import os
import sys
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.ERROR)



class TestLib(object):
    def __init__(self):
        logger.debug("Testparser init()")

    def print_result(self, id, params, output, status):
        print ''.join(['=' for i in range(1, 100)])
        print "\nTest ID: %s" % id
        print "Test type: %s" % params['type']
        print "Test name: %s" % params['name']
        print "Test status: %s" % ("passed" if status else "failed")
        print ''.join(['=' for i in range(1, 100)])
        sys.stdout.flush()
        logger.debug("Expected result: %s" % params['cmd_expected_result'])
        logger.debug("Actual result: %s" % output)

    def _execute_cmd(self, host, dut, cmd_str, cmd_timeout, cmd_expected_result, hint):
        output, status = "Invalid command", False
        if cmd_str.startswith('host:'):
            cmd = cmd_str[5:]
            output, status = host.send_command(cmd, cmd_timeout, hint)
            if cmd_expected_result != '':
                status = host.check_output(cmd_expected_result)
        elif cmd_str.startswith('remote:'):
            cmd = cmd_str[7:]
            output, status = dut.send_command(cmd, cmd_timeout, hint)
            if cmd_expected_result != '':
                status = dut.check_output(cmd_expected_result)

        if status is False:
            logger.debug("Command %s Failed" % cmd_str)
            logger.debug("Actual result: %s" % output)

        return output, status

    def execute_cmd_list(self, host, dut, cmd_list, cmd_timeout, cmd_expected_result, hint):
        output, status = "Invalid command", False

        for cmd_str in cmd_list:
            output, status = self._execute_cmd( host, dut, cmd_str, cmd_timeout, cmd_expected_result, hint)
            if status is False:
                break

        return output, status

    def execute_test(self, host, dut, id, params):
        output, status = "Invalid command", False
        get_cmd_params = lambda x, i: params[x][i] if i < len(params[x]) else params['default_' + x]

        for index, cmd_str in enumerate(params['cmd_list']):
            cmd = ''
            cmd_timeout = get_cmd_params('cmd_timeout', index)
            cmd_error_hint = get_cmd_params('cmd_error_hint', index).split('|')
            cmd_expected_result = get_cmd_params('cmd_expected_result', index)

            output, status = self._execute_cmd(host, dut, cmd_str, cmd_timeout, cmd_expected_result, cmd_error_hint)
            if status is False:
                break

        self.print_result(id, params, output, status)

        return output, status


