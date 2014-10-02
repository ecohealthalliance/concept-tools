#!/usr/bin/env python
"""
Parse the DBPedia categories file:

http://data.dws.informatik.uni-mannheim.de/dbpedia/2014/en/article_categories_en.nt.bz2

A sample line is:

<http://dbpedia.org/resource/Albedo> <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:Climate_forcing> .
"""

import sys
import os
import re
import codecs
import argparse
import urllib2

import pymongo

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from util import is_meta

class DBPediaCategoriesParser():

    line_patt = re.compile("""^<http://dbpedia.org/resource/(.*)> <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:(.*)> .$""")

    errors = []

    def __init__(self, coll=None):

        if coll:
            self.coll = coll
        else:
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = client.concepts
            self.concept_categories_coll = db.dbpedia_concept_categories
            self.category_concepts_coll = db.dbpedia_category_concepts

    def parse_line(self, line):

        match = self.line_patt.match(line)

        if match:
            _id = match.groups()[0]
            category = match.groups()[1]
            return (_id, category)
        else:
            return None


    def parse_all(self, titles):

        for title in titles:
            yield parse_line(title)

    def parse_file(self, filename):

        with codecs.open(filename, 'r', encoding='utf8', errors='ignore') as fp:
            for line in fp:
                res = self.parse_line(line)
                if res:
                    yield res

    def load_file(self, filename):

        i = 0

        for concept, category in self.parse_file(filename):
            if not is_meta(concept):
                i += 1
                if i % 1000 == 0:
                    print i, concept, category
                self.concept_categories_coll.update({'_id': concept}, {'$addToSet': {"categories": category}}, upsert=True)
                self.category_concepts_coll.update({'_id': category}, {'$addToSet': {"concepts": concept}}, upsert=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Process the DBPedia categories file and load into mongo')
    parser.add_argument('category_file', type=str,
        help='path to the file containing the DBPedia dump of categories')
    args = parser.parse_args()

    dp = DBPediaCategoriesParser()

    dp.load_file(args.category_file)

