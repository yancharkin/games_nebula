import os

try:
    from ConfigParser import ConfigParser as ConfigParser
except:
    from configparser import ConfigParser as ConfigParser

def mylib_tags_get_all(tags_file):

    all_tags = []

    parser = ConfigParser()
    parser.read(tags_file)

    if 'mylib tags' in parser.sections():

        for game_name in parser.options('mylib tags'):
            game_tags = parser.get('mylib tags', game_name).split(',')

            if len(game_tags) != 0:
                for tag in game_tags:
                    if tag not in all_tags:
                        all_tags.append(tag)

    return sorted(all_tags)

if __name__ == "__main__":
    import sys
    mylib_tags_get_all(sys.argv[1])
