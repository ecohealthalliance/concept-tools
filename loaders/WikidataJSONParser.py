#!/usr/bin/env python
"""
Load geo location data from the wikidata JSON file:

http://dumps.wikimedia.org/other/wikidata/20141013.json.gz

"""
import sys
import os
import codecs
import argparse
import pymongo
import json

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from util import get_canonical_id_from_title

class WikidataJSONParser:


    def __init__(self, coll=None):

        if coll:
            self.coll = coll
        else:
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = client.concepts
            self.coll = db.wikidata_geo

    def get_article_name(self, obj):
        if ('sitelinks' in obj and
            'enwiki' in obj['sitelinks'] and
            'title' in obj['sitelinks']['enwiki']):
           return obj['sitelinks']['enwiki']['title']
        else:
            return None

    def parse(self, wikidata_json_file):
        """Parses the wikidata json dump"""

        lines = 0
        matching_lines = 0
        non_matching_lines = 0

        last_concept = None
        forms = []
        concept_counts = {}

        i = 0
        yielded = 0

        with codecs.open(wikidata_json_file, 'r', encoding='utf8', errors='ignore') as fp:
            for line in fp:

                i += 1

                if i % 1000 == 0:
                    print 'i', i
                    print

                if lines > 0:
                    obj = json.loads(line.replace(',\n', ''))

                    if ('claims' in obj and
                        'P625' in obj['claims']):


                        for claim in obj['claims']['P625']:

                            if ('mainsnak' in claim and
                                'datavalue' in claim['mainsnak'] and
                                claim['mainsnak']['datavalue']['type'] == 'globecoordinate'):

                                lat = claim['mainsnak']['datavalue']['value']['latitude']
                                lon = claim['mainsnak']['datavalue']['value']['longitude']
                                article = self.get_article_name(obj)

                                if article:
                                    article_id = get_canonical_id_from_title(article)
                                    yielded += 1
                                    if yielded % 100 == 0:
                                        print 'yielded:', yielded, article_id, lat, lon
                                        print
                                    yield (article_id, lat, lon)

                lines += 1


    def load_all(self, wikidata_json_file):

        for article, lon, lat in self.parse(wikidata_json_file):
            self.insert(article, lat, lon)

    def insert(self, article, lat, lon):
        try:
            self.coll.insert( { '_id': article, 'lat': lat, 'lon': lon } )
        except pymongo.errors.DuplicateKeyError:
            print "DuplicateKeyError:", article

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=
        'Process the Wikidata json dump and load facts of interest')

    # wikidata_json_file
    parser.add_argument('wikidata_json_file', type=str,
        help='path to the Wikidata json file')

    args = parser.parse_args()

    dp = WikidataJSONParser()
    dp.load_all(args.wikidata_json_file)
