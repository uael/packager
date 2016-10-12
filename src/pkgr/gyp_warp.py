import json
import os
import subprocess
import sys

import pkgr.common

try:
  # noinspection PyUnresolvedReferences
  import multiprocessing.synchronize

  gyp_parallel_support = True
except ImportError:
  gyp_parallel_support = False

CC = os.environ.get('CC', 'cc')

def compiler_version():
  process = subprocess.Popen(CC.split() + ['--version'], stdout=subprocess.PIPE)
  is_clang = 'clang' in process.communicate()[0].split('\n')[0]
  process = subprocess.Popen(CC.split() + ['-dumpversion'], stdout=subprocess.PIPE)
  version = process.communicate()[0].split('.')
  version = map(int, version[:2])
  version = tuple(version)
  return version, is_clang

def run_gyp(args):
  root = os.getcwd()
  output_dir = os.path.join(os.path.abspath(root), 'out')

  args.append('--depth=.')
  args.extend(['-Goutput_dir=' + output_dir])
  args.extend(['--generator-output', output_dir])

  if sys.platform != 'win32':
    if '-f' not in args:
      if pkgr.common.exe_exists('ninja'):
        args.extend('-f ninja'.split())
      else:
        args.extend('-f make'.split())
    (major, minor), is_clang = compiler_version()
    args.append('-Dgcc_version=%d' % (10 * major + minor))
    args.append('-Dclang=%d' % int(is_clang))

  if not gyp_parallel_support:
    args.append('--no-parallel')

  return os.system("gyp " + ' '.join(args))

def gen(composer_json, file_path, deps_dir, deps):
  gyp_json = {}
  for key in ['variables', 'target_defaults', 'targets', 'conditions', 'includes']:
    if key in composer_json:
      gyp_json[key] = composer_json[key]
      if 'targets' == key:
        for i, target in enumerate(gyp_json['targets']):
          if 'dependencies' in target:
            for j, dependency in enumerate(target['dependencies']):
              dep_name = dependency.split(':')[0]
              if dep_name in deps:
                gyp_json['targets'][i]['dependencies'][j] = str(dependency).replace(
                  dep_name,
                  os.path.join(
                    os.path.relpath(
                      os.path.join(deps_dir, dep_name), os.path.dirname(file_path)
                    ),
                    os.path.basename(file_path)
                  )
                )
  if os.path.isfile(file_path):
    os.remove(file_path)
  with open(file_path, 'w') as outfile:
    json.dump(gyp_json, outfile)
