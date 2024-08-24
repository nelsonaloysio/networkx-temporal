# Documentation

To build the documentation, the following requirements are needed:

```bash
pip install sphinx sphinx-autodoc-typehints sphinx_rtd_theme sphinxemoji
```

Optionally install the package in development mode from source with:

```bash
pip install -e '.[docs]'
```

Afterwards, generate the documentation files with:

```bash
cd docs &&
make html
```

The whole documentation should then be available in the folder `docs/build`.
