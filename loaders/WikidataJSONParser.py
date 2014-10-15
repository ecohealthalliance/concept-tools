#!/usr/bin/env python
"""


"""

import codecs
import argparse
import pymongo
import json

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

        with codecs.open(wikidata_json_file, 'r', encoding='utf8', errors='ignore') as fp:
            for line in fp:

                if lines > 0:
                    obj = json.loads(line.replace(',\n', ''))

                    try:
                        print "x:", obj['claims']['P625']
                        print
                    except KeyError:
                        pass

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
                                    print article, lat, lon
                                    yield (article, lat, lon)

                lines += 1


    def load_all(self, wikidata_json_file):

        for article, lon, lat in self.parse(wikidata_json_file):
            print
            self.insert(article, lat, lon)

    def insert(self, article, lat, lon):
        self.coll.insert( { '_id': article, 'lat': lat, 'lon': lon } )

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=
        'Process the Wikidata json dump and load facts of interest')

    # wikidata_json_file
    parser.add_argument('wikidata_json_file', type=str,
        help='path to the Wikidata json file')

    args = parser.parse_args()

    dp = WikidataJSONParser()
    dp.load_all(args.wikidata_json_file)
