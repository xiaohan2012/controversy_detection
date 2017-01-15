
# Controversy Detection in Twitter Stream

## Usage:

### Setting up environtment

- prepare virtual environment: `virtualenv -p python3 venv`
- `source venv/bin/activate`
- install software dependencies: `pip install -r requirements.txt`
- running Notebook: `ipython notebook `

### Running experiments

All experiments are written in the Notebook scripts with extension ".ipynb"

- Section 5.2: `dynamic_graph_partitioning.ipynb`
- Section 5.3: `simulation.ipynb`


----------------------

## Done

- controversy score calculation: `controversy_score.ipynb`
- dynamic graph partitioning: `dynamic_graph_partitioning.ipynb`
- Incremental controversy score update and evaluation
  - when new edges are added or old edges are removed,
  - incrementally partition the graph and incrementally update the controversy score
  - compare the score and running time with calculating the score from scratch
- The skeleton code for simulation on twitter stream
- Comparing through-put for both incremental (IC) approach and from-scratch (FS) approach
- Periodical update improvement: track `last_updated_time` for each hashtag
- Comparing controversy score of IC approach and FS approach
- Integrate top-k hashtag selection algorithm
- Fixed RWC computation error: 1) works on largest CC 2) thresholding RWC computation by largest CC size (not graph size)

## Todo

These are must-do:

1. Manually check some top controversial events


These are optional:

1. Incremental graph partitioning:
   - add node skipping in incremental graph partitioning
   - evaluate the tradeoff between cut objective and computation time
   - optimize the graph partitioning code (profiling even cython)
2. Find a way to summarize the controversial hashtag. For example, what are the typical opnions/tweets of the opposing sides/communities?
   - one goal is: by checking the summarization, one can decide whether this hashtag is controversial or not.
3. Label ground truth on which tags are controversial (so that we can have precision/recall/F1)?

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

## Incremental controversy score update

Check out `incremental_controversy_score.ipynb`.

Some quick result (add/remove 10% of the edges):

1. average running time reduction is 18%
2. the Pearson correlation coefficient of RWC scores is: 0.994445283425 with p-value 4.26692170169e-07.

TODO:

1. what if fewer edges are added/removed?

## Throughput test

Refer to `simulation.ipynb`.


1e5 retweets, 60 mins time window, 5 mins update interval

- Incremental: 216 seconds
- From scracth: 422 seconds

## Correlation of RWCs between IC approach and FS approach

Averaged over RWC scores over multiple updates on multiple graphs.

Average: 0.9, not as high as the previous result (0.99) averaged over multiple graphs but only one update each.

I guess: incremental graph partition accumulates errors.

Plotted RWC score evoluation for \#VeranoMTV2016.

Check `simulation.ipynb`

## Stream volume graph of top events

Check `simulations.ipynb` out.


## evaluating hashtag

Check `manually_check_hashtag.ipynb`


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
   - I take the largest CC and compute RWC based on it.
4. How to make RWC more robust?
   - varying number of partitionings
   - scattered CCs
   - the largest CC size should be big enough
   - for small graphs, like a retweet tree, this method does not work very well.
5. Computing largest CC
   - now is from-scratch
   - should make it incremental
6. RWC does not perform that well
   - maybe minimum RWC score needs to be tuned. That's a pain.


