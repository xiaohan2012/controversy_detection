import random
import networkx as nx


def build_graph_from_df(df):
    g = nx.Graph()
    for _, r in df.iterrows():
        g.add_edge(r['retweeter'], r['retweetee'])
    return g


def sample_edges_to_add(g, n_edges_to_add):
    n = 0
    edges_to_add = []
    nodes = g.nodes()
    while n < n_edges_to_add:
        while True:
            u = v = random.choice(nodes)
            while u == v:
                v = random.choice(nodes)
            if not g.has_edge(u, v):
                edges_to_add.append((u, v))
                break
        n += 1
    return edges_to_add
