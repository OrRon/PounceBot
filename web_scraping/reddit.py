#!/usr/bin/python
import praw
import json
import pandas as pd
from OpenAIClient import OpenAIClient

# Reddit API credentials
creds = json.loads(open('/home/lsaddan/keys/reddit.json').read())
client_id = creds['client_id']
client_secret = creds['secret']
user_agent = 'user_agent'

# Create a Reddit instance
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

# Define the subreddit you want to search in
subreddit_name = 'devops'
subreddit = reddit.subreddit(subreddit_name)

# Define the search query
search_query = 'Vault'

# Perform the search
search_results = subreddit.search(search_query, limit=100)  # Change the limit as needed
#search_results = pd.read_csv('out.csv')

prompt = json.load(open('prompts/reddit.json'))
chat = OpenAIClient(prompt)

# Print the search results
results = []
for submission in search_results:

    results.append(
        {
          'title': submission.title,
          'relevant': chat.is_description_related(submission.selftext),
          'url': submission.url,
          'selftext': submission.selftext,
        }
    )

    
    if False:
        submission.comments.replace_more(limit=None)  # Retrieve all comments, including nested ones
        for comment in submission.comments.list():
            print('Comment:', comment.body)
print(results)
df = pd.DataFrame(results, columns=['title', 'relevant', 'url', 'selftext'])
df.to_csv('out.csv')
