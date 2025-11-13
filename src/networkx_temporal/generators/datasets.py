import gzip
from datetime import datetime
from pathlib import Path

import networkx as nx

from ..transform import from_static
from ..typing import TemporalGraph

DATA_PATH = Path(__file__).parent.resolve() / "data"


def collegemsg_graph() -> TemporalGraph:
    """ Returns the CollegeMsg temporal graph.

    The CollegeMsg dataset [12]_ is a temporal social network representing private
    messages sent between students at the University of California, Irvine.
    Nodes represent students, and a directed edge from node :math:`u` to node :math:`v`
    at time :math:`t` indicates that student :math:`u` sent a message to student :math:`v`
    at time :math:`t`. The dataset spans 1,899 students and 59,835 messages over 193 days.

    Edges have a ``'time'`` attribute indicating the date the message was sent, following
    the ``'%m/%d/%y %I:%M %p'`` format, e.g., ``'4/5/02 12:30 PM'``, which may be parsed
    to produce a sliced graph.

    .. rubric:: Example

    To load the dataset and :func:`~networkx_temporal.classes.TemporalGraph.slice` the graph into
    daily snapshots:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>> from datetime import datetime
        >>>
        >>> TG = tx.collegemsg_graph()
        >>>
        >>> def to_date(x):
        >>>     # Convert dates to YYYY-MM-DD format, allowing to sort them correctly.
        >>>     return datetime.strptime(x.strip(), "%m/%d/%y %I:%M %p").strftime("%Y-%m-%d")
        >>>
        >>> TG = TG.slice(attr="time", apply_func=to_date)
        >>> print(TG)

        TemporalMultiDiGraph with 1899 nodes and 59835 temporal edges

    .. [12] Pietro Panzarasa, Tore Opsahl, and Kathleen M. Carley.
        ''Patterns and dynamics of users' behavior and interaction: Network analysis of an
        online community''. Journal of the American Society for Information Science and
        Technology 60.5 (2009): 911-932.
        doi: `10.1002/asi.21015 <https://doi.org/10.1002/asi.21015>`__.

    """
    with gzip.open(DATA_PATH / "collegemsg.csv.gz", "r") as f:
        G = nx.read_edgelist(f.readlines()[1:],
                             create_using=nx.MultiDiGraph,
                             data=[("time", str)],
                             delimiter=",",
                             nodetype=int)
    return from_static(G)
