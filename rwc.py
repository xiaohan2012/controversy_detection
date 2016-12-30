import networkx as nx
import numpy as np
from collections import Counter


def populate_r_and_c(g, pr, target_nodes, k):
    """
    populate data to vectors

    g: graph
    pr: pagerank scores (dict)
    targetr_nodes: list of nodes to consider
    k: number of highest degree nodes to take
    
    return: two vectors
    r: page rank score
    c: node importance on target_nodes in terms of
    """
    r = np.zeros(g.number_of_nodes())
    node2id = {n: i for i, n in enumerate(g.nodes_iter())}
    for n in g.nodes_iter():
        r[node2id[n]] = pr[n]
        
    # take highest degree nodes
    top_nodes = sorted(target_nodes,
                       key=lambda n: g.degree(n),
                       reverse=True)[:k]
    c = np.zeros(g.number_of_nodes())
    for n in top_nodes:
        c[node2id[n]] = 1
    return r, c


def controversy_score(g, node2cluster, top_percent=0.001, nstart0=None, nstart1=None):
    """consider only two sides only                               
    
    node2cluster: node to cluster id dict
    
    top_percent: percentage of high degree nodes to consider for the c vector
    
    nstart1, nstart2: the nstart parameter in networkx.pagerank for both sides
        if None, then start from scratch
        
    returns:
    
    rwc_score
    
    aux_info: for example, pagerank for both sides
    """
    k = int(g.number_of_nodes() * top_percent)
    if k == 0:
        raise ValueError('only contains {} nodes, does not work for percent {}'.format(
            g.number_of_nodes(), top_percent))

    # cuts, node2cluster = metis.part_graph(g)
    aux = lambda p, target: int(target == p)

    # personalization vector
    part_sizes = Counter(node2cluster.values())
    e_0 = {n: aux(p, 0) / part_sizes[0] for n, p in node2cluster.items()}
    e_1 = {n: aux(p, 1) / part_sizes[1] for n, p in node2cluster.items()}

    # pagerank scores
    pr0 = nx.pagerank(g, alpha=0.85, personalization=e_0, dangling=e_0, max_iter=10000, nstart=nstart0)
    pr1 = nx.pagerank(g, alpha=0.85, personalization=e_1, dangling=e_1, max_iter=10000, nstart=nstart1)

    # nodes at two sides
    nodes0 = [n for n, p in node2cluster.items() if p == 0]
    nodes1 = [n for n, p in node2cluster.items() if p == 1]

    r0, c0 = populate_r_and_c(g, pr0, nodes0, k)
    r1, c1 = populate_r_and_c(g, pr1, nodes1, k)

    r_list = [r0, r1]
    c_list = [c0, c1]
    rwc0 = rwc1 = 0
    k = len(r_list)
    for i, r in enumerate(r_list):
        for j, c in enumerate(c_list):
            prod = np.sum(r * c)
            # print(prod, prod * part_sizes[i])    
            if i == j:
                rwc0 += (prod * part_sizes[i])
            else:
                rwc1 += (prod * part_sizes[i])
    rwc = rwc0 / (rwc0 + rwc1)
    aux_info = {
        'pr0': pr0,
        'pr1': pr1
    }
    return rwc, aux_info
