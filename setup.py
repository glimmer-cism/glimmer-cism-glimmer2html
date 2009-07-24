#!/usr/bin/env python

from distutils.core import setup
import os, sys

data_files = [('share/glimmer2html/',['template/glimmer2html.cfg',
                                      'template/index.tmpl',
                                      'template/snapshots.tmpl',
                                      'template/rsl.tmpl']),
              ('bin',['g2h_run.py'])]

setup (name = 'glimmer2html',
       version = "0.1",
       description = "Python module for creating HTML pages from GLIMMER output",
       author = "Magnus Hagdorn",
       author_email = "Magnus.Hagdorn@ed.ac.uk",
       packages = ['glimmer2html'],
       data_files=data_files,
       )

#EOF
