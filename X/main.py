import pandas as pd
from dotenv import load_dotenv
import os
import requests
import json
from bs4 import BeautifulSoup
import tweepy

load_dotenv()


consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET_KEY")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")


url = "https://www.allmysportsteamssuck.com/ncaa-division-i-football-and-basketball-twitter-hashtags-and-handles/"

def scrape_team_twitter_info():
    response = requests.get(url)
    if response.status_code == 200: # OK
        # create a "soup" object from the response text
        soup = BeautifulSoup(response.text, "html.parser")
        # print(soup)
        # find the rankingstable
        table = soup.find("table", attrs={"id": "rankingstable"})
        # print(table)
        # parse the header
        thead = table.find("thead")
        # print(thead)
        # grab all the column names from the header
        ths = thead.find_all("th")
        # print(ths)
        col_names = [th.get_text() for th in ths]
        print(col_names)
        # task: try to parse the tbody
        # a table (2D list) of all the rows in the body
        tbody = table.find("tbody")
        trs = tbody.find_all("tr")
        rows = []
        for tr in trs:
            row = []
            tds = tr.find_all("td")
            for td in tds:
                row.append(td.get_text())
            rows.append(row)
        # print(rows)
        df = pd.DataFrame(rows, columns=col_names)
        df = df.set_index("School")
        return df
    return None # TODO: should do better error handling

def fetch_user_account_info(client, username):
    # https://docs.tweepy.org/en/stable/client.html#tweepy.Client.get_user_by_username
    response = client.get_user(username=username)
    user = response.data
    print(user)
    return user

def search_all_tweets(client, query):
    # https://docs.tweepy.org/en/stable/client.html#tweepy.Client.search_all_tweets
    response = client.search_recent_tweets(query=query, tweet_fields=["created_at", "public_metrics"])
    print(type(response.data))
    tweets = response.data
    print(len(tweets))
    for tweet in tweets:
        print(tweet.text)
        print(tweet.created_at)
        print(tweet.public_metrics)
        print("----")
    return tweets

if __name__ == "__main__":
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    fetch_user_account_info(client, "elonmusk")
