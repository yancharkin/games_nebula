import os, sys
from modules import goglib_get_banner

nebula_dir = sys.path[0]

def games_info(data_dir):

    list_names = []
    list_titles = []
    list_icons = []

    games_list = os.path.abspath(data_dir + '/config/games_list')

    with open(games_list, 'r') as in_file:
        for line in in_file:
            if 'gamename: ' in line:
                list_names.append(line.split('name: ',1)[1].replace('\n', ''))
            if 'title: ' in line:
                list_titles.append(line.split('title: ',1)[1].replace('\n', ''))
            if 'icon: ' in line:
                list_icons.append(line.split('icon: ',1)[1].replace('\n', ''))
    in_file.close()

    number_of_games = len(list_names)

    if not os.path.exists(data_dir + '/images'):
        os.makedirs(data_dir + '/images')
    if not os.path.exists(data_dir + '/images/goglib'):
        os.makedirs(data_dir + '/images/goglib')
    if not os.path.exists(data_dir + '/images/goglib/unavailable'):
        os.makedirs(data_dir + '/images/goglib/unavailable')

    for i in range(0, number_of_games):

        banner_path_0 = data_dir + '/images/goglib/' + list_names[i] + '.jpg'
        banner_path_1 = nebula_dir + '/images/goglib/' + list_names[i] + '.jpg'

        if (not os.path.exists(banner_path_0)) and (not os.path.exists(banner_path_1)):
            goglib_get_banner.goglib_get_banner(banner_path_0)

    available_scripts = os.listdir(data_dir + '/scripts/goglib/')

    return (number_of_games, list_names, list_titles, list_icons, available_scripts)
