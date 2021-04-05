# -*- coding:utf-8 -*-
# !/usr/bin/env python3

"""Find

Usage:
  find [--path=<start-path>] <pattern>... [--exec=<exec-program>] [--regex=<regex-match>]
                                          [--dry]

Options:
  pattern                   such as "*.c" "*.py"
  -p --path=<start-path>    find start from startdir(default os.curdir)
  -e --exec=<exec-program>  exec other command by pipe like -exec "xxx %s ", %s:file-name
  -r --regex=<regex-match>  use regex match
  --dry        dry run

Examples:
  find -p . "*.enfp" -e "echo {} | sed 's/.enfp.*//' | xargs -0 mv {}"  # repair broken filename caused by virus.
"""
import os

import minghu6
import minghu6.etc.cmd as cmd
from docopt import docopt
from minghu6.etc.find import find


def handle_exec_string(raw_s: str, fn: str) -> str:
    raw_s = raw_s.replace('{}', f'"{fn}"')

    return raw_s

def cli():
    arguments = docopt(__doc__, version=minghu6.__version__)
    if arguments['--path'] is None:
        start_path = os.curdir
    else:
        start_path = arguments['--path']

    start_path = os.path.abspath(start_path)

    for fn in find(arguments['<pattern>'], start_path,
                   regex_match=arguments['--regex']):
        if arguments['--exec'] is not None:
            if os.path.isfile(fn):
                exec_cmd_completely = handle_exec_string(arguments['--exec'], fn)
                if arguments['--dry']:
                    print(exec_cmd_completely)
                    return
                else:
                    print(fn)
                info, err = cmd.exec_cmd(exec_cmd_completely)
                print('\n'.join(info), '\n'.join(err))
        else:
            print(fn)


if __name__ == '__main__':
    cli()
