# -*- coding:utf-8 -*-
# !/usr/bin/env python3

"""
################################################################################
About decorator
################################################################################
"""
from functools import partial
import inspect

from minghu6.text.seq_enh import camelize

__all__ = ['LackMethodError', 'LackPropertyError',
           'require_vars',
           'exception_handler',
           'ignore',
           'mock_func',
           'singleton',
           'timer']


class LackPropertyError(BaseException):
    pass


class LackMethodError(BaseException):
    pass


def require_vars(property_args=set(), method_args=set()):
    """Class decorator to require methods on a subclass.
    pyversion >= 2.6
    Example usage
    ------------
    @require_methods(prperty_args=['m1'], method_args=['m2'])
    class C(object):
        'This class cannot be instantiated'
        'unless the subclass defines m1 and m2().'
        def __init__(self):
            pass
    """
    import sys
    if sys.version_info.major == 2 and sys.version_info.minor < 6:
        raise Exception('python version do not support this decorator')

    def fn(cls):
        orig_init = cls.__init__

        def init_wrapper(self, *args, **kwargs):
            for method in method_args:
                if (not (method in dir(self))) or \
                        (not callable(getattr(self, method))):
                    raise LackMethodError(("Required method `%s` "
                                           "not implemented") % method)

            for each_property in property_args:
                if (not (each_property in dir(self))) or \
                        (callable(getattr(self, each_property))):
                    raise LackPropertyError(("Required property `%s` "
                                             "not implemented") % each_property)

            orig_init(self, *args, **kwargs)

        cls.__init__ = init_wrapper
        return cls

    return fn


def exception_handler(*kwargs):
    """
    An exception handling idiom using decorators
    Specify exceptions in order, first one is handled first
    last one last.
    """
    import warnings
    warnings.warn("decorator exception_handler is deprecated, use handle_exception instead.", DeprecationWarning)

    def wrapper(f):
        if kwargs:
            (handler, li) = kwargs
            t = [(ex, handler)
                 for ex in li]
            t.reverse()
        else:
            t = [(Exception, None)]

        def newfunc(t, *args, **func_kwargs):  # recursion
            ex, handler = t[0]

            try:
                if len(t) == 1:
                    f(*args, **func_kwargs)
                else:
                    newfunc(t[1:], *args, **func_kwargs)
            except ex as e:
                if handler:
                    handler(e)
                else:
                    print(e.__class__.__name__, ':', e)

        return partial(newfunc, t)

    return wrapper


def handle_exception(exception_handler, exception_classes):
    """
    An exception handling idiom using decorators
    Specify exceptions in order, first one is handled first
    last one last.
    >>> def handler(ex):
    ...     print(ex, type(ex))
    ...     return ex.args
    >>> from collections import OrderedDict
    >>> @handle_exception(handler, Exception)
    ... def f():
    ...     d=OrderedDict()
    ...     d['a']=1
    ...     d['b']=2
    ...     raise Exception([1, 2, '3'], d)
    >>> f()
    ([1, 2, '3'], OrderedDict([('a', 1), ('b', 2)])) <class 'Exception'>
    ([1, 2, '3'], OrderedDict([('a', 1), ('b', 2)]))
    >>> @handle_exception(handler, (FileExistsError, FileNotFoundError))
    ... def f2():
    ...     raise FileNotFoundError('abc.txt')
    >>> f2()
    abc.txt <class 'FileNotFoundError'>
    ('abc.txt',)
    """

    def wrapper(f):
        nonlocal exception_classes

        if inspect.isclass(exception_classes):
            exception_classes = [exception_classes]

        exception_chain = list(exception_classes)
        exception_chain.reverse()  # for recursive invokation

        def newfunc(exception_chain, *args, **kwargs):  # recursion
            exception_class = exception_chain[0]

            try:
                if len(exception_chain) == 1:
                    result = f(*args, **kwargs)
                else:
                    result = newfunc(exception_chain[1:], *args, **kwargs)  # spread exception
            except exception_class as ex:
                return exception_handler(ex)
            else:
                return result

        return partial(newfunc, exception_chain)

    return wrapper


