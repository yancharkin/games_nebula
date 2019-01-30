import os, sys
from modules import goglib_get_banner

nebula_dir = sys.path[0]

def games_info(data_dir):

    list_names = []
    list_titles = []
    list_icons = []
    name2id = {}

    games_list = os.path.abspath(data_dir + '/config/games_list')

    game_name = ''
    with open(games_list, 'r') as in_file:
        for line in in_file:
            if 'gamename: ' in line:
                game_name = line.split('name: ',1)[1].replace('\n', '')
                list_names.append(game_name)
            if 'product id: ' in line:
                game_id = line.split('product id: ',1)[1].replace('\n', '')
                name2id[game_name] = game_id
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
        unavailable_path = data_dir + '/images/goglib/unavailable/' + list_names[i] + '.jpg'
        game_id = name2id[list_names[i]]

        if (not os.path.exists(banner_path_0)) and (not os.path.exists(banner_path_1)):
            goglib_get_banner.goglib_get_banner(banner_path_0, unavailable_path, game_id)

    available_scripts = os.listdir(data_dir + '/scripts/goglib/')

    return (number_of_games, list_names, list_titles, list_icons, available_scripts)
