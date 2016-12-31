import random
import string
import networkx as nx
from collections import defaultdict


def build_graph_from_df(df):
    g = nx.Graph()
    for _, r in df.iterrows():
        g.add_edge(r['retweeter'], r['retweetee'])
    return g


def sample_edges_to_add(g, n_edges_to_add,
                        unknown_nodes_pool=list(string.ascii_lowercase)):
    n = 0
    edges_to_add = []
    nodes = g.nodes()
    while n < n_edges_to_add:
        while True:
            u = v = random.choice(nodes)
            
            if random.random() > 0.5:  # 0.5 proba to sample unknown nodes
                edges_to_add.append((u, random.choice(unknown_nodes_pool)))
                break
            else:  # 0.5 proba to sample existing edge
                while u == v:
                    v = random.choice(nodes)
                if not g.has_edge(u, v):
                    edges_to_add.append((u, v))
                    break
        n += 1
    return edges_to_add


class tw_list():
    def __init__(self, data=None, timestamps=None):
        if data is None or timestamps is None:
            data = []
            timestamps = []
        assert len(data) == len(timestamps)
        self.data = data
        self.ts = timestamps
        
    def remove_before_time(self, t):
        i = 0
        while i < len(self.ts) and self.ts[i] < t:
            i += 1
        removed_data = self.data[:i]
        self.ts = self.ts[i:]
        self.data = self.data[i:]
        return removed_data
        
    def append(self, e, t):
        self.data.append(e)
        self.ts.append(t)
        
    def __repr__(self):
        return ', '.join(map(lambda t: '{0}({1})'.format(t[0], t[1]),
                             zip(self.data, self.ts)))


def get_cut_ratio(g, cluster_node_ids):
    """support only 2 partitions currently
    """
    partition = defaultdict(set)
    for n, c in zip(g.nodes_iter(), cluster_node_ids):
        partition[c].add(n)
        
    c1, c2 = list(partition.values())
    cuts = 0.0
    for u, v in g.edges_iter():
        if (u in c1 and v in c2) or (u in c2 and v in c1):
            cuts += 1

    return cuts / g.number_of_edges()


def add_edges(g, edges):
    """the same edges can be added multiple times"""
    for i, j in edges:
        if g.has_edge(i, j):
            g[i][j]['count'] += 1
        else:
            g.add_edge(i, j, count=1)
    return g


def remove_edges(g, edges):
    """the same edges can be removed multiple times. 
    It will be really removed if the count drops to 0"""
    for i, j in edges:
        g[i][j]['count'] -= 1
        if g[i][j]['count'] == 0:
            g.remove_edge(i, j)
    return g


def get_largest_connected_subgraph(g):
    ccs = nx.connected_components(g)
    nodes = max(ccs, key=len)
    return g.subgraph(nodes)


def largest_cc_size(g):
    ccs = nx.connected_components(g)
    return max(map(len, ccs))
