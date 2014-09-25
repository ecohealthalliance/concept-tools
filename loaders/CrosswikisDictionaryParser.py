#!/usr/bin/env python
"""
Prune the crosswikis dictionary file to only include those above a certain
probability.
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

    def __init__(self, coll=None, min_concept_prob=0.001, min_form_count=100):

        self.min_concept_prob = min_concept_prob
        self.min_form_count = min_form_count

        if coll:
            self.coll = coll
        else:
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = client.concepts
            self.coll = db.crosswiki_dictionary

    def parse_line(self, line):

        match = self.line_patt.match(line)

        if match:
            form = match.groups()[0]
            prob = float(match.groups()[1])
            unicode_concept = match.groups()[2]
            concept = urllib2.unquote(unicode_concept.encode('utf8'))
            return (form, prob, concept)
        else:
            return None


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

                    if prob >= self.min_concept_prob:
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

    def prune_all(self, dictionary_file, keep_file, kill_file):
        """Separate all lines in the dictionary file into those that are above
        the probability threshold and those below."""

        kept = 0
        killed = 0

        keep_fp = codecs.open(keep_file, 'w', encoding='utf8')
        kill_fp = codecs.open(kill_file, 'w', encoding='utf8')

        with codecs.open(dictionary_file, 'r', encoding='utf8', errors='ignore') as fp:
            for line in fp:
                res = self.parse_line(line)
                if res:
                    form, prob, concept = res
                    if prob >= self.min_concept_prob:
                        keep_fp.write(line)
                    else:
                        kill_fp.write(line)
                else:
                    print "BAD LINE", line

        keep_fp.close()
        kill_fp.close()



    def insert(self, form, counts, concepts):
        if counts['total'] > self.min_form_count:
            try:
                res = self.coll.insert({'_id': form, 'counts': counts, 'concepts': concepts})

            except pymongo.errors.DuplicateKeyError as error:
                print "ERROR"
                print error
                print
                self.insertion_errors.append(error)



    def get_counts(self, line):
        return [ (key, int(num), int(den)) for key, num, den in self.count_patt.findall(line) ]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Process the Google crosswiki dictionary file and load into Mongo, or prune file to only useful lines')
    parser.add_argument('dictionary_file', type=str,
        help='path to the crosswiki dictionary file')
    parser.add_argument('--min_concept_prob', type=float, default=0.001,
        help='minimum probability of the form referring to the concept for the record to be retained')
    parser.add_argument('--min_form_count', type=float, default=0.001,
        help='minimum number of times a form must have been seen to be retained')
    parser.add_argument('--action', type=str, default='load',
        help='action to take: load (default) or prune')
    parser.add_argument('--keep_file', type=str,
        help='file to store good lines when pruning')
    parser.add_argument('--kill_file', type=str,
        help='file to store bad lines when pruning')
    args = parser.parse_args()

    dp = CrosswikisDictionaryParser(
        min_concept_prob=args.min_concept_prob, min_form_count=args.min_form_count)
    if args.action == 'load':
        print "Loading from file", args.dictionary_file
        dp.load_all(args.dictionary_file)
    elif args.action == 'prune':
        dp.prune_all(args.dictionary_file, args.keep_file, args.kill_file)





