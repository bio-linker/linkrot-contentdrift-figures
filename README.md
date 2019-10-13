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

# Funding 

This work is funded in part by grant [NSF OAC 1839201](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1839201&HistoricalAwards=false) from the National Science Foundation.
