import os

try:
    from ConfigParser import ConfigParser as ConfigParser
except:
    from configparser import ConfigParser as ConfigParser

def goglib_tags_create(game_name, tags, tags_file):

    parser = ConfigParser()
    parser.read(tags_file)
    if 'goglib tags' in parser.sections():
        exists = True
    else:
        exists = False

    file = open(tags_file, 'w')
    if exists == False:
        parser.add_section('goglib tags')
    if tags == '':
        parser.remove_option('goglib tags', game_name)
    else:
        parser.set('goglib tags', game_name, str(tags))
    parser.write(file)
    file.close()

if __name__ == "__main__":
    import sys
    goglib_tags_create(sys.argv[1], sys.argv[2], sys.argv[3])
