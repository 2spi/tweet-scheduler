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

CONSUMER_KEY = environ["CONSUMER_KEY"]
CONSUMER_SECRET = environ["CONSUMER_SECRET"]
ACCESS_TOKEN = environ["ACCESS_TOKEN"]
ACCESS_SECRET = environ["ACCESS_SECRET"]

auth = tweepy.OAuth1UserHandler(
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET
)

api = tweepy.API(auth)

gc = gspread.service_account(filename='gsheet-credentials.json')
sh = gc.open_by_key('1nQ1EjWsjd4Cr_Ixlyijvu0-fXDcjbcbaj9DLDoyC__k')
worksheet = sh.sheet1

INTERVAL = int(environ['INTERVAL'])
DEBUG =  environ['DEBUG'] == '1'

def main():
    while True:
        tweet_records = worksheet.get_all_records()
        cur_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        logger.info(f'{len(tweet_records)} tweets scheduled at {cur_time.time()}')
        time.sleep(INTERVAL)

        for idx, tweet in enumerate(tweet_records, start=2):
            content = tweet['content']
            time_str = tweet['time']
            status = tweet['status']
            date_time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

            if not status:
                c_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
                if date_time_obj < c_time:
                    try:
                        # api.update_status(content)
                        worksheet.update_cell(idx, 3, 1)
                    except Exception as e:
                        logger.warning(f'Exception during tweet! {e}')


if __name__ == '__main__':
    main()