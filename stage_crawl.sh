#!/bin/bash

HASH=$1
DIR=tmp_crawls/$HASH

mkdir -p $DIR
preston get --remote http://preston.acis.ufl.edu hash://sha256/$HASH | sed -r 's/<([^>]*)>/\1/g' | tr ' ' '\t' | cut -f 1,2,3 > $DIR/$HASH
