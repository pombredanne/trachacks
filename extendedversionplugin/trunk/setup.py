#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2011 Malcolm Studd <mestudd@gmail.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from setuptools import find_packages, setup

setup(name='ExtendedVersionTracPlugin',
      version='0.1',
      description="Extend versions in trac",
      author='Malcolm Studd',
      author_email='mestudd@gmail.com',
      url='http://trac-hacks.org/wiki/ExtendedVersionPlugin',
      keywords='trac plugin',
      license='3-Clause BSD',
      packages=find_packages(exclude=['*.tests']),
      include_package_data=True,
      package_data={ 'extendedversion': ['templates/*.html', 'htdocs/css/*.css'] },
      zip_safe=False,
      entry_points = """
          [trac.plugins]
          extendedversion.environment = extendedversion.environment
          extendedversion.milestone = extendedversion.milestone
          extendedversion.roadmap = extendedversion.roadmap
          extendedversion.version = extendedversion.version
      """,
      )

