import hmac
import os
import hashlib
import time
from urlparse import urlparse, urljoin
from flask import request, url_for


file = open('static/secret.txt', 'r')
SECRET = file.read()

def hash_str(s):
    return hmac.new(SECRET, s, digestmod=hashlib.sha256).hexdigest()

def get_date():
    return time.strftime("%d %b %Y")

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc