# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 Bernhard Gruenewaldt <trac@gruenewaldt.net>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
"""
The !NoteBox macro will render a small colored box with an
icon and text. 

To display a !NoteBox on a page, you must call the !NoteBox
macro and pass the ''style'' and ''text'' as arguments. The
text may contain wiki formatting, however it is not possible
to embed other wiki macros within the macro. Also, commas must
be escaped with a backslash.

A third optional argument allows the ''width'' of the !NoteBox
to be specified as a percent of the page width. The default
width is 70%.

The following styles are available: '''warn''', '''tip'''
and '''note'''.

Examples:
{{{
[[NoteBox(warn,If you don't run `update` before `commit`\, your checkin may fail.)]]
[[NoteBox(tip,The !NoteBox macro can bring '''attention''' to text within a page.,50)]]
[[NoteBox(note,More styles may be added in a ''future'' release.,30)]]
}}}

[[NoteBox(warn,If you don't run `update` before `commit`\, your checkin may fail.)]]
[[NoteBox(tip,The !NoteBox macro can bring '''attention''' to text within a page.,50)]]
[[NoteBox(note,More styles may be added in a ''future'' release.,30)]]
"""

import re
from inspect import getdoc, getmodule
from pkg_resources import resource_filename
from genshi.builder import tag
from trac.core import Component, implements
from trac.web.chrome import ITemplateProvider, add_stylesheet
from trac.wiki.api import IWikiMacroProvider, parse_args
from trac.wiki.formatter import format_to_html

class NoteBox(Component):
    implements(IWikiMacroProvider, ITemplateProvider)

    # IWikiMacroProvider
    def get_macros(self):
        yield 'NoteBox'

    def expand_macro(self, formatter, name, content):
        add_stylesheet(formatter.req, 'notebox/css/notebox.css')
        args, kwargs = parse_args(content)
        width = args[2] if len(args) > 2 else 70
        div = tag.div(format_to_html(self.env, formatter.context, args[1]), 
                      class_='notebox-%s' % (args[0],),
                      style='width: %s%%' % (width,))
        return div

    def get_macro_description(self, name):        
        return getdoc(getmodule(self))

    # ITemplateProvider
    def get_htdocs_dirs(self):
        return [('notebox', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return []

