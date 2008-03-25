#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'TracWikiRename',
    version = '2.0',
    packages = ['wikirename'],
    package_data={ 'wikirename' : [ 'templates/*.html' ] },

    author = "Noah Kantrowitz",
    author_email = "noah@coderanger.net",
    description = "Add simple support for renaming/moving wiki pages",
    long_description = """Adds basic support for renaming wiki pages. A console script is provided, as is a WebAdmin module. \
                          Please read the notice on the homepage for a list of known shortcomings.""",
    license = "BSD",
    keywords = "trac plugin wiki page rename",
    url = "http://trac-hacks.org/wiki/WikiRenamePlugin",
    classifiers = [
        'Framework :: Trac',
    ],
    
    entry_points = {
        'trac.plugins': [
            'wikirename.web_ui = wikirename.web_ui',
            'wikirename.ctxtnav = wikirename.ctxtnav [ctxtnav]',
        ],
        'console_scripts': [
            'trac-wikirename = wikirename.script:run'
        ],
    },
    
    #install_requires = [],
    # Waiting on the extras support patch for this
    extras_require = {
        'ctxtnav' : [ 'TracCtxtnavAdd>=2.0' ],
    },
)
