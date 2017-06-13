import json
import sys
import math
import argparse
import sqlite3


def vector_diff_norm(vector1, vector2):
    sum = 0
    for user_id in vector1:
        diff = vector1[user_id] - vector2[user_id]
        sum += diff * diff
    return math.sqrt(sum)


def writeToDatabase(data, database):
    """
    Write data to database
    """
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS ranks")

    c.execute(
        "CREATE TABLE IF NOT EXISTS "
        "ranks (id INTEGER UNIQUE, rank REAL)"
    )
    query = "INSERT INTO ranks VALUES (?, ?);"
    for k, v in data.items():
        c.execute(query, (k, v))

    # commit and close
    conn.commit()
    conn.close()
    return True


def pagerank_iteration(graph, ranks, beta):
    """
    run one iteration of pagerank, using the given graph and rank vector
    """
    new_ranks = {}
    graph_len = len(graph)
    # Collect the sum of deadend outputs.  Add it to each element
    # after all else is done.  This is much more efficient than
    # behaving as if each deadend node literally had an outlink to
    # each node.
    deadend_sum = 0
    # initialize new vector to default weights
    for user_id in graph:
        new_ranks[user_id] = (1 - beta) / graph_len
    for user_id in graph:
        # look up the user_id in the vector and get its followees
        followees = graph[user_id]["following"]
        weight = graph[user_id]["weight"]
        if len(followees) > 0:
            for followee_id in followees:
                new_ranks[followee_id] += beta * ranks[user_id] * weight
        else:
            # dead end, treat as having outlinks to all nodes equally
            deadend_sum += beta * ranks[user_id] / graph_len
    for user_id in graph:
        new_ranks[user_id] += deadend_sum
    return new_ranks


def do_pagerank(graph, max_iterations=100, epsilon=0, beta=0.8):
    """
    do the PageRank.  Terminate either after max_iterations or when the difference norm between successive PageRank vectors is less than epsilon.  (1-beta) is probability of a hypothetical user jumping to a random node.

    Return the final PageRank vector, which is actually a dictionary of (key, pagerank) pairs
    """
    # build initial PageRank vector, n entries of the value 1/n.  this
    # is not actually a vector, but a dictionary, since ids (keys) are
    # not necessarily consecutive.
    ranks = {}
    for user_id in graph:
        ranks[user_id] = 1 / len(graph)

    iteration = 0
    epsilon = 0
    diff = 1
    while (iteration < max_iterations) and (diff > epsilon):
        new_ranks = pagerank_iteration(graph, ranks, beta)
        diff = vector_diff_norm(new_ranks, ranks)
        ranks = new_ranks
        sys.stderr.write(
            "iteration {0} done; diff={1}\n".format(iteration, diff))
        iteration += 1
    return ranks

if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument(
        "--infile",
        default="formatted_dataset.json",
        help="Name of a JSON file containing output of format_data.py"
    )
    arg_parse.add_argument(
        "--outfile",
        default="ranks.csv",
        help="Name of the file to output comma-separated (id,rank) pairs to."
    )
    arg_parse.add_argument(
        "--database",
        default="database.db",
        help="Name of SQLite database file to write data to"
    )
    arg_parse.add_argument(
        "--max_iters",
        default=10,
        help="Maximum number of iterations to run.",
        type=int
    )
    arg_parse.add_argument(
        "--epsilon",
        default=0,
        help="Acceptable PageRank difference vector norm to terminate at before reaching max_iters",
        type=float
    )
    arg_parse.add_argument(
        "--beta",
        default=0.8,
        help="Probability of not randomly teleporting.",
        type=float
    )

    args = arg_parse.parse_args()

    infile_name = args.infile
    infile = open(infile_name, "r")
    outfile_name = args.outfile
    outfile = open(outfile_name, "w")

    graph = json.load(infile)
    graph_len = len(graph)
    sys.stderr.write("loaded input file: {0} nodes\n".format(graph_len))

    ranks = do_pagerank(graph, args.max_iters, args.epsilon, args.beta)

    for user_id in ranks:
        outfile.write("{0},{1}\n".format(user_id, ranks[user_id]))

    writeToDatabase(ranks, args.database)
