import json
import argparse

from app_logger import logger
from twitter import *
import sqlite3
import os
import time

def _createUserTable(conn, force=False):
    logger.info("Creating user table")
    c = conn.cursor()
    if force:
        sub_c = conn.cursor()
        logger.info("Dropping user table")
        sub_c.execute("DROP TABLE IF EXISTS users")
        conn.commit()

    query = "CREATE TABLE IF NOT EXISTS {0} {1}"

    query = query.format("users", "(id INTEGER UNIQUE, user_id)")
    logger.info("Running query: {0}".format(query))
    c.execute(query)
    conn.commit()

def _fillUserTable(conn, data):
    c = conn.cursor()

    query = "INSERT OR REPLACE INTO users VALUES ({0}, {1})"
    logger.info("Loading data into user table")
    for k,v in data.items():
        q = query.format(k ,v)
        c.execute(q)

    conn.commit()

def _createTweetTable(conn, force=False):
    logger.info("Creating tweet table")
    c = conn.cursor()
    # drop the table and recreate
    if force:
        logger.info("Dropping tweet table")
        c.execute("DROP TABLE IF EXISTS tweets")
        conn.commit()
    query = "CREATE TABLE IF NOT EXISTS {0} {1}"

    query = query.format("tweets", "(id INTEGER UNIQUE, user_id, tweet text)")
    logger.info("Running query: {0}".format(query))
    c.execute(query)
    conn.commit()

def _formatData(data):
    if "user" not in data:
        return
    if "id" not in data:
        return
    if "text" not in data:
        return

    d = {
        "user_id": data['user']['id'] % _formatData.num_users,
        "id": data['id'],
        "tweet": data['text']
    }
    return (d['id'], d['user_id'], d['tweet'])

def streamData(conn, twitter_api, query):
    c = conn.cursor()
    insert = "INSERT INTO tweets VALUES (?, ?, ?);"

    num_items = 0

    logger.info("Starting stream")
    iterator = twitter_api.statuses.filter(track=query, _method="POST")

    # keep consuming tweets
    # for each tweet, pull out the relevant info
    # and then write it to the database
    for i in iterator:
        try:
            f = _formatData(
            # if formatData returns None, then there was an issue and we should continue through
            if f is None:
                logger.info("Processed {0} tweets".format(num_items))
                continue
            c.execute(insert, f)
            conn.commit()
            num_items = num_items + 1
            if num_items % 100000 == 0:
                logger.info("Processed {0} tweets".format(num_items))
                if num_items >= 10000000:
                    logger.info("Processed enough tweets".format(num_items))
                    conn.commit()
                    break
        except Exception as e:
            logger.warning("Error occured with tweet: {0}".format(i, e))
            logger.exception(e)
            conn.commit()


if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument(
        "filename", help="JSON file representing social graph"
    )
    arg_parse.add_argument(
        "query", help="The query to pass to the Twitter streaming API"
    )
    arg_parse.add_argument(
        "--force_tables",
        help="Force table creation.  "
        "This will recreate a table even if it already exists",
        action="store_true",
        default=False
    )
    arg_parse.add_argument(\
        "--skip_table_load",
        help="Skip the table loading process.",
        action="store_true",
        default=False
    )

    args = arg_parse.parse_args()
    # connect to database
    conn = sqlite3.connect("database.db")

    logger.info("Loading social graph")
    data = json.load(open(args.filename, 'r'))
    l = list(data.keys())

    # create hash of the user_ids
    NUM_USERS = len(l)
    users = {i:j for i,j in zip(l, range(NUM_USERS))}
    del(data)
    del(l)

    # assign some static variables
    _formatData.num_users = NUM_USERS



    # create and fill the user table
    if not args.skip_table_load:
        _createUserTable(conn, force=args.force_tables)
        _fillUserTable(conn, users)

        # create the tweet table
        _createTweetTable(conn, force=args.force_tables)

    # begin streaming tweets and putting them into the database
    logger.info("Setting up stream")
    t = TwitterStream(
        auth=OAuth(
            os.environ["TWITTER_API_KEY"],
            os.environ["TWITTER_API_SECRET"],
            os.environ['TWITTER_CONSUMER_KEY'],
            os.environ['TWITTER_CONSUMER_SECRET']
        )
    )
    streamData(conn, t, args.query)
