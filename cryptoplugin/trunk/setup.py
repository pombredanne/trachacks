#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from setuptools import find_packages, setup


setup(
    name = 'Crypto',
    version = '0.1',
    description = 'Cryptography for Trac',

    author = 'Steffen Hoffmann',
    author_email = 'hoff.st@web.de',
    license = 'BSD',
    url = 'http://trac-hacks.org/wiki/CryptoPlugin',

    packages=find_packages(),
    package_data={
        'crypto': [
            'htdocs/*', 'templates/*.html'
        ]
    },
    zip_safe=True,
    install_requires = ['Genshi >= 0.5', 'Trac >= 0.11'],
    entry_points = {
        'trac.plugins': [
            'crypto = crypto'
        ]
    }
)
