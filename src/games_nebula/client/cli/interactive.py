import os
import sys
import readline
import logging
import threading
import time
import locale

from games_nebula.client import config
from games_nebula.client import is_game_installed
from games_nebula.client.api_wrapper import Api
from games_nebula.client.logger import Logger
from games_nebula.client.commands import Commands
from games_nebula.client.translator import _tr
from games_nebula.client.cli import ansi
from games_nebula.client.cli import header
from games_nebula.client.cli.valid_commands import ValidCommands
from games_nebula.client.utils import reinput

class InteractiveApp:
    """Interactive CLI application."""

    def __init__(self):
        os.environ['LANG'] = config.get('locale')
        self.force_offline_mode = config.get('force_offline_mode')
        self.ansi_text = ansi.AnsiText(disable=config.get('disable_colors'))
        self.ansi_commands = ansi.AnsiCommands()
        self.api = Api(config.CONFIG_DIR, offline_mode=self.force_offline_mode)
        self.vc = ValidCommands()
        self.__setup_logger()
        self.prompt = '[ GN ]> '
        self.check_status()
        check_status_thread = threading.Thread(
                target=self.__check_status_daemon,
                kwargs={'interval': 600},
                daemon=True
        )
        check_status_thread.start()

    def start(self):
        """Start the application."""
        self.commands = Commands(self.api)
        self.ansi_commands.clear_screen()
        header.show()
        user_id = self.api.get_user_id()
        if not user_id:
            while True:
                try:
                    # Actually it is possible to use username and id not only email
                    username = reinput(_tr("Email") + ': ')
                    break
                except KeyboardInterrupt:
                    print()
                    self.ansi_commands.erase_prev_line()
                except Exception as e:
                    self.__logger.error(e)
                    return
            self.api.login(username=username)

            if self.api.get_user_id():
                self.commands.restart()
            self.__setup_logger()

        #self.commands = Commands(self.api)
        if not self.force_offline_mode:
            self.api.update_games_list()

        if self.api.is_gog_available() and not self.force_offline_mode:
            if not self.api.is_gog_authorized():
                self.api.login()
                self.__setup_logger()
            if self.api.is_gog_authorized():
                if config.get('auto_db_update'):
                    # Update local DB in background thread
                    update_db_thread_1 = threading.Thread(
                            target=self.update_db, args=('en',), daemon=True
                    )
                    update_db_thread_1.start()
                    pref_lang = config.get('pref_lang')
                    if pref_lang != 'en':
                        update_db_thread_2 = threading.Thread(
                                target=self.update_db, args=(pref_lang,), daemon=True
                        )
                        update_db_thread_2.start()
                self.__loop()
            else:
                print(_tr("Not authorized."))
        else:
            if not self.force_offline_mode:
                print(_tr("GOG server not available."))
            if self.api.is_offline_available():
                print(_tr("Starting in offline mode."))
                self.__loop()
            else:
                print(_tr("Can't be started in offline mode."))

    def __loop(self):
        readline.set_completer(self.__completer)
        readline.parse_and_bind('tab: complete')
        while True:
            command = None
            try:
                command, *command_args_list = input(self.prompt).split()
            except KeyboardInterrupt:
                print()
                self.ansi_commands.erase_prev_line()
            except EOFError:
                print()
                break
            except:
                pass
            if not command:
                pass
            elif command in self.vc.valid_commands_set:
                command = self.vc.get_cmd_uni_name(command)
                if command == 'exit':
                    break
                else:
                    if command in ('config', 'help', 'list', 'logout') and command_args_list:
                        sub_command = self.vc.get_cmd_uni_name(command_args_list[0])
                        command_args_list = [sub_command] + command_args_list[1:]
                    if command == 'queue' and command_args_list:
                        sub_command = self.vc.get_cmd_uni_name(command_args_list[0])
                        if command_args_list[0] in ('add', 'remove'):
                            if _tr('all') in command_args_list[1:]:
                                command_args_list = [sub_command] + \
                                        [self.vc.get_cmd_uni_name(_tr('all'))]
                    eval(f'self.commands.{command}({command_args_list})')
                    if command == 'login':
                        self.commands.restart()
            else:
                print(_tr("Unknown command:") + f' "{command}".')
        self.ansi_commands.clear_screen()

    def __setup_logger(self):
        user_id = self.api.get_user_id()
        if user_id:
            Logger(
                    log_dir=f'{config.CONFIG_DIR}/users/{user_id}',
                    log_name='cli.log',
                    stream_fmt='%(message)s'
            ).setup()
        else:
            Logger(
                    stream_fmt='%(message)s'
            ).setup()
        self.__logger = logging.getLogger(__name__)

    def get_installed_games(self):
        """Get list of installed games."""
        games_list = []
        install_dir = config.get('install_dir')
        if not os.path.exists(f'{install_dir}'):
            return games_list
        for game_slug in os.listdir(f'{install_dir}'):
            if game_slug in [x['slug'] for x in self.api.get_games_list()]:
                if is_game_installed(game_slug, quick_check=True)[0]:
                    games_list.append(game_slug)
        return games_list

    def __completer(self, text, state):
        def valid_options(state, options):
            if state < len(options):
                return options[state]
            else:
                return None
        current_line = readline.get_line_buffer()
        if current_line:
            if current_line[-1] == ' ':
                current_line = ' '.join(current_line.split()) + ' '
            else:
                current_line = ' '.join(current_line.split())
        if current_line.count(' ') == 0:
            options = [c for c in self.vc.valid_commands_set if c.startswith(text)]
            return valid_options(state, options)
        else:
            command = current_line.split()[0]
            command = self.vc.get_cmd_uni_name(command)
            if current_line.count(' ') == 1:
                if command == 'config':
                    options = [c for c in self.vc.valid_config_commands_set if c.startswith(text)]
                    return valid_options(state, options)
                elif command == 'list':
                    options = [c for c in self.vc.valid_list_commands_set if c.startswith(text)]
                    return valid_options(state, options)
                elif command == 'queue':
                    options = [c for c in self.vc.valid_queue_commands_set if c.startswith(text)]
                    return valid_options(state, options)
                elif command == 'help':
                    help_commands_set = self.vc.valid_commands_set.copy()
                    help_commands_set.discard('help')
                    help_commands_set.discard(_tr('help'))
                    options = [c for c in help_commands_set if c.startswith(text)]
                    return valid_options(state, options)
                elif command in ('launch', 'uninstall'):
                    options = [c for c in self.get_installed_games() if c.startswith(text)]
                    return valid_options(state, options)
                elif command == 'login':
                    options = [c for c in self.api.get_users() if c.startswith(text)]
                    return valid_options(state, options)
                elif command == 'logout':
                    options = [c for c in self.vc.valid_logout_commands_set if c.startswith(text)]
                    return valid_options(state, options)
                elif command in ('clear', 'exit', 'restart', 'update', 'user'):
                    pass
                elif command in self.vc.valid_commands.values():
                    games_list = [x['slug'] for x in self.api.get_games_list()]
                    options = [c for c in games_list if c.startswith(text)]
                    return valid_options(state, options)
            elif current_line.count(' ') == 2:
                if command == 'config':
                    config_command = current_line.split()[1]
                    if self.vc.get_cmd_uni_name(config_command) == 'set':
                        options = [c for c in config.get_all().keys() if c.startswith(text)]
                        return valid_options(state, options)
            if command == 'queue':
                if current_line.count(' ') >= 2:
                    queue_command = current_line.split()[1]
                    if self.vc.get_cmd_uni_name(queue_command) == 'add':
                        games_list = [x['slug'] for x in self.api.get_games_list()]
                        games_list.extend(['all', _tr('all')])
                        options = [c for c in set(games_list) if c.startswith(text)]
                        return valid_options(state, options)
                    elif self.vc.get_cmd_uni_name(queue_command) == 'remove':
                        games_list = list(self.commands._queue)
                        games_list.extend(['all', _tr('all')])
                        options = [c for c in set(games_list) if c.startswith(text)]
                        return valid_options(state, options)

    def update_db(self, lang):
        """ Update local DB without showing print output."""
        self.commands.update([lang, True])

    def check_status(self):
        """Check if GOG server is available. Change prompt text to indicate this."""
        # '\1' and '\2' escapes used to prevent non-printing characters saving to
        # readline history
        color_reset = f'{self.ansi_text.reset_all}\2'
        gog_available = False
        if not self.force_offline_mode:
            gog_available = self.api.is_gog_available()
        if gog_available:
            color = f'\1{self.ansi_text.fcolor_green}'
            text = '-GN-'
        else:
            color = f'\1{self.ansi_text.fcolor_red}'
            text = '_GN_'
        self.prompt = f'{color}[{text}]{color_reset}> '
        return gog_available

    def __check_status_daemon(self, interval=600):
        time.sleep(interval) # prevent prompt to show too early
        save_cp = '\0337' # save cursor position (DEC)
        restore_cp = '\0338' # restore cursor postion (DEC)
        prev_status = None
        while True:
            gog_available = self.check_status()
            if gog_available != prev_status:
                prev_status = gog_available
                # move cursor left # colums
                move_cp = '\033[#D'.replace('#', str(len(readline.get_line_buffer())+8))
                print(
                        f'{save_cp}{move_cp}{self.prompt}{restore_cp}',
                        end='', flush=True
                )
            time.sleep(interval)
