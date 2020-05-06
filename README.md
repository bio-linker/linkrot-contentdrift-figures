# linkrot-contentdrift-figures

## Separate iDigBio, GBIF, and BioCASe provenance

[separate-gbif-idigbio-biocase.py](https://github.com/bio-linker/linkrot-contentdrift-figures/blob/master/separate-gbif-idigbio-biocase.py) can be used to separate a combined provenance log for iDigBio, GBIF, and BioCASe into separate files.
```shell
preston ls | python separate-gbif-idigbio-biocase.py
```
Note that, at the moment, BioCASe output is combined with GBIF. By default, the script saves output to `./only-gbif.nq` and `./only-idigbio.nq`. To options for specifying output directories, change logging features etc., run `python separate-gbif-idigbio-biocase.py --help`.

## Build network URL-content figures

[build-figures.ipynb](https://github.com/bio-linker/linkrot-contentdrift-figures/blob/master/build-figures.ipynb) uses the graph indexing methods defined in [prestongraph.py](https://github.com/bio-linker/linkrot-contentdrift-figures/blob/master/prestongraph.py) to analyze Preston logs and construct figures.

Figure generation can be started on the command line by piping text in nquads format to the iPython script [build-figures.ipy](https://github.com/bio-linker/linkrot-contentdrift-figures/blob/master/build-figures.ipy)
```shell
cat [some nquads file] | ipython build-figures.ipy [job name] [output directory]
```
If `output directory` is not provided, it defaults to `[job name]-analysis`. All generated figures and text reports will be saved inside the output directory.

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

# Funding

This work is funded in part by grant [NSF OAC 1839201](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1839201&HistoricalAwards=false) from the National Science Foundation.

