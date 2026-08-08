from .generators import (generate_block_matrix,
                         generate_community_vector,
                         generate_transition_matrix)
from .sbm import dynamic_stochastic_block_model
from ..typing import TemporalMultiGraph


def example_sbm_graph() -> TemporalMultiGraph:
    """ Returns a dynamic stochastic block model graph.

    This function calls :func:`~networkx_temporal.generators.dynamic_sbm` to create a temporal
    graph with 75 nodes divided into 3 communities, composed of 3 snapshots. Edges between nodes
    within the same community are created with a probability of 20%, or 1% among different
    communities, and nodes transition communities with a probability of 10% at each snapshot.

    Not all nodes are guaranteed to be connected at each snapshot and isolates are removed.

    .. rubric:: Example

    To load the dataset:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.example_sbm_graph()
        >>> print(TG)

        TemporalMultiGraph (t=3) with 75 nodes and 563 edges

    Which corresponds to the graph generated with
    :func:`~networkx_temporal.generators.dynamic_sbm` as follows:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> k = 3         # Number of communities.
        >>> n = 25        # Number of nodes.
        >>> t = 3         # Number of snapshots.
        >>> p_in = 0.2    # Probability of within-community edges.
        >>> p_out = 0.01  # Probability of between-community edges.
        >>>
        >>> B = tx.generate_block_matrix(k, p=p_in, q=p_out)
        >>> z = tx.generate_community_vector(nodes=n, k=k)
        >>> tau = tx.generate_transition_matrix(k, eta=0.9)
        >>> TG = tx.dynamic_sbm(B, z, t=t, transition_matrix=tau, isolates=False, seed=10)
        >>>
        >>> tx.draw(TG,
        ...         figsize=(8, 3),
        ...         layout="circular",
        ...         node_size=30,
        ...         edge_color="#ccc",
        ...         temporal_node_color=tx.get_node_attributes(TG, "community", index=False),
        ...         with_labels=False)

    .. image:: ../../assets/figure/generators/example_sbm_graph.png
       :align: center
    """
    B = generate_block_matrix(k=3, p=0.2, q=0.01)
    z = generate_community_vector(nodes=25, k=3)
    tau = generate_transition_matrix(k=3, eta=0.9)
    TG = dynamic_stochastic_block_model(B, z, t=3, transition_matrix=tau, isolates=False, seed=10)
    return TG
