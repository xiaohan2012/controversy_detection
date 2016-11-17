import pandas as pd

from pymongo import MongoClient

DB = 'controversy'
mongo_col = 'test'
output_path = 'data/retweets_test.pkl'


def main():
    col = MongoClient()[DB][mongo_col]
    rows = []
    for r in col.find():
        del r['_id']
        rows.append(r)
    df = pd.DataFrame.from_records(rows)
    df.to_pickle(output_path)
    

if __name__ == '__main__':
    main()
        
