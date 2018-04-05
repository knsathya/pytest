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

    def generic_test(self, host, dut, id, params):

        get_cmd_params = lambda x, i: params[x][i] if i < len(params[x]) else params['default_' + x]

        for index, cmd_str in enumerate(params['cmd_list']):
            output, status = "Invalid command", False
            cmd = ''
            cmd_timeout = get_cmd_params('cmd_timeout', index)
            cmd_error_hint = get_cmd_params('cmd_error_hint', index).split('|')
            cmd_expected_result = get_cmd_params('cmd_expected_result', index)
            if cmd_str.startswith('host:'):
                cmd = cmd_str[5:]
                print cmd
                output, status = host.send_command(cmd, cmd_timeout, cmd_error_hint)
                if cmd_expected_result != '':
                    status = dut.check_output(cmd_expected_result)
            elif cmd_str.startswith('remote:'):
                cmd = cmd_str[7:]
                print cmd
                output, status = dut.send_command(cmd, cmd_timeout, cmd_error_hint)
                if cmd_expected_result != '':
                    status = dut.check_output(cmd_expected_result)

            self.print_result(id, params, output, status)

    def configure_gadget(self, host, dut, id, params, gadget_type):
        cmd_list = ['stop adbd']
        cmd_list.append("echo \"\" > " + os.path.join(params['gadget_path'], 'UDC'))
        cmd_list.append("echo 0xa4a0 > " + os.path.join(params['gadget_path'], 'idProduct'))
        cmd_list.append("echo 0x0525 > " + os.path.join(params['gadget_path'], 'idVendor'))
        if gadget_type == 'SourceSink':
            cmd_list.append("rm " + os.path.join(params['gadget_config_path'], 'f1'))
            cmd_list.append("ln -s " + params['sourcesink_fpath'] + ' ' + os.path.join(params['gadget_config_path'], 'f1'))
        cmd_list.append("echo "+ params['controller'] + " > " + os.path.join(params['gadget_path'], 'UDC'))

        for cmd in cmd_list:
            dut.send_command(cmd, params['remote_cmd_timeout'], params['remote_cmd_error_hint'])

    def exec_remote_cmd(self, host, dut, id, params):
        if params['remote_cmd'] != '':
            output, status = dut.send_command(params['remote_cmd'], params['remote_cmd_timeout'], params['remote_cmd_error_hint'])
            status = dut.check_output(params['remote_expected_result'])
            self.print_result(id, params, output, status)
            return output, status
        else:
            return "Invalid command", False

    def lspci_test(self, host, dut, id, params):
        params['remote_cmd'] = 'lspci -k'
        return self.exec_remote_cmd(host, dut, id, params)

    def nop_test(self, host, dut, id, params):
        self.print_result(id, params, 'NOP', True)
        return "NOP command", False

    def usb_device_test(self, host, dut, id, params):
        self.configure_gadget(host, dut, id, params, 'SourceSink')
        print params['host_cmd']
        host.send_command(params['host_cmd'], params['host_cmd_timeout'], params['host_cmd_error_hint'])


