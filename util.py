#!/usr/bin/env python
"""Utility functions for concepts"""

def is_meta(title):
    """Is the article a meta page, based on the title?"""
    meta_prefixes = [
        'List of ',
        'Meta:',
        'Help:',
        'Template:',
        'Talk:',
        'User talk:',
        'User:',
        'Portal:',
        'Category:',
        'MediaWiki:',
        'Wikipedia:',
        'File:',
        'Book:',
        'Draft:',
        'Education Program:',
        'TimedText:',
        'Module:',
        'WP:',
        'H:',
        'CAT:',
        'WT:',
        'MOS:',
        'Wikipedia talk:',
        'Special:',
        'Transwiki:']

    for meta_prefix in meta_prefixes:
        if title.startswith(meta_prefix):
            return True

    return False
