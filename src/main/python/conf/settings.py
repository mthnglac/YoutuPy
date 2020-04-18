import os

# python folder path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# log files path
DEBUG = os.path.join(BASE_DIR, 'logs', 'debug.txt')
WARNINGS = os.path.join(BASE_DIR, 'logs', 'warnings.txt')
ERRORS = os.path.join(BASE_DIR, 'logs', 'errors.txt')
FAILED_VIDEOS = os.path.join(BASE_DIR, 'logs', 'failed_videos.txt')

# regex for youtube url
regex_for_youtube_url = r'^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+'
