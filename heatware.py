import sys, os
from ConfigParser import SafeConfigParser
import logging
import praw
import re

# load config file
containing_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
cfg_file = SafeConfigParser()
path_to_cfg = os.path.join(containing_dir, 'config.cfg')
cfg_file.read(path_to_cfg)

#configure logging
logging.basicConfig(level=getattr(logging, cfg_file.get('logging', 'level')))

reddit_username = cfg_file.get('reddit', 'username')
logging.info('Logging in as /u/'+reddit_username)
r = praw.Reddit(user_agent=cfg_file.get('reddit', 'user_agent'))
r.login(cfg_file.get('reddit', 'username'), cfg_file.get('reddit', 'password'))
subreddit = cfg_file.get('reddit', 'subreddit')
submission = r.get_submission(submission_id='1nf8xp')

flat_comments = praw.helpers.flatten_tree(submission.comments)

for comment in flat_comments:

	if comment.is_root == True:

		url = re.findall('http[s]?://heatware.com/eval.php?id=[0-9][0-9][0-9][0-9][0-9][0-9]', comment.body)

		print url
