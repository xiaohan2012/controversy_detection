# Controversy Detection in Twitter Stream

## Done

- controversy score calculation: `controversy_score.ipynb`
- dynamic graph partitioning: `dynamic_graph_partitioning.ipynb`

## Todo

These are must-do:

1. Incremental controversy score update and evaluation
  - when new edges are added or old edges are removed,
  - incrementally partition the graph and incrementally update the controversy score
  - compare the score and running time (1. pagerank, 2. partition+pagerank) with calculating the score from scratch
2. Top-k hashtag selection algorithm
3. Try the method on real twitter stream on different parameters (time window, minimum controversy score, etc)
  - see how the controversy score changes, does it make sense?
  - are controversial hashtags detected?


These are optional:

1. Incremental graph partitioning:
   - add node skipping in incremental graph partitioning
   - evaluate the tradeoff between cut objective and computation time
   - optimize the graph partitioning code (profiling even cython)
2. Find a way to summarize the controversial hashtag. For example, what are the typical opnions/tweets of the opposing sides/communities?
   - one goal is: by checking the summarization, one can decide whether this hashtag is controversial or not.
5. Label ground truth on which tags are controversial (so that we can have precision/recall/F1)?

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


- ALDUB1stAnniversary: 0.04 (non-controversial)

## Normalizing RWC to [0.5, 1.0]

This is done by `controversy  / (controversy + non_controversy)`.

And some comparison on the example networks:

- barbell: 0.9942951520693315
- beefban: 0.8838806129369029
- ukraine: 0.8791934195724288
- **circular**: 0.8596169409366637 (this is very unexpected!)
- baltimore: 0.8172103276545415
- barabasi: 0.5599275837061325
- star: 0.5003170710418742


## Interesting tags

- MTVHottest: 0.12, 4 clusters (seems to be controversial)
- PokemonGO: seems to be non-controversial but receices score 0.13, plus the retweet graph is like two stars connected by one edge.


## RWC evolution

See `figs/{dataset}-volume.png` and `figs/{dataset}-rwc-vs-time.png`.

For beefban, ukraine:

1. The RWC score is high at the begining.
2. For beefban, the controversy score seems to go together with the temporal volume, but there are some minor trend differences
3. For ukraine, the above observation is not very obvious.

For MTVHottest, the volume and RWC score doesn't match in shape.
For RWC score, it increases while the volume graph is not very regular. 

## Installing metis

1. Install [metis wrapper](http://metis.readthedocs.io/en/latest/)
2. Install [Metis](http://glaros.dtc.umn.edu/gkhome/metis/metis/download)
3. Important: `make config static=1`


## Dynamic graph partitioning

Check out `dynamic_graph_partitioning.ipynb` for the code and evaluation.

TODO:

1. node skipping is not implemented yet
2. pure python impelementation is slower compared to metis, which is in C++.


## Issues (and solution)

The following issues are encountered, some are solved while some remain open:


1. how to apply Kiran's method on top this dataset espesially when there are many disconnected components?
   - pagerank can deal with that
2. issue on the controversy score definition:
   - the number of high degree nodes should be proportional to the network size: the above experient chose 1e-3
   - there is not explicit bound on the score
   - solution: takes k percent nodes and use division to bound the score.
   
2. hashtag may contain opinion bias such as NoDAPL (protest against oil pipeline)
3. At the begining, controversial hashtag may induce many disconnected components, how to deal with this?
   - A more fundamental question is, how does the graph on controversy-hashtag evolve?

