import pathlib as pl
import subprocess

pestdir = pl.Path("../exercises/PEST/notebooks")
nbs = pestdir.glob("*.ipynb")
for nb in nbs:
    print("clearing", nb)
    cmd = (
        "jupyter",
        "nbconvert",
        "--ClearOutputPreprocessor.enabled=True",
        "--ClearMetadataPreprocessor.enabled=True",
        "--ClearMetadataPreprocessor.preserve_nb_metadata_mask={('kernelspec')}",
        "--inplace",
        nb,
    )
    proc = subprocess.run(cmd)
    assert proc.returncode == 0, f"Error running command: {' '.join(cmd)}"
