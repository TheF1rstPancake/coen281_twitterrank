from pagerank import powerIteration
import argparse
import json
from app_logger import logger

if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("--filename", default="pageRank_dataset.json")

    args = arg_parse.parse_args()

    with open(args.filename, 'r') as f:
        data = json.load(f)

    logger.info("Running page rank")
    result = powerIteration(data, maxIterations=10)
    logger.info(
        "Max page rank: {0}:{1}".format(result.idxmax(), result.max())
    )
    logger.info("Min page rank {0}:{1}".format(
        result.idxmin(), result.min())
    )
    logger.info("Writing results to csv")
    result.to_csv("page_rank_result.csv")
