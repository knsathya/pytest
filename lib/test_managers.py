import os
import yaml
import logging
from lib.configobj import ConfigObj,flatten_errors
from lib.configobj.validate import Validator
from terminal import ShellTerminal, SerialTerminal, AdbTerminal
from decorators import format_h1, EntryExit

class TestManager(object):

    def _validate(self, obj):
        validator = Validator()
        results = obj.validate(validator)
        if results != True:
            for (section_list, key, _) in flatten_errors(obj, results):
                if key is not None:
                    raise Exception(
                        'The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list)))
                else:
                    raise Exception('The following section was missing:%s ' % ', '.join(section_list))

    def _key_check(self, configobj, *keys):
        obj = configobj
        for key in keys:
            if key not in obj.keys():
                return False
            else:
                obj = configobj[key]

        return True

    def _config_check(self, cfg):
        if not os.path.exists(cfg):
            raise IOError("File %s does not exists" % cfg)

    @EntryExit
    def _create_terminal(self, terminal):
        self.logger.debug(format_h1("Create %s terminal" % terminal['type']))
        if terminal['type'] == 'serial':
            return SerialTerminal(port=terminal['name'], baud=terminal['baudrate'],
                                  parity=terminal['parity'], stopbits=terminal['stopbit'],
                                  bytesize=terminal['bytesize'], hfc=terminal['hfc'], sfc=terminal['sfc'],
                                  timeout=terminal['timeout'])
        elif terminal['type'] == 'usb-adb':
            return  AdbTerminal()
        else:
            return ShellTerminal()

    @EntryExit
    def _setup_remote(self):
        self.logger.debug(format_h1("Setup remote"))
        self.remote.send_command(self.remote_params['login_cmd'])
        self.remote.send_command(self.remote_params['setup_cmd'])

    @EntryExit
    def _reset_remote(self):
        self.logger.debug(format_h1("Reset remote"))
        self.remote.send_command(self.remote_params['reset_cmd'])
        self.remote.send_command(self.remote_params['exit_cmd'])

    def __init__(self, setup_cfg, setup_spec, test_cfg, test_spec,
                 test_handlers, user_setup_cfg='', user_test_cfg='',
                 logger=None):

        self.logger = logger or logging.getLogger(__name__)

        for cfg in [setup_cfg, setup_spec, test_cfg, test_spec]:
            self._config_check(cfg)

        self.setupobj = ConfigObj(setup_cfg, configspec=setup_spec)
        self._validate(self.setupobj)

        if os.path.exists(user_setup_cfg):
            userobj = ConfigObj(user_setup_cfg, configspec=setup_spec)
            self._validate(userobj)
            self.setupobj.merge(userobj)

        self.testobj = ConfigObj(test_cfg, configspec=test_spec)
        self._validate(self.testobj)

        if os.path.exists(user_test_cfg):
            userobj = ConfigObj(user_test_cfg, configspec=test_spec)
            self._validate(userobj)
            self.testobj.merge(userobj)

        self.logger.debug(self.setupobj)
        self.logger.debug(self.testobj)

        host_keys = self.setupobj['test']['preffered-host-terminal'].split(':')
        remote_keys = self.setupobj['test']['preffered-remote-terminal'].split(':')


        self.host_params = self.setupobj[host_keys[0]][host_keys[1]][host_keys[2]]
        self.remote_params = self.setupobj[remote_keys[0]][remote_keys[1]][remote_keys[2]]

        self.host = self._create_terminal(self.host_params)
        self.remote = self._create_terminal(self.remote_params)

        self.test_handlers = test_handlers

    def _print_test_details(self, test):
        self.logger.debug(format_h1(" Test Details "))
        self.logger.debug("Name: %s" % test['name'])
        self.logger.debug("Type: %s" % test['type'])
        self.logger.debug("Handler: %s" % test['handler'])
        self.logger.debug("Local Cmd Timeout: %s" % test['local_cmd_timeout'])
        self.logger.debug("Local Cmd: %s" % test['local_cmd'])
        self.logger.debug("Remote Cmd Timeout: %s" % test['remote_cmd_timeout'])
        self.logger.debug("Remote Cmd: %s" % test['remote_cmd'])
        self.logger.debug("Remote Cmd Expected Results: %s" % test['remote_expected_result'])
        self.logger.debug(format_h1())

    @EntryExit
    def exec_tests(self, index=-1):
        self._setup_remote()
        if index == -1:
            for id, params in self.testobj.iteritems():
                env = self.setupobj['remote']['env']
                for handler in params['handler']:
                    self.logger.info(format_h1("Executing Test ID:%s Handler:%s()" % (str(id), str(handler))))
                    output, status = getattr(self.test_handlers, handler)(self.host, self.remote, id, dict(params.items() + env.items()))
        elif index >= 0:
            count = -1
            for id, params in self.testobj.iteritems():
                count =  count + 1
                if count == index:
                    env = self.setupobj['remote']['env']
                    for handler in params['handler']:
                        self.logger.info(format_h1("Executing Test ID:%s Handler:%s()" % (str(id), str(handler))))
                        output, status = getattr(self.test_handlers, handler)(self.host, self.remote, id, dict(params.items() + env.items()))
        self._reset_remote()