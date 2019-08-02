#!/bin/bash
crawl_uuid="$(grep 'http://www.w3.org/ns/prov#Activity' $1 | cut -f1 | sort | uniq)"
uuid_date="$(grep 'http://www.w3.org/ns/prov#startedAtTime' $1 | cut -f1,3 | sort | uniq)"

crawl_uuid_date="$(join -t $'\t' <(echo "${crawl_uuid}") <(echo "${uuid_date}") | sort -k2)"
echo "${crawl_uuid_date}"
