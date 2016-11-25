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

## Notes

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
