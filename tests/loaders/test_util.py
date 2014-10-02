#!/usr/bin/env python
"""Test the utils
"""

import sys
import os
import unittest
import pymongo

sys.path = ['./'] + sys.path

from util import is_meta

class is_meta_test(unittest.TestCase):

    kinds = ['List_of_',
            'Meta:',
            'Help:',
            'Template:',
            'Talk:',
            'User_talk:',
            'User:',
            'Portal:',
            'Category:',
            'MediaWiki:',
            'Wikipedia:',
            'File:',
            'Book:',
            'Draft:',
            'Education_Program:',
            'TimedText:',
            'Module:',
            'WP:',
            'H:',
            'CAT:',
            'WT:',
            'MOS:',
            'Wikipedia_talk:',
            'Special:',
            'Transwiki:']

    def test_kinds(self):

        for kind in self.kinds:

            self.assertEqual(is_meta(kind + "foo bar zap"), True)
            self.assertEqual(is_meta("foo" + kind + "foo bar zap"), False)

if __name__ == '__main__':
    unittest.main()
