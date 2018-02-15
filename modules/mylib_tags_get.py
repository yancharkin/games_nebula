import os

try:
    from ConfigParser import ConfigParser as ConfigParser
except:
    from configparser import ConfigParser as ConfigParser

def mylib_tags_get(game_name, tags_file):

    parser = ConfigParser()
    parser.read(tags_file)
    if 'mylib tags' in parser.sections():
        if game_name in parser.options('mylib tags'):
            tags = parser.get('mylib tags', game_name).split(',')
        else:
            tags = []
    else:
        tags = []

    return tags

if __name__ == "__main__":
    import sys
    mylib_tags_get(sys.argv[1], sys.argv[2])
