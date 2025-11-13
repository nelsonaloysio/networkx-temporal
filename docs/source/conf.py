# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os, sys
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from networkx_temporal import __version__
release = version = __version__

project = "networkx-temporal"
copyright = "2024"
author = "Nelson Aloysio Reis de Almeida Passos"

for _ in ["-", "a", "b", "post", "rc"]:
    version = version.split(_)[0].rstrip(".")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
    "sphinxemoji.sphinxemoji",
]
exclude_patterns = []
templates_path = ["_templates"]
add_module_names = False
autosummary_generate = True
autosummary_imported_members = True

# -- AutoDoc configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autodoc_mock_imports = [
    "dgl",
    "dynetx",
    "graph_tool",
    "igraph",
    "matplotlib",
    "networkit",
    "networkx",
    "pandas",
    "snap",
    "stellargraph",
    "teneto",
    "torch_geometric",
]
autodoc_member_order = "bysource"
autodoc_typehints = "both"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_static_path = ["../_static"]
html_logo = "../assets/logo-text.png"
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": False,
    "includehidden": True,
    "logo_only": True,
    "navigation_depth": 3,
    "prev_next_buttons_location": "bottom",
    'sticky_navigation': False,
    "style_external_links": False,
    "style_nav_header_background": "#343131",
    "titles_only": False,
}
html_css_files = [
    "css/custom.css",
]
html_favicon = "../assets/favicon/favicon.ico"

# -- Options for Edit on GitHub links ----------------------------------------
# https://docs.readthedocs.com/platform/latest/guides/edit-source-links-sphinx.html
html_context = {
    "display_github": True, # Integrate GitHub
    "github_user": "nelsonaloysio", # Username
    "github_repo": "networkx-temporal", # Repo name
    "github_version": "development", # Version
    "conf_py_path": "/docs/source/", # Path in the checkout to the docs root
}