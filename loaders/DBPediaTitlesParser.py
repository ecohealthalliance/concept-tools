#!/usr/bin/env python
"""
Parse the DBPedia article titles file.

A sample line is:

<http://dbpedia.org/resource/Analysis_of_variance> <http://www.w3.org/2000/01/rdf-schema#label> "Analysis of variance"@en .
"""

import sys
import re
import codecs
import argparse
import urllib2

import pymongo

class DBPediaTitlesParser():

    line_patt = re.compile("""^<http://dbpedia.org/resource/(.*)> <http://www.w3.org/2000/01/rdf-schema#label> "(.*)"@en .$""")

    errors = []


    def parse_line(self, line):

        match = self.line_patt.match(line)

        if match:
            _id = match.groups()[0]
            display = match.groups()[1]
            return (_id, display)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Process the Google crosswiki dictionary file and load into Mongo, or prune file to only useful lines')
    parser.add_argument('title_file', type=str,
        help='path to the file containing the DBPedia dump of WP article titles')
    args = parser.parse_args()

    dp = DBPediaTitlesParser()

    for _id, display in dp.parse_file(args.title_file):
        print _id, ' :: ', display
