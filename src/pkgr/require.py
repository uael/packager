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
