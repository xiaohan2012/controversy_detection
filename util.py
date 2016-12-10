import random
import string
import networkx as nx


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
