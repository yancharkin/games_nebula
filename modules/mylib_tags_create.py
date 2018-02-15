import os

try:
    from ConfigParser import ConfigParser as ConfigParser
except:
    from configparser import ConfigParser as ConfigParser

def mylib_tags_create(game_name, tags, tags_file):

    parser = ConfigParser()
    parser.read(tags_file)
    if 'mylib tags' in parser.sections():
        exists = True
    else:
        exists = False

    file = open(tags_file, 'w')
    if exists == False:
        parser.add_section('mylib tags')
    if tags == '':
        parser.remove_option('mylib tags', game_name)
    else:
        parser.set('mylib tags', game_name, str(tags))
    parser.write(file)
    file.close()

if __name__ == "__main__":
    import sys
    mylib_tags_create(sys.argv[1], sys.argv[2], sys.argv[3])
