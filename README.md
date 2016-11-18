# controversy detection

## Installing metis

1. Install [metis wrapper](http://metis.readthedocs.io/en/latest/)
2. Install [Metis](http://glaros.dtc.umn.edu/gkhome/metis/metis/download)
3. Important: `make config static=1`

## Issues

1. how to apply Kiran's method on top this dataset espesially when there are many disconnected components?
2. hashtag may contain opinion bias such as NoDAPL (protest against oil pipeline)
3. At the begining, controversial hashtag may induce many disconnected components, how to deal with this?
   - A more fundamental question is, hoes do the graph on controversy-hashtag evolve?
4. Ask for ground truth data, in one of the papers in "Related Work".
