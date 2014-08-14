#!/usr/bin/env python
"""
http://wiki.dbpedia.org/Downloads32

http://downloads.dbpedia.org/3.9/en/geo_coordinates_en.nt.bz2

Parse the geodata information from DBPedia
"""

import sys
import re
import codecs
import argparse
import urllib

from pymongo import MongoClient

class DBPediaGeoParser():

    client = MongoClient('mongodb://localhost:27017/')
    db = client.dbpedia
    coll = db.geo

    line_patt = re.compile("""^<http://dbpedia.org/resource/(.*)> <http://www.georss.org/georss/point> "(.*) (.*)"@en .$""")

    def parse(self, geo_file):

        lines = 0
        matching_lines = 0
        non_matching_lines = 0

        with codecs.open(geo_file, 'r', encoding='utf8', errors='ignore') as fp:
            for line in fp:

                lines += 1
                if lines % 10000 == 0:
                    print lines
                    print line

                match = self.line_patt.match(line)
                if match:
                    unicode_concept = match.groups()[0]
                    # It's 2014 and urllib/urllib2 don't work on unicode?
                    concept = urllib.unquote(unicode_concept.encode('utf8'))
                    lat = float(match.groups()[1])
                    lon = float(match.groups()[2])
                    self.coll.insert({'_id': concept, 'lat': lat, 'lon': lon})
                else:
                    non_matching_lines += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Process the DBPedia geo info file')
    parser.add_argument('geo_file', metavar='geo_file', type=str,
        help='path to the DBPedia geo file')
    args = parser.parse_args()
    glp = DBPediaGeoParser()
    glp.parse(args.geo_file)
