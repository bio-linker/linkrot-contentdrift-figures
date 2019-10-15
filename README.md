# linkrot-contentdrift-figures

## Patch qualified generations
The script patch-qualified-generations.py takes existing Preston provenance logs and outputs qualifiedGeneration statements for download events that lack one.

To add missing qualifiedGenerations for an existing Preston observatory:
```shell
preston ls | python3 path/to/patch-qualified-generations.py
```

The script also accepts a file in nquads format as input:
```shell
python3 patch-qualified-generations.py [file]
```

## Figures

[Build Figures.ipynb](https://github.com/bio-linker/linkrot-contentdrift-figures/blob/master/Build%20Figures.ipynb) uses the graph indexing methods defined in [prestongraph.py](https://github.com/bio-linker/linkrot-contentdrift-figures/blob/master/prestongraph.py) to analyze Preston logs and construct figures.

# Funding

This work is funded in part by grant [NSF OAC 1839201](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1839201&HistoricalAwards=false) from the National Science Foundation.

