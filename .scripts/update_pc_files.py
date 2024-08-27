import argparse
import os
import pathlib as pl
import subprocess

parser = argparse.ArgumentParser(
    description="Update netcdf-fortran package config file."
)
parser.add_argument(
    "-c",
    "--conda",
    action="store_true",
    help="Conda MODFLOW library dependencies",
)
args = parser.parse_args()

lib_path = None

if args.conda:
    lib_path = os.environ.get("CONDA_PREFIX", None)
    if lib_path is not None:
        lib_path = f"{lib_path}/lib"
else:
    pkgconfig_str = subprocess.check_output(
        ("pkg-config", "--libs", "netcdf-fortran")
    ).decode()
    print(f"{pkgconfig_str}")
    if len(pkgconfig_str) > 0:
        split_path = pkgconfig_str.split()
        if len(split_path) < 2:
            lib_path = "/usr/lib"
        else:
            lib_path = split_path.replace("-L", "")
lib_path = pl.Path(lib_path)
print(f"netcdf-fortran lib path: {lib_path}")

if lib_path is not None:
    netcdf_path = lib_path / "pkgconfig/netcdf-fortran.pc"
    if netcdf_path.is_file():
        with open(netcdf_path, "r") as f:
            lines = f.readlines()
        tag = "fmoddir="
        update = False
        for idx, line in enumerate(lines):
            if tag in line:
                test = line.strip()
                if test == tag:
                    update = True
                    lines[idx] = line.replace(
                        tag, f"{tag}{lib_path.parent / 'include'}"
                    )
                break
        if update:
            print(f"Updating {tag} with the include path.")
            with open(netcdf_path, "w") as f:
                for line in lines:
                    f.write(line)
        else:
            print("All files are in good shape.")
