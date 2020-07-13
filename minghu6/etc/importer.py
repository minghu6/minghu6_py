# -*- coding:utf-8 -*-
# !/usr/bin/env python3

"""
################################################################################
About Import function, class
################################################################################
"""
from importlib import import_module
import re
import os

from color import color

from minghu6.etc.cmd import exec_cmd
from minghu6.etc.version import ispython2, ispython3
from minghu6.algs.func import flatten
from minghu6.algs.var import findall_attr


__all__ = ['check_module', 'add_parent_path']


def check_module(module_name, install_name=''):
    """
    check if the module exist, if not exist try to install by pip
    (you can provide the install name manually)
    :param module_name:
    :param install_name: default equals module name
    :return:
    """
    try:
        import_module(module_name)

    except ImportError:
        color.print_warn(module_name, 'Not Exists')

        pip_name = 'python -m pip'

        color.print_info('Now, try to install through {}, wait please...:)'.format(pip_name))

        if install_name in ('', None):
            install_name = module_name

        info_lines, err_lines = exec_cmd('{0} install {1}'.format(pip_name, install_name))
        print('\n'.join(info_lines))
        if len(err_lines) != 0:
            print(''.join(err_lines))

    else:
        pass


def add_parent_path(plevel=1):
    """
    Solve "Parent module '' not loaded, cannot perform relative import" Issue
    :param plevel:
    :return:
    """
    from minghu6.etc.path import get_pre_path
    import os

    path = get_pre_path(__file__, plevel)

    os.path.join(path)


def findall_module_name(base_path, pattern):
    return [os.path.splitext(fn)[0] for fn in os.listdir(base_path)
            if re.match(pattern, os.path.splitext(fn)[0])]


def load_var_from_module(module_name, attrname_pattern):
    """get all attrtibute according to name pattern
    from a module(import from module name)
    """
    try:
        module = import_module(module_name)
    except ImportError:
        return []
    else:
        return findall_attr(module, attrname_pattern)


def auto_load_var(package_name, module_pattern, variable_pattern, base_path=None):
    """

    >>> auto_load_var('minghu6.etc', 'fi.*', '[f|F].*')
    [<function minghu6.etc.find.find>,
     <function minghu6.etc.find.findlist>,
     <module 'fnmatch' from '/usr/lib/python3.5/fnmatch.py'>,
     minghu6.etc.fileformat.FileTypePair,
     <function minghu6.etc.fileformat.fileformat>]
    """
    if base_path is None:
        base_path = package_name.replace('.', os.sep)

    return list(
        flatten(map(lambda module_name: load_var_from_module('%s.%s' % (package_name, module_name), variable_pattern),
                    findall_module_name(base_path, module_pattern))))


if __name__ == '__main__':
    check_module('1234', '1234')
    # add_parent_path(plevel=3)
