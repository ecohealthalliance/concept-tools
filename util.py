#!/usr/bin/env python
"""Utility functions for concepts"""

meta_prefixes = [
        'List_of_',
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

def is_meta(title):
    """Is the article a meta page, based on the title?"""

    for meta_prefix in meta_prefixes:
        if title.startswith(meta_prefix):
            return True

    return False
