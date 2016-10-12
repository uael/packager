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

import os

from packagist import Package

cache = {}

class Require(object):
  package = None
  composer = None

  def __init__(self, vendor, name, version):
    self.vendor = vendor
    self.name = name
    self.version = version

  def installed(self, deps_dir):
    return os.path.exists(os.path.join(deps_dir, self.vendor, self.name))

  def get_package(self):
    if self.package is not None:
      return self.package

    self.package = Package(self.vendor, self.name)

    return self.package

  def install(self, root, reporthook=None):
    self.get_package().find(self.version).install(root, reporthook)

  def __str__(self):
    return self.vendor + '/' + self.name

def loads(requirements):
  if not isinstance(requirements, dict):
    requirements = dict(requirements)
  deps = {}
  for package_name, version in requirements.iteritems():
    if package_name not in cache:
      try:
        vendor, name = package_name.split('/')
        cache[package_name] = Require(vendor, name, version)
      except ValueError:
        continue
    deps[package_name] = cache[package_name]
  return deps

# Local variables:
# tab-width: 2
# c-basic-offset: 2
# End:
# vim600: noet sw=2 ts=2 fdm=marker
# vim<600: noet sw=2 ts=2