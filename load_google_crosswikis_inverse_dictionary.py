#!/usr/bin/env python
"""
http://googleresearch.blogspot.com/2012/05/from-words-to-concepts-and-back.html

This script loads data from the inv.dict file into mongo:

http://www-nlp.stanford.edu/pubs/crosswikis-data.tar.bz2/inv.dict.bz2

Here's an example inv.dict line:

Maine   0.461444 Maine  W:22581/41237 Wx:13813/46647 w:7537/7776 w':764/1199

Corresponding line from the dictionary file:

"Maine\t0.716553 Maine D W:22581/27409 W08 W09 WDB Wx:13813/15925 c d dc:0 dl:0/1 ds:1 dt:0/5 p t w:7537/8534 w':764/10507 x"

Note: I'm pretty sure that the descriptions in the README regarding the rationals
are wrong, and that what is presented for the dictionary file is actually for the
inv.dict file.
http://www-nlp.stanford.edu/pubs/crosswikis-data.tar.bz2/READ_ME.txt

Typical usage:

python load_google_crosswikis_inverse_dictionary.py ../inv.dict

"""

import sys
import re
import codecs
import argparse
import urllib2

from pymongo import MongoClient

class InverseDictionaryParser():

    min_form_prob = 0.001
    min_concept_count = 100

    client = MongoClient('mongodb://localhost:27017/')
    db = client.concepts
    coll = db.crosswiki_invdict

    line_patt = re.compile("^(.*)\t(\S+) (.*)\t.*$")
    count_patt = re.compile(r"\b(w'|w|W|Wx):(\d+)\/(\d+)\b")


    def parse(self, inv_dict_file):
        """Parses the inverse dictionary file """

        lines = 0
        matching_lines = 0
        non_matching_lines = 0

        last_concept = None
        forms = []
        concept_counts = {}

        with codecs.open(inv_dict_file, 'r', encoding='utf8', errors='ignore') as fp:
            for line in fp:

                lines += 1
                if lines % 10000 == 0:
                    print 'lines', lines
                    print 'non_matching_lines', non_matching_lines
                    print line

                match = self.line_patt.match(line)
                if match:

                    matching_lines += 1
                    unicode_concept = match.groups()[0]
                    concept = urllib2.unquote(unicode_concept.encode('utf8'))

                    if last_concept != None and concept != last_concept:
                        total_count = sum(concept_counts.values())
                        concept_counts['total'] = total_count
                        self.insert(concept, concept_counts, forms)
                        forms = []
                        counts = {}
                    last_concept = concept

                    prob = float(match.groups()[1])
                    form = match.groups()[2]

                    if prob > self.min_form_prob:
                        counts = self.get_counts(line)
                        counts_dict = dict([(key, num) for key, num, den in counts])
                        forms.append({'prob': prob, 'form': form, 'counts': counts_dict})

                        updated_counts = False
                        for key, num, den in counts:
                            concept_counts[key] = den

                else:
                    non_matching_lines += 1


            total_count = sum(concept_counts.values())
            concept_counts['total'] = total_count

            self.insert(last_concept, concept_counts, forms)

    def insert(self, concept, counts, forms):
        if counts['total'] > self.min_concept_count:
            try:
                self.coll.insert({'_id': concept, 'counts': counts, 'forms': forms})
            except pymongo.errors.DuplicateKeyError as error:
                print "ERROR"
                print error
                print
                self.insertion_errors.append(error)

    def get_counts(self, line):
        return [ (key, int(num), int(den)) for key, num, den in self.count_patt.findall(line) ]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Process the Google crosswiki inverted dictionary file and load into Mongo')
    parser.add_argument('inv_dict_file', metavar='inv_dict_file', type=str,
        help='path to the crosswiki inverted dictionary file')
    args = parser.parse_args()
    print args.inv_dict_file
    dp = InverseDictionaryParser()
    dp.parse(args.inv_dict_file)
