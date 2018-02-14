#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-install_mode: t; c-basic-offset: 4; tab-width: 4 -*-

import os
import ConfigParser

def goglib_tags_get(game_name, tags_file):

    parser = ConfigParser.ConfigParser()
    parser.read(tags_file)
    if 'goglib tags' in parser.sections():
        if game_name in parser.options('goglib tags'):
            tags = parser.get('goglib tags', game_name).split(',')
        else:
            tags = []
    else:
        tags = []

    return tags

if __name__ == "__main__":
    import sys
    goglib_tags_get(sys.argv[1], sys.argv[2])
