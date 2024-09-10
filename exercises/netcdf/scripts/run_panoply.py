import pathlib as pl
import sys
from subprocess import Popen, run

# Run this script in the anaconda shell with "gw3099viz" environment activated
# This script runs the following command:
#   java -Xms512m -Xmx4g -cp {jar_path} gov.nasa.giss.panoply.Panoply "$@"

# jar_path
jar_path = None
rel_path = "Lib\\java\\PanoplyJ\\jars\\Panoply.jar"

# locate java paths
cmd = "where java"
result = run(cmd, capture_output=True, shell=True)
if result.returncode != 0:
    sys.stderr.write("error: unable to locate java\n")
    sys.exit(1)
output = result.stdout.decode("utf-8")

paths = output.splitlines()
for p in paths:
    path = pl.Path(p)
    parts = path.parts

    # create jar_path if env found
    if "gw3099viz" in parts:
        index = parts.index("gw3099viz")
        base_path = pl.Path(*parts[: index + 1])
        jar_path = base_path / rel_path
        break

if jar_path:
    sys.stdout.write(f"using jar file: {jar_path}\n")
    cmd = f'java -Xms512m -Xmx4g -cp {jar_path} gov.nasa.giss.panoply.Panoply "$@"'
    process = Popen(cmd, start_new_session=True)
else:
    sys.stderr.write("error: unable to identify panoply jar path\n")
    sys.exit(1)
