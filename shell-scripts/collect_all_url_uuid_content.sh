#!/bin/bash

# Download crawl logs to "tmp_crawls/012...def"
echo "Retrieving crawl logs"
preston history -l tsv --remote http://preston.acis.ufl.edu | grep -o 'hash:\/\/sha256\/[a-f0-9]*' | sed -r 's/hash:\/\/sha256\/([a-f0-9]*)/\1/g' | sort | uniq | xargs -L 1 sh stage_crawl.sh

# Extract url_uuid_content logs from each crawl
echo "Building (url, uuid, content) triples"
find tmp_crawls/*/* | grep -E "[0-9a-f]{64}$" | xargs -L 1 sh extract_crawl_url_uuid_content.sh

# Combine url_uuid_content files into one (the weird awking is to fix sorting bugs)
echo "Saving all triples to tmp/url_uuid_content"
find tmp_crawls/*/url_uuid_content | xargs cat | awk '{ print $2 "\t" $3 "\t" $1 }' | sort -k 3 | uniq | awk '{ print $3 "\t" $1 "\t" $2 }' > tmp/url_uuid_content
