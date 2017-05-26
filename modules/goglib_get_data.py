import os

import goglib_get_banner
import goglib_get_icon

def games_info(data_dir):

    list_names = []
    list_titles = []
    list_icons = []

    games_list = os.path.abspath(data_dir + '/config/games_list')

    with open(games_list, 'r') as in_file:
        for line in in_file:
            if 'gamename: ' in line:
                list_names.append(line.split('name: ',1)[1].translate(None, '\n'))
            if 'title: ' in line:
                list_titles.append(line.split('title: ',1)[1].translate(None, '\n'))
            if 'icon: ' in line:
                list_icons.append(line.split('icon: ',1)[1].translate(None, '\n'))
    in_file.close()

    number_of_games = len(list_names)

    if not os.path.exists(data_dir + '/images'):
        os.makedirs(data_dir + '/images')
    if not os.path.exists(data_dir + '/images/goglib_banners'):
        os.makedirs(data_dir + '/images/goglib_banners')
    if not os.path.exists(data_dir + '/images/goglib_banners/unavailable'):
        os.makedirs(data_dir + '/images/goglib_banners/unavailable')
    if not os.path.exists(data_dir + '/images/goglib_icons'):
        os.makedirs(data_dir + '/images/goglib_icons')

    for i in range(0, number_of_games):

        if not os.path.exists(data_dir + '/images/goglib_icons/' + list_names[i] + '.jpg'):
            goglib_get_icon.goglib_get_icon(list_names[i], list_icons[i], data_dir + '/images/goglib_icons/')
        if not os.path.exists(data_dir + '/images/goglib_banners/' + list_names[i] + '.jpg'):
            goglib_get_banner.goglib_get_banner(list_names[i], data_dir + '/images/goglib_icons/', data_dir + '/images/goglib_banners/')
            goglib_get_banner.goglib_get_banner(list_names[i], data_dir + '/images/goglib_icons/', data_dir + '/images/goglib_banners/')

    available_scripts = os.listdir(data_dir + '/scripts/goglib/')
    
    
    linux_games_list_file = open(os.path.abspath(data_dir + '/config/linux_games_list'), 'r')
    linux_games_list = linux_games_list_file.read().splitlines()
    linux_games_list_file.close()
    
    for game in linux_games_list:
        if game not in available_scripts:
            available_scripts.append(game)
    
    available_scripts = sorted(available_scripts)

    return (number_of_games, list_names, list_titles, list_icons, available_scripts)

if __name__ == "__main__":
    import sys
    games_info()
