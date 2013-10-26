import sys, os
import praw
from ConfigParser import SafeConfigParser
import logging

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
submission = r.get_submission(submission_id=cfg_file.get('reddit', 'link_id'))

flat_comments = praw.helpers.flatten_tree(submission.comments)

for comment in flat_comments:
	
	if 'confirm' in comment.body and comment.is_root == False:

		parent = [com for com in flat_comments if com.fullname == comment.parent_id][0]

		if comment.author_flair_text or comment.author_flair_css_class:
			child_css = str(int(comment.author_flair_css_class) + 1)
			child_text = comment.author_flair_text
		if parent.author_flair_text or parent.author_flair_css_class:
			parent_css = str(int(parent.author_flair_css_class) + 1)
			parent_text = parent.author_flair_text
		if not comment.author_flair_css_class:
			child_css = '1'
		if not comment.author_flair_text:
			child_text = ''
		if not parent.author_flair_css_class:
			parent_css = '1'
		if not parent.author_flair_text:
			parent_text = ''

		# Prevent users from confirming under their own comments
		if comment.author == parent.author:
			comment.reply('You have confirmed a trade under your own post, this action has been reported to the Moderators')
			comment.report()		
			parent.report()

		#Karma check verification
		elif comment.author.link_karma + comment.author.comment_karma < 0:
			comment.reply('You do not have enough link karma')
			comment.report()

		elif parent.author.link_karma + parent.author.comment_karma < 0:
			parent.reply('You do not have enough link karma')
			parent.report()

		# Make sure mod flair_css does not change
		elif comment.author_flair_css_class == 'mod':
			for com in flat_comments:
				if com.author == parent.author:
					com.author_flair_css_class = parent_css

		elif parent.author_flair_css_class == 'mod':
			for com in flat_comments:
				if com.author == child.author:
					com.author_flair_css_class = child_css
		
		# The regular actions
		else:
			comment.subreddit.set_flair(comment.author, child_text, child_css)
			for com in flat_comments:
				if com.author == comment.author:
					com.author_flair_css_class = child_css
			logging.info('Changed Child CSS')
			
			parent.subreddit.set_flair(parent.author, parent_text, parent_css)
			for com in flat_comments:
				if com.author == parent.author:
					com.author_flair_css_class = parent_css
			logging.info('Changed Parent CSS')