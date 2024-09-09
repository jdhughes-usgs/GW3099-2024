#! /usr/bin/env python

import sys
import pathlib as pl
from subprocess import run, Popen

# run this script in anaconda shell with "gw3099viz" environment activated
# this script runs the following command:
#   java -Xms512m -Xmx4g -cp {panoply_jar_path} gov.nasa.giss.panoply.Panoply "$@"

# jar_path
jar_path = None
rel_path = "Lib\\java\\PanoplyJ\\jars\\Panoply.jar"

# locate java paths
cmd = "where java"
result = run(cmd, capture_output=True, shell=True)
output = result.stdout.decode("utf-8")

paths = output.splitlines()
for p in paths:
    path = pl.Path(p)
    parts = path.parts

    # create jar_path if env found
    if "gw3099viz" in parts:
        index = parts.index("gw3099viz")
        base_path = pl.Path(*parts[:index + 1])
        jar_path = base_path / rel_path

if jar_path:
    cmd = f"java -Xms512m -Xmx4g -cp {jar_path} gov.nasa.giss.panoply.Panoply \"$@\""
    process = Popen(cmd, start_new_session=True)
    print(process)
else:
    sys.stderr.write("error: unable to identify panoply jar path\n")
    sys.exit(1)

