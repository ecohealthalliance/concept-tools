#!/usr/bin/env python
"""
http://wiki.dbpedia.org/Downloads32

http://downloads.dbpedia.org/3.2/links/links_geonames_en.nt.bz2

Parse the links between DBPedia resources (same as Wikipedia URL segments)
and geoname ids.
"""

import sys
import re
import codecs
import argparse
import urllib2

from pymongo import MongoClient

class GeonameLinksParser():

    client = MongoClient('mongodb://localhost:27017/')
    db = client.dbpedia
    coll = db.geoname_links

    line_patt = re.compile("^<http://dbpedia.org/resource/(.*)> <http://www.w3.org/2002/07/owl#sameAs> <http://sws.geonames.org/(.*)/> .$")

    def parse(self, inv_dict_file):

        lines = 0
        matching_lines = 0
        non_matching_lines = 0

        with codecs.open(inv_dict_file, 'r', encoding='utf8', errors='ignore') as fp:
            for line in fp:
                print 'type(line)', type(line)
                lines += 1
                if lines % 1000 == 0:
                    print lines
                    print line

                match = self.line_patt.match(line)
                if match:
                    unicode_concept = match.groups()[0]
                    concept = urllib2.unquote(unicode_concept.encode('utf8'))
                    geoname_id = long(match.groups()[1])
                    self.coll.insert({'_id': concept, 'geoname_id': geoname_id})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Process the links_geonames file from DBPedia and load into Mongo')
    parser.add_argument('links_geonames_file', metavar='links_geonames_file', type=str,
        help='path to the links_geonames file')
    args = parser.parse_args()
    glp = GeonameLinksParser()
    glp.parse(args.links_geonames_file)
