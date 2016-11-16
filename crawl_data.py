import sys
import ujson as json

import pymongo
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from datetime import datetime as dt


with open('keys.txt', 'r') as f:
    consumer_key = f.readline().strip()
    consumer_secret = f.readline().strip()
    access_token = f.readline().strip()
    access_token_secret = f.readline().strip()


DB = 'controversy'


def convert_tweet(d):
    return {
        'message_id': d['id'],
        'body': d['text'],
        'retweeter': d['user']['id'],
        'retweetee': d['retweeted_status']['user']['id'],
        'created_at': dt.fromtimestamp(float(d['timestamp_ms']) / 1000),
        "hashtags": [h['text'] for h in d['entities']["hashtags"]],
    }


class StdOutListener(StreamListener):
    def __init__(self, mongo_col):
        self.collection = pymongo.MongoClient()[DB][mongo_col]
        # self.collection.remove()
        
    def on_data(self, raw_data):
        try:
            data = json.loads(raw_data)
            if ('retweeted_status' in data and data.get("lang") == 'en'):
                if ("entities" in data and
                    len(data["entities"].get('hashtags', [])) > 0):
                    tweet = convert_tweet(data)
                    self.collection.insert(tweet)
        except:
            import traceback
            traceback.print_exc(file=sys.stdout)
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('')
    
    parser.add_argument('--terms', nargs='*')
    parser.add_argument('--mongo_col')
    
    args = parser.parse_args()

    l = StdOutListener(args.mongo_col)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    if args.terms:
        stream.filter(track=args.terms)
    else:
        while True:
            try:
                stream.sample()
            except:
                pass
