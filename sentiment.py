import re
import sqlite3
from textblob import TextBlob


class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def fetch_tweets(self):
        print("fetching tweets")
        tweets = []
        conn = sqlite3.connect('database.db')
        cursor = conn.execute("SELECT * from TWEETS")
        for row in cursor:
            tweet = {"id":row[0], "tweet":row[2]}
            tweets.append(tweet)
        conn.close()
        print("finished fetching tweets")
        return tweets

    def write_tweets(self, tweets):
        print("Writing tweets to DB")
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS sentiment')
        cur.execute('CREATE TABLE sentiment (id INT PRIMARY KEY NOT NULL, polarity REAL, subjectivity REAL)')
        cur.executemany('INSERT INTO sentiment (id, polarity, subjectivity) VALUES(?,?,?)',tweets)
        print("Finished writing tweets")
        conn.commit()
        conn.close()

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w +:\ / \ / \S +)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        return analysis.sentiment

    def get_tweets(self):
        '''
        Main function to fetch tweets and parse them.
        '''
        tweets = []
        fetched_tweets = self.fetch_tweets()

        print("processing tweets")
        # parsing tweets one by one
        for tweet in fetched_tweets:
            sentiment = self.get_tweet_sentiment(tweet["tweet"])
            current = (tweet['id'], sentiment.polarity, sentiment.subjectivity)
            tweets.append(current)


        print("finished processing tweets")
        # return parsed tweets
        return tweets


def main():
    # creating object of TwitterClient Class
    client = TwitterClient()
    # calling function to get tweets
    tweets = client.get_tweets()

    client.write_tweets(tweets)


if __name__ == "__main__":
    # calling main function
    main()