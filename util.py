import networkx as nx


def build_graph_from_df(df):
    g = nx.Graph()
    for _, r in df.iterrows():
        g.add_edge(r['retweeter'], r['retweetee'])
    return g
