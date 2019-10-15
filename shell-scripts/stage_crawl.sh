#!/bin/bash

HASH=$1
DIR=tmp_crawls/$HASH

mkdir -p $DIR

# TODO: all spaces are currently being replaced by tabs -- this is bad; spaces within "" or <> delimiters should be preserved. For our current purposes, though, this is inconsequential
preston get --remote http://preston.acis.ufl.edu hash://sha256/$HASH | sed -r 's/<([^>]*)>/\1/g' | tr ' ' '\t' | cut -f 1,2,3 > $DIR/$HASH
