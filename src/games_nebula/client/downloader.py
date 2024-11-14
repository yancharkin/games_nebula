import os
import logging

from games_nebula.client import config
from games_nebula.client.cli.fancyprint import full_line_of
from games_nebula.client.translator import _tr
from games_nebula.client.utils import Downloader as DownloaderUtil
from games_nebula.client.utils.md5generator import md5generator

class Downloader:
    """Combines GOG API and download utility to download games."""

    def __init__(self, api):
        self.__logger = logging.getLogger(__name__)
        self.__api = api
        self.__downloader = DownloaderUtil()

    def download(self, game_slug):
        """Show info and download a game."""
        #self.__logger.info(_tr("Downloading" + f': {game_slug}'))
        lang = config.get('pref_lang')
        installer = self.__api.get_installer(game_slug, os=config.get('pref_os'), lang=lang)
        if not installer:
            self.__logger.warning(_tr("No installer is available for") + f': {game_slug}')
            return
        installer_os = installer['os']
        installer_lang = installer['language']
        installer_lang_full = installer['language_full']
        locale = os.getenv('LANG').split('_')[0]
        download_dir = config.get('download_dir')
        download_dir = f'{download_dir}/{installer_os}/{installer_lang}/{game_slug}'
        if not os.path.exists(f'{download_dir}'):
            os.makedirs(f'{download_dir}')
        title = self.__api.get_game_title(game_slug, locale=locale)
        version = self.__api.get_installer_version(game_slug, lang=lang, os=installer_os)
        size, unit = self.__api.get_installer_total_size(game_slug, lang=lang, os=installer_os)
        ifiles = self.__api.get_installer_files(game_slug, lang=lang, os=installer_os)
        print(full_line_of('='))
        print(_tr("Title") + f': {title}')
        print(_tr("Language") + f': {installer_lang_full}')
        print(_tr("OS") + f': {installer_os.capitalize()}')
        print(_tr("Version") + f': {version}')
        print(_tr("Total size") + f': {size} {unit}')
        print(full_line_of('='))
        for ifile in ifiles:
            file_info = self.__api.get_installer_file_info(ifile)
            file_name = file_info['name']
            file_size = file_info['size']
            file_md5 = file_info['md5']
            link = file_info['link']
            resume = False
            if os.path.exists(f'{download_dir}/{file_name}') and file_md5:
                if os.path.exists(f'{download_dir}/{file_name}.md5'):
                    with open(f'{download_dir}/{file_name}.md5', 'r') as f:
                        old_md5 = f.readline().strip()
                else:
                    old_md5 = md5generator(f'{download_dir}/{file_name}')
                    with open(f'{download_dir}/{file_name}.md5', 'w') as f:
                        f.write(old_md5)
                if file_md5 == old_md5:
                    resume = True
            if resume == False:
                try:
                    os.remove(f'{download_dir}/{file_name}.md5')
                    os.remove(f'{download_dir}/{file_name}')
                except:
                    pass
            if file_md5:
                with open(f'{download_dir}/{file_name}.md5', 'w') as f:
                    f.write(file_md5)
            self.__downloader.download(
                    link,
                    download_dir,
                    file_name = file_name,
                    timeout = 0,
                    preallocate = True,
                    resume = resume
            )
