import argparse
import os
import shutil
import sys

from common import BuildError
from common import PkgrError
from package import Tag
from pkgr import gyp_warp
from pkgr import install

def pkgr_main(args):
  parser = argparse.ArgumentParser()
  parser.add_argument('-C', '--directory', dest='cwd', action='store', help='DIRECTORY')
  options, unknown = parser.parse_known_args(args)

  if options.cwd:
    if not os.path.exists(options.cwd):
      raise PkgrError("-C option DIRECTORY must be a directory.")
    try:
      idx = args.index('-C')
    except ValueError:
      idx = args.index('-C' + options.cwd)
    try:
      idx_cwd = args.index(options.cwd) + 1
    except ValueError:
      idx_cwd = idx + 1
    args = args[:idx] + args[idx_cwd:]
    os.chdir(options.cwd)

  root = os.getcwd()
  gyp_file_name = '.gyp'
  composer_file_name = 'composer.json'
  output_dir = os.path.join(os.path.abspath(root), 'out')
  deps_dir = os.path.join(os.path.abspath(root), 'vendor')

  if args:
    if 'clean' == args[0]:
      if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
      if os.path.exists(deps_dir):
        shutil.rmtree(deps_dir)
      gyp_file = os.path.join(root, gyp_file_name)
      if os.path.isfile(gyp_file):
        os.remove(gyp_file)
      return 0
    if args[0] in ['gyp', 'generate', 'gen']:
      args.pop(0)
    elif 'ninja' == args[0]:
      args.pop(0)
      for r, dirs, files in os.walk(output_dir):
        if 'build.ninja' in files:
          os.chdir(r)
          return os.system("ninja " + ' '.join(args))
      raise BuildError("Unable to ninja anything.")
    elif 'make' == args[0]:
      args.pop(0)
      for r, dirs, files in os.walk(output_dir):
        if 'Makefile' in files:
          os.chdir(r)
          return os.system("make " + ' '.join(args))
      raise BuildError("Unable to make anything.")
    elif 'help' == args[0]:
      return os.system(args[1] + " -h")
    elif 'install' == args[0]:
      args.pop(0)
      install.make(root, deps_dir, composer_file_name, gyp_file_name)
  else:
    install.make(root, deps_dir, composer_file_name, gyp_file_name)

  # Run gyp in all other case
  ex = gyp_warp.run_gyp(args)
  if ex != 0: return ex

  has_ninja = 0
  has_make = 0
  for r, dirs, files in os.walk(output_dir):
    if not has_make and 'build.ninja' in files:
      os.chdir(r)
      has_ninja = 1
      ex = os.system("ninja")
      if ex != 0: return ex
    elif not has_ninja and 'Makefile' in files:
      os.chdir(r)
      has_make = 1
      ex = os.system("make")
      if ex != 0: return ex

  return 0

def main(args):
  try:
    return pkgr_main(args)
  except PkgrError, e:
    sys.stderr.write("packager: %s\n" % e)
    return 1

def script_main():
  return main(sys.argv[1:])

if __name__ == '__main__':
  sys.exit(script_main())
