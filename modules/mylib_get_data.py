import os
from os import listdir

def games_info(data_dir):

    list_titles = []

    mylib_dir = data_dir + '/scripts/mylib'

    list_names = sorted(list(os.listdir(mylib_dir)))

    for game_name in list_names:

        file = open(mylib_dir + '/' + game_name + '/setup', 'r')
        title = file.readlines()[-1].translate(None, '#\n')
        list_titles.append(title)
        file.close()

    number_of_games = len(list_names)

    return (number_of_games, list_names, list_titles)

if __name__ == "__main__":
    import sys
    games_info(sys.argv[1])
