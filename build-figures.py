# Usage:
#   cat network.tsv | python build-figures.py NetworkName OutputDirectory
#
# where "network.tsv" has columns
#   dataset_url dataset_version crawl_date
#
# Expects "Computer Modern" font to be installed. If not installed, probably a default (ugly) font will be used instead
#

#%%

import sys
import os
import io

import numpy as np
import pandas as pd
from enum import Enum

INCLUDE_LEGEND = False
INCLUDE_TITLE = False
FIGURE_DPI = 300

# Set start/end times to None to use the timestamps of the first and last crawls
START_TIME = "\"2019-03-01T00:00:00.000Z\"^^<http://www.w3.org/2001/XMLSchema#dateTime>"
END_TIME = "\"2020-05-01T00:00:00.000Z\"^^<http://www.w3.org/2001/XMLSchema#dateTime>"

MAKE_URL_UNAVAILABLE_HISTOGRAM = False
MAKE_URL_UNSTABLE_HISTOGRAM = False

MAKE_CRAWL_STATUS_COUNTS_PER_CRAWL_BAR_GRAPH = False
MAKE_CRAWL_STATUS_COUNTS_OVER_TIME_BAR_GRAPH = False

# TODO: pretty command line interface
#  - turn on/off annotations
#  - choose which results/figures to save
#  - use non-LaTeX fonts
#  - set figure dpi
#  - set figure time frames

try:
    INTERACTIVE = (get_ipython().__class__.__name__ == "ZMQInteractiveShell")
except NameError:
    INTERACTIVE = False


output_directory = None
data_path = None

if not INTERACTIVE:
    network_name = sys.argv[1] if len(sys.argv) > 1 else "Network"
    output_directory = sys.argv[2] if len(sys.argv) > 2 else None
else:
    network_name = "BHL"
    data_path = "./bhl.tsv" #"./idigbio.tsv"

if output_directory == None:
    output_directory = "./" + network_name.lower().replace(" ", "-") + "-analysis/"

try:
    os.mkdir(output_directory)
except OSError:
    # Hopefully the directory was already created
    pass

print("Saving output in %s" % str(output_directory))

#%%

SKIP_HEADER = True
if SKIP_HEADER:
    sys.stdin.readline()

all_url_queries = dict()
crawl_times = list()
crawl_times_set = set()

if data_path:
    file = open(data_path, "r")
    sys.stdin = io.StringIO(file.read())

for line in sys.stdin:
    # Remove \n and get tsv column values
    parts = line[:-1].split("\t")
    url = parts[0]
    content = parts[1]
    crawl_time = parts[2]

    crawl_times_set.add(crawl_time)

    if url not in all_url_queries:
        all_url_queries[url] = dict()
    all_url_queries[url][crawl_time] = content

crawl_times = list(crawl_times_set)
crawl_times.sort()
num_crawls = len(crawl_times)

if data_path:
    file.close()

#%%

class Status(Enum):
    UNKNOWN             = 0    # Did not check for content
    FIRST_CONTENT       = 1    # Returned content for the first time
    SAME_CONTENT        = 2    # Returned the same content as the last successful query
    CHANGED_CONTENT     = 3    # Returned new content
    OLD_CONTENT         = 4    # Returned previously seen content that is different from the previous successful data
    BECAME_UNRESPONSIVE = 5    # Failed to return content after a successful query
    STILL_UNRESPONSIVE  = 6    # Failed to return content again
    ERROR               = 7    # Returned malformed content

class UrlLifetime:
    def __init__(self):
        self.statuses = []
        self.contents = []

        self.first_crawl_position = None
        self.last_crawl_position = None
        self.last_known_status = Status.UNKNOWN
        self.first_response_position = None
        self.first_change_position = None
        self.first_break_position = None

        self.num_resolves = 0
        self.num_breaks = 0
        self.num_contents = 0
        self.num_content_changes = 0


#%%

### Collect the contents seen over the course of each URL's lifetime

def content_is_missing(content):
    return str(content).startswith("<http")

