#!/usr/bin/env python
"""
"""

import sys
import os
import unittest
import pymongo
import json

sys.path = ['./'] + sys.path

from loaders import CrosswikisInverseDictionaryParser

class CrosswikisInverseDictionaryParserTest(unittest.TestCase):

    def test_maine_parsing(self):

        loader = CrosswikisInverseDictionaryParser.CrosswikisInverseDictionaryParser(
            min_form_prob=0.001, min_concept_count=100)


        filename = os.path.join(os.path.dirname(__file__), 'resources/inv.dict.maine')

        parsed = list(loader.parse(filename))

        self.assertEqual(len(parsed), 1)

        maine = parsed[0]
        concept = maine[0]
        concept_counts = maine[1]
        forms = maine[2]

        self.assertEqual(concept, 'Maine')
        self.assertEqual(concept_counts['total'], 96859)
        self.assertEqual(len(forms), 118)
        self.assertEqual(forms[0]['id'], 'Maine')
        self.assertEqual(forms[0]['prob'], 0.461444)
        self.assertEqual(forms[1]['id'], "Wikipedia: 'Maine'")

    def test_maine_loading(self):

        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client.concepts_test
        coll = db.crosswiki_inverse_dictionary
        coll.drop()

        loader = CrosswikisInverseDictionaryParser.CrosswikisInverseDictionaryParser(
            min_form_prob=0.001, min_concept_count=100, coll=coll)
        filename = os.path.join(os.path.dirname(__file__), 'resources/inv.dict.maine')

        loader.load_all(filename)

        record = coll.find_one()

        self.assertEqual(record['_id'], 'Maine')
        self.assertEqual(record['counts']['total'], 96859)
        self.assertEqual(len(record['forms']), 118)
        self.assertEqual(record['forms'][0]['id'], 'Maine')
        self.assertEqual(record['forms'][0]['prob'], 0.461444)
        self.assertEqual(record['forms'][1]['id'], "Wikipedia: 'Maine'")


    def test_1978_parsing(self):

        loader = CrosswikisInverseDictionaryParser.CrosswikisInverseDictionaryParser()

        filename = os.path.join(os.path.dirname(__file__), 'resources/inv.dict.1978')

        parsed = list(loader.parse(filename))

        print "\n\nparsed:"
        print json.dumps(parsed, indent=4)
        print
        print

        self.assertEqual(len(parsed), 5)

        record = parsed[4]
        concept = record[0]
        concept_counts = record[1]
        forms = record[2]

        self.assertEqual(concept, '1978')
        self.assertEqual(concept_counts['total'], 175474)
        self.assertEqual(len(forms), 54)
        self.assertEqual(forms[0]['id'], '1978')
        self.assertEqual(forms[0]['prob'], 0.739346)
        self.assertEqual(forms[1]['id'], "Wikipedia: '1978'")


if __name__ == '__main__':
    unittest.main()
