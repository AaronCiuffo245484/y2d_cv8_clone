# temporarily add to ensure document creation is working as expected
from importlib.metadata import version

from thalianacv import utils  # noqa: F401

__version__ = version("thalianacv")


def hello() -> str:
    return "thalianacv"
