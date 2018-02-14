#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-install_mode: t; c-basic-offset: 4; tab-width: 4 -*-

import os
import ConfigParser

def goglib_tags_get_all(tags_file):

    all_tags = []

    parser = ConfigParser.ConfigParser()
    parser.read(tags_file)

    if 'goglib tags' in parser.sections():

        for game_name in parser.options('goglib tags'):
            game_tags = parser.get('goglib tags', game_name).split(',')

            if len(game_tags) != 0:
                for tag in game_tags:
                    if tag not in all_tags:
                        all_tags.append(tag)

    return sorted(all_tags)

if __name__ == "__main__":
    import sys
    goglib_tags_get_all(sys.argv[1])
