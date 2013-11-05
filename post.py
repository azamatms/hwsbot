import praw
import time


month=time.strftime('%B')

r = praw.Reddit(user_agent='/r/hardwareswap bot')
r.login('hwsbot', 'vuF*reddit')
r.submit('hardwareswap','%s Confirmed Trade Thread' % month, text='Post your confirmed trades below, this post will be edited in the future.')
r.send_message('/r/hardwareswap', 'New Trade Thread', 'A new trade thread has been posted for the month, please update the sidebar and lock the previous thread.')
