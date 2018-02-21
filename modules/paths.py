import os, sys

from modules import mylib_create_banner, goglib_get_banner

nebula_dir = sys.path[0]
data_dir = os.getenv('HOME') + '/.games_nebula'

def get_image_path(lib, game_name, *args):

    if not os.path.exists(data_dir + '/images'):
        os.makedirs(data_dir + '/images')
    if not os.path.exists(data_dir + '/images/mylib'):
        os.makedirs(data_dir + '/images/mylib')
    if not os.path.exists(data_dir + '/images/goglib'):
        os.makedirs(data_dir + '/images/goglib')
    if not os.path.exists(data_dir + '/images/goglib/unavailable'):
        os.makedirs(data_dir + '/images/goglib/unavailable')

    if lib == 'goglib':
        color = args[0]
        if color == 'normal':
            path_0 = data_dir + '/images/goglib/' + game_name + '.jpg'
            path_1 = nebula_dir + '/images/goglib/' + game_name + '.jpg'
        elif color == 'gray':
            path_0 = data_dir + '/images/goglib/unavailable/' + game_name + '.jpg'
            path_1 = nebula_dir + '/images/goglib/unavailable/' + game_name + '.jpg'
    elif lib == 'mylib':
        path_0 = data_dir + '/images/mylib/' + game_name + '.jpg'
        path_1 = nebula_dir + '/images/mylib/' + game_name + '.jpg'

    if os.path.exists(path_0):
        return path_0
    elif os.path.exists(path_1):
        return path_1
    else:
        if lib == 'goglib':
            # FIX Hack to prevent crash in launchers (trying to create banner for game that not in lib)
            if len(args) < 2:
                if color == 'normal':
                    goglib_get_banner.goglib_get_banner(path_0)
                if color == 'gray':
                    goglib_get_banner.goglib_get_banner(path_0, 'gray')
        if lib == 'mylib':
            # Same as above
            if len(args) == 0:
                mylib_create_banner.mylib_create_banner(game_name)
        return path_0

def get_setup_script_path(lib, game_name):

    if lib == 'goglib':
        script_path_0 = data_dir + '/scripts/goglib/' + game_name + '/setup'
        script_path_1 = nebula_dir + '/scripts/goglib/' + game_name + '/setup'
    elif lib == 'mylib':
        script_path_0 = data_dir + '/scripts/mylib/' + game_name + '/setup'
        script_path_1 = nebula_dir + '/scripts/mylib/' + game_name + '/setup'

    if os.path.exists(script_path_0):
        return script_path_0
    else:
        return script_path_1
