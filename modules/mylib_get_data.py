import os
from os import listdir

def games_info(data_dir):

    list_names = []
    list_titles = []
    mylib_dir = data_dir + '/scripts/mylib'

    list_all_files = sorted(list(os.listdir(mylib_dir)))

    for file_name in list_all_files:
        setup_file_path = mylib_dir + '/' + file_name + '/setup'

        if os.path.exists(setup_file_path):
            list_names.append(file_name)

            file = open(setup_file_path, 'r')
            title = file.readlines()[-1].translate(None, '#\n')
            list_titles.append(title)
            file.close()

    number_of_games = len(list_names)

    return (number_of_games, list_names, list_titles)

if __name__ == "__main__":
    import sys
    games_info(sys.argv[1])
