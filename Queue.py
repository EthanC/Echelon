import datetime
import json
import os
import sys
import time

import praw
import requests

# Load Configuration
try:
    with open("config.json", "r") as configFile:
        config = json.load(configFile)

    clientID = config["credentials"]["clientID"]
    clientSecret = config["credentials"]["clientSecret"]
    username = config["credentials"]["username"]
    password = config["credentials"]["password"]
    userAgent = config["credentials"]["userAgent"]
    interval = config["interval"]
    subreddits = config["subreddits"]
    webhookAvatarURL = config["webhook"]["avatarURL"]
    embedColor = config["webhook"]["embedColor"]
    webhookURL = config["webhook"]["url"]
    webhookUsername = config["webhook"]["username"]
except Exception as e:
    print(e)

# Initialize Reddit Instance
try:
    reddit = praw.Reddit(client_id=clientID, client_secret=clientSecret,
                         user_agent=userAgent, username=username, password=password)
except Exception as e:
    print(e)

# Initialize Fields list for EmbedBuilder()
fields = []


# Get Mod Queue for the specified Subreddit
# Returns total submissions in Queue
def GetModqueue(subreddit):
    try:
        count = 0

        for submission in reddit.subreddit(subreddit).mod.modqueue(limit=None):
            count = count + 1

        # Reddit Queues are limited to 1,000 Submissions.
        # However, when the Queue is full (1,000) the API
        # tends to return in the 990's despite being at 1,000.
        if count > 990:
            return "1,000"
        else:
            return count
    except Exception as e:
        print(f"{e}\nSubmission: {submission}")


# Get Unmoderated Queue for the specified Subreddit
# Returns total submissions in Queue
def GetUnmoderated(subreddit):
    try:
        count = 0

        for submission in reddit.subreddit(subreddit).mod.unmoderated(limit=None):
            count = count + 1
        
        # Reddit Queues are limited to 1,000 Submissions.
        # However, when the Queue is full (1,000) the API
        # tends to return in the 990's despite being at 1,000.
        if count > 990:
            return "1,000"
        else:
            return count
    except Exception as e:
        print(f"{e}\nSubmission: {submission}")


# Add a Field to the Fields list
# Call EmbedBuilder() using Fields list once it is equal in length to the Subreddits list
def FieldsBuilder(field):
    try:
        fields.append(field)

        if len(fields) == len(subreddits):
            EmbedBuilder(fields)
    except Exception as e:
        print(e)


# Build a Discord Embed object
# Call Notify() using the Embed object
def EmbedBuilder(fields):
    try:
        timestamp = datetime.datetime.utcnow().isoformat()
        color = int(embedColor, base=16)
        fields = fields

        embed = [{"color": color, "fields": fields, "timestamp": timestamp}]

        Notify(embed)
    except Exception as e:
        print(e)


# POST to the Discord Webhook specified in config
# Reset the Fields list
def Notify(embed):
    try:
        payload = {"username": webhookUsername,
                   "avatar_url": webhookAvatarURL, "embeds": embed}
        headers = {"content-type": "application/json"}
        response = requests.post(
            webhookURL, data=json.dumps(payload), headers=headers).text

        fields.clear()
    except Exception as e:
        print(f"{e}\n{response}")


# Once authenticated with Reddit, begin to examine queues for each Subreddit listed in config
# Call FieldsBuilder() using the queue results
# Sleep for the interval specified in config, repeat
def main():
    while reddit.read_only == False:
        for subreddit in subreddits:
            try:
                modqueue = GetModqueue(subreddit)
                unmoderated = GetUnmoderated(subreddit)

                print(
                    f"/r/{subreddit} - Mod Queue: {modqueue}, Unmoderated Queue: {unmoderated}")
                FieldsBuilder(
                    {"name": f"/r/{subreddit}", "value": f"Mod Queue: {modqueue}\nUnmoderated Queue: {unmoderated}", "inline": False})
            except Exception as e:
                print(e)
        print(f"Queues fetched! Sleeping for {interval}s...\n")
        time.sleep(interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as e:
        print(e)
