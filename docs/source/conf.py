# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os, sys
sys.path.insert(0, os.path.abspath('../../src'))

from networkx_temporal import __version__

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "networkx-temporal"
copyright = "2024"
author = "Nelson Aloysio Reis de Almeida Passos"

release = __version__
version = __version__
for _ in ["-", "a", "b", "post", "rc"]:
    version = version.split(_)[0].rstrip(".")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_rtd_theme",
    "sphinxemoji.sphinxemoji",
]
templates_path = ["_templates"]
exclude_patterns = ["*/convert/nx2*.py"]

# -- AutoDoc configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

autodoc_mock_imports = ["matplotlib", "pandas"]
autodoc_typehints = "both"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ["../_static"]
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": False,
    "includehidden": True,
    "logo_only": True,
    "navigation_depth": 3,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "style_nav_header_background": "#343131",
    "titles_only": False,
}
html_css_files = [
    "css/custom.css",
]
html_logo = "../figure/logo.png"
# html_favicon = 'favicon.ico'
