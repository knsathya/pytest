import logging

def format_h1(str='', width=100, fc='='):
    str_len = len(str)
    if len(str) < width:
        flen = (width - str_len) / 2
        return ''.join([fc for i in range(1, flen)]) + str + ''.join([fc for i in range(1, flen)])
    else:
        return "\n" + str + "\n"

class Decorator(object):
    def __init__(self, func, obj_=None, type_=None):
        self.func = func
        self.type = type_
        self.obj = obj_

    def __get__(self, obj, type_=None):
        func = self.func.__get__(obj, type_)
        return self.__class__(func, obj, type_)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class EntryExit(Decorator):
    def __init__(self, func, obj_=None, type_=None):
        self.func = func
        self.type = type_
        self.obj = obj_

    def __get__(self, obj, type_=None):
        func = self.func.__get__(obj, type_)
        return self.__class__(func, obj, type_)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
        #print('called %s with args=%s kwargs=%s' % (name, args, kwargs))
        name = '%s.%s' % (self.type.__name__, self.func.__name__)
        if hasattr(self.obj, 'logger'):
            self.obj.logger.debug(format_h1("%s() Entry" % name))
        else:
            print format_h1("%s() Entry" % name)

        ret = self.func(*args, **kwargs)

        if hasattr(self.obj, 'logger'):
            self.obj.logger.debug(format_h1("%s() Exit" % name))
        else:
            print format_h1("%s() Exit" % name)

        return ret
