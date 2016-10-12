import argparse
import os
import sys

from common import BuildError
from common import PkgrError
from pkgr import command

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
  commands = []

  if args:
    if 'clean' == args[0]:
      commands.append(command.Clean(root))
    elif 'generate' == args[0]:
      commands.append(command.Generate(root))
    elif 'install' == args[0]:
      commands.append(command.Install(root))
    elif 'build' == args[0]:
      commands.append(command.Build(root))
    else:
      raise PkgrError('Unknown command '+args[0])
  else:
    commands.append(command.Build(root))

  for cmd in commands:
    ex = cmd.run()
    if ex != 0:
      return ex

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
