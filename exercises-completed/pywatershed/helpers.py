import pathlib as pl

from IPython.core.magic import register_cell_magic


@register_cell_magic
def do_not_run_this_cell(line, cell):
    return


def get_mf6_nightly_build(nightly_build_dir: pl.Path, date: str = None):
    """Get and unpack MF6 nightly build.

    Args:
        nightly_build_dir: pl.Path where the nightly build dir should be created.
        date: string of format YYYYMMDD, default is None for yesterday's build.
    """
    import datetime
    import platform
    import shutil
    import urllib.request
    import zipfile

    if not nightly_build_dir.exists():
        nightly_build_dir.mkdir()

    system_file_map = {"Linux": "linux", "Darwin": "mac", "Windows": "win64"}
    system = system_file_map[platform.system()]
    if platform.processor() == "arm":
        system += "arm"
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    if date is None: 
        YYYYMMDD = yesterday.strftime("%Y%m%d")
    else:
        YYYYMMDD = date
    zip_file = nightly_build_dir / f"{system}.zip"
    url = (
        "https://github.com/MODFLOW-USGS/modflow6-nightly-build/"
        f"releases/download/{YYYYMMDD}/{zip_file.name}"
    )
    extract_dir = zip_file.with_suffix("")
    if not (extract_dir).exists():
        urllib.request.urlretrieve(url, zip_file)
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        # annoying renaming on extraction
        alias = sorted(extract_dir.glob("*"))
        assert len(alias) == 1
        alias = alias[0]
        for ff in alias.glob("*"):
            new_file = nightly_build_dir / ff.name
            if new_file.exists():
                if new_file.is_dir():
                    shutil.rmtree(new_file)
                else:
                    new_file.unlink()
            # <<
            ff.rename(new_file)
        shutil.rmtree(alias)