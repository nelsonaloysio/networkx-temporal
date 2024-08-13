# Documentation

To build the documentation, the following requirements are needed:

```bash
pip install sphinx sphinx-autodoc-typehints sphinx_rtd_theme sphinxemoji
```

Optionally install **networkx-temporal** in development mode from source with:

```bash
pip install -e .
```

Afterwards, generate the documentation files with:

```bash
cd docs &&
make html
```

It should then be available in the folder `docs/build`.
