import sys, os
from ConfigParser import SafeConfigParser
import logging
import praw
from praw.handlers import MultiprocessHandler
import datetime
from datetime import datetime, timedelta

# load config file
containing_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
cfg_file = SafeConfigParser()
path_to_cfg = os.path.join(containing_dir, 'config.cfg')
cfg_file.read(path_to_cfg)

#configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', filename='actions.log')

username = cfg_file.get('reddit', 'username')
password = cfg_file.get('reddit', 'password')
subreddit = cfg_file.get('reddit', 'subreddit')
link_id = cfg_file.get('reddit', 'link_id')

with open (subreddit+".id.txt", 'r') as myfile:
	completed = myfile.read()

# Log in
logging.info('Logging in as /u/'+username)
handler = MultiprocessHandler()
r = praw.Reddit(user_agent=username)
r.login(username, password)

# Get the submission and the comments
submission = r.get_submission(submission_id=link_id)
submission.replace_more_comments(limit=None, threshold=0)
flat_comments = list(praw.helpers.flatten_tree(submission.comments))

for comment in flat_comments:
	
	content = comment.body

	if comment.id in completed:
		continue
	if not hasattr(comment.author, 'name'):
		continue
	if 'confirm' not in content.lower():
		continue
	if comment.author.name == username:
		continue
	if comment.is_root == True:
		continue

	parent = [com for com in flat_comments if com.fullname == comment.parent_id][0]
	child_date = datetime.utcfromtimestamp(comment.author.created_utc)
	child_age = (datetime.utcnow() - child_date).days
	parent_date = datetime.utcfromtimestamp(parent.author.created_utc)
	parent_age = (datetime.utcnow() - parent_date).days
	child_karma = comment.author.link_karma + comment.author.comment_karma
	parent_karma = parent.author.link_karma + parent.author.comment_karma
	child_css = comment.author_flair_css_class
	parent_css = parent.author_flair_css_class

	if comment.author.name == parent.author.name:
		comment.reply('You have confirmed a trade under your own post, this action has been reported to the Moderators')
		comment.report()	
		parent.report()
		myfile.write('%s\n' % comment.id)
	if child_age < 14 and child_css < 1:
		comment.reply('Your account has been created recently, this has been sent for further review')
		comment.report()
		myfile.write('%s\n' % comment.id)
	if parent_age < 14 and parent_css < 1:
		parent.reply('Your account has been created recently, this has been sent for further review')
		parent.report()
		myfile.write('%s\n' % comment.id)
	if child_karma < 10 and child_css < 1:
		comment.reply('You do not have enough karma, this has been sent for further review')
		comment.report()
		myfile.write('%s\n' % comment.id)
	if parent_karma < 10 and child_css < 1:
		parent.reply('You do not have enough karma, this has been sent for further review')
		parent.report()
		myfile.write('%s\n' % comment.id)

	# Child Flair CSS
	if not comment.author_flair_css_class:
		child_css = '1'
	elif comment.author_flair_css_class and 'mod' in comment.author_flair_css_class:
		child_css = comment.author_flair_css_class
	else:
		child_css = str(int(comment.author_flair_css_class) + 1)
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

	# Flairs up in here
	if child_css != 'mod':
		comment.subreddit.set_flair(comment.author, child_text, child_css)
		logging.info('Set flair for '+comment.author.name, 'to '+child_css)
	if parent_css != 'mod':
		parent.subreddit.set_flair(parent.author.name, parent_text, parent_css)
		logging.info('Set flair for '+parent.author.name, 'to '+parent_css)

	comment.reply('added')

	for com in flat_comments:
		if hasattr(com.author, 'name'):
			if com.author.name == comment.author.name:
				com.author_flair_css_class = child_css
			if com.author.name == parent.author.name:
				com.author_flair_css_class = parent_css
	
	with open (subreddit+".id.txt", 'a') as myfile:
		myfile.write('%s\n' % comment.id)