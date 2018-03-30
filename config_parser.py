import os
import sys
import logging
from configparser import ExtendedInterpolation
from configparser import ConfigParser, SafeConfigParser
from usb_config_template import config_template

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)

__all__ = ("Namespace", "as_namespace")

config_type_map = {
    'str' : (str, 'get'),
    'int' : (int, 'getint'),
    'bool': (bool, 'getboolean'),
    'float': (int, 'getfloat'),
}

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

    def compare_template(self):
        if self.template is None:
            return True
        for section in self.parser.sections():
            if section not in self.template.keys():
                logger.debug("section %s does not exist in template" % section)
                return False
            for option in self.parser.options(section):
                if option not in self.template[section].keys():
                    logger.debug("option %s does not exist in template" % option)
                    return  False
        return  True

    def __init__(self, cfg, template=None):

        if not os.path.exists(os.path.abspath(cfg)):
            raise IOError("File %s does not exist" % cfg)

        self.cfg_file =  cfg
        self.template = template
        self.parser = ConfigParser()
        self.parser.read(cfg)

        if not self.compare_template():
            raise IOError("Template does not match config")

        cfg_dict = {}

        for section in self.parser.sections():
            res = {}
            for option in self.parser.options(section):
                if template is not None:
                    type = config_type_map[template[section][option][0]][0]
                    getfunc = config_type_map[template[section][option][0]][1]
                    default = template[section][option][1]
                    res[option] = type(getattr(self.parser, getfunc)(section, option))
                    if default != [] and res[option] not in default:
                        logger.debug(default)
                        logger.debug(res[option])
                        raise IOError("value does not match defaults")
                else:
                    res[option] = getattr(self.parser, "get")(section, option)

                cfg_dict[section] = Namespace(res)

        self.cfg = Namespace(cfg_dict)



if __name__ == "__main__":

    obj = TestConfigParser("usb-config.ini", config_template)
    print obj.cfg
    print "test"