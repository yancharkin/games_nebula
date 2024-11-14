import os
import shutil
import fnmatch
import subprocess
import logging

from games_nebula.client import config
from games_nebula.client import is_game_installed
from games_nebula.client.translator import _tr
from games_nebula.client.utils import platform_name

class Launcher:
    def __init__(self, api):
        self.__all_games_list = []
        if api.is_available():
            self.__all_games_list = [x['slug'] for x in api.get_games_list()]
        self.__logger = logging.getLogger(__name__)

    def launch(self, game_slug):
        """Launch a game using appropriate method."""
        self.game_slug = game_slug
        game_installed, game_path = is_game_installed(game_slug)
        if game_installed:
            self.__logger.info(
                    _tr("Launching") +  f" '{game_slug}' " +
                    _tr("from") + f" '{game_path}'."
            )
            self.__prepare(game_path)
        elif os.path.exists(os.path.dirname(game_path)):
            self.__logger.warning(f"'{game_slug}' " + _tr("is not correctly installed."))
        elif game_slug in self.__all_games_list:
            self.__logger.info(f"'{game_slug}' " + _tr("is not installed."))
        else:
            self.__logger.info(_tr("Invalid identifier") + f": '{game_slug}'.")

    def __is_dosbox_game(self, game_path):
        dir_content_list = os.listdir(game_path)
        for fn in dir_content_list:
            if fnmatch.fnmatch(fn.lower(), '*dosbox*'):
                return True

    def __is_scummvm_game(self, game_path):
        return False

    def __get_game_config_dir(self):
        game_config_dir = f'{config._USER_CONFIG_DIR}/configs/{self.game_slug}'
        if not os.path.exists(game_config_dir):
            os.makedirs(game_config_dir)
        return game_config_dir

    def __prepare_dosbox_game(self, game_path):
        game_config_dir = self.__get_game_config_dir()
        dosbox_config_files = []
        for fn in os.listdir(game_path):
            if fn != fn.lower():
                shutil.move(f'{game_path}/{fn}', f'{game_path}/{fn.lower()}')
            fn = fn.lower()
            if fnmatch.fnmatch(fn, '*dosbox*.conf'):
                file_path_new = f'{game_config_dir}/{fn}'
                dosbox_config_files.append(file_path_new)
                if not os.path.exists(file_path_new):
                    #with open(f'{game_path}/{fn}', 'r', errors='replace') as f:
                    with open(f'{game_path}/{fn}', 'r', encoding='latin1') as f:
                        file_content = f.readlines()
                        for i in range(len(file_content)):
                            if any(word in file_content[i].lower() \
                                    for word in ('mount ', 'imgmount ')):
                                file_content[i] = \
                                        file_content[i].replace('..', '.').replace('\\', '/').lower()
                                if 'imgmount ' in file_content[i]:
                                    file_content[i] = f'c:\n{file_content[i]}'
                    with open(file_path_new, 'w', encoding='latin1') as f:
                        f.writelines(file_content)
        # TODO Option to use global dosbox config (as a first conf)
        launch_command = ['dosbox', '-conf', None, '-conf', None]
        for config_file in dosbox_config_files:
            if fnmatch.fnmatch(config_file, '*single.conf'):
                launch_command[4] = config_file
            elif fnmatch.fnmatch(config_file, '*settings.conf'):
                # TODO Decide what to do
                pass
            else:
                launch_command[2] = config_file
        return launch_command

    def __cp_and_update_scummvm_conf(self, game_path):
        print(game_path)

    def __launch_using_dosbox(self, game_path):
        if self.__is_dosbox_game(game_path) and config.get('use_dosbox'):
            if shutil.which('dosbox'):
                self.__logger.info(_tr("Launch using DOSBox."))
                launch_command = self.__prepare_dosbox_game(game_path)
                self.__launch_subprocess(launch_command, game_path)

            else:
                self.__logger.warning(_tr("DOSBox not found. Is it installed?"))
            return True
        return False

    def __launch_using_scummvm(self, game_path):
        if self.__is_scummvm_game(game_path) and config.get('use_scummvm'):
            if shutil.which('scummvm'):
                self.__logger.info(_tr("Launch using ScummVM."))
                self.__cp_and_update_scummvm_conf(game_path)
            else:
                self.__logger.warning(_tr("ScummVM not found. Is it installed?"))
            return True
        return False

    def __launch_using_wine(self, game_path):
        if shutil.which('wine') and config.get('use_wine'):
            self.__logger.info(_tr("Launch using WINE."))
            os.environ['WINEPREFIX'] = f'{os.path.split(game_path)[0]}/wineprefix'
            os.environ['WINEDEBUG'] = '-all'
            #os.environ['WINEDLLOVERRIDES'] = 'mshtml,mscoree=d;winmm=n,b'
            os.environ['WINEDLLOVERRIDES'] = 'mshtml,mscoree=d'
            # 1st way use .lnk file
            launcher = None
            for filename in os.listdir(game_path):
                if '.lnk' in filename:
                    launcher = filename
            if launcher:
                launch_command = ['wine', 'C:\\windows\\command\\start.exe',
                        '/Unix', f'{game_path}/{launcher}']
                self.__launch_subprocess(launch_command, game_path)
            # 2nd way use goggame.info file
        else:
            self.__logger.info(_tr("Windows game. Impossible to launch without WINE."))

    def __prepare(self, game_path):
        # TODO Remove/move to config?
        os.environ['SDL_VIDEO_FULLSCREEN_HEAD'] = '0'
        if 'linux' in game_path:
            self.__launch_linux_game(game_path)
        elif 'windows' in game_path:
            self.__launch_windows_game(game_path)
        elif 'mac' in game_path:
            self.__launch_mac_game(game_path)

    def __launch_linux_game(self, game_path):
        # TODO Search for dosbox and scummvm in the custom path
        if not self.__launch_using_dosbox(game_path) and \
                not self.__launch_using_scummvm(game_path):
            self.__launch_subprocess([f'{game_path}/start.sh'], game_path)

    def __launch_mac_game(self, game_path):
        pass

    def __launch_windows_game(self, game_path):
        if platform_name != 'windows':
            if not self.__launch_using_dosbox(game_path) and \
                    not self.__launch_using_scummvm(game_path):
                self.__launch_using_wine(game_path)
        else:
            # Do Windows stuff
            pass

    def __launch_subprocess(self, launch_command, game_path):
        #print(launch_command, game_path)
        subprocess.run(launch_command, cwd=game_path)
