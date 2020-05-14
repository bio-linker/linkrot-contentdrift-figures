# linkrot-contentdrift-figures

## Build network URL-content figures

Use [build-figures.py](https://github.com/bio-linker/linkrot-contentdrift-figures/blob/master/build-figures.py) to generate figures. The script takes a list of tab separated rows of (url, content, crawl time) as input, e.g.
```
<https://iptmuse.colorado.edu/eml.do?r=cuinvertpaleo> <hash://sha256/5d9811d9149e52c64791b0486c5ac80ba061d81593f49886e4e146a938c23a55>  "2019-09-01T09:34:33.505Z"^^<http://www.w3.org/2001/XMLSchema#dateTime>
```
and can be used like so:
```shell
cat [query output] | python build-figures.py [network name] [?output directory]
```
If `output directory` is not provided, it defaults to `[network name]-analysis`. All generated figures and text reports will be saved inside the output directory.

Example using iDigBio data:
```shell
$ preston ls | tail -n +21918337 | bzip2 > prov.nq.bz2 # Start at the 2019-03 crawl
$ tdbloader --loc index/ prov.nq.bz2
$ tdbquery --time --loc index --query sparql-queries/select-by-network-idigbio.rq --results tsv | tail -n+2 > idigbio.tsv
$ tdbquery --time --loc index --query sparql-queries/select-idigbio-by-activity.rq --results tsv | tail -n+2 >> idigbio.tsv
$ cat idigbio.tsv | python build-figures.py iDigBio
```
which should result in
```
$ ls idigbio-analysis/
crawl-status-totals-df.tsv           reliability-over-time.pdf                      running-total-urls-and-contents-legend.pdf  url-break-freq-dist-annotated.pdf
reliability-over-time-annotated.pdf  report.txt                                     running-total-urls-and-contents.pdf         url-break-freq-dist.pdf
reliability-over-time-legend.pdf     running-total-urls-and-contents-annotated.pdf  totals
```

# Funding

This work is funded in part by grant [NSF OAC 1839201](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1839201&HistoricalAwards=false) from the National Science Foundation.

