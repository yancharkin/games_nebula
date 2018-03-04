import os, sys

nebula_dir = sys.path[0]


def games_info(data_dir):

    list_names = []
    list_titles = []

    mylib_dir_0 = data_dir + '/scripts/mylib'
    mylib_dir_1 = nebula_dir + '/scripts/mylib'
    games_list_0 = os.listdir(mylib_dir_0)
    games_list_1 = os.listdir(mylib_dir_1)
    games_list_2 = []

    for game_name in games_list_1:
        if game_name not in games_list_0:
            games_list_2.append(game_name)

    dict_name2title_0 = get_info(games_list_0, mylib_dir_0)
    dict_name2title_1 = get_info(games_list_2, mylib_dir_1)

    dict_name2title_0.update(dict_name2title_1)

    list_names = sorted(dict_name2title_0)
    for name in list_names:
        list_titles.append(dict_name2title_0[name])

    number_of_games = len(list_names)

    return number_of_games, list_names, list_titles


def get_info(games_list, mylib_dir):

    dict_name2title = {}

    for game_name in games_list:

        setup_file_path = mylib_dir + '/' + game_name + '/setup'

        if os.path.exists(setup_file_path):

            setup_file = open(setup_file_path, 'r')
            data = setup_file.readlines()
            setup_file.close()

            title = data[-1].replace('#', '').replace('\n', '')
            dict_name2title[game_name] = title

    return dict_name2title
