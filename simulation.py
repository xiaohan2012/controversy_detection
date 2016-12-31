import networkx as nx
import metis
from collections import defaultdict
from datetime import timedelta, datetime
from tqdm import tqdm

from rwc import controversy_score
from util import tw_list, get_cut_ratio, add_edges, remove_edges, largest_cc_size
from leopard import update_partition

DEBUG = False


# prevent pickling error in multiprocessing
def defaultdict_using_list_func():
    return defaultdict(list)


def earlist_date_func():
    return datetime(1970, 1, 1)


def run_simulation(retweets, update_interval,
                   T_window, top_node_percent, incremental,
                   top_k=10,
                   top_k_computation_interval=timedelta(days=365),
                   min_rwc_score=0.8,
                   head_n=12*1e5,
                   return_log=False,
                   return_graph=False):
    """
    update_interval: graph stat update interval
    T_window: time window
    top_node_percent: the number of nodes to consider for RWC calculation
    incremental: incremental1 computation or not
    
    top_k: integer
    top_k_computation_interval: interval to update top-k list
    min_rwc_score: minimum RWC score to be considered as controversial
    head_n: number of retweets to process
    
    Returns:
    
    tag2log: logging for update on each tag
    running_stat: running statistics
    top_hashtags_by_time: top hashtags at different times
    tag2g: hashtag to graph
    """
    running_stat = {
        'start_time': datetime.now(),
        'update_interval': update_interval,
        'T_window': T_window,
        'incremental': incremental
    }
    # logging for tags
    tag2log = defaultdict(defaultdict_using_list_func)
    
    # internal data structures
    tag2g = defaultdict(nx.Graph)
    tag2edge_list = defaultdict(tw_list)
    tag2edges_rm = defaultdict(list)
    tag2edges_add = defaultdict(list)
    
    top_hashtags_by_time = []  # TODO: top hashtags at different time points

    last_updated_time = defaultdict(earlist_date_func)
    last_topk_computation_time = earlist_date_func()
    
    for i, rt in tqdm(retweets.head(int(head_n)).iterrows()):
        if i % 5000 == 0:
            # print('#hashtags {}'.format(len(tag2g)))
            # print('now {}'.format(rt['created_at']))
            pass

        h = rt['hashtag']
        g = tag2g[h]
        edge_list = tag2edge_list[h]

        u, v, now = rt['retweeter'], rt['retweetee'], rt['created_at']

        tag2edges_add[h].append((u, v))
        edge_list.append((u, v), now)
        
        # remove expired edges by triggered hashtag or do it periodically?
        earlist_time = now - T_window
        edges_to_remove = edge_list.remove_before_time(earlist_time)
        if edges_to_remove:
            # print('#edges_to_remove {}'.format(len(edges_to_remove)))
            tag2edges_rm[h] += edges_to_remove

        last_updated_time = g.graph.get('last_updated_time')

        if last_updated_time is None or now - last_updated_time > update_interval:
            # when the graph is processed for the 1st time
            # and it's very small, it will not be updated
            updated = False

            # update
            edges_to_add = tag2edges_add[h]
            edges_to_rm = tag2edges_rm[h]
            
            # empty it
            tag2edges_add[h] = []
            tag2edges_rm[h] = []

            pr_vects = g.graph.get('pagerank_vectors')
            if not pr_vects or not incremental:  # 1st time
                add_edges(g, edges_to_add)
                remove_edges(g, edges_to_rm)
                # g.add_edges_from(edges_to_add)
                # g.remove_edges_from(edges_to_rm)
                
                # remove zero degree nodes
                nodes_to_remove = [n for n in g.nodes_iter() if g.degree(n) == 0]
                if nodes_to_remove:
                    # print('removing {} nodes'.format(len(nodes_to_remove)))
                    g.remove_nodes_from(nodes_to_remove)
                
                if largest_cc_size(g) > 100:  # only calculate RWC when the largest CC is big enough
                    if DEBUG:
                        # print_log()
                        pass
                    cuts, node_cluster_ids = metis.part_graph(g, 2)
                    node2cluster = {n: c for n, c in zip(g.nodes_iter(), node_cluster_ids)}
                    rwc, aux = controversy_score(g, node2cluster, top_percent=top_node_percent)
                    assert g.number_of_nodes() == len(node_cluster_ids)
                    updated = True
            else:  # incremental
                if DEBUG:
                    print('updating')
                    # print_log()
                node2cluster = g.graph['node2cluster']
                node2cluster = update_partition(g, node2cluster,
                                                edges_to_add=edges_to_add,
                                                edges_to_remove=edges_to_rm,
                                                verbose=False)
                # print('hashtag {}'.format(h))
                # print('tag2log {}'.format(tag2log[h]))

                # only update if graph is big enough
                if largest_cc_size(g) > 100:
                    pr0 = {n: pr_vects['pr0'].get(n, 1e-8) for n in g.nodes_iter()}
                    pr1 = {n: pr_vects['pr1'].get(n, 1e-8) for n in g.nodes_iter()}
                    rwc, aux = controversy_score(g, node2cluster,
                                                 top_percent=top_node_percent,
                                                 nstart0=pr0,
                                                 nstart1=pr1)
                    updated = True
                else:
                    updated = False
            if updated:
                # remove zero-degree nodes
                g.graph['node2cluster'] = node2cluster
                g.graph['pagerank_vectors'] = {'pr0': aux['pr0'], 'pr1': aux['pr1']}
                g.graph['rwc'] = rwc
                g.graph['last_updated_time'] = now  # TODO: now should be changed

                tag2log[h]['rwc'].append(rwc)
                tag2log[h]['graph_size'].append(g.number_of_nodes())
                tag2log[h]['cut_ratio'].append(get_cut_ratio(g, node_cluster_ids))
                tag2log[h]['updated_time'].append(now)

        if (now - last_topk_computation_time) > top_k_computation_interval:
            # filter out non-controversial hashtags
            controversial_tags = filter(lambda h: tag2g[h].graph.get('rwc', 0.0) >= min_rwc_score, tag2g)
            
            # top-k hashtag update
            # greedy approach
            node_set = set()
            top_tags = []
            candidate_tags = set(controversial_tags)
            while len(top_tags) < top_k:
                max_set_size = len(node_set)
                best_tag = None
                for h in candidate_tags:
                    new_set_size = len(node_set | set(tag2g[h].nodes()))
                    if max_set_size < new_set_size:
                        max_set_size = new_set_size
                        best_tag = h
                if best_tag is not None:
                    top_tags.append(best_tag)
                    # print('adding {} new nodes from "{}"'.format(len(set(tag2g[best_tag].nodes()) - node_set), best_tag))
                    node_set |= set(tag2g[best_tag].nodes())
                    candidate_tags.remove(best_tag)
                else:
                    break
            # print('top-k tags: {}'.format(top_tags))
            top_hashtags_by_time.append({
                    'list': [{'tag': t,
                              'size': tag2g[t].number_of_nodes(),
                              'rwc': tag2g[t].graph['rwc'],
                             }
                             for t in top_tags],
                    'time': now
                    })
            last_topk_computation_time = now

    running_stat['end_time'] = datetime.now()
    to_return = (running_stat, top_hashtags_by_time)
    if return_log:
        to_return += (tag2log, )
    if return_graph:
        to_return += (tag2g, )
    return to_return
