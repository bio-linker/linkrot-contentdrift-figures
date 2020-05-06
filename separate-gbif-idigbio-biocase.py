
# Separates a combined provenance log for GBIF, iDigBio, and BioCASe into three smaller provenance logs, one for each network.
#
# Use argument -h or --help for help
#
# Example use:
#   $ python separate-gbif-idigbio-biocase.py prov.nq
# or
#   $ preston ls | python separate-gbif-idigbio-biocase.py
#
# To print debug information, add -v 3 or --verbose 3
#
# By default, logs for each network are saved to
#   GBIF: ./only-gbif.nq
#   iDigBio: ./only-idigbio.nq
#   BioCASe: ./only-biocase.nq

# tail preston.acis.ufl.edu.nq -n +21918337 > 2018-03-to-2020-04.nq

import sys
import argparse

from pythonutil.patterns import statement_pattern as sp
from pythonutil.terms import ACTIVITY, DESCRIPTION, GENERATION, HAD_MEMBER, HAS_QUALIFIED_GENERATION, HAS_TYPE, HAS_VERSION, STARTED_AT_TIME, TYPE, USED, WAS_ASSOCIATED_WITH, WAS_INFLUENCED_BY, WAS_INFORMED_BY


COMBINE_BIOCASE_WITH_GBIF = True # Can't easily separate GBIF from BioCASe for older logs (e.g. 2019-09-01), so let's just combine the two


parser = argparse.ArgumentParser(
    description="Separates a combined provenance log for GBIF, iDigBio, and BioCASe into three smaller provenance logs, one for each network."
)
parser.add_argument("file_paths", nargs="*")
parser.add_argument("-v", "--verbose", dest="verbosity", default=1, type=int, help="0, 1, 2, or 3")
parser.add_argument("--gbif", dest="gbif_output_path", default="only-gbif.nq", type=str)
parser.add_argument("--idigbio", dest="idigbio_output_path", default="only-idigbio.nq", type=str)
parser.add_argument("--biocase", dest="biocase_output_path", default="only-biocase.nq", type=str)

args = parser.parse_args(sys.argv)

if args.verbosity >= 1:
    def verbose1(*args):
        print(*args)
else:
    def verbose1(*args):
        pass

if args.verbosity >= 2:
    def verbose2(*args):
        print("\t", *args)
else:
    def verbose2(*args):
        pass

if args.verbosity >= 3:
    def verbose3(*args):
        print("\t\t", *args)
else:
    def verbose3(*args):
        pass


line_in_queue = list()
line_out_queue = list()
next_line = None

LINE_OUT_QUEUE_SIZE = 3

# Stuff for sneaky output interception
last_hash_with_generation = None
current_crawl_uuid = None


