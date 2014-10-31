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
import BeautifulSoup

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from loaders import DBPediaTitlesParser
from util import is_meta
from util import get_canonical_id_from_url_segment

class WikipediaCategoryScraper():

    html_url = 'http://en.wikipedia.org/w/index.php?action=render&title=Category:'

    category_pat = re.compile('(?:.*en.wikipedia.org)?/wiki/Category:(.*)$')
    article_pat = re.compile('(?:.*en.wikipedia.org)?/wiki/(.*)$')

    def request_category_page_html(self, category):
        url = self.html_url + category
        print "\nurl:", url
        res = requests.get(url)

        if not res.ok:
            return None
        else:
            return res.content

    def get_subcategories_and_articles(self, html):

        subcategories, articles = self.get_subcategories_and_articles_with_forms(html)

        formless_subcategories = [ subcategory[0] for subcategory in subcategories ]
        formless_articles = [ article[0] for article in articles ]

        return (formless_subcategories, formless_articles)

    def get_subcategories_and_articles_with_forms(self, html):

        subcategories = set()
        articles = set()

        for link in BeautifulSoup.BeautifulSoup(html).findAll('a'):
            href = link.get('href')
            print "link", link
            print 'href', href
            if href:
                category_match = self.category_pat.match(href)
                if category_match:
                    category_id = get_canonical_id_from_url_segment( category_match.groups()[0] )
                    form = link.text
                    subcategories.add( (_id, form) )
                else:
                    article_match = self.article_pat.match(href)
                    if article_match:
                        article_id = get_canonical_id_from_url_segment( article_match.groups()[0] )
                        form = form = link.text
                        if not is_meta(article_id):
                            articles.add( (article_id, form) )

        return (subcategories, articles)

    def get_all_subcategories_and_articles(self, category, level=3):

        html = self.request_category_page_html(category)

        subcategories, articles = self.get_subcategories_and_articles(html)
        unchecked_subcategories = set()
        checked_subcategories = set()
        for subcategory in subcategories:
            if self.query_subcategory(subcategory):
                unchecked_subcategories.add(subcategory)
            else:
                checked_subcategories.add(category)

        while len(unchecked_subcategories):

            subcategory = unchecked_subcategories.pop()
            print "doing sc:", subcategory
            checked_subcategories.add(subcategory)

            subcategory_html = self.request_category_page_html(subcategory)

            if subcategory_html:

                new_subcategories, new_articles = self.get_subcategories_and_articles(subcategory_html)

                unseen_subcategories = new_subcategories.difference(checked_subcategories)

                for unseen_subcategory in unseen_subcategories:

                    if self.query_subcategory(unseen_subcategory):
                        unchecked_subcategories.add(unseen_subcategory)
                    else:
                        checked_subcategories.add(category)

                unchecked_subcategories = unchecked_subcategories.union(unseen_subcategories)
                articles = articles.union(new_articles)

                print "New subcategories from:", subcategory
                print unseen_subcategories
                print
                subcategories = subcategories.union(new_subcategories)

        return subcategories, articles

    def query_subcategory(self, subcategory):
        print subcategory, ': y[n]'
        char = raw_input()
        if char == 'y' or char == '':
            return True
        else:
            return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Get all articles and from a category and its subcategories')
    parser.add_argument('category', type=str,
        help='initial category to start with')
    args = parser.parse_args()

    ws = WikipediaCategoryScraper()

    subcategories, articles = ws.get_all_subcategories_and_articles(args.category)

    for subcategory in subcategories:
        print subcategory

    print

    for article in articles:
        print article
