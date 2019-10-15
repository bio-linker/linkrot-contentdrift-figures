#!/bin/bash

#echo hahaha
PROV=$1
DIR=$(dirname "${PROV}")
#echo "Prov: ""${PROV}"
#echo "Dir: ""${DIR}"

#cat $PROV | grep ^http | grep 'http://purl.org/pav/hasVersion' | sort -k 1 | head

cat $PROV | grep ^http | grep 'http://purl.org/pav/hasVersion' | sort -k 1 | uniq \
> $DIR/url_hasVersion_content

cat $PROV | grep -e ^http -e ^hash | grep 'http://www.w3.org/ns/prov#wasGeneratedBy' | sort -k 1 | uniq \
> $DIR/content_wasGeneratedBy_uuid

cat $DIR/url_hasVersion_content | awk '{ print $3 "\t" $1 }' | sort -k 1 | uniq \
> $DIR/content_url

# We don't need to join URL/content/UUID since we're only looking at one crawl at a time now
#cat $DIR/content_wasGeneratedBy_uuid | awk '{ print $1 "\t" $3 }' \
#> $DIR/content_uuid

#join $DIR/content_url $DIR/content_uuid | awk '{ print $1 "\t" $3 "\t" $2 }' | sort -k 3 | \
#awk '{ print $3 "\t" $2 "\t" $1 }' > $DIR/url_uuid_content

uuid=$(grep 'http://www.w3.org/ns/prov#startedAtTime' $PROV | head -1 | cut -f 1)
cat $DIR/content_url | awk -v uuid="${uuid}" '{ print $2 "\t" uuid "\t" $1}' \
> $DIR/url_uuid_content
