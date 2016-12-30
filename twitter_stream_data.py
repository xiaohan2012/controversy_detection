
# coding: utf-8

# In[55]:

import bz2
import ujson as json
import os
import sys
import pandas as pd
from glob import glob
from pprint import pprint
from tqdm import tqdm
from datetime import datetime as dt

# In[ ]:

rootdir = '/home/cloud-user/Downloads/2016-07/'

if False:
    output_dir = 'data/retweets_16july'
    retweets = []
    bulk_counter = 0
    for dirname, _, files in os.walk(rootdir):
        print(dirname)
        for filename in files:
            with bz2.BZ2File(os.path.join(dirname, filename)) as f:
                for l in f:
                    r = json.loads(l)
                    if r.get('lang') == 'en' and r['entities'].get('hashtags') and 'retweeted_status' in r:
                        for h in r['entities']["hashtags"]:
                            retweets.append({
                                'message_id': r['id'],
                                'retweeter': r['user']['id'],
                                'retweetee': r['retweeted_status']['user']['id'],
                                'created_at': dt.fromtimestamp(float(r['timestamp_ms']) / 1000),
                                "hashtag": h['text'],
                           })
                            if len(retweets) % 1e5 == 0:
                                df = pd.DataFrame.from_records(retweets)
                                df.to_pickle(os.path.join(output_dir, '{}.pkl'.format(bulk_counter)))
                                retweets = []
                                bulk_counter += 1
                                print(bulk_counter)


if True:
    retweets = []
    bulk_counter = 0
    output_dir = 'data/july_text'
    for dirname, _, files in os.walk(rootdir):
        for filename in files:
            with bz2.BZ2File(os.path.join(dirname, filename)) as f:
                for l in tqdm(f):
                    r = json.loads(l)
                    if r.get('lang') == 'en' and r['entities'].get('hashtags') and 'retweeted_status' in r:
                        retweets.append((r['id'], r['text']))
                    if len(retweets) > 0 and len(retweets) % 1e5 == 0:
                        df = pd.DataFrame(retweets, columns=('id', 'body'))
                        df.to_pickle(os.path.join(output_dir, '{}.pkl'.format(bulk_counter)))
                        retweets = []
                        bulk_counter += 1
                        print(bulk_counter)
