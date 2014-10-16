#!/usr/bin/env python
"""
"""

import sys
import os
import unittest
import pymongo

sys.path = ['./'] + sys.path

from loaders import CrosswikisDictionaryParser

class CrosswikisDictionaryParserTest(unittest.TestCase):

    def setUp(self):

        self.loader = CrosswikisDictionaryParser.CrosswikisDictionaryParser(
            min_concept_prob=0.02, min_form_count=100)

    def test_maine_parsing(self):

        filename = os.path.join(os.path.dirname(__file__), 'resources/maine.dict')

        parsed = list(self.loader.parse(filename))

        self.assertEqual(len(parsed), 1)

        maine = parsed[0]
        form = maine[0]
        form_counts = maine[1]
        concepts = maine[2]

        self.assertEqual(form, 'Maine')
        self.assertEqual(form_counts['total'], 62375)
        self.assertEqual(len(concepts), 2)
        self.assertEqual(concepts[0]['id'], 'Maine')
        self.assertEqual(concepts[0]['prob'], 0.716553)
        self.assertEqual(concepts[1]['id'], 'Maine_(province)')

    def test_maine_loading(self):

        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client.concepts_test
        coll = db.crosswiki_dictionary
        coll.drop()

        loader = CrosswikisDictionaryParser.CrosswikisDictionaryParser(
            min_concept_prob=0.02, min_form_count=100, coll=coll)
        filename = os.path.join(os.path.dirname(__file__), 'resources/maine.dict')

        loader.load_all(filename)

        record = coll.find_one()

        self.assertEqual(record['_id'], 'Maine')
        self.assertEqual(record['counts']['total'], 62375)
        self.assertEqual(len(record['concepts']), 2)
        self.assertEqual(record['concepts'][0]['id'], 'Maine')
        self.assertEqual(record['concepts'][0]['prob'], 0.716553)
        self.assertEqual(record['concepts'][1]['id'], 'Maine_(province)')

    def test_middle_east_parsing(self):

        filename = os.path.join(os.path.dirname(__file__), 'resources/dictionary.middle_east')

        parsed = list(self.loader.parse(filename))

        self.assertEqual(len(parsed), 1)

        item = parsed[0]
        form = item[0]
        form_counts = item[1]
        concepts = item[2]

        self.assertEqual(form, 'the Middle East')
        self.assertEqual(form_counts['total'], 416)
        self.assertEqual(len(concepts), 2)
        self.assertEqual(concepts[0]['id'], 'Middle_East')
        self.assertEqual(concepts[0]['prob'], 0.870192)
        self.assertEqual(concepts[1]['id'], 'the_Middle_East')

    def test_middle_east_loading(self):

        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client.concepts_test
        coll = db.crosswiki_dictionary
        coll.drop()

        loader = CrosswikisDictionaryParser.CrosswikisDictionaryParser(
            min_concept_prob=0.02, min_form_count=100, coll=coll)
        filename = os.path.join(os.path.dirname(__file__), 'resources/dictionary.middle_east')

        loader.load_all(filename)

        record = coll.find_one()

        self.assertEqual(record['_id'], 'the Middle East')
        self.assertEqual(record['counts']['total'], 416)
        self.assertEqual(len(record['concepts']), 2)
        self.assertEqual(record['concepts'][0]['id'], 'Middle_East')
        self.assertEqual(record['concepts'][0]['prob'], 0.870192)
        self.assertEqual(record['concepts'][1]['id'], 'the_Middle_East')



if __name__ == '__main__':
    unittest.main()
