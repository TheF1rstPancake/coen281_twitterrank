import sqlite3
import argparse
from app_logger import logger

class Sentiment(object):

    def __init__(self, database):
        self.database = database

    # Retrieves data from database
    # Returns tweet_id, rank, polarity, subjectivity
    def fetch_data(self):
        logger.info("Fetching Data")

        conn = sqlite3.connect(self.database)
        cur = conn.execute('SELECT tweets.id, ranks.rank, sentiment.polarity, sentiment.subjectivity FROM users, ranks, sentiment, tweets WHERE users.id = ranks.id AND tweets.id = sentiment.id AND users.user_id = tweets.user_id')
        data = [{
            'rank': row[1],
            'polarity': row[2],
            'subjectivity': row[3]
        } for row in cur]

        return data

    # Parses Data and Prints our result
    # 0.21 was average of our data set
    def parse_data(self, data):
        logger.info("Parsing Data")
        rank_sum = 0
        for d in data:
            rank_sum += d['rank']
        threshold = 0.13
        pos_sum = 0
        pos_sum_ranked = 0
        neg_sum = 0
        neg_sum_ranked = 0
        for d in data:
            if d['polarity'] > threshold and d['subjectivity'] > 0.2:
                pos_sum_ranked += d['rank']**2
                pos_sum += 1
            elif d['polarity'] < threshold and d['subjectivity'] > 0.2:
                neg_sum_ranked += d['rank']**2
                neg_sum += 1
        total_sum = pos_sum + neg_sum
        total_sum_ranked = pos_sum_ranked + neg_sum_ranked
        logger.info('Positive (Unranked): {0}'.format(float(pos_sum) / total_sum))
        logger.info('Negative (Unranked): {0}'.format(float(neg_sum) / total_sum))
        logger.info('Positive (Ranked): {0}'.format(float(pos_sum_ranked) / total_sum_ranked))
        logger.info('Negative (Ranked) {0}: '.format(float(neg_sum_ranked) / total_sum_ranked))


def main(database):
    # creating object of TwitterClient Class
    client = Sentiment(database)
    # calling function to get tweets

    data = client.fetch_data()
    client.parse_data(data)


if __name__ == "__main__":
    # calling main function
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument(
        "database",
        default="database.db",
        help="The name of the database file"
    )
    args = arg_parse.parse_args()
    main(args.database)