def build_url_lifetime(queries, crawl_times):
    lifetime = UrlLifetime()

    statuses = [Status.UNKNOWN] * len(crawl_times)
    contents = [None] * len(crawl_times)

    for (crawl, content) in queries.items():
        i = crawl_times.index(crawl)
        contents[i] = content

    # Fill statuses and stuff
    was_alive = True
    most_recent_content = None
    for i, content in enumerate(contents):

        if content is not None:
        # Became unresponsive
            if content_is_missing(content):
                if was_alive:
                    status = Status.BECAME_UNRESPONSIVE
                    lifetime.num_breaks += 1

        # Still unresponsive
                else:
                    status = Status.STILL_UNRESPONSIVE

                was_alive = False
            
                if lifetime.first_break_position is None:
                    lifetime.first_break_position = i

        # First content
            else:
                if most_recent_content == None:
                    status = Status.FIRST_CONTENT
                    most_recent_content = content
                    lifetime.num_contents += 1
                    lifetime.first_response_position = i

        # Same content
                elif content == most_recent_content:
                    status = Status.SAME_CONTENT

                else:
        # Old content
                    if content in lifetime.contents[0:i]:
                        status = Status.OLD_CONTENT

        # Changed content
                    else:
                        status = Status.CHANGED_CONTENT
                        if lifetime.first_change_position is None:
                            lifetime.first_change_position = i
                        lifetime.num_contents += 1

                    most_recent_content = content
                    lifetime.num_content_changes += 1

                was_alive = True
                lifetime.num_resolves += 1

            lifetime.last_known_status = status

            if lifetime.first_crawl_position is None:
                lifetime.first_crawl_position = i
            lifetime.last_crawl_position = i

        # Unknown
        else:
            status = Status.UNKNOWN

        statuses[i] = status

    lifetime.contents = contents
    lifetime.statuses = statuses
    return lifetime

# url = '<http://65.52.215.125/ipt/eml.do?r=eggs>'
# lifetime = build_url_lifetime(all_url_queries[url], crawl_times)
# print("Lifetime for %s\n" % url)
# print("\n".join(["%d:\t%s\t%s" % (i, lifetime.statuses[i], lifetime.contents[i]) for i in range(num_crawls)]))

#%%

all_url_lifetimes = { url : build_url_lifetime(all_url_queries[url], crawl_times) for url in all_url_queries }

#%%

content_first_crawl_positions = dict()
for lifetime in all_url_lifetimes.values():
    for i, content in enumerate(lifetime.contents):
        if not content_is_missing(content):
            current_first = content_first_crawl_positions[content] if content in content_first_crawl_positions else num_crawls
            content_first_crawl_positions[content] = min(i, current_first)

#%%

### Build figures

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import datetime
from itertools import cycle, islice

rc("text", usetex=False)
rc("savefig", format="png", dpi=FIGURE_DPI)
rc("font", size=14, family="DejaVu Sans")

# Only do this in Jupyter Notebook
# if INTERACTIVE:
#     %matplotlib inline

#%%

crawl_status_totals = [(dict([(status, 0) for status in Status])) for crawl_times in crawl_times]

for _, lifetime in all_url_lifetimes.items():
    for i, status in enumerate(lifetime.statuses):
        crawl_status_totals[i][status] += 1

crawl_status_totals_df = pd.DataFrame(
    index = [datetime.datetime.strptime(x, "\"%Y-%m-%dT%H:%M:%S.%fZ\"^^<http://www.w3.org/2001/XMLSchema#dateTime>") for x in crawl_times],
    data = crawl_status_totals
)

crawl_status_totals_df.to_csv(output_directory + "crawl-status-totals-df.tsv", sep='\t')
crawl_status_totals_df.transpose()

# %%

col_hex = {
    "blue"      : "#1f77b4",
    "orange"    : "#ff7f0e",
    "green"     : "#2ca02c",
    "red"       : "#d62728",
    "purple"    : "#9467bd",
    "brown"     : "#8c564b",
    "pink"      : "#e377c2",
    "gray"      : "#7f7f7f",
    "yellow"    : "#bcbd22",
    "teal"      : "#17becf",
    
    "bright green"  : "#00ff00",
    "bright red"    : "#ff0000",
    "green yellow"  : "#9ACD32",
    "olive"         : "#808000"
}

fig_df = crawl_status_totals_df[[
    Status.SAME_CONTENT,
    Status.FIRST_CONTENT,
    Status.OLD_CONTENT,
    Status.CHANGED_CONTENT,
    Status.STILL_UNRESPONSIVE,
    Status.BECAME_UNRESPONSIVE,
    Status.UNKNOWN,
    Status.ERROR
]]

