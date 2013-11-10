import sys, os
from ConfigParser import SafeConfigParser
import logging
import praw
import datetime
from datetime import datetime, timedelta

# load config file
containing_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
cfg_file = SafeConfigParser()
path_to_cfg = os.path.join(containing_dir, 'config.cfg')
cfg_file.read(path_to_cfg)

#configure logging
logging.basicConfig(level=getattr(logging, cfg_file.get('logging', 'level')))

username = cfg_file.get('reddit', 'username')
password = cfg_file.get('reddit', 'password')
print 'Logging in as /u/'+username
r = praw.Reddit(user_agent=cfg_file.get('reddit', 'user_agent'))
r.login(username, password)
subreddit = cfg_file.get('reddit', 'subreddit')
submission = r.get_submission(submission_id=cfg_file.get('reddit', 'link_id'))

with open ("id.txt", "r") as myfile:
    completed=myfile.read()

submission.replace_more_comments(limit=None, threshold=0)
flat_comments = list(praw.helpers.flatten_tree(submission.comments))

for comment in flat_comments:
	
	content = comment.body

	if 'confirm' in content.lower() and comment.is_root == False and comment.id not in completed and comment.author.name != 'hwsbot':

		parent = [com for com in flat_comments if com.fullname == comment.parent_id][0]
		account_date = datetime.utcfromtimestamp(comment.author.created_utc)
		account_age = (datetime.utcnow() - account_date).days

		# Flair Flair CSS
		if not comment.author_flair_css_class:
			child_css = '1'
		elif comment.author_flair_css_class and 'mod' in comment.author_flair_css_class:
			child_css = comment.author_flair_css_class
		else:
			child_css = str(int( comment.author_flair_css_class) + 1)
		# Child Flair Text
		if not comment.author_flair_text:
			child_text = ''
		else:
			child_text = comment.author_flair_text

		# Parent Flair CSS
		if not parent.author_flair_css_class:
			parent_css = '1'
		elif parent.author_flair_css_class and 'mod' in parent.author_flair_css_class:
			parent_css = parent.author_flair_css_class
		else:
			parent_css = str(int(parent.author_flair_css_class) + 1)
		# Parent Flair Text
		if not parent.author_flair_text:
			parent_text = ''
		else:
			parent_text = parent.author_flair_text

		# Prevent users from confirming under their own comments
		if comment.author.name == parent.author.name:
			comment.reply('You have confirmed a trade under your own post, this action has been reported to the Moderators')
			comment.report()	
			parent.report()

		if account_age < 14:
			comment.reply('Your account has been created recently and has been reported to the moderators')
			comment.report()

		# The regular actions
		else:
			comment.subreddit.set_flair(comment.author, child_text, child_css)
			for com in flat_comments:
				if com.author.name == comment.author.name:
					com.author_flair_css_class = child_css
			comment.reply('added')

			parent.subreddit.set_flair(parent.author, parent_text, parent_css)
			for com in flat_comments:
				if com.author.name == parent.author.name:
					com.author_flair_css_class = parent_css

		with open("id.txt", "a") as myfile:
 			myfile.write('%s\n' % comment.id)
