import tweepy
consumer_key = "iTgGukoBAPecLL5awvC0b7jp7"
consumer_secret = "2jXCBmYLBSubcXtCljbSP1eBfsUbeFgUlsclswt8tQ5Gn4DDXf"
access_token = "1166697426318757888-QBNkGhVY8bqeycxRulTLYAiZrhnN1m"
access_token_secret = "d0zLEPH8ZqNSePfyaZqIpCEHp7CfdJh04u7V3lscRh2ev"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

u1 = api.get_user("CNN")

for page in tweepy.Cursor(api.user_timeline, id = u1.id).pages(1):
    for item in page:
        if item.in_reply_to_user_id_str == u1.id_str:
            last_tweet = item
            while True:
                print(last_tweet.text)
                prev_tweet = api.get_status(last_tweet.in_reply_to_status_id_str)
                last_tweet = prev_tweet
                if not last_tweet.in_reply_to_status_id_str:
                    break