status_colors = {
    Status.UNKNOWN             : "gray",
    Status.FIRST_CONTENT       : "bright green",
    Status.SAME_CONTENT        : "green",
    Status.CHANGED_CONTENT     : "yellow",
    Status.OLD_CONTENT         : "olive",
    Status.BECAME_UNRESPONSIVE : "bright red",
    Status.STILL_UNRESPONSIVE  : "red",
    Status.ERROR               : "purple",
}

status_color_map = list(islice(cycle([col_hex[status_colors[x]] for x in fig_df.columns]), None, 256))

#%%

if MAKE_CRAWL_STATUS_COUNTS_PER_CRAWL_BAR_GRAPH:
    figure_title = network_name + ": Stacked URL status counts per crawl"
    output_file = output_directory + "stacked-query-status-counts-per-crawl"

    ax = fig_df.plot(
        kind="bar",
        stacked=True,
        width=.95,
        color=status_color_map,
        figsize=(15, 5),
        legend=False
    );

    # Bare
    plt.savefig(output_file, dpi=FIGURE_DPI);

    # Annotated
    plt.title(figure_title)
    plt.legend()
    plt.savefig(output_file[:-4] + "-annotated.png", dpi=FIGURE_DPI);

# %%

if MAKE_CRAWL_STATUS_COUNTS_OVER_TIME_BAR_GRAPH:
    figure_title = network_name + ": Stacked URL Status Counts Over Time (Stepped)"
    output_path = output_directory + "stacked-query-status-counts-over-time"

    fig = plt.figure(figsize=(16, 5))
    ax = fig.add_subplot(111)

    # Fill in space between lines
    x = fig_df.index.append(pd.Index([datetime.datetime.now()]))
    y1 = pd.Series({ q : 0 for q in x })

    columns = fig_df.columns
    n = len(columns)
    for i in range(0, n):
        y2 = y1 + fig_df[columns[i]] + 0
        ax.fill_between(x, y1, y2, step="post", color=status_color_map[i])
        y1 = y2

    # Bare
    plt.savefig(output_path, dpi=FIGURE_DPI);

    # Annotated
    plt.title(figure_title)
    plt.savefig(output_path[:-4] + "-annotated.png", dpi=FIGURE_DPI);

# %%

crawl_url_totals = [0] * num_crawls
crawl_content_totals = [0] * num_crawls
crawl_abandoned_totals = [0] * num_crawls
crawl_first_response_totals = [0] * num_crawls
crawl_first_break_totals = [0] * num_crawls
crawl_first_change_totals = [0] * num_crawls
crawl_first_unreliable_totals = [0] * num_crawls

num_unresponsive = 0
num_responsive = 0
num_stable = 0
num_reliable = 0
num_abandoned = 0

total_num_resolves = 0
total_num_breaks = 0
total_num_contents = 0
total_num_content_changes = 0
max_num_content_changes = 0

total_num_urls = len(all_url_lifetimes)
max_num_breaks   = total_num_urls * (np.ceil(num_crawls / 2)) # Round up; if the responsiveness is [0, 1, 0] across three crawls, there are at most two breaks
max_num_contents = total_num_urls * (num_crawls)

breakCounts = []
content_change_counts = []

for _, lifetime in all_url_lifetimes.items():
    #if lifetime.first_crawl_position:
    crawl_url_totals[lifetime.first_crawl_position] += 1

    total_num_resolves += lifetime.num_resolves
    total_num_breaks += lifetime.num_breaks
    total_num_contents += lifetime.num_contents
    total_num_content_changes += lifetime.num_content_changes
    max_num_content_changes += lifetime.num_resolves - 1

    breakCounts.append(lifetime.num_breaks)
    content_change_counts.append(lifetime.num_content_changes)

    if lifetime.num_breaks == 0:
        num_responsive += 1

    if lifetime.num_contents == 1:
        num_stable += 1

    if lifetime.num_breaks == 0 and lifetime.num_contents == 1:
        num_reliable += 1

    if lifetime.last_known_status in (Status.BECAME_UNRESPONSIVE, Status.STILL_UNRESPONSIVE):
        num_unresponsive += 1

    first_unreliable = num_crawls
    if lifetime.first_response_position is not None:
        crawl_first_response_totals[lifetime.first_response_position] += 1
    
    if lifetime.first_break_position is not None:
        crawl_first_break_totals[lifetime.first_break_position] += 1
        first_unreliable = lifetime.first_break_position

    if lifetime.first_change_position is not None:
        crawl_first_change_totals[lifetime.first_change_position] += 1
        first_unreliable = min(lifetime.first_change_position, first_unreliable)
    
    if first_unreliable < num_crawls:
        crawl_first_unreliable_totals[first_unreliable] += 1

    # If the URL stopped being queried, find out when
    for i, status in enumerate(lifetime.statuses[::-1]):
        if status != Status.UNKNOWN:
            break

    if i > 0:
        crawl_abandoned_totals[num_crawls - i] += 1
        num_abandoned += 1

