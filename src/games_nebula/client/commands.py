import os
import sys
import re
import logging
import __main__

from games_nebula.client import config
from games_nebula.client import is_game_installed
from games_nebula.client.downloader import Downloader
from games_nebula.client.installer import Installer
from games_nebula.client.launcher import Launcher
from games_nebula.client.uninstaller import Uninstaller
from games_nebula.client.translator import _tr
from games_nebula.client.cli.pager import pager, remove_html_tags, convert_to_list
from games_nebula.client.cli.fancyprint import full_line_of
from games_nebula.client.cli import ansi
from games_nebula.client.cli.help import Help


class Commands:
    """All available client commands."""

    def __init__(self, api):
        self.__logger = logging.getLogger(__name__)
        self.__api = api
        if config.get('force_offline_mode'):
            self.__api.is_online = lambda: False
        self.__simple_games_list = []
        if self.__api.is_available():
            self.__simple_games_list = [x['slug'] for x in self.__api.get_games_list()]
        self.__installer = Installer(api)
        self.__downloader = Downloader(api)
        self.__launcher = Launcher(api)
        self.__uninstaller = Uninstaller(api)
        self.__ansi_commands = ansi.AnsiCommands()
        self.__ansi_text = ansi.AnsiText(disable=config.get('disable_colors'))
        self._queue = set()

    def __colorize_text(self, text):
        return self.__ansi_text.fcolor_blue + \
                text + \
                self.__ansi_text.reset_all

    def __process_input(self, func, func_args_list):
        def func_except_wrapper(func, game_slug):
            func(game_slug)
            return
            try:
                func(game_slug)
            except:
                self.__logger.info(_tr("Couldn't get info for") + f' "{game_slug}".')
        if len(func_args_list) < 1:
            self.__logger.info(_tr("The game identifier is missing."))
            return
        if func_args_list[0] in self.__simple_games_list:
            game_slug = func_args_list[0]
            func_except_wrapper(func, game_slug)
        else:
            games_slugs_list = [game_slug for game_slug in self.__simple_games_list \
                    if game_slug.startswith(func_args_list[0])]
            if games_slugs_list:
                for game_slug in games_slugs_list:
                    func_except_wrapper(func, game_slug)
            else:
                self.__logger.info(_tr("Invalid identifier") + f': "{func_args_list[0]}".')

    def clear(self, *args):
        """Clearing the screen."""
        self.__ansi_commands.clear_screen()

    def info(self, args_list):
        def get_info(game_slug):
            lang = config.get('pref_lang')
            locale = os.getenv('LANG').split('_')[0]
            title = self.__api.get_game_title(game_slug, locale=locale)
            category = self.__api.get_game_category(game_slug)
            tags = self.__api.get_game_tags(game_slug)
            oses = ', '.join(self.__api.get_game_oses(game_slug))
            languages = None
            genres = None
            #size = None
            #store_page = None
            description = None
            if (self.__api.is_online() and not self.__api._offline_mode) or \
                    (self.__api.is_offline_available() == 2):
                languages = ', '.join(
                        [l.capitalize() for l in self.__api.get_game_languages(game_slug).values()]
                )
                version = self.__api.get_installer_version(game_slug, lang=lang)
                size, unit = self.__api.get_installer_total_size(game_slug, lang=lang)
                store_page = self.__api.get_game_store_page(game_slug)
                try:
                    genres = ', '.join(self.__api.get_game_genres(game_slug, locale=locale))
                    #size, unit = self.__api.get_installer_total_size(game_slug, lang=lang)
                    #store_page = self.__api.get_game_store_page(game_slug)
                except:
                    pass
                description = self.__api.get_game_description(game_slug, locale=locale)
            full_info = []
            full_info.append(full_line_of('-'))
            full_info.extend(convert_to_list(title))
            full_info.append(full_line_of('-'))
            if genres: full_info.extend(convert_to_list(_tr("Genres") + f': {genres}'))
            if not genres and category:
                full_info.extend(convert_to_list(_tr("Category") + f': {category}'))
            if tags: full_info.extend(convert_to_list(_tr("Tags") + f': {tags}'))
            full_info.extend(convert_to_list(_tr("Supported OSes") + f': {oses}'))
            if languages: full_info.extend(convert_to_list(_tr("Languages") + f': {languages}'))
            if size: full_info.extend(convert_to_list(_tr("Download size") + f': {size} {unit}'))
            if version: full_info.extend(convert_to_list(_tr("Version") + f': {version}'))
            if store_page: full_info.extend(convert_to_list(_tr("Store page")+ f': {store_page}'))
            full_info.append('')
            if description:
                description_stripped = remove_html_tags(description["full"].replace("\n", " "))
                description_full = _tr("Description") + f': {description_stripped}'
                full_info.extend(convert_to_list(description_full))
            pager(full_info)
            print()
        self.__process_input(get_info, args_list)

    def list(self, args_list=None, use_pager=True):
        """
        Usage: list [all/installed/downloaded] [os<linux, windows, mac>] [lang<en, ru>]
        - without arg: list games only for current os/lang
        """
        games_list = []
        games_dict = {}
        command = 'all'
        if args_list:
            command = args_list[0]
        if command == 'all':
            if not self.__simple_games_list:
                self.__simple_games_list = [x['slug'] for x in self.__api.get_games_list()]
            games_list = sorted(self.__simple_games_list)
        elif (command == 'downloaded') or command == ('installed'):
            os_dir = None
            lang_dir = None
            if len(args_list) >= 2:
                for arg in args_list[1:]:
                    if arg in ('linux', 'windows', 'mac'):
                        os_dir = arg
                    elif len(arg) == 2:
                        lang_dir =  arg
            if command == 'downloaded':
                target_dir_path = config.get('download_dir')
            elif command == 'installed':
                target_dir_path = config.get('install_dir')
            if os.path.exists(target_dir_path):
                def make_list(target_dir_path):
                    listdir_target_dir = [os_dir]
                    if not os_dir:
                        listdir_target_dir = os.listdir(target_dir_path)
                    for cur_os_dir in listdir_target_dir:
                        os_dir_path = f'{target_dir_path}/{cur_os_dir}'
                        if os.path.exists(os_dir_path):
                            listdir_os_dir = [lang_dir]
                            if not lang_dir:
                                listdir_os_dir = os.listdir(os_dir_path)
                            for cur_lang_dir in listdir_os_dir:
                                lang_dir_path = f'{os_dir_path}/{cur_lang_dir}'
                                if os.path.exists(lang_dir_path) and os.listdir(lang_dir_path):
                                    key = f'{cur_os_dir}, {cur_lang_dir}'
                                    if key not in games_dict.keys():
                                        if command == 'installed':
                                            games_dict[key] = [f'  {game_dir}']
                                        else:
                                            games_dict[key] = sorted([f'  {x}' for x in os.listdir(lang_dir_path)])
                                    else:
                                        games_dict[key].append(f'  {game_dir}')
                if command == 'downloaded':
                    make_list(target_dir_path)
                elif command == 'installed':
                    listdir_target_dir = [x for x in os.listdir(target_dir_path) if x in self.__simple_games_list]
                    for game_dir in listdir_target_dir:
                        game_dir_path = f'{target_dir_path}/{game_dir}'
                        make_list(game_dir_path)
                if games_dict:
                    for key in sorted(games_dict.keys()):
                        if (not os_dir) and (not lang_dir):
                            for game_slug in games_dict[key]:
                                game_slug = game_slug.strip()
                                if self.__api.is_available() == 2:
                                    installer = self.__api.get_installer(
                                            game_slug, os=config.get('pref_os'),
                                            lang=config.get('pref_lang')
                                    )
                                    installer_os = installer['os']
                                    installer_lang = installer['language']
                                    if key == f'{installer_os}, {installer_lang}':
                                        games_list.append(game_slug)
                                else:
                                    games_list.append(game_slug)
                            games_list = sorted(list(set(games_list)))
                        else:
                            games_list.append(key)
                            games_list.extend(games_dict[key])
        else:
            self.__logger.info(_tr("Unknown command") + f': "{command}".')
            return
        if use_pager:
            pager(games_list)
        else:
            for game_slug in games_list:
                print(game_slug)

    def update(self, args_list=None):
        """
        Update localdb for a specified locale ('en' by default)
        Usage: update [locale <en, ru, pl>]
        """
        locale='en'
        if args_list:
            locale = args_list[0]
        noprint = False
        if args_list and len(args_list) > 1:
            noprint = bool(args_list[1])
        if self.__api.is_online() and not self.__api._offline_mode:
            self.__api.update_localdb(details=True, locale=locale, noprint=noprint)
        else:
            self.__logger.info(_tr("Not available in offline mode."))
        self.__simple_games_list = [x['slug'] for x in self.__api.get_games_list()]

    def config(self, args_list):
        if not args_list:
            command = 'show'
        else:
            command = args_list[0]
        if command == 'show':
            pager(sorted([f'{key}: {value}' for key,value in config.get_all().items()]))
        elif command == 'set':
            if len(args_list) < 3:
                self.__logger.info(_tr("Not enough arguments."))
                return
            option = args_list[1]
            value = args_list[2]
            config.set(option, value)
        else:
            self.__logger.info(_tr("Unknown command") + f': "{command}".')

    def queue(self, args_list):
        def get_matched_games(input_list):
            tmp_set = set()
            for x in input_list:
                if x in self.__simple_games_list:
                    tmp_set.add(x)
                else:
                    m = [game_slug for game_slug in self.__simple_games_list if bool(re.match(x, game_slug))]
                    tmp_set.update(m)
            return tmp_set
        if not args_list:
            command = 'show'
        else:
            command = args_list[0]
        if command == 'add':
            if 'all' in args_list[1:]:
                self._queue = set(self.__simple_games_list)
            else:
                matched_games = get_matched_games(args_list[1:])
                self._queue.update(matched_games)
        elif command == 'remove':
            if 'all' in args_list[1:]:
                self._queue.clear()
            else:
                matched_games = get_matched_games(args_list[1:])
                for game_slug in matched_games:
                    self._queue.discard(game_slug)
        elif command == 'clear':
            self._queue.clear()
        elif command in ('show', 'download', 'install', 'uninstall'):
            for game_slug in sorted(list(self._queue)):
                if command == 'show':
                    print(game_slug)
                elif command == 'download':
                    self.download([game_slug])
                elif command == 'install':
                    self.install([game_slug])
                elif command == 'uninstall':
                    self.uninstall([game_slug])

    def download(self, args_list):
        if not self.__api.is_online() or self.__api._offline_mode:
            self.__logger.info(_tr("Impossible to download in offline mode."))
            return False
        def download_files(game_slug):
            self.__downloader.download(game_slug)
        try:
            self.__process_input(download_files, args_list)
            return True
        except KeyboardInterrupt:
            print()
            self.__logger.info(_tr("Download canceled."))
            return False

    def install(self, args_list):
        def install_game(game_slug):
            if is_game_installed(game_slug)[0]:
                self.__logger.info(_tr("The game is already installed."))
                return
            if self.__api.is_online() and not self.__api._offline_mode:
                if self.download([game_slug]): # download/re-download if not up-to-date
                    self.__installer.install(game_slug)
            else:
                self.__installer.install(game_slug)
        try:
            self.__process_input(install_game, args_list)
        except KeyboardInterrupt:
            print()
            self.__logger.info(_tr("Installation canceled."))

    def launch(self, args_list):
        if not args_list:
            self.__logger.info(_tr("The game identifier is missing."))
            return
        game_slug = args_list[0]
        self.__launcher.launch(game_slug)

    def uninstall(self, args_list):
        if not args_list:
            self.__logger.info(_tr("The game identifier is missing."))
            return
        game_slug = args_list[0]
        self.__uninstaller.uninstall(game_slug)

    def logout(self, args_list=None):
        if args_list and args_list[0] == 'completely':
            self.__api.logout(completely=True)
        else:
            self.__api.logout()
        sys.exit()

    def login(self, args_list):
        user = None
        password = None
        if len(args_list) >= 1:
            user = args_list[0]
        if len(args_list) >= 2:
            password = args_list[1]
        if user:
            self.__api.login(user=user, password=password)

    def help(self, args_list):
        """Show help."""
        commands_help = Help()
        if not args_list:
            commands_help._help()
        else:
            command = args_list[0]
            try:
                help_func = getattr(commands_help, command)
                help_func()
            except:
                self.__logger.info(_tr("Unknown command") + f': "{command}".')

    def user(self, args_list=None):
        """Show info about the logged in user."""
        print(self.__colorize_text(
                _tr("Username") + ': ' + self.__api.get_user_name() + '\n' + \
                _tr("Email") + ': ' + self.__api.get_user_email() + '\n' + \
                _tr("Number of games") + ': ' + str(len(self.__api.get_games_list()))
        ))

    def restart(self, args_list=None):
        """Restart the application."""
        os.execv(__main__.__file__, sys.argv)
