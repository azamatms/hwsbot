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
username = cfg_file.get('reddit', 'username')
password = cfg_file.get('reddit', 'password')
multiprocess = cfg_file.get('reddit', 'multiprocess')

#configure logging
logging.basicConfig(level=logging.INFO, filename='actions.log')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)


def main():
	while True:
		try:
			logging.info('Logging in as /u/'+username)
			if multiprocess == 'true':
				handler = MultiprocessHandler()
				r = praw.Reddit(user_agent=username, handler=handler)
			else:
				r = praw.Reddit(user_agent=username)
			r.login(username, password)
			subreddit = cfg_file.get('reddit', 'subreddit')


			# Get the submission and the comments
			submission = r.get_submission(submission_id='1nf8xp')
			submission.replace_more_comments(limit=None, threshold=0)
			flat_comments = list(praw.helpers.flatten_tree(submission.comments))

			for comment in flat_comments:

				if not hasattr(comment, 'author'):
					continue
				if comment.is_root == True:
					heatware = re.search('(http://(?:www\.)?heatware\.com/eval\.php\?id=\d{1,7})', comment.body)
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
		except Exception as e:
			logging.error(e)
			break

if __name__ == '__main__':
	main()