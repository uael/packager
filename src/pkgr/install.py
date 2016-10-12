import json
import os

from pkgr import PkgrError
from pkgr import Tag

def make(root, deps_dir, composer_file_name, gyp_file_name):
  gyp_file = os.path.join(root, gyp_file_name)
  if os.path.isfile(gyp_file):
    os.remove(gyp_file)
  composer_file = os.path.join(root, composer_file_name)
  if not os.path.isfile(composer_file):
    raise PkgrError("Unable to fetch " + composer_file_name + " file.")
  with open(composer_file) as data_file:
    tag = Tag(json.load(data_file))
  if tag.require and not os.path.exists(deps_dir):
    os.mkdir(deps_dir, 0755)
    tag.install_deps(deps_dir)
  tag.gen_gyp(root, deps_dir, composer_file_name, gyp_file_name)
  return 0
