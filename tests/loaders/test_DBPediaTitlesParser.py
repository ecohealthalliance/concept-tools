#!/usr/bin/env python
"""
"""

import sys
import os
import unittest
import pymongo

sys.path = ['./'] + sys.path

from loaders import DBPediaTitlesParser

class DBPediaTitlesParserTest(unittest.TestCase):

    def setUp(self):

        self.parser = DBPediaTitlesParser.DBPediaTitlesParser()

    def test_parsing(self):

        filename = os.path.join(os.path.dirname(__file__), 'resources/labels_en.nt.1000')

        parsed = list(self.parser.parse_file(filename))

        self.assertEqual(len(parsed), 1000)
        print parsed
        self.assertEqual(parsed[90][0], 'Ascii_Art')
        self.assertEqual(parsed[90][1], 'Ascii Art')

if __name__ == '__main__':
    unittest.main()