for i in content_first_crawl_positions.values():
    #if lifetime.first_crawl_position:
    crawl_content_totals[i] += 1

really_bads = list()
for url, lifetime in all_url_lifetimes.items():
    skip = False
    for status in lifetime.statuses:
        if status not in (Status.BECAME_UNRESPONSIVE, Status.STILL_UNRESPONSIVE, Status.UNKNOWN):
            skip = True
            break
    if not skip:
        really_bads.append((url, lifetime))

num_never_responded = len(really_bads)
num_responded = total_num_urls - num_never_responded

num_unreliable = total_num_urls - num_reliable
num_unstable = total_num_urls - num_stable
num_unresponsive = total_num_urls - num_responsive


# %%

with open(output_directory + "totals", 'w') as file:
    file.write("\n".join([ "%s\t%d" % (label, value) for (label, value) in {
        "total_num_urls" : total_num_urls,
        "total_num_resolves" : total_num_resolves,
        "total_num_breaks" : total_num_breaks,
        "total_num_contents" : total_num_contents,
        "total_num_content_changes" : total_num_content_changes,
        "maxnum_content_changes" : max_num_content_changes,
        "num_never_responded" : num_never_responded,
        "num_unreliable" : num_unreliable,
        "num_unstable" : num_unstable,
        "num_unresponsive" : num_unresponsive
    }.items()]))

# %%

text_report = ""

# Totals
text_report += ("Of all %s observed URLs,\n"
    % ("{0:,}".format(total_num_urls)))
text_report += ("\t%s of URLs (%s total) were responsive\n"
    % ("{0:.2%}".format(num_responsive / total_num_urls), "{0:,}".format(num_responsive)))
text_report += ("\t%s of URLs (%s total) were stable\n"
    % ("{0:.2%}".format(num_stable / num_responded), "{0:,}".format(num_stable)))
text_report += ("\t%s of URLs (%s total) were reliable (both responsive and stable)\n"
    % ("{0:.2%}".format(num_reliable / total_num_urls), "{0:,}".format(num_reliable)))
text_report += ("\t%s of URLs (%s total) were responsive in the last crawl\n"
    % ("{0:.2%}".format(num_unresponsive / total_num_urls), "{0:,}".format(num_unresponsive)))
text_report += ("\t%s of URLs (%s total) never responded in any crawl\n"
    % ("{0:.2%}".format(num_never_responded / total_num_urls), "{0:,}".format(num_never_responded)))
text_report += ("\t%s of URLs (%s total) were abandoned\n"
    % ("{0:.2%}".format(num_abandoned / total_num_urls), "{0:,}".format(num_abandoned)))

# Unreliable URLs
text_report += "\n"
text_report += ("Of the %s unreliable URLs,\n"
    % ("{0:,}".format(num_unreliable)))
text_report += ("\t%s of unreliable URLs (%s total) were not always responsive\n"
    % ("{0:.2%}".format(num_unresponsive / num_unreliable), "{0:,}".format(num_unresponsive)))
text_report += ("\t%s of unreliable URLs (%s total) were not always stable\n"
    % ("{0:.2%}".format(num_unstable / num_unreliable), "{0:,}".format(num_unstable)))

# Behavior
text_report += "\n"
text_report += ("URLs break %s of the time between queries\n"
    % ("{0:.2%}".format(total_num_breaks / (total_num_resolves + total_num_breaks))))
text_report += ("URLs contents change %s of the time between queries\n"
    % ("{0:.2%}".format(total_num_content_changes / max_num_content_changes)))

