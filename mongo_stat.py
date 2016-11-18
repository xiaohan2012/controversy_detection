import pymongo
from collections import Counter

DB = 'controversy'
mongo_col = 'nov16'
col = pymongo.MongoClient()[DB][mongo_col]

print('#retweets {}'.format(col.find().count()))

hashtag_freq = Counter([h for r in col.find() for h in r['hashtags']])
print(hashtag_freq.most_common(10))

    
