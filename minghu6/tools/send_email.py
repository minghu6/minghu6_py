# -*- coding:utf-8 -*-

"""SEND_EMAIL

Usage:
  send_email <from> <to> <subj> <body> [--attachments=<attachments>] [--password=<password>] [--cc=<cc>] [--bcc=<bcc>] [--debug]


Options:
  <from>  from email address
  <to>    to email address
  <subj>  subject of the email
  <body>  body of the email
  -a --attachments=<attachments>  attach paths split with ":" or ";" based on OS
  -p --password=<password>        user password
  -c --cc=<cc>                    cc split with ":" or ";" based on OS
  -b --bcc=<bcc>                  bcc split with ":" or ";" based on OS
  -d --debug                      enable debug mode

"""

from docopt import docopt
from minghu6.etc.cmd import env_sep
#from minghu6.email import EmailSender
from minghu6.internet.email_test import EmailSender


def cli():
    arguments = docopt(__doc__)

    email_sender = EmailSender(arguments['<from>'],
                               arguments['--password'] if arguments['--password'] else None,
                               debug=arguments['--debug'])

    cc = arguments['--cc'].split(env_sep) if arguments['--cc'] else ()
    bcc = arguments['--bcc'].split(env_sep) if arguments['--bcc'] else ()
    att = arguments['--attachments'].split(env_sep) if arguments['--attachments'] else ()

    email_sender.send([arguments['<to>']],
                      [*map(lambda x:('cc', x), cc), *map(lambda x:('bcc', x), bcc)],
                      arguments['<subj>'],
                      arguments['<body>'],
                      att)


if __name__ == '__main__':
    cli()
