import pathlib as pl
import subprocess
import sys

import pytest

# "Official" notebooks are numbered
ex_notebooks = sorted(
    pl.Path("../exercises/pywatershed").glob("step[0-9]*.ipynb")
)
ex_comp_notebooks = sorted(
    pl.Path("../exercises-completed/pywatershed").glob("step[0-9]*.ipynb")
)

notebooks = ex_notebooks + ex_comp_notebooks

notebook_ids = [nb.name for nb in notebooks]


@pytest.mark.parametrize("notebook", notebooks, ids=notebook_ids)
def test_notebooks(notebook):
    # Convert the notebook to a .py version of itself using jupyter nbconvert
    # this formats magics in a way that ipython can run
    cmd = [
        "jupyter",
        "nbconvert",
        "--to",
        "script",
        str(notebook),
    ]
    proc = subprocess.run(cmd)
    assert (
        proc.returncode == 0
    ), f"Failed to convert notebook to script: {notebook}"
    nb_py = notebook.with_suffix(".py")
    assert nb_py.exists(), f"Expected script does not exists: {nb_py}"

    bin_path = pl.Path(sys.executable).parent
    ipython = bin_path / "ipython"
    assert ipython.exists(), f"ipython not found at: {ipython}"

    cmd = ["ipython", str(nb_py)]
    proc = subprocess.run(cmd)
    assert proc.returncode == 0, f"Running the notebook failed: {notebook}"

    nb_py.unlink()
    assert not nb_py.exists(), "Problem removing {nb_py}"
