import os
import pathlib as pl
import subprocess
import sys

ROOT_DIR = pl.Path(os.getcwd()).resolve()
DIRS = (
    pl.Path("../exercises-completed/flopy/").resolve(),
    pl.Path("../base/watershed/").resolve(),
    pl.Path("../exercises-completed/netcdf/").resolve(),
    pl.Path("../exercises-completed/parallel/").resolve(),
)
SKIP_NOTEBOOKS = {
    "step0_netcdf_output": ("win32",),
    "mf6minsim-plot": ("win32", "darwin", "linux"),
}


def get_notebook_paths(dir_path):
    names = sorted(f"{f.name}" for f in dir_path.glob("*.ipynb"))
    select_names = []
    os_name = sys.platform.lower()
    for name in names:
        add_name = True
        for key, values in SKIP_NOTEBOOKS.items():
            if key == pl.Path(name).stem and os_name in values:
                add_name = False
                break
        if add_name:
            select_names.append(name)
    return tuple(select_names)


def run_cmd(cmd):
    print(f"Running command: {' '.join(cmd)}")
    proc = subprocess.run(cmd)
    assert proc.returncode == 0, f"Error running command: {' '.join(cmd)}"


def run_notebook(nb_name):
    py_script = "test.py"
    cmd = ("jupytext", "--output", f"{py_script}", f"{nb_name}")
    run_cmd(cmd)

    cmd = ("python", f"{py_script}")
    run_cmd(cmd)

    pl.Path(py_script).unlink()


if __name__ == "__main__":
    for idx, dir_path in enumerate(DIRS):
        nb_paths = get_notebook_paths(dir_path)
        os.chdir(dir_path)
        for p in nb_paths:
            success = run_notebook(p)
        os.chdir(ROOT_DIR)
