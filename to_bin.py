# -*- coding: utf-8 -*-

from distutils.core import setup
from Cython.Build import cythonize

setup(name='daydayfishing', ext_modules=cythonize(["daydayfishing.py", ]), )
