import praw
import time


month=time.strftime('%B')

subreddit = 'softwareswap'

r = praw.Reddit(user_agent='hwsbot')
r.login('hwsbot', 'vuF*reddit')
r.submit(subreddit,'%s Confirmed Trade Thread' % month, text='Post your confirmed trades below, this post will be edited in the future.')
r.send_message('/r/'+subreddit, 'New Trade Thread', 'A new trade thread has been posted for the month, please update the sidebar and lock the previous thread.')
