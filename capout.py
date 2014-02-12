#!/usr/bin/python

"""Runs a command, saves the output to a tempfile, and prints its name.

capout (capture output) is a command-line utility that runs a command, saves
its output to a temporary file and prints that file's name. The goal is to
make it easier to use commands that expect filenames as parameters, instead of
pipes. For example:

diff `capout command_1` `capout command_2`

There are also shell specific facilities to do the same, like in bash:

diff <(command_1) <(command_2)

But this fails for processes that open in the background, such as many GUI
diff tools.

The temporary files created by capout are not automatically managed. Users must
either run "capout -c" to clean out these temporary files, or rely on their
filesystem to clear out the temporary file directory as it will.
"""


__author__ = 'Dustin Long'


import os
import subprocess
import sys
import tempfile


def usage():
  print("Usage: capout [-c] | <command...>")
  print("    Runs a command, saves the output to a temporary file, and prints")
  print("    the name of the temporary file.")
  print("")
  print("  Options:")
  print("  -c Cleans the temporary files created by capout.")
  sys.exit(1)


def clear_tempfiles(tempdir, capout_manifest):
  # Read the manifest.
  fp = open(capout_manifest, "r")
  content = fp.read()
  fp.close()
  for filename in content.split("\n"):
    # As long as the filename is in the temporary directory, delete it.
    if os.path.dirname(filename) == tempdir:
      os.unlink(filename)
  # Clear the manifest.
  fp = open(capout_manifest, "w")
  fp.close()


def create_tempfile(capout_manifest):
  # Create temporary filename.
  (temp_handle, temp_name) = tempfile.mkstemp()
  # Add that filename to the manifest.
  fp = open(capout_manifest, "a")
  fp.write(temp_name + "\n")
  fp.close()
  # Execute the command.
  p = subprocess.Popen(sys.argv[1:], stdout=subprocess.PIPE, stderr=None)
  content = p.communicate()[0]
  # Write the output to the temporary filename.
  fp = os.fdopen(temp_handle, "w")
  fp.write(content)
  fp.close()
  # Print temporary filename.
  print(temp_name)


def run():
  if len(sys.argv) < 2:
    usage()
  tempdir = tempfile.gettempdir()
  capout_manifest = os.path.join(tempdir, "capout.manifest")
  if sys.argv[1:] == ['-c']:
    clear_tempfiles(tempdir, capout_manifest)
  else:
    create_tempfile(capout_manifest)


if __name__ == '__main__':
  run()
