#!/usr/bin/env python

"""
smtp2trac:
a email plugin for Trac
http://trac.edgewall.org
"""

import email
import sys

from mail2trac.interface import IEmailHandler

from trac.core import *
from trac.env import open_environment


class EmailException(Exception):
    """exception when processing email messages"""

def mail2project(project, message):
    """
    relays an email message to a project
    
    """

    # open the environment
    env = open_environment(project)

    # read the email
    message = email.message_from_string(message)

    # handle the message
    handlers = ExtensionPoint(IEmailHandler).extensions(env)
    for handler in handlers:
        try:
            handler.invoke(message)
        except EmailException:
            # TODO : handle the exception
            pass
    

if __name__ == '__main__':

    # parse the options
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-p', '--project', '--projects', 
                      dest='projects', action='append', 
                      default=[],
                      help='projects to apply to',
                      )
    parser.add_option('-f', '--file',
                      dest='file',
                      help='email file to read;  if not specified, taken from stdin')

    options, args = parser.parse_args()

    if options.file:
        f = file(options.file)
    else:
        f = sys.stdin

    if not options.projects:
        parser.print_help()
        sys.exit()

    # relay the email
    for project in options.projects:
        mail2project(project, f.read())
        