def main():
    gbif = open(args.gbif_output_path, "w")
    idigbio = open(args.idigbio_output_path, "w")

    if COMBINE_BIOCASE_WITH_GBIF:
        biocase = gbif
        all = [gbif, idigbio]
    else:
        biocase = open(args.biocase_output_path, "w")
        all = [gbif, idigbio, biocase]

    nquad_matches_start_of_crawl = nquad_matches(None, "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>", "<http://www.w3.org/ns/prov#SoftwareAgent>")
    nquad_matches_reprocess_description = nquad_matches(subject='"An event that (re-) processes existing biodiversity datasets graphs and their provenance."@en')

    while (next_line):

        # Include header for all
        matched_line = echo_up_to(all, nquad_matches(predicate=DESCRIPTION))
        if matched_line["subject"] == '"An event that (re-) processes existing biodiversity datasets graphs and their provenance."@en':
            verbose1("Skipping (re-) processing event")
            echo_until(None, nquad_matches_start_of_crawl, must_find_match=False)
            continue

        echo_up_to(all, nquad_matches(predicate=STARTED_AT_TIME))
        log_date = look_back(0)["object"]
        verbose1("Processing log with timestamp " + log_date)
        echo_until(all, nquad_matches("<https://idigbio.org>", WAS_ASSOCIATED_WITH))

        # Only include relevant seed
        verbose2("Reading seeds...")
        echo_up_to(idigbio, nquad_matches("<https://idigbio.org>", WAS_ASSOCIATED_WITH))
        echo_up_to(gbif, nquad_matches("<https://gbif.org>", WAS_ASSOCIATED_WITH))
        echo_up_to(biocase, nquad_matches("<http://biocase.org>", WAS_ASSOCIATED_WITH))

        # iDigBio seed description and download
        verbose2("Reading iDigBio seed description and generation...")
        echo_up_to(idigbio, nquad_matches("<https://search.idigbio.org/v2/search/publishers>", HAS_VERSION))
        idigbio_seed_hash = look_back(0)["object"]
        verbose3("idigbio_seed_hash", ":", idigbio_seed_hash)

        # GBIF seed description and download
        verbose2("Reading GBIF seed description and generation...")
        echo_up_to(gbif, nquad_matches("<https://api.gbif.org/v1/dataset>", HAS_VERSION))
        gbif_seed_hash = look_back(0)["object"]
        verbose3("gbif_seed_hash", ":", gbif_seed_hash)

        # BioCASe seed description and download
        verbose2("Reading BioCASe seed description and generation...")
        echo_up_to(biocase, nquad_matches("<https://bms.gfbio.org/services/data-sources/>", HAS_VERSION))
        biocase_seed_hash = look_back(0)["object"]
        verbose3("biocase_seed_hash", ":", biocase_seed_hash)

        matched_nquad = echo_until(biocase, nquad_matches(idigbio_seed_hash, HAD_MEMBER))

        # Parse iDigBio seed
        verbose2("Reading iDigBio RSS feeds list...")
        first_idigbio_rss_uuid = matched_nquad["object"]
        verbose3("first_idigbio_rss_uuid", ":", first_idigbio_rss_uuid)
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(1)):
            rewind(2)

        echo_up_to(idigbio, nquad_matches(first_idigbio_rss_uuid, HAD_MEMBER))
        first_idigbio_rss_url = look_back(0)["object"]
        verbose3("first_idigbio_rss_url", ":", first_idigbio_rss_url)

        echo_up_to(idigbio, nquad_matches(first_idigbio_rss_url, HAS_VERSION))
        first_idigbio_rss_hash = look_back(0)["object"]
        verbose3("first_idigbio_rss_hash", ":", first_idigbio_rss_hash)

        matched_nquad = echo_until(idigbio, nquad_matches(gbif_seed_hash, HAD_MEMBER))

        # Parse GBIF seed
        verbose2("Reading GBIF pages list...")
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(1)):
            rewind(2)

        echo_up_to(gbif, nquad_matches("<https://api.gbif.org/v1/dataset?offset=20&limit=20>", HAS_VERSION))
        second_gbif_page_hash = look_back(0)["object"]
        verbose3("second_gbif_page_hash", ":", second_gbif_page_hash)

        matched_nquad = echo_until(gbif, either(nquad_matches(biocase_seed_hash, HAD_MEMBER), nquad_matches_start_of_crawl), must_find_match=False)
        if matched_nquad == None or nquad_matches_start_of_crawl(matched_nquad):
            verbose2("Reached end of crawl log before finding BioCASe seed parsing... skipping to next crawl log")
            echo_until(None, nquad_matches_start_of_crawl, must_find_match=False)
            continue

        # Parse BioCASe seed
        verbose2("Reading BioCASe datasets list...")
        first_biocase_dataset_url = matched_nquad["object"]
        verbose3("first_biocase_dataset_url", ":", first_biocase_dataset_url)
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(1)):
            rewind(2)

        echo_up_to(biocase, nquad_matches(first_biocase_dataset_url, HAS_VERSION))
        first_biocase_dataset_hash = look_back(0)["object"]
        verbose3("first_biocase_dataset_hash", ":", first_biocase_dataset_hash)

        matched_nquad = echo_until(biocase, either(nquad_matches(first_idigbio_rss_hash, HAD_MEMBER), nquad_matches(second_gbif_page_hash, HAD_MEMBER)))

        # Parse iDigBio RSS feeds
        if matched_nquad["subject"] == first_idigbio_rss_hash:
            verbose2("Reading iDigBio RSS feed parsing...")
            if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(1)):
                rewind(2)

            echo_until(idigbio, nquad_matches(second_gbif_page_hash, HAD_MEMBER))
        else:
            verbose2("It looks like iDigBio RSS feeds were not parsed in the current crawl log; skipping to GBIF page parsing")

        # Parse GBIF pages
        verbose2("Reading GBIF page parsing...")
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(1)):
            rewind(2)

        echo_until(gbif, nquad_matches(first_biocase_dataset_hash, HAD_MEMBER))

        # Parse BioCASe registry
        verbose2("Reading BioCASe registry parsing...")
        if nquad_matches(None, HAS_TYPE, ACTIVITY)(look_back(1)):
            rewind(2)

        echo_until(biocase, nquad_matches_start_of_crawl, must_find_match=False)

    gbif.close()
    idigbio.close()
    # biocase.close()

    verbose1("Done!")


