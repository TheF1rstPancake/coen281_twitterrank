import pandas as pd
from itertools import islice
from app_logger import logger
import json
import argparse


def formatData(
    edge_filename,
    outfile,
    format="json",
    num_edges=1000000,
    page_rank=True
):
    outfile = outfile + ".json" if format == "json" else outfile+".csv"
    with open(edge_filename, 'r') as f:
        head = list(islice(f, num_edges))
        d = {}
        for ix, l in enumerate(head):
            # In our dataset every row is two values and
            # represents a graph where user 1 follows user B
            # "1,2" means user 1 follows user 2
            # for pageRank we really want the opposite
            # we want our column,row entries to show
            # that column  is followed by row.
            # For TrustRank we want column follows row
            node, edge = l.strip().split(",")[::-1] \
                if page_rank else l.strip().split(",")

            # add this node/edge pair to our dictionary
            if node in d:
                d[node][edge] = 1
            else:
                d[node] = {edge: 1}

            # add the edge to the dictionary as a node
            # it will be empty until we find an edge for it
            if edge not in d:
                d[edge] = {}

        # Right now, all of the weights are 1
        # but really it should be 1/number of inlinks
        for k, v in d.items():
            for s_k, s_v in v.items():
                d[k][s_k] = s_v/len(v)

    logger.info("Edges loaded.  Writing to JSON file")
    with open(outfile.format("json"), 'w') as f:
        json.dump(d, f, indent=2)

    logger.info("Finished writing to JSON")
    logger.info("Stats:\n\tUsers: {0}".format(len(d)))


if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument(
        "--edge_filename",
        default="data/edges.csv",
        help="Name of the file that contains the edges"
    )
    arg_parse.add_argument(
        "--page_rank",
        action="store_true",
        help="Use this argument if you want to create a"
        "dataset for use with PageRank",
        default=False
    )
    arg_parse.add_argument(
        "--outfile",
        default="rank_dataset",
        help="Name of the file you want to write data out to."
        "Do not include an extension"
    )
    arg_parse.add_argument(
        "--num_edges",
        default=1000000,
        help="Number of edges to parse from the edge file",
        type=int
    )

    logger.info("Starting data format")
    args = arg_parse.parse_args()
    formatData(
        args.edge_filename,
        args.outfile,
        format="json",
        page_rank=args.page_rank,
        num_edges=args.num_edges
    )
