class PkgrError(Exception):
  pass

class BuildError(PkgrError):
  pass

def exe_exists(program):
  import os
  def is_exe(f):
    return os.path.isfile(f) and os.access(f, os.X_OK)

  fpath, fname = os.path.split(program)
  if fpath:
    if is_exe(program):
      return True
  else:
    for path in os.environ["PATH"].split(os.pathsep):
      path = path.strip('"')
      exe_file = os.path.join(path, program)
      if is_exe(exe_file):
        return True

  return False
