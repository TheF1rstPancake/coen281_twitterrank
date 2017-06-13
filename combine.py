import sqlite3

class Sentiment(object):
    # Retrieves data from database
    # Returns tweet_id, rank, polarity, subjectivity
    def fetch_data(self):
        print("Fetching Data")

        conn = sqlite3.connect('database2.db')
        cur = conn.execute('SELECT tweets.id, ranks.rank, sentiment.polarity, sentiment.subjectivity FROM users, ranks, sentiment, tweets WHERE users.id = ranks.id AND tweets.id = sentiment.id AND users.user_id = tweets.user_id')
        data = []
        for row in cur:
            current = {'rank':row[1], 'polarity':row[2], 'subjectivity':row[3]}
            data.append(current)
        return data

    # Parses Data and Prints our result
    # 0.21 was average of our data set
    def parse_data(self,data):
        print("Parsing Data")
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
        total_sum = pos_sum+neg_sum
        total_sum_ranked = pos_sum_ranked+neg_sum_ranked
        print('Positive (Unranked): ', pos_sum/total_sum)
        print('Negative (Unranked): ', neg_sum/total_sum)
        print('Positive (Ranked)', pos_sum_ranked/total_sum_ranked)
        print('Negative (Ranked)', neg_sum_ranked/total_sum_ranked)


def main():
    # creating object of TwitterClient Class
    client = Sentiment()
    # calling function to get tweets

    data = client.fetch_data()
    client.parse_data(data)

if __name__ == "__main__":
    # calling main function
    main()