with open(output_directory + "report.txt", "w+") as file:
    file.write(text_report)

print(text_report)

#%%

rc("text", usetex=True)
rc("savefig", format="pdf", dpi=FIGURE_DPI)
rc("font", size=14, family="serif", serif="Computer Modern")

#%%

breakCountFrequencies = np.unique(breakCounts, return_counts=True)
figure_title = network_name + ": Frequency Distribution of Total Losses of Responsiveness Per URL"
output_path = output_directory + "url-break-freq-dist"

plt.plot(
    breakCountFrequencies[0],
    breakCountFrequencies[1],
    "-o",
    color="black"
);
ax = plt.gca()

plt.xlabel("Number of losses of responsiveness");
plt.ylabel("Number of URLs");

ax.set_yticklabels(["{:,}k".format(int(y / 1000)) for y in plt.yticks()[0]]);

# Bare
plt.savefig(output_path, dpi=FIGURE_DPI);

# Annotated
plt.title(figure_title)
plt.savefig(output_path + "-annotated", dpi=FIGURE_DPI);

#%%

content_change_counts = None # Unimplemented

if MAKE_URL_UNAVAILABLE_HISTOGRAM or MAKE_URL_UNSTABLE_HISTOGRAM:
    content_change_count_frequencies = np.unique(content_change_counts, return_counts=True)

    maxCount = max(len(breakCountFrequencies[0]), len(content_change_count_frequencies[0]))

    frequencies_df = pd.DataFrame(
        columns=["Unresolvable", "Changed Content"],
        index=range(maxCount),
        data=0
    )

    for i, numBreaks in enumerate(breakCountFrequencies[0]):
        numUrls = breakCountFrequencies[1][i]
        frequencies_df["Unresolvable"][numBreaks] = numUrls

    for i, numChanges in enumerate(content_change_count_frequencies[0]):
        numUrls = content_change_count_frequencies[1][i]
        frequencies_df["Changed Content"][numChanges] = numUrls

#%%

if MAKE_URL_UNSTABLE_HISTOGRAM:
    figure_title = network_name + ": Frequency Distribution of Total Content Changes Per URL"
    output_path = output_directory + "url-unstable-histogram"

    plt.plot(
        content_change_count_frequencies[0],
        content_change_count_frequencies[1],
        "-o",
        color="black"
    );
    ax = plt.gca()

    plt.xlabel("Number of content changes");
    plt.ylabel("Number of URLs");

    ax.set_yticklabels(["{:,}k".format(int(y / 1000)) for y in plt.yticks()[0]]);

    # Bare
    plt.savefig(output_path, dpi=FIGURE_DPI);

    # Annotated
    plt.title(figure_title)
    plt.savefig(output_path + "-annotated", dpi=FIGURE_DPI);

#%%

if MAKE_URL_UNAVAILABLE_HISTOGRAM:
    figure_title = network_name + ": Frequency Distribution of Breaks and Changes"
    output_path = output_directory + "url-unavailable-histogram"

    ax = frequencies_df.plot(
        color="black",
        style=["-+", "--o"],
        legend=False
    );

    plt.ylabel("Number of URLs");
    plt.xlabel("Number of queries");

    ax.set_yticklabels(["{:,}k".format(int(y / 1000)) for y in plt.yticks()[0]]);

    # Bare
    plt.savefig(output_path, dpi=FIGURE_DPI);

    # Annotated
    plt.title(figure_title)
    plt.legend()
    plt.savefig(output_path + "-annotated", dpi=FIGURE_DPI);

#%%

crawl_totals_df = pd.DataFrame(
    index   = [datetime.datetime.strptime(x, "\"%Y-%m-%dT%H:%M:%S.%fZ\"^^<http://www.w3.org/2001/XMLSchema#dateTime>") for x in crawl_times],
)

