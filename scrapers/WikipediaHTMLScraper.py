#!/usr/bin/env python
"""
Prune the crosswikis dictionary file to only include those above a certain
probability.
"""

import re
import sys
import os
import datetime
import codecs
import argparse
import requests
import urllib2

import pymongo

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from loaders import DBPediaTitlesParser
from util import is_meta

class WikipediaHTMLScraper():

    def __init__(self, coll=None):

        if coll:
            self.coll = coll
        else:
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = client.wikipedia
            self.coll = db.articles

    html_url = 'http://en.wikipedia.org/w/index.php?action=render&title='

    def request_page_html(self, title):
        res = requests.get(self.html_url + title)

        if not res.ok:
            return None
        else:
            return res.content

    def request_and_store_page(self, title):
        """Download and store a wikipedia page, overwriting the existing if there
        already is one.
        """
        html = self.request_page_html(title)
        if not html:
            self.coll.insert(
                {'_id': title,
                 'error': True,
                 'updated': datetime.datetime.utcnow()})
        else:
            self.coll.insert(
                {'_id': title,
                 'html': html,
                 'error': False,
                 'updated': datetime.datetime.utcnow()})

    def get_or_request_page(self, title):
        """Check mongo first, otherwise go to wikipedia API for page"""

        res = coll.find({'_id': title})

        if res and not res['error']:
            return res['html']
        else:
            return self.request_and_store_page(title)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Scrape HTML from the Wikipedia api')
    parser.add_argument('title_file', type=str,
        help='path to a list of headwords')
    args = parser.parse_args()

    ws = WikipediaHTMLScraper()
    dp = DBPediaTitlesParser.DBPediaTitlesParser()

    titles = dp.parse_file(args.title_file)

    i = 0

    for title, display in titles:
        i += 1
        if i % 10 == 0:
            print i, title, display, is_meta(title)
        if not is_meta(title):
            ws.request_and_store_page(title)

