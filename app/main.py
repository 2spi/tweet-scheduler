from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import gspread
app = Flask(__name__)

# gspread authentication, gsheet-credentials.json stores google service account credentials
gc = gspread.service_account(filename='gsheet-credentials.json')
sh = gc.open_by_key('1nQ1EjWsjd4Cr_Ixlyijvu0-fXDcjbcbaj9DLDoyC__k')
worksheet = sh.sheet1

# content = content of the tweet, time = scheduled time for the tweet, status = 0 for posted 1 for int queue, row_idx = row in the google sheet
class Tweet:
    def __init__(self, content, time, status, row_idx):
        self.content = content
        self.time = time
        self.status = status
        self.row_idx = row_idx

# to check if input time is in the correct format and to return datetime object
def get_date_time(date_time_str):
    date_time_obj = None
    error_code = None
    try:
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        error_code = f'Error! {e}'

    if date_time_obj is not None:
        cur_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        if date_time_obj < cur_time:
            error_code = "Invalid time."
    
    return date_time_obj, error_code

# home page, used gspread to get all records from the sheet, store in a list
@app.route("/")
def tweet_list():
    tweet_records = worksheet.get_all_records()
    tweets = []
    for idx, tweet in enumerate(tweet_records, start=2):
        tweet = Tweet(**tweet, row_idx=idx)
        tweets.append(tweet)

    tweets.reverse()
    n_open_tweets = sum(1 for tweet in tweets if not tweet.status)
    return render_template('index.html', tweets=tweets, n_open_tweets=n_open_tweets)

# add a new tweet into the queue, input from form, also appended into the google sheet
@app.route("/tweet", methods=['POST'])
def add_tweet():
    content = request.form['content']
    if not content:
        return "ERROR! No content added for the tweet."
    
    time = request.form['time']
    if not time:
        return "Please enter a time for the tweet to be posted."

    date_time_obj, error_code = get_date_time(time)
    if error_code is not None:
        return error_code
    
    new_tweet = [str(date_time_obj), content, 0]
    worksheet.append_row(new_tweet)
    return redirect('/')

# delete a tweet from the record
@app.route("/delete/<int:row_idx>")
def delete_tweet(row_idx):
    worksheet.delete_rows(row_idx)
    return redirect('/')