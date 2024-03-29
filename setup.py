#!/usr/bin/env python

# Copyright (c) 2016 Abel Lucas
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import setup

setup(
  name='packager',
  version='0.2.1',
  description='C/C++ package manager built on the top of gyp',
  author='Abel Lucas',
  author_email='ylilt71@gmail.com',
  url='https://github.com/packager/packager',
  package_dir={'': 'src'},
  install_requires=['requests'],
  packages=['pkgr'],
  entry_points={'console_scripts': ['packager=pkgr:script_main']}
)

# Local variables:
# tab-width: 2
# c-basic-offset: 2
# End:
# vim600: noet sw=2 ts=2 fdm=marker
# vim<600: noet sw=2 ts=2