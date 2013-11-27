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
logging.basicConfig(level=logging.INFO, filename='actions.log')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)


def main():
	while True:
		try
			reddit_username = cfg_file.get('reddit', 'username')
			logging.info('Logging in as /u/'+reddit_username)
			r = praw.Reddit(user_agent=cfg_file.get('reddit', 'user_agent'))
			r.login(cfg_file.get('reddit', 'username'), cfg_file.get('reddit', 'password'))
			subreddit = cfg_file.get('reddit', 'subreddit')


			# Get the submission and the comments
			submission = r.get_submission(submission_id='1nf8xp')
			submission.replace_more_comments(limit=None, threshold=0)
			flat_comments = list(praw.helpers.flatten_tree(submission.comments))

			for comment in flat_comments:

				if not hasattr(comment, 'author'):
					continue
				if comment.is_root == True:
					heatware = re.search('(http://(?:www\.)?heatware\.com/eval\.php\?id=\d{5,7})', comment.body)
					if heatware:
						url = heatware.group(0)
						if not comment.author_flair_text:
							if comment.author_flair_css_class:
								comment.subreddit.set_flair(comment.author, url, comment.author_flair_css_class)
							else:
								comment.subreddit.set_flair(comment.author, url, '')
							comment.reply('added')
			logging.info('Sleeping for 10 minutes')
			sleep(600)
		except:
			logging.info('I\'ve made a huge little mistake...')

if __name__ == '__main__':
	main()