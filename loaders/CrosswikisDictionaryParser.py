#!/usr/bin/env python
"""
http://googleresearch.blogspot.com/2012/05/from-words-to-concepts-and-back.html

This script loads data from the dictionary file into mongo:

http://www-nlp.stanford.edu/pubs/crosswikis-data.tar.bz2/dictionary.bz2

Here's an example line:

"Maine\t0.716553 Maine D W:22581/27409 W08 W09 WDB Wx:13813/15925 c d dc:0 dl:0/1 ds:1 dt:0/5 p t w:7537/8534 w':764/10507 x"

Corresponding line from the inv.dict file:

Maine   0.461444 Maine  W:22581/41237 Wx:13813/46647 w:7537/7776 w':764/1199

Note: I'm pretty sure that the descriptions in the README regarding the rationals
are wrong, and that what is presented for the dictionary file is actually for the
inv.dict file.
http://www-nlp.stanford.edu/pubs/crosswikis-data.tar.bz2/READ_ME.txt

Typical usage:

python load_google_crosswikis_dictionary.py ../dictionary
"""

import sys
import re
import codecs
import argparse
import urllib2

import pymongo

class CrosswikisDictionaryParser():


    line_patt = re.compile("^(.*)\t(\S+) (\S+) .*$")
    count_patt = re.compile(r"\b(w'|w|W|Wx):(\d+)\/(\d+)\b")

    insertion_errors = []

    def __init__(self, min_concept_prob=0.001, min_form_count=100, coll=None):

        self.min_concept_prob = min_concept_prob
        self.min_form_count = min_form_count

        if coll:
            self.coll = coll
        else:
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = client.concepts
            self.coll = db.crosswiki_dictionary

    def parse(self, dictionary_file):
        """Parses the dictionary file and loads it into Mongo"""

        self.lines = 0
        self.matching_lines = 0
        self.non_matching_lines = 0

        last_form = None
        concepts = []
        form_counts = {}

        self.insertion_errors = []

        with codecs.open(dictionary_file, 'r', encoding='utf8', errors='ignore') as fp:
            for line in fp:

                self.lines += 1
                if self.lines % 10000 == 0:
                    print self.lines
                    print line

                match = self.line_patt.match(line)
                if match:

                    self.matching_lines += 1
                    form = match.groups()[0]

                    if last_form != None and form != last_form:
                        total_count = sum(form_counts.values())
                        form_counts['total'] = total_count
                        yield((last_form, form_counts, concepts))
                        concepts = []
                        form_counts = {}
                    last_form = form

                    prob = float(match.groups()[1])
                    unicode_concept = match.groups()[2]
                    concept = urllib2.unquote(unicode_concept.encode('utf8'))

                    if prob > self.min_concept_prob:
                        counts = self.get_counts(line)
                        counts_dict = dict([(key, num) for key, num, den in counts])
                        concepts.append({'prob': prob, 'id': concept, 'counts': counts_dict})

                        for key, num, den in counts:
                            form_counts[key] = den

                else:
                    self.non_matching_lines += 1
                    print "Non-matching line:", line

            total_count = sum(form_counts.values())
            form_counts['total'] = total_count
            yield((last_form, form_counts, concepts))


    def load_all(self, dictionary_file):

        for last_form, form_counts, concepts in self.parse(dictionary_file):

            self.insert(last_form, form_counts, concepts)


    def insert(self, form, counts, concepts):
        print "insert", form
        print counts
        print concepts
        print "self.min_form_count", self.min_form_count
        if counts['total'] > self.min_form_count:
            print "yes bigger"
            try:
                print 'trying'
                res = self.coll.insert({'_id': form, 'counts': counts, 'concepts': concepts})
                print 'tried'
                print 'res', res

            except pymongo.errors.DuplicateKeyError as error:
                print "ERROR"
                print error
                print
                self.insertion_errors.append(error)



    def get_counts(self, line):
        return [ (key, int(num), int(den)) for key, num, den in self.count_patt.findall(line) ]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Process the Google crosswiki dictionary file and load into Mongo')
    parser.add_argument('dictionary_file', metavar='dictionary_file', type=str,
        help='path to the crosswiki dictionary file')
    args = parser.parse_args()
    dp = CrosswikisDictionaryParser()
    dp.load_all(args.dictionary_file)
