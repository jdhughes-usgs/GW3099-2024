import os
import pathlib as pl

conda_path = os.environ.get("CONDA_PREFIX", None)
if conda_path is not None:
    conda_path = pl.Path(conda_path)
    netcdf_path = conda_path / "lib/pkgconfig/netcdf-fortran.pc"
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
                        tag, f"{tag}{conda_path / 'include'}"
                    )
                break
        if update:
            print(f"Updating {tag} with the include path.")
            with open(netcdf_path, "w") as f:
                for line in lines:
                    f.write(line)
        else:
            print("All files are in good shape.")