def look_back(n):
    return sp.match(line_out_queue[n][1]).groupdict()


def pop_queue_and_echo():
    (out, line) = line_out_queue.pop()
    line = doctor_line(line)
    if isinstance(out, list):
        for x in out:
            x.write(line)
    elif out:
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


def either(*conditions):
    return lambda nquad : (
        any([condition(nquad) for condition in conditions])
    )


def nquad_to_str(nquad):
    if "context" in nquad:
        return "%s %s %s %s .\n" % (nquad["subject"], nquad["predicate"], nquad["object"], nquad["context"])
    else:
        return "%s %s %s .\n" % (nquad["subject"], nquad["predicate"], nquad["object"])


# Called when writing lines to sneakily transform them and add missing lines; performs the same functions as past patch scripts
def doctor_line(line):
    from uuid import uuid4 as UUID
    global last_hash_with_generation
    global current_crawl_uuid

    nquad = sp.match(line).groupdict()

    # Do some sneaky monitoring

    if nquad["predicate"] == HAS_QUALIFIED_GENERATION:
        last_hash_with_generation = nquad["subject"]

    elif nquad_matches(None, DESCRIPTION, '"A crawl event that discovers biodiversity archives."@en')(nquad):
        current_crawl_uuid = nquad["subject"]

    # Do some sneaky fixing

    ## Replace misused "activity" verbs with "wasInformedBy"
    elif nquad["predicate"] == WAS_INFLUENCED_BY:
        nquad["predicate"] = WAS_INFORMED_BY
        line = nquad_to_str(nquad)

    ## Cheat-in missing generation events
    elif nquad["predicate"] == HAS_VERSION and last_hash_with_generation != nquad["object"]:
        uuid = "<%s>" % UUID()
        line = (
            "%s %s %s .\n" % (nquad["object"], HAS_QUALIFIED_GENERATION, uuid) +
            "%s %s %s .\n" % (uuid, TYPE, GENERATION) +
            "%s %s %s .\n" % (uuid, WAS_INFORMED_BY, current_crawl_uuid) +
            "%s %s %s .\n" % (uuid, USED, nquad["subject"]) +
            line
        )

    return line


if __name__ == "__main__":
    file = None
    if len(args.file_paths) > 1:
        import io
        inputPath = args.file_paths[1]
        file = open(inputPath, "r")
        sys.stdin = io.StringIO(file.read())
    
    next_line = sys.stdin.readline()

    main()
    
    if file:
        file.close()
