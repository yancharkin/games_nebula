import os
import shutil
import subprocess
import logging

from games_nebula.client import config
from games_nebula.client import is_game_installed
from games_nebula.client.translator import _tr
from games_nebula.client.utils import platform_name
from games_nebula.client.utils import Unzipper

class Installer:
    """Combines GOG API and extractors/installers to install games."""

    def __init__(self, api):
        self.__api = api
        self.__unzipper = Unzipper()
        self.__logger = logging.getLogger(__name__)

    def install(self, game_slug):
        """Install a game using appropriate method."""
        #self.__logger.info(_tr("Installing") + f': {game_slug}')
        download_dir = config.get('download_dir')
        lang = config.get('pref_lang')
        installer_os = config.get('pref_os')
        installer_lang = lang
        if self.__api.is_online() or (self.__api.is_offline_available == 2):
            installer = self.__api.get_installer(game_slug, os=config.get('pref_os'), lang=lang)
            if installer:
                installer_os = installer['os']
                installer_lang = installer['language']
            else:
                return False
        else:
            if os.path.exists(f'{download_dir}/{installer_os}/{installer_lang}/{game_slug}'):
                pass
            elif os.path.exists(f'{download_dir}/{installer_os}/en/{game_slug}'):
                installer_lang = 'en'
            elif os.path.exists(f'{download_dir}/windows/{installer_lang}/{game_slug}'):
                installer_os = 'windows'
            else:
                installer_os = 'windows'
                installer_lang = 'en'
        download_dir = f'{download_dir}/{installer_os}/{installer_lang}/{game_slug}'
        setup_file = None
        if os.path.exists(download_dir):
            installer_files = os.listdir(download_dir)
            if len(installer_files) > 0:
                if installer_os == 'linux':
                    setup_file_ext = 'sh'
                elif installer_os == 'windows':
                    setup_file_ext = 'exe'
                elif installer_os == 'mac':
                    setup_file_ext = 'pkg'
                for f in installer_files:
                    if setup_file_ext == f.split('.')[-1]:
                        setup_file = f
        if setup_file:
            setup_file_path = f'{download_dir}/{setup_file}'
            install_dir = config.get("install_dir")
            install_dir = f'{install_dir}/{game_slug}/{installer_os}/{installer_lang}'
            if installer_os == 'linux':
                self.__install_linux_game(setup_file_path, install_dir)
            elif installer_os == 'windows':
                self.__install_windows_game(setup_file_path, install_dir)
            elif installer_os == 'mac':
                self.__install_mac_game(setup_file_path, install_dir)
            if not config.get('keep_installers') and is_game_installed(game_slug)[0]:
                self.__logger.info(_tr("Removing installer.") + f' {download_dir}')
                shutil.rmtree(download_dir)
            return True
        else:
            self.__logger.info(_tr("The setup file was not found."))
            return False

    def __install_linux_game(self, setup_file_path, install_dir):
        install_dir = f'{install_dir}/game'
        self.__unzipper.extract(setup_file_path, f'{install_dir}/tmp')
        for file_name in os.listdir(f'{install_dir}/tmp'):
            file_path = f'{install_dir}/tmp/{file_name}'
            if file_name != 'data':
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                elif os.path.isfile(file_path):
                    os.remove(file_path)
        noarch_dir_path = f'{install_dir}/tmp/data/noarch'
        for file_name in os.listdir(noarch_dir_path):
            src_path = f'{noarch_dir_path}/{file_name}'
            dest_path = f'{install_dir}/{file_name}'
            if os.path.isdir(src_path) and os.path.exists(dest_path):
                pass
            else:
                shutil.move(src_path, dest_path)
        shutil.rmtree(f'{install_dir}/tmp')

    def __install_mac_game(self, setup_file_path, install_dir):
        pass

    def __install_windows_game(self, setup_file_path, install_dir):
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
        if platform_name != 'windows':
            if shutil.which('wine') and config.get('use_wine'):
                os.environ['WINEPREFIX'] = f'{install_dir}/wineprefix'
                os.environ['WINEDEBUG'] = '-all'
                os.environ['WINEDLLOVERRIDES'] = 'mshtml,mscoree=d'
                proc = subprocess.run(
                        ['winepath', '-w', f'{install_dir}/game'],
                        text = True,
                        stdout = subprocess.PIPE
                )
                install_dir_winepath = proc.stdout.strip()
                subprocess.run(['wine', setup_file_path, f'/DIR={install_dir_winepath}'])
            else:
                self.__logger.info(_tr("Windows installer. Impossible to install without WINE."))
        else:
            # TODO Do Windows stuff
            pass
