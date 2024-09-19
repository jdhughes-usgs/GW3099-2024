import pathlib as pl

from IPython.core.magic import register_cell_magic


@register_cell_magic
def do_not_run_this_cell(line, cell):
    return


def read_yaml(yaml_file: pl.Path) -> dict:
    import yaml

    with pl.Path(yaml_file).open("r") as file_stream:
        yaml_dict = yaml.load(file_stream, Loader=yaml.Loader)
    return yaml_dict


def write_yaml(yaml_dict: dict, yaml_file: pl.Path):
    import yaml

    with open(yaml_file, "w") as file:
        _ = yaml.dump(yaml_dict, file)
    return None


def help_head(what, n=22):
    """Equivalent to help() but we get the multiline string and just look the first n lines."""
    import pydoc

    the_help = pydoc.render_doc(what, "Help on %s")
    print("\n".join(the_help.splitlines()[0:n]))
    return
