"""Read course assets from an editable checkout or an installed wheel."""

from importlib.resources import files
from pathlib import Path


def resource_directory(name):
    bundled = files("sns_recommend").joinpath("resources", name)
    if bundled.is_dir():
        return bundled
    directory = Path(__file__).resolve().parents[3] / name
    if not directory.is_dir():
        raise FileNotFoundError(f"missing course resource directory: {name}")
    return directory
