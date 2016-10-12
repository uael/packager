import json
import os

import requests

import package
from common import PkgrError

class Dependency:
  package = None

  def __init__(self, vendor, name, version):
    self.vendor = vendor
    self.name = name
    self.version = version

  def exists_in(self, deps_dir):
    return os.path.exists(os.path.join(deps_dir, self.vendor, self.name))

  def get_package(self):
    if self.package is not None:
      return self.package
    try:
      resp = requests.get('https://packagist.org/p/' + self.vendor + '/' + self.name + '.json')
      jsn = json.loads(resp.text)
      if 'error' in jsn:
        raise PkgrError("Undefined dependency :" + self.vendor + '/' + self.name)
      self.package = package.parse(jsn)
      return self.package
    except requests.ConnectionError:
      raise PkgrError("Cannot establish connection to host https://packagist.org")

  def get_tag(self):
    return self.get_package().tags[self.version]

  def install(self, deps_dir):
    return self.get_package().install(self.version, deps_dir)

  def __str__(self):
    return self.vendor + '/' + self.name

def loads(requirements):
  if not isinstance(requirements, dict):
    requirements = dict(requirements)
  deps = []
  for name, version in requirements.iteritems():
    try:
      vendor, name = name.split('/')
      deps.append(Dependency(vendor, name, version))
    except ValueError:
      continue
  return deps
