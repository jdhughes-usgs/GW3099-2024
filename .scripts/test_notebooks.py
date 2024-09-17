import argparse
import os
import pathlib as pl
import subprocess
import sys

conda_env_name = os.getenv("CONDA_DEFAULT_ENV")

ROOT_DIR = pl.Path(os.getcwd()).resolve()
DIRS = (
    pl.Path("../exercises-completed/flopy/").resolve(),
    pl.Path("../base/watershed/").resolve(),
    pl.Path("../exercises-completed/xt3d/").resolve(),
    pl.Path("../exercises-completed/gwf_advanced/").resolve(),
    pl.Path("../exercises-completed/gwt/").resolve(),
    pl.Path("../exercises-completed/gwe/").resolve(),
    pl.Path("../exercises-completed/prt/").resolve(),
    pl.Path("../exercises-completed/csub/").resolve(),
    pl.Path("../exercises-completed/modflowapi/").resolve(),
    pl.Path("../exercises-completed/parallel/").resolve(),
    pl.Path("../exercises-completed/pywatershed/").resolve(),
    pl.Path("../exercises/netcdf/").resolve(),
    pl.Path("../exercises/PEST/notebooks").resolve(),
    pl.Path("../exercises/pywatershed").resolve(),
)
SKIP_NOTEBOOKS = {
    "step0_netcdf_output": ("win32",),
    "step1_netcdf_input": ("win32",),
    "step2_netcdf_ncf": ("win32",),
}

GIT_RESET_DIRS = (
    pl.Path("../data/watershed/").resolve(),
    pl.Path("../exercises/PEST/pest_background_files/").resolve(),
)


def pws_filter(dir_path) -> bool:
    """Filter in/out pywatershed notebooks and the repo, if present

    Returns:
        bool where True means return an empty list and False means continue..
    """
    pws_env = conda_env_name == "gw3099pws"
    pws_dir = "pywatershed" in str(dir_path)
    if pws_env and not pws_dir:
        return True
    if not pws_env and pws_dir:
        return True

    return False


def get_notebook_paths(dir_path):
    if pws_filter(dir_path):
        return []

    names = sorted(f.name for f in dir_path.glob("*.ipynb"))
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
    cmd = ("jupytext", "--execute", f"{nb_name}")
    run_cmd(cmd)


def clean_notebook(nb_name):
    cmd = (
        "jupyter",
        "nbconvert",
        "--ClearOutputPreprocessor.enabled=True",
        "--ClearMetadataPreprocessor.enabled=True",
        "--ClearMetadataPreprocessor."
        + "preserve_nb_metadata_mask={('kernelspec')}",
        "--inplace",
        f"{nb_name}",
    )
    run_cmd(cmd)


def run_script(nb_name):
    py_script = "test.py"
    cmd = ("jupytext", "--output", f"{py_script}", f"{nb_name}")
    run_cmd(cmd)

    cmd = ("python", f"{py_script}")
    run_cmd(cmd)

    pl.Path(py_script).unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test gw3099 completed notebooks."
    )
    parser.add_argument(
        "-s",
        "--script",
        action="store_true",
        help="Convert notebooks to scripts",
    )
    parser.add_argument(
        "-c",
        "--clean-only",
        action="store_true",
        help="Clean notebooks",
    )
    parser.add_argument(
        "-d",
        "--dir",
        nargs="?",
        type=str,
        default=None,
        help="Run notebooks in a select subdirectories. "
        + "Use a comma separated string for multiple "
        + "subdirectories (--dir dirA,dirB).",
    )
    args = parser.parse_args()

    selection = None
    if args.dir is not None:
        selection = args.dir.split(",")

    for idx, dir_path in enumerate(DIRS):
        if selection is not None:
            skip_dir = True
            for value in selection:
                if value in str(dir_path):
                    skip_dir = False
                    break
            if skip_dir:
                continue

        nb_paths = get_notebook_paths(dir_path)

        os.chdir(dir_path)

        for p in nb_paths:
            if not args.clean_only:
                if args.script:
                    print(f"Testing notebook as script: {dir_path / p}")
                    run_script(p)
                else:
                    print(f"Testing notebook: {dir_path / p}")
                    run_notebook(p)
            clean_notebook(p)

        os.chdir(ROOT_DIR)

    for dir_path in GIT_RESET_DIRS:
        cmd = ("git", "restore", f"{dir_path}/*")
        run_cmd(cmd)
