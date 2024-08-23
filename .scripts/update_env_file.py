import pathlib as pl
import sys

file_path = pl.Path("../environment.yml")
with open(file_path, "r") as f:
    lines = f.readlines()

tags = ("openmpi", "gfortran", "petsc", "netcdf-fortran")
update_file = True
for line in lines:
    for tag in tags:
        if tag in line:
            update_file = False
            break

if update_file:
    print(f"Updating...{file_path}")
    with open(file_path, "a") as f:
        f.write("\n  # MODFLOW build dependencies\n")
        f.write("  - pkg-config\n")
        if sys.platform.lower() == "darwin":
            f.write("  - openmpi<5.0.0\n")
        else:
            f.write("  - openmpi\n")
        f.write("  - gfortran\n")
        f.write("  - petsc\n")
        f.write("  - netcdf-fortran\n")
        f.write("  - meson>=1.1.0\n")
        f.write("  - ninja\n")
else:
    print(f"No need to update...{file_path}")
