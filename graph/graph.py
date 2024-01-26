import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


def _process_params(center, dim):
    # Some boilerplate code.
    import numpy as np

    if center is None:
        center = np.zeros(dim)
    else:
        center = np.asarray(center)

    print(center, dim)
    if len(center) != dim:
        msg = "length of center coordinates must match dimension of layout"
        raise ValueError(msg)

    return center

class RandomGraph:
    """
    A class for creating and analyzing random undirected or directed graphs using the Snap.py library.

    Parameters:
    - n_nodes (int): The number of nodes in the graph.
    - n_edges (int): The number of edges in the graph.
    - is_directed (bool): True for directed graphs, False for undirected graphs.

    Example Usage:
    ```python
    # Create an undirected graph with 10 nodes and 20 edges
    graph = PlainGraph(n_nodes=10, n_edges=20, is_directed=False)
    ```

    Attributes:
    - n_nodes (int): The number of nodes in the graph.
    - n_edges (int): The number of edges in the graph.
    - is_directed (bool): True for directed graphs, False for undirected graphs.
    - graph (Snap.py graph object): The Snap.py graph representing the random graph.
    - n_degree (dict): A dictionary to store the degree distribution of nodes.
    """

    def __init__(self, n_nodes=0, n_edges=0, is_directed=False, verbose=False):
            """
            Initialize a RandomGraph object with the specified number of nodes and edges.

            Parameters:
            - n_nodes (int): The number of nodes in the graph.
            - n_edges (int): The number of edges in the graph.
            - is_directed (bool): True for directed graphs, False for undirected graphs.
            """
            self.n_nodes = n_nodes
            self.n_edges = n_edges
            self.is_directed = is_directed
            self.verbose = verbose

            # Check if the number of edges is appropriate for the number of nodes
            max_edges = self.n_nodes * (self.n_nodes - 1)
            if not is_directed:
                max_edges /= 2
            if n_edges > max_edges:
                raise ValueError(f"Number of edges cannot be more than {max_edges} for a {self.n_nodes} node {'directed' if is_directed else 'undirected'} graph")

            # Create a random graph using networkx
            if self.is_directed:
                self.graph = nx.gnm_random_graph(n=self.n_nodes, m=self.n_edges, directed=True)
            else:
                self.graph = nx.gnm_random_graph(n=self.n_nodes, m=self.n_edges, directed=False)

            # Initialize degree distribution dictionary
            self.n_degree = {i: 0 for i in range(n_nodes)}
            for _, degree in self.graph.degree():
                self.n_degree[degree] += 1

            if self.verbose:
                print(f"Random {'directed' if is_directed else 'undirected'} graph with {n_nodes} nodes and {n_edges} edges created.")

    def __repr__(self):
        """
        Return a string representation of the PlainGraph object.
        """
        graph_type = "Directed" if self.is_directed else "Undirected"
        return f"Random Snap Graph ({graph_type}): Nodes={self.n_nodes}, Edges={self.n_edges}"

    def set_nodes(self):
        """
        Set the list of nodes in the graph.
        """
        self.nodes = list(self.graph.nodes())

    @property
    def get_nodes(self) -> list:
        """
        Get the list of nodes in the graph.

        Returns:
        - list: A list of node IDs.
        """
        if not hasattr(self, 'nodes'):
            self.set_nodes()
        return self.nodes

    def set_edges(self):
        """
        Set the list of edges in the graph.
        """
        self.edges = [(u, v) for u, v in self.graph.edges()]

    @property
    def get_edges(self) -> list:
        """
        Get the list of edges in the graph.

        Returns:
        - list: A list of edge tuples (source node, target node).
        """
        if not hasattr(self, 'edges'):
            self.set_edges()
        if self.verbose:
            for u, v in self.graph.edges():
                print(f"edge: ({u}, {v})")
        return self.edges

    def create_adjacency_list(self):
        """
        Create an adjacency list from the edges data.

        Returns:
        - list of lists: An adjacency list where each index indicates a vertex, and the item is a list of adjacent vertices.
        """
        adjacency_list = [[] for _ in range(self.n_nodes)]

        for edge in self.get_edges:
            source, target = edge
            adjacency_list[source].append(target)
            if not self.is_directed:
                adjacency_list[target].append(source)  # For undirected graphs, add both directions

        return adjacency_list

    @property
    def get_adjacency_list(self):
        """
        Get the adjacency list for the graph.

        Returns:
        - list of lists: An adjacency list where each index indicates a vertex, and the item is a list of adjacent vertices.
        """
        if not hasattr(self, 'adjacency_list'):
            self.adjacency_list = self.create_adjacency_list()
        if self.verbose:
            print(f"Adjacency list for the graph: {self.adjacency_list}")
        return self.adjacency_list


    def get_degree_distribution(self):
        """
        Get the degree distribution of nodes in the graph.

        Returns:
        - dict: A dictionary with node IDs as keys and their degrees as values.
        """
        return dict(self.graph.degree())

    def get_average_degree(self):
        """
        Get the average degree of nodes in the graph.

        Returns:
        - float: The average degree.
        """
        if len(self.graph) == 0:
            return 0
        return 2 * self.graph.number_of_edges() / len(self.graph)

    def get_clustering_coefficient(self):
        """
        Get the clustering coefficient of the graph.

        Returns:
        - float: The clustering coefficient.
        """
        return nx.average_clustering(self.graph)

    def get_number_of_connected_components(self):
        """
        Get the number of connected components in the graph.

        Returns:
        - int: The number of connected components.
        """
        if self.is_directed:
            return nx.number_strongly_connected_components(self.graph)
        else:
            return nx.number_connected_components(self.graph)

    def random_layout(self, center=None, dim=2, seed=42):
        """Position nodes uniformly at random in the unit square.

        For every node, a position is generated by choosing each of dim
        coordinates uniformly at random on the interval [0.0, 1.0).

        NumPy (http://scipy.org) is required for this function.

        Parameters
        ----------

        center : array-like or None
            Coordinate pair around which to center the layout.

        dim : int
            Dimension of layout.

        seed : int, RandomState instance or None  optional (default=None)
            Set the random state for deterministic node layouts.
            If int, `seed` is the seed used by the random number generator,
            if numpy.random.RandomState instance, `seed` is the random
            number generator,
            if None, the random number generator is the RandomState instance used
            by numpy.random.

        Returns
        -------
        pos : dict
            A dictionary of positions keyed by node

        Examples
        --------
        >>> G = nx.lollipop_graph(4, 3)
        >>> pos = nx.random_layout(G)

        """
        import numpy as np

        center = _process_params(center, dim)

        # Set the default seed if none is provided
        default_seed = 42  # Arbitrary number; you can choose any integer
        rng = np.random.default_rng(seed if seed is not None else default_seed)

        # Generate random positions in the range [-3, 3) for each dimension
        pos = rng.uniform(-3.5, 3.5, (len(self.graph), dim))
        if center is not None:
            pos += center

        pos = pos.astype(np.float32)
        pos = dict(zip(self.graph, pos))

        return pos
    
    def plot_graph(self, filename='graph_edges.jpg', graph_title='List of edges'):
        plt.figure(figsize=(8, 6))
        nx.draw_random(self.graph, with_labels=False, font_weight='bold', node_size=40, width=0.2)
        plt.title(graph_title)
        plt.savefig(filename)
        plt.close()

    def save_graph_txt(self, filename='graph_edges.txt', title='List of edges'):
        with open(filename, 'w') as f:
            for line in nx.generate_edgelist(self.graph, data=False):
                f.write(f"{line}\n")
        return f"Graph saved to {filename}"





if __name__ == "__main__" :
    random_graph = RandomGraph(n_nodes=30, n_edges=100, verbose=True, is_directed=False)
    random_graph.plot_graph()
    random_graph.save_graph_txt()
    print(random_graph.random_layout())

    