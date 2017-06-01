from twitter import *
from app_logger import logger
import json
import argparse
import os
import time


if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument(
        "filename",
        help="Name of file representing Twitter social graph"
    )

    args = arg_parse.parse_args()

    logger.info("Loading data file")
    data = json.load(open(args.filename))
    users = list(data.keys())
    del(data)
    logger.info("File loaded")

    t = Twitter(
        auth=OAuth(
            os.environ["TWITTER_API_KEY"],
            os.environ["TWITTER_API_SECRET"],
            os.environ['TWITTER_CONSUMER_KEY'],
            os.environ['TWITTER_CONSUMER_SECRET']
        )
    )
    logger.info("Requesting data from Twitter")
    valid_users = []
    for i in range(0, len(users), 100):
        logger.info("Searching for batch #{0}: {1}".format(i/100, (i, i+100)))
        user_list = ",".join(users[i:i+100])
        try:
            r = t.users.lookup(
                user_id=",".join(users[i:i+100]),
                _method="POST",
            )
        except TwitterHTTPError as e:
            logger.warning("Twitter returned error: {0}".format(e.__dict__))
            # 88 means we exceeed the rate limit.  Go to sleep and try again
            if(e.response_data['errors'][0]['code'] == 88):
                try:
                    time.sleep((60*16))
                    r = t.users.lookup(
                        user_id=",".join(users[i:i+100]),
                        _method="POST",
                    )
                except Exception as e:
                    logger.error("Something really screwed up: {0}".format(e))
                    break
        # add the user id into the list
        valid_users.extend([u["id"] for u in r])

    valid_users = {"users": valid_users}
    json.dump(valid_users, open("valid_twitter_users.json",'w'))
