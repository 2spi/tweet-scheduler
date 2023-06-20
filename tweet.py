import gspread
import tweepy
import time
import logging
from os import environ
from dotenv import load_dotenv
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# tweepy client authentication, api keys in dotenv file
client = tweepy.Client(
    consumer_key=environ["CONSUMER_KEY"],
    consumer_secret=environ["CONSUMER_SECRET"],
    access_token=environ["ACCESS_TOKEN"],
    access_token_secret=environ["ACCESS_SECRET"]
)

# gspread authentication
gc = gspread.service_account(filename='gsheet-credentials.json')
sh = gc.open_by_key('1nQ1EjWsjd4Cr_Ixlyijvu0-fXDcjbcbaj9DLDoyC__k')
worksheet = sh.sheet1

# INTERVAL = time interval at which the script checks the sheet
INTERVAL = int(environ['INTERVAL'])
DEBUG =  environ['DEBUG'] == '1'

def main():
    while True:
        tweet_records = worksheet.get_all_records()
        cur_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        logger.info(f'{len(tweet_records)} tweets found at {cur_time.time()}')
        time.sleep(INTERVAL)

        for idx, tweet in enumerate(tweet_records, start=2):
            content = tweet['content']
            time_str = tweet['time']
            status = tweet['status']
            date_time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

            # if status = 0 and scheduled time is passed, then tweet posted
            if not status:
                c_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
                if date_time_obj < c_time:
                    try:
                        client.create_tweet(text=content)
                        worksheet.update_cell(idx, 3, 1)
                    except Exception as e:
                        logger.warning(f'Exception during tweet! {e}')


if __name__ == '__main__':
    main()