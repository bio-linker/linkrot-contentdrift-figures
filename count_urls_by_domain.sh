#!/bin/bash
cat tmp/urls | sed -r 's/^(https?:\/\/[^/]+\/).*/\1/g' | sort | uniq -c | sort -nr > tmp/url_counts_by_domain
