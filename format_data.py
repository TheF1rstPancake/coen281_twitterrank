import pandas as pd
import itertools
from app_logger import logger
import json
import argparse

import multiprocessing as mp


def _buildData(in_queue, out_dict, lock):
    # In our dataset every row is two values and
    # represents a graph where user 1 follows user B
    # "1,2" means user 1 follows user 2
    # for pageRank we really want the opposite
    # we want our column,row entries to show
    # that column  is followed by row.
    # For TrustRank we want column follows row
    while True:
        item = in_queue.get()
        if item is None:
            return

        node, edge = item.strip().split(",")
        # add this node/edge pair to our dictionary
        lock.acquire()
        out_dict.update({
            node:
                {
                    'following': out_dict.get(node, {}).get("following", []) + [edge],
                    'followers': out_dict.get(node, {}).get("followers", [])
                }
        })
        lock.release()
        # add the edge to the dictionary as a node
        # it will be empty until we find an edge for it
        lock.acquire()
        out_dict.update({
            edge: {
                'followers': out_dict.get(edge, {}).get("followers", []) + [node],
                'following': out_dict.get(edge, {}).get('following', [])
            }
        })
        lock.release()

def postProcess(data):
    # calculate the weights for each edge
    # This is 1/len(following)
    for k, v in data.items():
        data[k]['weight'] = 1.0/len(v['following']) \
            if len(v['following']) > 0 else 0
    return data

def formatData(
    edge_filename,
    outfile,
    format="json",
    num_edges=None,
    step=None
):
    outfile = outfile + ".json" if format == "json" else outfile+".csv"

    num_workers = mp.cpu_count()
    manager = mp.Manager()
    results = manager.dict()
    work = manager.Queue(num_workers)

    lock = manager.Lock()

    pool = []
    for i in range(num_workers):
        p = mp.Process(target=_buildData, args=(work, results, lock))
        p.start()
        pool.append(p)

    # if step is not None,
    # then the number of edges we want to adjust the num_edges so that
    # we read the correct number of lines
    if step is not None and num_edges is not None:
        num_edges = num_edges * step

    # open the file and keep loading lines from it
    # each line will be added into the pool
    # the pool will then consume items and update the dictionary values
    # we add "None" values into the end of the queue to signal when the
    # pool can stop processing

    with open(edge_filename, 'r') as f:
        head = itertools.chain(
            itertools.islice(f, 0, num_edges, step),
            (None, )*num_workers
        )
        for ix, l in enumerate(head):
            if ix % 100000 == 0:
                logger.info("Processed {0} entries".format(ix))
            work.put(l)

    for p in pool:
        p.join()

    logger.info("Post processing results")
    results = results.copy()
    results = postProcess(results)

    logger.info("Edges loaded.  Writing to JSON file")
    with open(outfile.format("json"), 'w') as f:
        json.dump(results, f, indent=2)

    logger.info("Finished writing to JSON")
    logger.info("Stats:\n\tUsers: {0}".format(len(results)))


if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument(
        "--edge_filename",
        default="data/edges.csv",
        help="Name of the file that contains the edges"
    )
    arg_parse.add_argument(
        "--outfile",
        default="rank_dataset",
        help="Name of the file you want to write data out to."
        "Do not include an extension"
    )
    arg_parse.add_argument(
        "--num_edges",
        default=None,
        help="Number of edges to parse from the edge file",
        type=int
    )

    arg_parse.add_argument(
        "--step",
        default=None,
        help="How to read the file."
        "  If step is 2, then only 1 in every 2 lines will be read.",
        type=int
    )

    logger.info("Starting data format")
    args = arg_parse.parse_args()
    formatData(
        args.edge_filename,
        args.outfile,
        format="json",
        num_edges=args.num_edges,
        step=args.step
    )
