# Ranking social media content to aid predictive modeling
COEN 281 Group 7 Term Project

Authors:
  - Giovanni Briggs
  - Maxen Chung
  - Jeffery Wick
  - Vincent Tai

## Initial Setup
Our code is written in Python 3.5.  We have included a *requirements.txt* file that includes all of the packages necessary to run our project.  To install them run `pip install -r requirements.txt`.

### Twitter Social Graph Dataset
Dataset is downloadable from: http://socialcomputing.asu.edu/datasets/Twitter.
After downloading, copy the contents from the `data` directory in the download
into the `data` directory here.

## Formatting Dataset and Getting Tweets
The current format of the dataset is too large for us to work with in a resonable amount of time.
We wrote a script to reformat a subset of the larger dataset and then we wrote a script to assign tweets to those users.

### Formatting Social Graph
Too run the script:
  `python format_data.py --edge_filename data/edges.csv --outfile formatted_data.json --num_edges 10000`

This will process 10,000 edges from the larger dataset into an easier to work with JSON format named "formatted_data.json".  You can change the number of edges accordingly.  You can also have the script only read a certain percentage of the larger dataset by running:
  `python format_data.py --edge_filename data/edges.csv --outfile formatted_data.json --skip_lines 25`

This will tell the script to read 1 in every 25 lines.  This is the command we used for our final output.

### Getting Tweets
In order to gather the tweets, we used the Twitter Streaming API and wrote the corresponding Tweets into a SQLite database.  We also load and write the formatted data from the last step into a different table in the same database.

First, you need to get the Twitter API credentials in order to make API calls.  Go to https://apps.twitter.com/ to create a new app.  This requires that you also have a Twitter account.  Once you've created the app, your app settings will list four different keys:
  1. Consumer Key (API Key)
  2. Consumer Secret (API Secret)
  3. Access Token
  4. Access Token Secret

You will need all of these values and set them as environment variables in order to run our tweet collection script.
The environment variables are:
  1. TWITTER_CONSUMER_KEY
  2. TWITTER_CONSUMER_SECRET
  3. TWITTER_API_KEY
  4. TWITTER_API_SECRET

Once these values are set, you can run the script collection by:
  `python get_tweets.py formatted_data.json "trump, donald trump, realDonaldTrump --database database.db"`

The first argument is the formatted dataset from the previous step.  The second is a query that you want to gather tweets for.  In our project we used "trump, donald trump, realDonaldTrump" which looks for any tweets that have the phrases "trump", "donald trump", or "realDonaldTrump".  The third is optional where you can set the name of the file where the SQLite database will be written (defaults to *database.db*).

This process will also loaded the social graph from the formatted_data.json file into a table called "users".  That loading process can take some time and only needs to be run once.  You can skip that process by calling:
 `python get_tweets.py formatted_data.json "trump, donald trump, realDonaldTrump" --skip_table_load`

 The user table contains:
  - *id*: the unique user ID from the formatted dataset
  - *user_id*: a unique integer.  All of the ids are sequential from 0 to the number of users.

The script will run and continue collecting Tweets until:
  a) it has collected 10,000,000 tweets (completely arbitrarily chosen number to prevent dataset from growing too large)
  b) you kill the script

The tweets will be written to a table named "tweets" which will contain:
  - *id*: ID of the tweet.  This is a unique value to prevent us from writting the same tweet multiple times
  - *user_id*: the hashed value of the ID of the user who made the tweet.
  - *tweet*: the actual text of the tweet

You can join these tables with the following query:
  `SELECT * FROM users, tweets WHERE users.user_id = tweets.user_id`

## Running PageRank
Now that we have our social graph and our tweets, we can run our ranking algorithm.  We've implemented a simple version of Google's PageRank to rank the different nodes in the social graph.

To run the ranking algorithm:
 `python small_pagerank.py --infile formatted_dataset.json --outfile ranks.csv --database database.db --max_iters 50 --beta 0.8`

The `max_iters` and `epsilon` paramters can be whatever you want them to be, but these are the values we used in our paper.

This script will take in our JSON formatted social graph and output a CSV file where each row is the ID of a user followed by their PageRank.  It will also write to the database at a table named *ranks*.  This table includes:
  1. *id*: the unique user ID
  2. *rank*: the rank of that user in the social graph

The reason we included a CSV output for this was beecause we originally wanted the rank to be more portable.  We figured that the combination of the JSON formatted social graph and the CSV rank results could have greater uses outside of this application.

## Running Sentiment Analysis
We provide a script for running straight sentiment analysis.  The results of this script are added to our SQLite database under a table named *sentiment*.  This table will include:
  1. *id*: the ID of the tweet
  2. *polarity*: a float value ranging from -1 to 1, with -1 being negative sentiment and 1 being positive sentiment.
  3. *subjectivity*: a float value ranging from 0 to 1 with 0 being objective and 1 being extremely subjective.

To run the script:
  `python sentiment.py database.db`

The first argument is the name of the database file that you created when running `get_tweets.py`.

## Running PageRank and Sentiment Analysis
We have a final script named `combine.py` that combines the ranking results with the sentiment analysis to give us a final weighted sentiment analysis result.

  `python combine.py database.db`

This will run the combination metric and output the 4 values:
  1. **Positive (Unranked)**: The percentage of tweets that are *positive* using basic sentiment analysis
  2. **Negative (Unranked)**: The percentage of tweets that are *negative* using basic sentiment analysis
  3. **Positive (Ranked)**: The percentage of tweets that are *positive* using the weighted (ranked) sentiment analysis
  4. **Negative (Ranked)**: The percentage of tweets that are *negative* using the weighted sentiment analysis

## Sample Datasets
In our final submission we included our *formatted_data.json* and *database.db* files.  *formatted_data.json* includes the JSON formatted social graph created from the ASU dataset.  *database.db* has all four tables loaded with data.
