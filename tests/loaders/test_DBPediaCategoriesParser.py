#!/usr/bin/env python
"""Test parsing the DBPedia categories
"""

import sys
import os
import unittest
import pymongo

sys.path = ['./'] + sys.path

from loaders import DBPediaCategoriesParser

class DBPediaCategoriesParserTest(unittest.TestCase):

    def setUp(self):

        self.parser = DBPediaCategoriesParser.DBPediaCategoriesParser()

    def test_parsing(self):

        filename = os.path.join(os.path.dirname(__file__), 'resources/article_categories_en.nt.64')

        parsed = list(self.parser.parse_file(filename))

        self.assertEqual(len(parsed), 64)

        self.assertEqual(parsed[0][0], 'Albedo')
        self.assertEqual(parsed[0][1], 'Climate_forcing')

        self.assertEqual(parsed[21][0], 'An_American_in_Paris')
        self.assertEqual(parsed[21][1], 'Symphonic_poems')

        self.assertEqual(parsed[57][0], 'Aristotle')
        self.assertEqual(parsed[57][1], 'Philosophers_and_tutors_of_Alexander_the_Great')

if __name__ == '__main__':
    unittest.main()
