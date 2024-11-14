import os
import fnmatch

from games_nebula.client import config
from games_nebula.client.api_wrapper import Api

def is_game_installed(game_slug, quick_check=False):
    """
    Check if the game is installed. Also return path to the installtion directory.

    Arguments:
        quick_check: Bypass API just search for the files on a disk.
                     Also, check only the existence of the directory, not it's content.

    A quick check / offline mode not very reliable (but much faster):
    will return True if any version of the game is installed (any os/lang combination)
    even if a different os/lang is set in the configuration file.
    Example:
          - for the game both linux and windows versions are available
          - for some reason windows version was installed
          - if in config file: pref_os = linux, the functon should return False
            but it will return True
    """
    install_dir = config.get('install_dir')
    installer_os = config.get('pref_os')
    installer_lang = config.get('pref_lang')
    game_path = ''
    use_api = False
    if not quick_check:
        api = Api(config.CONFIG_DIR, offline_mode=config.get('force_offline_mode'))
        use_api = api.is_online() or api.is_offline_available == 2
    if use_api and not quick_check:
        installer = api.get_installer(game_slug, os=installer_os, lang=installer_lang)
        if installer:
            installer_os = installer['os']
            installer_lang = installer['language']
            # Use the directory one level above the 'game' directory to list
            # not fully installed games (for example, canceled installation)
            # to allow 'uninstall' them easily.
            #game_path = f'{install_dir}/{game_slug}/{installer_os}/{installer_lang}/game'
            game_path = f'{install_dir}/{game_slug}/{installer_os}/{installer_lang}'
    else:
        path0 = f'{install_dir}/{game_slug}/{installer_os}/{installer_lang}'
        path1 = f'{install_dir}/{game_slug}/{installer_os}/en'
        path2 = f'{install_dir}/{game_slug}/windows/{installer_lang}'
        path3 = f'{install_dir}/{game_slug}/windows/en'
        for path in (path0, path1, path2, path3):
            if os.path.exists(path):
                game_path = path
                break
    if quick_check:
        game_installed = os.path.exists(game_path)
    else:
        game_installed = False
        if os.path.exists(f'{game_path}/game'):
            dir_content_list = os.listdir(f'{game_path}/game')
            c1 = fnmatch.filter(dir_content_list, 'goggame*.info')
            c2 = fnmatch.filter(dir_content_list, 'start.sh')
            #c3 = fnmatch.filter(dir_content_list, 'gameinfo')
            c3 = fnmatch.filter(dir_content_list, '*.lnk')
            game_installed = bool(c1 + c2 + c3)
    if game_path:
        game_path = f'{game_path}/game'
    return game_installed, game_path
