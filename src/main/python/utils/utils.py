import requests
import re


def verify_url(link):
    request = requests.get(link)
    if request.status_code == 200:
        return True
    else:
        return False


def verify_spelling(text):
    # noinspection All
    regex = re.compile(r'^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+')
    return re.match(regex, text) is not None
