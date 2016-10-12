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

import os
import shutil
import subprocess

import sys

from pkgr import common

from pkgr.composer import Composer

class Command(object):
  def __init__(self, root):
    self.root = root

  def run(self):
    pass

class Install(Command):
  def __init__(self, root, deps_dirname='vendor', composer_file_name='composer.json', gyp_file_name='.gyp'):
    super(Install, self).__init__(root)
    self.deps_dir = os.path.join(self.root, deps_dirname)
    self.composer_file_name = composer_file_name
    self.gyp_file_name = gyp_file_name

  def run(self):
    deps_path = os.path.join(self.root, self.deps_dir)
    if not os.path.exists(deps_path):
      print "Installing package ..."
      os.mkdir(deps_path, 0755)
    else:
      print "Updating package ..."

    composer = Composer(self.root, self.deps_dir, self.composer_file_name, self.gyp_file_name)
    composer.install()

    return 0

class Generate(Install):
  CC = os.environ.get('CC', 'cc')

  def __init__(self, root, generator='ninja', deps_dirname='vendor', output_dirname='out',
               composer_file_name='composer.json', gyp_file_name='.gyp'):
    super(Generate, self).__init__(root, deps_dirname, composer_file_name, gyp_file_name)
    self.generator = generator
    self.output_dirname = output_dirname

  def run(self):
    super(Generate, self).run()
    print "Generating package ..."

    args = []
    output_dir = os.path.join(os.path.abspath(self.root), 'out')

    args.append('--depth=.')
    args.extend(['-Goutput_dir=' + output_dir])
    args.extend(['--generator-output', output_dir])

    if sys.platform != 'win32':
      if common.exe_exists(self.generator):
        args.extend(['-f', self.generator])
      (major, minor), is_clang = self.compiler_version()
      args.append('-Dgcc_version=%d' % (10 * major + minor))
      args.append('-Dclang=%d' % int(is_clang))

    try:
      # noinspection PyUnresolvedReferences
      import multiprocessing.synchronize
    except ImportError:
      args.append('--no-parallel')

    return os.system("gyp " + ' '.join(args))

  def compiler_version(self):
    process = subprocess.Popen(self.CC.split() + ['--version'], stdout=subprocess.PIPE)
    is_clang = 'clang' in process.communicate()[0].split('\n')[0]
    process = subprocess.Popen(self.CC.split() + ['-dumpversion'], stdout=subprocess.PIPE)

    return tuple(map(int, process.communicate()[0].split('.')[:2])), is_clang

class Clean(Command):
  def __init__(self, root, deps_dirname='vendor', output_dirname='out', gyp_filename='.gyp'):
    super(Clean, self).__init__(root)
    self.deps_dirname = deps_dirname
    self.output_dirname = output_dirname
    self.gyp_filename = gyp_filename

  def run(self):
    print "Cleaning package ..."

    for path in [os.path.join(self.root, self.deps_dirname), os.path.join(self.root, self.output_dirname)]:
      if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
    gyp_file = os.path.join(self.root, self.gyp_filename)
    if os.path.isfile(gyp_file):
      os.remove(gyp_file)

    return 0

class Build(Generate):
  def run(self):
    super(Build, self).run()
    print "Building package ..."

    has_ninja = 0
    has_make = 0
    output_dir = os.path.join(self.root, self.output_dirname)

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

# Local variables:
# tab-width: 2
# c-basic-offset: 2
# End:
# vim600: noet sw=2 ts=2 fdm=marker
# vim<600: noet sw=2 ts=2