
# Separates a combined provenance log for GBIF, iDigBio, and BioCASe into three smaller provenance logs, one for each network.
#
# Example use:
#   $ python separate-gbif-idigbio-biocase.py prov.nq
# or
#   $ preston ls | python separate-gbif-idigbio-biocase.py
#
# By default, logs for each network are saved to
#   GBIF: ./only-gbif.nq
#   iDigBio: ./only-idigbio.nq
#   BioCASe: ./only-biocase.nq


import sys

from pythonutil.patterns import statement_pattern as sp
from pythonutil.terms import ACTIVITY, CREATED_BY, HAD_MEMBER, HAS_TYPE, HAS_VERSION, WAS_ASSOCIATED_WITH


out_prefix = "only-"

LINE_OUT_QUEUE_SIZE = 3

line_in_queue = list()
line_out_queue = list()
seek = 0
next_line = None


if "-v" in sys.argv or "--verbose" in sys.argv:
    def verbose(*args):
        print("\t", *args)
else:
    def verbose():
        pass


def main():
    global out_prefix

    gbif = open(out_prefix + "gbif.nq", "w")
    idigbio = open(out_prefix + "idigbio.nq", "w")
    biocase = open(out_prefix + "biocase.nq", "w")

    all = [gbif, idigbio, biocase]

    while (next_line):
        # Include header for all
        print("Reading header...")
        echo_until(all, nquad_matches("<https://idigbio.org>", WAS_ASSOCIATED_WITH))

        # Only include relevant seed
        print("Reading seeds...")
        echo_up_to(idigbio, nquad_matches("<https://idigbio.org>", WAS_ASSOCIATED_WITH))
        echo_up_to(gbif, nquad_matches("<https://gbif.org>", WAS_ASSOCIATED_WITH))
        echo_up_to(biocase, nquad_matches("<http://biocase.org>", WAS_ASSOCIATED_WITH))

        # iDigBio seed description and download
        print("Reading iDigBio seed description and generation...")
        echo_up_to(idigbio, nquad_matches("<https://search.idigbio.org/v2/search/publishers>", HAS_VERSION))
        idigbio_seed_hash = look_back(0)["object"]
        verbose("idigbio_seed_hash", ":", idigbio_seed_hash)

        # GBIF seed description and download
        print("Reading GBIF seed description and generation...")
        echo_up_to(gbif, nquad_matches("<https://api.gbif.org/v1/dataset>", HAS_VERSION))
        gbif_seed_hash = look_back(0)["object"]
        verbose("gbif_seed_hash", ":", gbif_seed_hash)

        # BioCASe seed description and download
        print("Reading BioCASe seed description and generation...")
        echo_up_to(biocase, nquad_matches("<https://bms.gfbio.org/services/data-sources/>", HAS_VERSION))
        biocase_seed_hash = look_back(0)["object"]
        verbose("biocase_seed_hash", ":", biocase_seed_hash)

        echo_up_to(biocase, nquad_matches(idigbio_seed_hash, HAD_MEMBER))

        # Parse iDigBio seed
        print("Reading iDigBio RSS feeds list...")
        first_idigbio_rss_uuid = look_back(0)["object"]
        verbose("first_idigbio_rss_uuid", ":", first_idigbio_rss_uuid)
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(2)):
            rewind(3)

        echo_up_to(idigbio, nquad_matches(first_idigbio_rss_uuid, HAD_MEMBER))
        first_idigbio_rss_url = look_back(0)["object"]
        verbose("first_idigbio_rss_url", ":", first_idigbio_rss_url)

        echo_up_to(idigbio, nquad_matches(first_idigbio_rss_url, HAS_VERSION))
        first_idigbio_rss_hash = look_back(0)["object"]
        verbose("first_idigbio_rss_hash", ":", first_idigbio_rss_hash)

        echo_up_to(idigbio, nquad_matches(gbif_seed_hash, HAD_MEMBER))

        # Parse GBIF seed
        print("Reading GBIF pages list...")
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(2)):
            rewind(3)

        echo_up_to(gbif, nquad_matches(None, CREATED_BY, "<https://gbif.org>"))
        second_gbif_page_url = look_back(0)["subject"]
        verbose("second_gbif_page_url", ":", second_gbif_page_url)

        echo_up_to(gbif, nquad_matches(second_gbif_page_url, HAS_VERSION))
        second_gbif_page_hash = look_back(0)["object"]
        verbose("second_gbif_page_hash", ":", second_gbif_page_hash)

        echo_up_to(gbif, nquad_matches(biocase_seed_hash, HAD_MEMBER))

        # Parse BioCASe seed
        print("Reading BioCASe datasets list...")
        first_biocase_dataset_url = look_back(0)["object"]
        verbose("first_biocase_dataset_url", ":", first_biocase_dataset_url)
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(2)):
            rewind(3)

        echo_up_to(biocase, nquad_matches(first_biocase_dataset_url, HAS_VERSION))
        first_biocase_dataset_hash = look_back(0)["object"]
        verbose("first_biocase_dataset_hash", ":", first_biocase_dataset_hash)

        echo_up_to(biocase, nquad_matches(first_idigbio_rss_hash, HAD_MEMBER))

        # Parse iDigBio RSS feeds
        print("Reading iDigBio RSS feed parsing...")
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(2)):
            rewind(3)

        echo_up_to(idigbio, nquad_matches(second_gbif_page_hash, HAD_MEMBER))

        # Parse GBIF pages
        print("Reading iDigBio page parsing...")
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(2)):
            rewind(3)

        echo_up_to(gbif, nquad_matches(first_biocase_dataset_hash, HAD_MEMBER))

        # Parse BioCASe registry
        print("Reading BioCASe registry parsing...")
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(2)):
            rewind(3)

        echo_until(biocase, nquad_matches("<https://preston.guoda.bio>", "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>", "<http://www.w3.org/ns/prov#SoftwareAgent>"), must_find_match=False)

    gbif.close()
    idigbio.close()
    biocase.close()

    print("Done!")


