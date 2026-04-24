# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib

sys.path.insert(0, os.path.abspath("../src"))

with open(os.path.abspath("../pyproject.toml"), "rb") as f:
    _toml = tomllib.load(f)

# -- Project information -----------------------------------------------------

project = "thalianacv"
copyright = "2026, 2025/26 Y2D CV8 (ACiuffo, AHumeha, YMedun, LPeggeman, ARak)"
author = "2025/26 Y2D CV8 (ACiuffo, AHumeha, YMedun, LPeggeman, ARak)"
release = _toml["project"]["version"]

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.10", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

todo_include_todos = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "navigation_with_keys": True,
}
