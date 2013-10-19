import sys, os
import praw
from ConfigParser import SafeConfigParser

# load config file
containing_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
cfg_file = SafeConfigParser()
path_to_cfg = os.path.join(containing_dir, 'config.cfg')
cfg_file.read(path_to_cfg)

r = praw.Reddit(user_agent=cfg_file.get('reddit', 'user_agent'))
r.login(cfg_file.get('reddit', 'username'), cfg_file.get('reddit', 'password'))
subreddit = cfg_file.get('reddit', 'subreddit')
submission = r.get_submission(submission_id=cfg_file.get('reddit', 'link_id'))

flat_comments = praw.helpers.flatten_tree(submission.comments)

for comment in flat_comments:

	if comment.body == 'second' and comment.is_root == False:

		parent_comment = [com for com in flat_comments if com.fullname == comment.parent_id][0]

		if comment.author_flair_css_class or comment.author_flair_text:
			child_css = str(int(comment.author_flair_css_class) + 1)
			child_text = comment.author_flair_text
		elif not comment.author_flair_css_class:
			child_css = '1'
		elif not comment.author_flair_text:
			child_text = 'Empty'
			

		if parent_comment.author_flair_css_class or parent_comment.author_flair_text:
			parent_css = str(int(parent_comment.author_flair_css_class) + 1)
			parent_text = parent_comment.author_flair_text
		elif not parent_comment.author_flair_css_class:
			parent_css = '1'
		elif not parent_comment.author_flair_text:
			parent_text = 'Empty'

		comment.subreddit.set_flair(comment.author, child_text, child_css)
		comment.author_flair_css_class = child_css
		print 'Changed Child CSS'
		parent_comment.subreddit.set_flair(parent_comment.author, parent_text, parent_css)
		parent_comment.author_flair_css_class = parent_css
		print 'Changed Parent CSS'