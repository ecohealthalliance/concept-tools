#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the utils"""


import sys
import os
import unittest

sys.path = ['./'] + sys.path

from util import is_meta
from util import get_canonical_id_from_url_segment
from util import get_canonical_id_from_title


class UtilTest(unittest.TestCase):

    def test_is_meta(self):

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

        for kind in kinds:

            self.assertEqual(is_meta(kind + "foo bar zap"), True)
            self.assertEqual(is_meta("foo" + kind + "foo bar zap"), False)

    def test_get_canonical_id_from_url_segment(self):
        segment = 'Champs-%C3%89lys%C3%A9es'
        _id = 'Champs-Élysées'
        self.assertEqual(_id, get_canonical_id_from_url_segment(segment))

    def test_get_canonical_id_from_title(self):
        title = 'Middle East'
        _id = 'Middle_East'
        self.assertEqual(_id, get_canonical_id_from_title(title))

if __name__ == '__main__':
    unittest.main()
