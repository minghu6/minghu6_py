# -*- coding:utf-8 -*-
# !/usr/bin/env python3

"""
 Add specific path to PYTHONPATH
"""
import os
import sys

from minghu6.etc.version import iswin, islinux


def where_pth():
    if islinux():
        for path in sys.path:
            if os.path.basename(path) in ('dist-packages', 'site-packages'):
                return path
        raise Exception(f'Packages Stub Not Found!\n'+"\n".join(sys.path))

    elif iswin():
        return os.path.split(sys.executable)[0]

    else:
        raise Exception('Not Implemented!')


def main(paths):
    paths = [os.path.realpath(path) for path in paths]
    print(paths)
    pth_dir = where_pth()

    pth_file = os.path.join(pth_dir, 'minghu6.pth')
    print(pth_file)
    with open(pth_file, 'a') as file:
        file.write('\n')
        [file.write(path + '\n') for path in paths]


def shell_interactive():
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('paths', nargs='*',
                        help='paths will be added into PYTHONPATH')

    args = parser.parse_args().__dict__

    if args['paths'] in (None, ['.'], list()):
        args['paths'] = [os.path.abspath(os.path.curdir)]

    return args

def cli():
    args = shell_interactive()
    main(args.get('paths'))


if __name__ == '__main__':
    cli()
