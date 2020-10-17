#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
################################################################################
About Path(File,Directory,Atty,Link etc)
################################################################################
"""

import os
import ctypes
import warnings

from minghu6.etc.version import iswin

__all__ = ['get_cwd_pre_dir',
           'get_cwd_preDir',
           'get_pre_path',
           'add_parent_path',
           'isempty_dir',
           'isempty_file',
           'add_postfix']


################################################################################
class DirectoryConflicsError(Exception):
    """The first arg of the exception should be conflicted directory path"""
    pass


def get_cwd_preDir(n):
    """
    equal to get_cwd_pres_dir
    :param n:
    :return:
    """
    return get_cwd_pre_dir(n)


def get_cwd_pre_dir(n):
    """
    get n level before cwd 's dir
    """
    path = get_pre_path(path=os.getcwd(), plevel=n)

    return path


def get_pre_path(path, plevel=1):
    warnings.warn("use pathlib.Path(path).parents[plevel-1] instead.", DeprecationWarning)

    def get_parent_dir(path):
        """
        get one level before path
        """
        # print(path)
        path = os.path.abspath(path)
        return os.path.split(path)[0]

    for i in range(plevel):
        path = get_parent_dir(path)

    return path


################################################################################


def add_parent_path(path, plevel=1):
    path = get_pre_path(path, plevel)
    os.path.join(path)


def isempty_file(fn):
    with open(fn, 'rb') as f:
        length = len(f.read(1))
    return length == 0


def isempty_dir(fn):
    return os.listdir(fn).__len__() == 0


def add_postfix(fn, postfix, sep='_'):
    name, ext = os.path.splitext(fn)

    return ''.join([name, sep, postfix, ext])


def get_home_dir():

    warnings.warn("use pathlib.Path.home instead.", DeprecationWarning)
    return os.path.expanduser('~')


def get_drivers():
    if not iswin():
        raise OSError('only support in Windows')

    lp_buffer = ctypes.create_string_buffer(78)
    ctypes.windll.kernel32.GetLogicalDriveStringsA(ctypes.sizeof(lp_buffer), lp_buffer)
    drivers = lp_buffer.raw.split(b'\x00')

    return [each_driver.decode()[:2] for each_driver in drivers if each_driver and os.path.isdir(each_driver)]


def ensure_dir_exists(path):
    if not os.path.isdir(path):
        if os.path.lexists(path):  # broken link is True
            raise DirectoryConflicsError(path)
        else:
            os.makedirs(path)


def path_level(path):
    """
    >>> path_level('/home/john')
    2
    >>> path_level('/home/john/')
    3
    """

    def _path_level(path, n=0):
        dir_path = os.path.dirname(path)
        if path == dir_path:
            return n
        else:
            n += 1
            return _path_level(dir_path, n)

    return _path_level(path)


def path_to(from_path: str, to_path: str):
    """
    Warning: this function is OS dependent

    >>> path_to('/home/john/coding', '/home/alice/Download')
    '../../alice/Download'
    >>> path_to('/home/john/coding', '/home/john/coding/tmp')
    './tmp'
    >>> try:
    ...     path_to('d:\\abc', 'c:\\abc\\def')
    ... except ValueError as ex:
    ...     print(ex)
    Paths don't have the same drive
    """
    from_path = os.path.abspath(from_path)
    to_path = os.path.abspath(to_path)

    if iswin() and os.path.splitdrive(from_path) != os.path.splitdrive(to_path):
        return to_path
    else:
        common_path = os.path.commonpath([from_path, to_path])

    from_extra_path = from_path.split(common_path)[1]
    to_extra_path = to_path.split(common_path)[1]

    parpath = os.path.sep.join([os.pardir] * path_level(from_extra_path))

    if parpath:
        target_path = parpath + to_extra_path
    else:
        target_path = os.curdir + to_extra_path

    return target_path


def is_relative_path(path):
    """don't care about if the path exists"""
    if iswin():
        if not os.path.splitdrive(path)[0]:
            return False
        else:
            return True
    else:
        if path.startswith('/'):
            return False
        else:
            return True
