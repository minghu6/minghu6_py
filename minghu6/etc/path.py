#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
################################################################################
About Path(File,Directory,Atty,Link etc)
################################################################################
"""

import os

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
    return os.path.expanduser('~')


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


def path_to(from_path:str, to_path:str):
    """
    >>> path_to('/home/john/coding', '/home/alice/Download')
    '../../alice/Download'
    >>> path_to('/home/john/coding', '/home/john/coding/tmp')
    './tmp'
    """
    from_path = os.path.abspath(from_path)
    to_path = os.path.abspath(to_path)

    common_path = os.path.commonpath([from_path, to_path])

    from_extra_path = from_path.split(common_path)[1]
    to_extra_path = to_path.split(common_path)[1]

    parpath = os.sep.join([os.pardir] * path_level(from_extra_path))

    if parpath:
        target_path = parpath + to_extra_path
    else:
        target_path = os.curdir + to_extra_path

    return target_path