def look_back(n):
    return sp.match(line_out_queue[seek + n][1]).groupdict()


def pop_queue_and_echo():
    (out, line) = line_out_queue.pop()
    if isinstance(out, list):
        for x in out:
            x.write(line)
    else:
        out.write(line)


def flush_out():
    while len(line_out_queue) > 0:
        pop_queue_and_echo()


def rewind(n):
    global next_line
    global line_in_queue
    global line_out_queue

    assert n <= len(line_out_queue), "rewind count %d out of range" % n

    line_in_queue = [x[1] for x in [(None, next_line)] + line_in_queue + line_out_queue[:n]]
    next_line = line_in_queue.pop()
    line_out_queue = line_out_queue[n:]


def echo_and_get_next_line(out):
    global next_line
    if next_line:
        line_out_queue.insert(0, (out, next_line))
    
    while len(line_out_queue) > LINE_OUT_QUEUE_SIZE:
        pop_queue_and_echo()

    if len(line_in_queue) > 0:
        next_line = line_in_queue.pop()
    else:
        next_line = sys.stdin.readline()


def echo_until(out, condition, must_find_match=True):
    global next_line

    while (next_line):
        nquad = sp.match(next_line).groupdict()

        if condition(nquad):
            return nquad
        echo_and_get_next_line(out)

    if must_find_match:
        assert False, "failed to find expected nquad while parsing"
    else:
        return None


def echo_up_to(out, condition, must_find_match=True):
    global next_line

    while (next_line):
        nquad = sp.match(next_line).groupdict()

        echo_and_get_next_line(out)
        if condition(nquad):
            return nquad

    if must_find_match:
        assert False, "failed to find expected nquad while parsing"
    else:
        return None


def echo_remaining(out):
    global next_line
    while (next_line):
        echo_and_get_next_line(out)

    flush_out()


def nquad_matches(subject=None, predicate=None, object_=None, context=None):
    return lambda nquad : (
        (subject == None or nquad["subject"] == subject) and
        (predicate == None or nquad["predicate"] == predicate) and
        (object_ == None or nquad["object"] == object_) and
        (context == None or nquad["context"] == context)
    )


if __name__ == "__main__":
    file = None
    if len(sys.argv) > 1:
        import io
        inputPath = sys.argv[1]
        file = open(inputPath, "r")
        sys.stdin = io.StringIO(file.read())
    
    next_line = sys.stdin.readline()

    main()
    
    if file:
        file.close()