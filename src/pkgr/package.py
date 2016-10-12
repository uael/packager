import json
import os
import shutil
import sys
import urllib
import zipfile

import dependency
from pkgr import gyp_warp

rem_file = ""

def reporthook(blocknum, blocksize, totalsize):
  readsofar = blocknum * blocksize
  if totalsize > 0:
    percent = readsofar * 1e2 / totalsize
    s = "\r" + rem_file + "%5.1f%% %*d / %d" % (
      percent, len(str(totalsize)), readsofar, totalsize)
    sys.stderr.write(s)
    if readsofar >= totalsize:  # near the end
      sys.stderr.write("\n")
  else:  # total size is unknown
    sys.stderr.write("\r" + rem_file + "%5.1f%% * / *" % 100, 100)

class Dist:
  def __init__(self, jsn):
    self.type = jsn['type']
    self.url = jsn['url']
    self.reference = jsn['reference']
    self.shasum = jsn['shasum']

class Tag:
  dist = None
  version = None
  require = []
  require_dev = []

  def __init__(self, jsn):
    self.vendor, self.name = jsn['name'].split('/')
    if 'dist' in jsn:
      self.dist = Dist(jsn['dist'])
    if 'version' in jsn:
      self.version = jsn['version']
    if 'require' in jsn:
      self.require = dependency.loads(jsn['require'])
    if 'require_dev' in jsn:
      self.require_dev = dependency.loads(jsn['require_dev'])

  def download(self):
    global rem_file
    rem_file = "Downloading package " + self.vendor + "/" + self.name + " (" + self.version + "): "
    handle, _ = urllib.urlretrieve(self.dist.url, reporthook=reporthook)
    return handle

  def unzip(self, deps_dir):
    vendor_dir = os.path.join(deps_dir, self.vendor)
    package_dir = os.path.join(vendor_dir, self.name)
    if os.path.exists(package_dir):
      shutil.rmtree(package_dir)
    zip_file = zipfile.ZipFile(self.download(), 'r')
    zip_root = zip_file.namelist().pop(0)
    zip_file.extractall(vendor_dir)
    os.rename(os.path.join(vendor_dir, zip_root), package_dir)
    zip_file.close()
    return True

  def install(self, deps_dir):
    vendor_dir = os.path.join(deps_dir, self.vendor)
    if not os.path.exists(vendor_dir):
      os.mkdir(vendor_dir, 0755)
    elif os.path.exists(os.path.join(vendor_dir, self.name)):
      return True
    self.install_deps(deps_dir)
    if 'zip' == self.dist.type:
      return self.unzip(deps_dir)
    return False

  def install_deps(self, deps_dir):
    for dep in self.require:
      dep.install(deps_dir)

  def get_deps(self):
    deps = {}
    for dep in self.require:
      deps[dep.__str__()] = dep
      for _dep in dep.get_tag().get_deps():
        deps[_dep.__str__()] = _dep
    return deps

  def gen_gyp(self, root, deps_dir, composer_file_name, gyp_file_name):
    deps = self.get_deps()
    composer_file = os.path.join(root, composer_file_name)
    if os.path.isfile(composer_file):
      with open(composer_file) as data_file:
        gyp_warp.gen(json.load(data_file), os.path.join(root, gyp_file_name), deps_dir, deps)
    for dep_name, dep in deps.iteritems():
      dep_dir = os.path.join(deps_dir, dep_name)
      dep_composer_file = os.path.join(dep_dir, composer_file_name)
      if os.path.isfile(dep_composer_file):
        with open(dep_composer_file) as dep_data_file:
          gyp_warp.gen(json.load(dep_data_file), os.path.join(dep_dir, gyp_file_name), deps_dir, deps)

class Package:
  def __init__(self, vendor, name, tags):
    self.vendor = vendor
    self.name = name
    self.tags = tags

  def install(self, version, deps_dir):  # todo version handling
    if version not in self.tags:
      raise KeyError
    tag = self.tags[version]
    return tag.install(deps_dir)

def parse(jsn):
  key, json_tags = dict(jsn['packages']).popitem()
  vendor, name = key.split('/')
  tags = {}
  for version, tag in json_tags.iteritems():
    tags[version] = Tag(tag)
  return Package(vendor, name, tags)
