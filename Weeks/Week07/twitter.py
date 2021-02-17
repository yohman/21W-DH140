########################################

#     Libraries

########################################

# to explore the data
import pandas as pd

# to get tweets
import tweepy as tw

# to manipulate csv files
import csv
from csv import DictWriter

# to parse arguments passed by user
import argparse

# system stuff
import time
import sys

########################################

#     Set up the command arguments

########################################

parser = argparse.ArgumentParser(description='This twitter scraper allows you to search twitter for a specified term, for a given number of  times (--times default 10), for a given time interval (--rest default 60 seconds), and retrieve 500 tweets at a time. ')

# request inputs
consumer_key = input("Your consumer key: ")
consumer_secret = input("Your consumer secret: ")
access_token = input("Your access token: ")
access_token_secret = input("Your access token secret: ")

# required arguments
parser.add_argument("--q", 
                    default='covid', 
                    type=str, 
                    required=True, 
                    help="Enter a query text")

# optional arguments
parser.add_argument("--times", 
                    default=20, 
                    type=int, 
                    required=False, 
                    help="How many times to run (default=20)")

parser.add_argument("--rest", 
                    default=60, 
                    type=int, 
                    required=False, 
                    help="How many seconds to rest between calls (default=60)")

parser.add_argument("--filename", 
                    default='tweets.csv', 
                    required=False, 
                    type=str, 
                    help="File name with csv extension (default='tweets.csv')")

args = parser.parse_args()

########################################

# authenticate thyself with twitter

########################################
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

########################################

# writing to csv file ('w') 

########################################
# field names  
fields = ['created_at','text','screen_name','profile_image']

with open(args.filename, 'w') as csvfile:  
    # creating a csv writer object  
    csvwriter = csv.writer(csvfile)  
        
    # writing the fields  
    csvwriter.writerow(fields)  

########################################

# search query

########################################
searchterm = args.q

# filter out retweets (optional of course)
q = searchterm + " -filter:retweets"

# how many?
max_tweets = 500

########################################

# function to call tweets

########################################
def get_tweets():

    # Throw an error if the call to twitter fails
    try:
        tweets = tw.Cursor(api.search,
                           q=q,
                           tweet_mode='extended').items(max_tweets)

        # convert json tweets to dataframe
        json_data = [tweet._json for tweet in tweets]
        df = pd.json_normalize(json_data)

        # trim the columns
        df = df[['created_at','full_text','user.screen_name','user.profile_image_url_https']]

        # rename the columns
        df.columns = ['created_at','text','screen_name','profile_image']

        # append the new data to csv file (add the bus route to the file name)
        with open(args.filename, 'a') as tweetfile: 

            dictwriter = DictWriter(tweetfile, fieldnames=fields) 

            for index, row in df.iterrows():
                dictwriter.writerow(row.to_dict()) 

            tweetfile.close()
        
        print('sample tweet: ' + df.sample().iloc[0]['text'])
        # run this every x seconds
        time.sleep(args.rest)

    except Exception as e:
        print(e)
        print('Failed to get tweets. Trying again in 60 seconds...')
        time.sleep(60)
#         get_tweets()
#         sys.exit('Twitter could not authenticate you. Try again!')

########################################

#     Automate the call

########################################

# set a counter
i = 1

# start the loop
print('Starting the twitter scraper for "'+args.q+'". Running query ' + str(args.times) + ' times every ' + str(args.rest) + ' seconds.')
while i <= args.times:
    print('Getting tweets #' + str(i) + '...')
    get_tweets()

    i += 1
    
print('Ended the twitter scraper. Look for the file ' + args.filename)