crawl_totals_df["New URLs"] = crawl_url_totals
crawl_totals_df["New Contents"] = crawl_content_totals
crawl_totals_df["Abandoned"] = crawl_abandoned_totals
crawl_totals_df["First Response"] = crawl_first_response_totals
crawl_totals_df["First Break"] = crawl_first_break_totals
crawl_totals_df["First Change"] = crawl_first_change_totals
crawl_totals_df["First Unreliable"] = crawl_first_unreliable_totals
crawl_totals_df["Total URLs"] = crawl_totals_df["New URLs"].cumsum()
crawl_totals_df["Total Contents"] = crawl_totals_df["New Contents"].cumsum()
crawl_totals_df["Total Abandoned"] = crawl_totals_df["Abandoned"].cumsum()
crawl_totals_df["Total Responded"] = crawl_totals_df["First Response"].cumsum()
crawl_totals_df["Total Intermittent"] = crawl_totals_df["First Break"].cumsum()
crawl_totals_df["Total Unstable"] = crawl_totals_df["First Change"].cumsum()
crawl_totals_df["Total Unreliable"] = crawl_totals_df["First Unreliable"].cumsum()
crawl_totals_df["Percent Responsive"] = 1 - crawl_totals_df["Total Intermittent"] / crawl_totals_df["Total URLs"]
crawl_totals_df["Percent Stable"] = 1 - crawl_totals_df["Total Unstable"] / crawl_totals_df["Total Responded"]
crawl_totals_df["Percent Reliable"] = 1 - crawl_totals_df["Total Unreliable"] / crawl_totals_df["Total URLs"]

crawl_totals_df

#%%

start_time = START_TIME if START_TIME else crawl_times[0]
end_time = END_TIME if END_TIME else crawl_times[-1]
time_frame = (
    datetime.datetime.strptime(start_time, "\"%Y-%m-%dT%H:%M:%S.%fZ\"^^<http://www.w3.org/2001/XMLSchema#dateTime>"),
    datetime.datetime.strptime(end_time, "\"%Y-%m-%dT%H:%M:%S.%fZ\"^^<http://www.w3.org/2001/XMLSchema#dateTime>"),
)

#%%

figure_title = network_name + ": Running Total of Unique URLs and Contents"
output_path = output_directory + "running-total-urls-and-contents"

df = crawl_totals_df[[
    "Total URLs",
    "Total Contents",
#     "Total Abandoned"
]]

ax = df.plot(
    color="black",
    style=["--", ":", "-"],
    legend=False,
    fillstyle="none",
    markersize=7
);
for i, line in enumerate(ax.get_lines()):
    line.set_marker(["s", "D"][i])

plt.xlim(time_frame);
plt.ylim([0, max(df.max()) * 1.05])

ax.set_yticklabels(["{:,}k".format(int(y / 1000)) for y in plt.yticks()[0]]);

# Bare
plt.savefig(output_path, dpi=FIGURE_DPI);

# Annotated
plt.title(figure_title)
plt.legend()
plt.savefig(output_path + "-annotated", dpi=FIGURE_DPI);

# Export legend (https://stackoverflow.com/a/50279532)
figsize = (2.2, .75)
fig_leg = plt.figure(figsize=figsize)
ax_leg = fig_leg.add_subplot(111)
# add the legend from the previous axes
ax_leg.legend(*ax.get_legend_handles_labels(), loc='center')
# hide the axes frame and the x/y labels
ax_leg.axis('off')
fig_leg.savefig(output_path + "-legend")

#%%

figure_title = network_name + ": Responsiveness, Stability, Reliability Over Time"
output_path = output_directory + "reliability-over-time"

ax = crawl_totals_df[[
    "Percent Responsive",
    "Percent Stable",
    "Percent Reliable"
]].plot(
    color="black",
    style=["--", ":", "-"],
    legend=False,
    fillstyle="none",
    markersize=8
);
for i, line in enumerate(ax.get_lines()):
    line.set_marker(["x", "+", "o"][i])

plt.xlim(time_frame);
plt.ylim([0.0, 1.05]);
ax.set_yticklabels(["{:.0%}".format(float(y)) for y in plt.yticks()[0]]);

# Bare
plt.savefig(output_path, dpi=FIGURE_DPI);

# Annotated
plt.title(figure_title)
leg = plt.legend()
plt.savefig(output_path + "-annotated");

# Export legend (https://stackoverflow.com/a/50279532)
figsize = (2.5, 1)
fig_leg = plt.figure(figsize=figsize)
ax_leg = fig_leg.add_subplot(111)
# add the legend from the previous axes
ax_leg.legend(*ax.get_legend_handles_labels(), loc='center')
# hide the axes frame and the x/y labels
ax_leg.axis('off')
fig_leg.savefig(output_path + "-legend")


# %%
