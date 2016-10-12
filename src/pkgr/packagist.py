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

import json
import os
import shutil
import urllib
import zipfile

import requests

from pkgr import PkgrError

class Dist(object):
  def __init__(self, type, url, reference, shasum):
    self.type = type
    self.url = url
    self.reference = reference
    self.shasum = shasum

  def download(self, reporthook=None):
    handle, _ = urllib.urlretrieve(self.url, reporthook=reporthook)
    return handle

  def install(self, path, reporthook=None):
    if os.path.exists(path):
      shutil.rmtree(path)
    vendor_path = os.path.abspath(os.path.join(path, '..'))
    zip_file = zipfile.ZipFile(self.download(reporthook), 'r')
    zip_file.extractall(vendor_path)
    os.rename(os.path.join(vendor_path, zip_file.namelist().pop(0)), path)
    zip_file.close()

class Package(object):
  def __init__(self, vendor, name):
    self.vendor = vendor
    self.name = name
    self.dists = {}

    try:
      resp = requests.get('https://packagist.org/p/' + vendor + '/' + name + '.json')
    except requests.ConnectionError:
      raise PkgrError("Could not resolve host https://packagist.org")

    self.json = json.loads(resp.text)
    if 'error' in self.json:
      raise PkgrError("Undefined package :" + vendor + '/' + name)

    key, dists = dict(self.json['packages']).popitem()
    for version, dist in dists.iteritems():
      _dist = dist['dist']
      self.dists[version] = Dist(_dist['type'], _dist['url'], _dist['reference'], _dist['shasum'])

  def find(self, version):
    return self.dists[version]

# Local variables:
# tab-width: 2
# c-basic-offset: 2
# End:
# vim600: noet sw=2 ts=2 fdm=marker
# vim<600: noet sw=2 ts=2