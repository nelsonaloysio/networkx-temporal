<!--# networkx-temporal-->

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figure/banner.png)

Python package to build and manipulate temporal graphs using [NetworkX](https://pypi.org/project/networkx/) as backend.

## Requirements

* **Python>=3.7**
* networkx>=2.1
* pandas>=1.1.0

## Install

Package is available to install on [PyPI](https://pypi.org/project/networkx-temporal/):

```bash
pip install networkx-temporal
```

## Quick example

For detailed information on using the usage, please refer to its [official documentation](https://networkx-temporal.readthedocs.io/en/latest/).

> An interactive Jupyter notebook with examples is also [available here](https://github.com/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal.ipynb) ([open on Colab](https://colab.research.google.com/github/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal.ipynb)).

```python
import networkx_temporal as tx
from networkx_temporal.example.draw import draw_temporal_graph

# Build temporal graph.
TG = tx.TemporalGraph(directed=True)
TG.add_edge("a", "b", time=0)
TG.add_edge("c", "b", time=1)
TG.add_edge("d", "c", time=2)
TG.add_edge("d", "e", time=2)
TG.add_edge("a", "c", time=2)
TG.add_edge("f", "e", time=3)
TG.add_edge("f", "a", time=3)
TG.add_edge("f", "b", time=3)

# Slice into snapshots.
TG = TG.slice(attr="time")

# Plot resulting object.
draw_temporal_graph(TG)
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_7.png)

## Cite

At the moment, we do not have a published article about **networkx-temporal**. If it is useful for your research, please consider citing it by linking to the project page instead:


```tex
@misc{networkxtemporal2024,
    title = {The networkx-temporal Python library: build and manipulate dynamic graphs},
    author = {Nelson Aloysio Reis de Almeida Passos and Emanuele Carlini and Salvatore Trani},
    url = {http://pypi.org/p/networkx-temporal},
    year = {2024}
}
```

```tex
@inproceedings{networkx2008,
  title={Exploring network structure, dynamics, and function using NetworkX},
  author={Aric Hagberg and Pieter Swart and Daniel S Chult},
  booktitle={Proceedings of the 7th Python in Science Conference (SciPy2008)},
  location={Pasadena, CA USA},
  year={2008},
  pages={11--15},
  month={8},
}
```

___

## References

* [Deep Graph Library](https://www.dgl.ai/)
* [graph-tool](https://graph-tool.skewed.de/)
* [igraph](https://igraph.org/python/)
* [Leiden](https://leidenalg.readthedocs.io)
* [NetworKit](https://networkit.github.io/)
* [NetworkX](https://networkx.github.io)
* [Pandas](https://pandas.pydata.org/)
* [PyTorch Geometric](https://pytorch-geometric.readthedocs.io)
* [Teneto](https://teneto.readthedocs.io)
