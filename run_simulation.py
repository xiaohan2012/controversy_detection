
# coding: utf-8

# In[2]:
import networkx as nx
import metis
import pickle
import pandas as pd
import random
from scipy.stats import pearsonr
from collections import defaultdict
from datetime import timedelta, datetime
from tqdm import tqdm
from joblib import Parallel, delayed

from rwc import controversy_score
from util import tw_list, get_cut_ratio, add_edges, remove_edges
from leopard import update_partition



# In[3]:

retweets = pd.read_pickle('data/july.pkl')


# In[4]:

retweets.sort_values(by=['created_at'], axis='index', inplace=True)


# In[5]:

DEBUG = False
incremental = True
update_interval = timedelta(minutes=10)
T_window = timedelta(minutes=60*12)
top_node_percent=0.01


# In[6]:

# prevent pickling error in multiprocessing
def defaultdict_using_list_func(): 
    return defaultdict(list)

def earlist_date_func(): 
    return datetime(1970, 1, 1)


# In[13]:

from simulation import run_simulation
# some test
result = run_simulation(retweets,
                        T_window=T_window,
                        top_node_percent=top_node_percent,
                        update_interval=update_interval,                        
                        incremental=True,
                        top_k=10,
                        top_k_computation_interval=timedelta(minutes=60),
                        min_rwc_score=0.85,
                        head_n=12*1e5,
                        return_graph=True
                       )


pickle.dump(result, open('output/simulation_result.pkl', 'wb'))