def cli_handle_exception(exception_handler, exception_classes):
    """
    deal with exception stack info, and then just throw the wrapper exception by cli
    >>> def cli_handler1(ex):
    ...     assert False, 'Need root permission'
    >>> @cli_handle_exception(cli_handler1, ZeroDivisionError)
    ...     def f():
    ...         1/0
    >>> f()
    AssertionError                            Traceback (most recent call last)
    <ipython-input-9-c43e34e6d405> in <module>()
    ----> 1 f()

    <ipython-input-7-1220a5dc628a> in newfunc(exception_chain, *args, **kwargs)
         25                 return result
         26
    ---> 27             exception_handler(raised_exception)
         28
         29         return partial(newfunc, exception_chain)

    <ipython-input-4-7313ecff13f5> in cli_handler1(ex)
          1 def cli_handler1(ex):
    ----> 2     assert False, 'Need root permission'

    AssertionError: Need root permission
    """
    import inspect
    from functools import partial

    def wrapper(f):
        nonlocal exception_classes

        if inspect.isclass(exception_classes):
            exception_classes = [exception_classes]

        exception_chain = list(exception_classes)
        exception_chain.reverse()  # for recursive invokation

        def newfunc(exception_chain, *args, **kwargs):  # recursion
            exception_class = exception_chain[0]
            raised_exception = None
            try:
                if len(exception_chain) == 1:
                    result = f(*args, **kwargs)
                else:
                    result = newfunc(exception_chain[1:], *args, **kwargs)  # spread exception
            except exception_class as ex:
                raised_exception = ex  # goto next exception_handler to clean old exception stack.
            else:
                return result

            exception_handler(raised_exception)

        return partial(newfunc, exception_chain)

    return wrapper


REQUIRED = 'required'
def required(f):
    def wrapper_func(*args, **kwasrgs):
        raise NotImplementedError

    setattr(wrapper_func, REQUIRED, True)

    return wrapper_func


def ignore(func):
    """
    ignore all exception,
    Usage: @ignore
            def func():
               #...
               pass

    :param func:
    :return:
    """

    def func_pass(ex):
        pass

    return partial(handle_exception, func_pass, Exception)


def assert_exception(exception):
    def wrapper(func):
        def new_func():
            assert_true = False
            exception_received = None

            try:
                func()
            except exception:
                pass
            except Exception as ex:
                assert_true = True
                exception_received = ex

            if assert_true:
                raise AssertionError(exception_received)

        return new_func

    return wrapper


def mock_func(*return_args, **return_kwargs):
    def wrapper(f):
        def inner(*inner_args, **inner_kwargs):
            if not return_args and not return_kwargs:
                return None
            else:
                return return_args + tuple(return_kwargs.values())

        return inner

    return wrapper


skip = mock_func()


def singleton(cls):
    """
    More Advanced Select Enable Version can ref metaclass.singleton_basic
    :param cls:
    :return:
    """
    instances = {}

    def default_get_instance_key(*args, **kwargs):
        return 'singleton'

    def _singleton(*args, **kw):
        get_instance_key = getattr(cls, '_get_instance_key', default_get_instance_key)
        instance_key = get_instance_key(*args, **kw)

        if instance_key not in instances:
            instances[instance_key] = cls(*args, **kw)

        return instances[instance_key]

    for method_name in filter(lambda name: not (name.startswith('__') and name.endswith('__')), dir(cls)):
        setattr(_singleton, method_name, getattr(cls, method_name))

    return _singleton


def timer(label='', unit='ms', trace=True):  # On decorator args: retain args
    import time

    def onDecorator(func):  # On @: retain decorated func
        def onCall(*args, **kargs):  # On calls: call original
            start = time.process_time() # State is scopes + func attr
            result = func(*args, **kargs)
            elapsed = time.process_time() - start
            onCall.alltime += elapsed
            if trace:
                unit_conversion = {'ms': 1e3,
                                   's': 1,
                                   'min': 1 / 60,
                                   'h': 1 / (60 * 60)
                                   }

                format = '%s%s: %.5f, %.5f %s'
                values = (label, func.__name__,
                          elapsed * unit_conversion[unit],
                          onCall.alltime * unit_conversion[unit],
                          unit)

                print(format % values)

            return result

        onCall.alltime = 0
        return onCall

    return onDecorator


def to_class(return_func_name='get_result'):
    def wrapper(func):
        def __init__(self, *args, **kwargs):
            self._result = func(*args, **kwargs)

        def get_result_func(self):
            return self._result

        cls_name = camelize(func.__name__)
        cls_dict = {'__init__': __init__, return_func_name: get_result_func}
        one_class = type(cls_name, (list,), cls_dict)

        return one_class

    return wrapper


if __name__ == '__main__':

    @require_vars(property_args=['a'], method_args=['a'])
    class T:
        @property
        def a(self):
            print('haha')


    try:
        T()
    except Exception as e:
        print(e)


    @singleton
    class T2:
        def __init__(self, t=2):
            self.t = t

        pass


    t1 = T2()
    # print(t1.t)
    t2 = T2()
    assert t1 == t2


    def myhandler(e):
        print('Caught exception!', e)


    # Examples
    # Specify exceptions in order, first one is handled first
    # last one last.

    @exception_handler(myhandler, (ZeroDivisionError,))
    @exception_handler(None, (AttributeError, ValueError))
    def f1():
        1 / 0


    @exception_handler()
    def f3(*pargs):
        l = pargs
        return l.index(10)


    f1()
    f3()
