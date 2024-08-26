[![networkx-temporal](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figure/banner.png)]()

___

[![PyPI package](https://badge.fury.io/py/networkx-temporal.svg)](https://pypi.org/p/networkx-temporal/)
[![Documentation Status](https://readthedocs.org/projects/networkx-temporal/badge/?version=latest)](https://networkx-temporal.readthedocs.io/en/latest)
[![Downloads](https://static.pepy.tech/badge/networkx-temporal)](https://pepy.tech/project/networkx-temporal)
[![Downloads](https://static.pepy.tech/badge/networkx-temporal/month)](https://pepy.tech/project/networkx-temporal)
[![License](https://img.shields.io/pypi/l/networkx-temporal)](https://github.com/nelsonaloysio/networkx-temporal/blob/main/LICENSE.md)

Python package to build and manipulate temporal graphs using [NetworkX](https://pypi.org/project/networkx/) as backend.

## Requirements

* **Python>=3.7**
* networkx>=2.1
* pandas>=1.1.0

## Install

Package is available to install on [PyPI](https://pypi.org/project/networkx-temporal/):

```bash
$ pip install 'networkx-temporal[draw]'
```

> The `[draw]` extra includes `matplotlib`, required to plot graphs as in the example below.

## Quick example

For detailed information on using the package, please refer to its [official documentation](https://networkx-temporal.readthedocs.io/en/latest/).

> An interactive Jupyter notebook with more examples is also [available here](https://github.com/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal.ipynb) ([open on Colab](https://colab.research.google.com/github/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal.ipynb)).

```python
>>> import networkx_temporal as tx
>>>
>>> # Build directed temporal graph.
>>> TG = tx.TemporalDiGraph()
>>> TG.add_edge("a", "b", time=0)
>>> TG.add_edge("c", "b", time=1)
>>> TG.add_edge("d", "c", time=2)
>>> TG.add_edge("d", "e", time=2)
>>> TG.add_edge("a", "c", time=2)
>>> TG.add_edge("f", "e", time=3)
>>> TG.add_edge("f", "a", time=3)
>>> TG.add_edge("f", "b", time=3)
>>>
>>> # Slice it into snapshots.
>>> TG = TG.slice(attr="time")
>>>
>>> # Plot resulting object.
>>> tx.draw(TG, layout="kamada_kawai", figsize=(8,2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figure/fig-0.png)

## Contributing

Contributions are welcome! If you find any bugs or have any suggestions, feel free to [open a ticket](issues/new), [fork the repository](fork) and create a [pull request](compare), or simply [send an e-mail](mailto:nelson.reis@phd.unipi.it).
Please keep in mind that any out-of-scope contributions (not regarding temporal networks) should instead be directed to the [NetworkX](https://github.com/networkx/networkx) repository.

## License

This package is released under the [MIT License](LICENSE.md).

## Cite

In case this package is useful for your research, please kindly consider [citing it](https://networkx-temporal.readthedocs.io/en/latest/cite.html).
