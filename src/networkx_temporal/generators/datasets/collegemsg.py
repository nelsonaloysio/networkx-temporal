import gzip
from datetime import datetime
from pathlib import Path

import networkx as nx

from ...transform import from_static
from ...typing import TemporalMultiDiGraph

DATA_PATH = Path(__file__).parent.resolve() / "collegemsg"


def collegemsg_graph() -> TemporalMultiDiGraph:
    """ Returns the CollegeMsg temporal graph.

    The CollegeMsg dataset [12]_ is a temporal social network representing private
    messages sent between students at the University of California, Irvine.
    Nodes represent students, and a directed edge from node :math:`u` to node :math:`v`
    at time :math:`t` indicates that student :math:`u` sent a message to student :math:`v`
    at time :math:`t`. The dataset spans 1,899 students and 59,835 messages over 193 days.

    Edges have a ``'time'`` attribute indicating the date the message was sent, following
    the ``'YYYY-MM-DD HH:MM'`` format, e.g., ``'2002-04-05 17:30'``.

    .. rubric:: Example

    To load the dataset and :func:`~networkx_temporal.classes.TemporalGraph.slice` the graph into
    daily snapshots:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>> from datetime import datetime
        >>>
        >>> TG = tx.generators.collegemsg_graph()
        >>>
        >>> def to_date(x):
        >>>     # Convert hourly dates to YYYY-MM-DD format, allowing to sort them by day.
        >>>     return datetime.strptime(x.strip(), "%Y-%m-%d %H:%M").strftime("%Y-%m-%d")
        >>>
        >>> TG = TG.slice(attr="time", apply_func=to_date)
        >>> print(TG)

        TemporalMultiDiGraph (t=193) with 1899 nodes and 59835 edges

    .. [12] Pietro Panzarasa, Tore Opsahl, and Kathleen M. Carley.
        ''Patterns and dynamics of users' behavior and interaction: Network analysis of an
        online community''. Journal of the American Society for Information Science and
        Technology 60.5 (2009): 911-932.
        doi: `10.1002/asi.21015 <https://doi.org/10.1002/asi.21015>`__.

    """
    def to_date(x):
        return datetime.strptime(x.strip(), "%m/%d/%y %I:%M %p").strftime("%Y-%m-%d %H:%M")

    with gzip.open(DATA_PATH / "collegemsg.csv.gz", "r") as f:
        G = nx.read_edgelist(f.readlines()[1:],
                             create_using=nx.MultiDiGraph,
                             data=[("time", str)],
                             delimiter=",",
                             nodetype=int)

    # Convert date attribute "4/5/02 05:30 PM" to "2002-04-05 17:30" for correct sorting.
    nx.set_edge_attributes(
        G,
        {e: to_date(d["time"]) for e, d in G.edges.items()},
        "time"
    )

    TG = from_static(G)
    TG = TG.slice(attr="time", apply_func=lambda x: x.split()[0])
    TG.name = "CollegeMsg"
    return TG
