import numpy as np
from tqdm import tqdm
from itertools import chain
from collections import defaultdict
from util import add_edges, remove_edges


GAMMA = 1.5


def get_alpha(g, k=2, gamma=GAMMA):
    return np.sqrt(k) * g.number_of_edges() / np.power(g.number_of_nodes(), GAMMA)


def attempt_reassignment(g, n, partition, node2cluster, gamma, alpha):
    assert g.has_node(n)
    
    c_star = best_cluster_id(g, n, partition, gamma, alpha)
    did_it = False
    node_exist = (n in node2cluster)
    if node_exist:
        if node2cluster[n] != c_star:
            partition[node2cluster[n]].remove(n)
            partition[c_star].add(n)
            node2cluster[n] = c_star
            did_it = True
    else:
        partition[c_star].add(n)
        node2cluster[n] = c_star
        did_it = True
    return did_it, partition, node2cluster


def best_cluster_id(g, u, part, gamma, alpha):
    """part: dict(cluster_id, set of node)
    the partition information
    alpha, gamma: balancing parameter"""
    N_u = set(g.neighbors(u))
    
    def score(c):
        s = (len(part[c].intersection(N_u)) -
             alpha * gamma / 2 * np.power(len(part[c]), gamma-1))
        return s
    
    return max(part, key=score)


def update_partition(g,
                     node2cluster,
                     k=2,
                     edges_to_add=[],
                     edges_to_remove=[],
                     gamma=GAMMA,
                     verbose=True):
    """                                                                                                                                                                             
    incrementally update the partitioning
    node2cluster: node to cluster id

    return:
        list of updated cluster ids
    """
    if len(edges_to_add) == 0 and len(edges_to_remove) == 0:
        print('nothing to update')
        return node2cluster

    assert len(node2cluster) == g.number_of_nodes(), '{} \n {}'.format(
        set(node2cluster) - set(g.nodes()),
        set(g.nodes()) - set(node2cluster)
    )

    # print(node2cluster)
    if edges_to_add:
        add_edges(g, edges_to_add)
    if edges_to_remove:
        remove_edges(g, edges_to_remove)

    partition = defaultdict(set)  # cluster id to list of nodes
    for n, p in node2cluster.items():
        partition[p].add(n)

    alpha = get_alpha(g, gamma=gamma)
    params = {'gamma': gamma, 'alpha': alpha}
    edge_iters = chain(edges_to_add, edges_to_remove)
    if verbose:
        edge_iters = tqdm(edge_iters)

    for u, v in edge_iters:
        if verbose:
            print('edge ({}, {})'.format(u, v))
        if not g.has_node(u):
            print(u)
            print(edges_to_add)
            print(edges_to_remove)
        affected_nodes = set()
        did_it, partition, node2cluster = attempt_reassignment(g, u,
                                                               partition,
                                                               node2cluster,
                                                               **params)
        if did_it:
            if verbose:
                print('moved node {}'.format(u))
            affected_nodes |= set(g.neighbors(u))

        did_it, partition, node2cluster = attempt_reassignment(g, v,
                                                               partition,
                                                               node2cluster,
                                                               **params)
        if did_it:
            if verbose:
                print('moved node {}'.format(v))
            affected_nodes |= set(g.neighbors(v))

        for n in affected_nodes:
            if True:
                did_it, partition, node2cluster = attempt_reassignment(
                    g, n, partition, node2cluster, **params)
                if verbose:
                    if did_it:
                        print('moved node {}'.format(n))
                    else:
                        print('{} stayed'.format(n))

    # remove zero degree nodes
    nodes_to_remove = [n for n in g.nodes_iter() if g.degree(n) == 0]
    if nodes_to_remove:
        # print('removing {} nodes'.format(len(nodes_to_remove)))
        g.remove_nodes_from(nodes_to_remove)
        for n in nodes_to_remove:
            del node2cluster[n]
                        
    return node2cluster
