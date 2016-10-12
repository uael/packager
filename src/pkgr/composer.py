import os
import json

import sys

from pkgr import PkgrError
from pkgr import require

class Composer(object):
  require = None
  require_dev = None

  def __init__(self, root, deps_path, file_name, gyp_file_name):
    self.root = root
    self.deps_path = deps_path
    self.file_name = file_name
    self.gyp_file_name = gyp_file_name
    self.file = os.path.join(root, file_name)

    if not os.path.isfile(self.file):
      raise PkgrError("Unable to fetch composer " + self.file + " file.")

    with open(self.file) as data:
      self.json = json.load(data)

    if 'require' in self.json:
      self.require = require.loads(self.json['require'])
    if 'require_dev' in self.json:
      self.require_dev = require.loads(self.json['require_dev'])

  def install(self):
    if self.require:
      for r in self.require.itervalues():
        root = os.path.join(self.deps_path, r.vendor, r.name)
        if not r.installed(self.deps_path):
          rem_file = "Downloading requirement "+r.vendor+"/"+r.name+" "
          def reporthook(num, size, total_size):
            if total_size < size:
              size = total_size
            n = num * size
            percent = n * 1e2 / total_size
            sys.stderr.write("\r" + rem_file + "%5.1f%% %*d / %d" % (percent, len(str(total_size)), n, total_size))
            if n >= total_size:  # near the end
              sys.stderr.write("\n")
          r.install(root, reporthook)
        Composer(root, self.deps_path, self.file_name, self.gyp_file_name).install()

    self.gypize()

  def gypize(self):
    gyp_file = os.path.join(self.root, self.gyp_file_name)
    gyp_json = {}

    if os.path.isfile(gyp_file):
      os.remove(gyp_file)

    for key in ['variables', 'target_defaults', 'targets', 'conditions', 'includes']:
      if key in self.json:
        gyp_json[key] = self.json[key]
        if 'targets' == key:
          for i, target in enumerate(gyp_json['targets']):
            if 'dependencies' in target:
              for j, dep in enumerate(target['dependencies']):
                dep_name = dep.split(':')[0]
                if dep_name in self.require or dep_name in self.require_dev:
                  gyp_json['targets'][i]['dependencies'][j] = str(dep).replace(
                    dep_name,
                    os.path.join(
                      os.path.relpath(
                        os.path.join(self.deps_path, dep_name),
                        os.path.dirname(gyp_file)
                      ),
                      self.gyp_file_name
                    )
                  )

    with open(gyp_file, 'w') as outfile:
      json.dump(gyp_json, outfile)