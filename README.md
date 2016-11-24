# Controversy Detection in Twitter Stream

## Data preparation

All retweets from 2016 July.

Use `twitter_stream_data.py` to extract the retweets from raw data.

## Controversy score checking

- beefban: 2e4, 0.16
- baltimore: 9e4, 0.17
- ukraine: 5e4, 0.12
- curcular: 5e4, 0.0014
- star: 5e4, 0.0014
- Barabasi: 5e4, 0.0056

Notes:

- the number of high degree nodes should be proportional to the network size: the above experient chose 1e-3
- there is not explicit bound on the score

## Installing metis

1. Install [metis wrapper](http://metis.readthedocs.io/en/latest/)
2. Install [Metis](http://glaros.dtc.umn.edu/gkhome/metis/metis/download)
3. Important: `make config static=1`

## Issues

1. how to apply Kiran's method on top this dataset espesially when there are many disconnected components?
   - pagerank can deal with that
2. hashtag may contain opinion bias such as NoDAPL (protest against oil pipeline)
3. At the begining, controversial hashtag may induce many disconnected components, how to deal with this?
   - A more fundamental question is, how does the graph on controversy-hashtag evolve?
4. Ask for ground truth data, in one of the papers in "Related Work".
