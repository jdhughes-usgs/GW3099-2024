import os
import pathlib as pl
import subprocess

ROOT_DIR = pl.Path(os.getcwd()).resolve()
DIRS = (
    pl.Path("../base/watershed/").resolve(),
    pl.Path("../exercises-completed/parallel/").resolve(),
)

def get_notebook_paths(dir_path):
    return sorted(f.name for f in dir_path.glob("*.ipynb"))

def run_cmd(cmd):
    print(f"Running command: {' '.join(cmd)}")
    proc = subprocess.run(cmd)
    assert proc.returncode == 0, f"Error running command: {' '.join(cmd)}"

def run_notebook(nb_name):
    cmd = ("jupytext", "--execute", f"{nb_name}")
    run_cmd(cmd)

if __name__ == "__main__":
    for idx, dir_path in enumerate(DIRS):
        nb_paths = get_notebook_paths(dir_path)
        os.chdir(dir_path)
        for p in nb_paths:
            success = run_notebook(p)
        os.chdir(ROOT_DIR)