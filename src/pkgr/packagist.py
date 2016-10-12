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