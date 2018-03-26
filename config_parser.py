import os
import sys
import logging
from configparser import ExtendedInterpolation
from configparser import ConfigParser, SafeConfigParser

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)

def config_to_dict(parser):
    cfg_dict = {}
    for section in parser.sections():
        cfg_dict[section] = {}
        for option in parser.options(section):
            cfg_dict[section][option] = parser.get(section, option)

    return cfg_dict

template = {
    'remote_terminal' : (
        True, dict,
        {
            'type' : (True, "get", ['serial', 'adb', 'local'])
        }
    ),
    'serial' : (
        False, dict,
        {
            'name' : (True, "get", None),
            'baudrate' : (True, "getint", [9600, 115200]),
            'parity' : (True, "get", ['Odd', 'Even', 'None']),
            'stopbit' : (True, "getint", [1.5, 1, 2]),
            'bytesize' : (True, "getint", [8, 7, 6, 5]),
            'hfc' : (True, "getboolean", [True, False]),
            'sfc' : (True, "getboolean", [True, False])
        }
    ),
    'adb'   : (
        False, dict,
        {
            'name' : (True, "get", None)
        }
    ),
    'local'   : (
        False, dict,
        {
            'name' : (True, "get", None)
        }
    ),
    'test_1'    : (
        False, dict,
        {
            'name'  : (True, "get", None),
            'type'  : (True, "get", None),
            'remote_cmd'    : (False, "get", None),
            'local_cmd' : (False, "get", None),
            'expected_remote_result': (False, "get", None),
            'expected_local_result': (False, "get", None),
        }
    )
}

__all__ = ("Namespace", "as_namespace")

class Namespace(dict, object):
    """A dict subclass that exposes its items as attributes.

    Warning: Namespace instances do not have direct access to the
    dict methods.

    """

    def __init__(self, obj={}):
        super(Namespace, self).__init__(obj)

    def __dir__(self):
        return tuple(self)

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__,
                super(Namespace, self).__repr__())

    def __getattribute__(self, name):
        try:
            return self[name]
        except KeyError:
            msg = "'%s' object has no attribute '%s'"
            raise AttributeError(msg % (type(self).__name__, name))

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    #------------------------
    # "copy constructors"

    @classmethod
    def from_object(cls, obj, names=None):
        if names is None:
            names = dir(obj)
        ns = {name:getattr(obj, name) for name in names}
        return cls(ns)

    @classmethod
    def from_mapping(cls, ns, names=None):
        if names:
            ns = {name:ns[name] for name in names}
        return cls(ns)

    @classmethod
    def from_sequence(cls, seq, names=None):
        if names:
            seq = {name:val for name, val in seq if name in names}
        return cls(seq)

    #------------------------
    # static methods

    @staticmethod
    def hasattr(ns, name):
        try:
            object.__getattribute__(ns, name)
        except AttributeError:
            return False
        return True

    @staticmethod
    def getattr(ns, name):
        return object.__getattribute__(ns, name)

    @staticmethod
    def setattr(ns, name, value):
        return object.__setattr__(ns, name, value)

    @staticmethod
    def delattr(ns, name):
        return object.__delattr__(ns, name)

class TestConfigParser(object):
    def __init__(self, cfg):
        if not os.path.exists(os.path.abspath(cfg)):
            raise IOError("File %s does not exist" % cfg)
        self.cfg_file =  cfg
        self.parser = ConfigParser()
        self.parser.read(cfg)
        self.cfg = config_to_dict(self.parser)

        if not self.parser.has_section("remote_terminal"):
            raise Exception("Missing terminal section")

        if self.parser.get("remote_terminal", "type") not in ["local", 'adb', 'serial']:
            raise Exception("Invalid terminal type %s" % self.parser.get("terminal", "type"))

    def get_params(self, section):
        res = {}



if __name__ == "__main__":

    TestConfigParser("usb-config.ini")