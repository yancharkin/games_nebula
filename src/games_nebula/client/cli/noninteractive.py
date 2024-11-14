import os
import sys
import argparse
import logging

from games_nebula import __version__
from games_nebula.client import config
from games_nebula.client.api_wrapper import Api
from games_nebula.client.logger import Logger
from games_nebula.client.commands import Commands
from games_nebula.client.translator import _tr
from games_nebula.client.cli.help import Help
from games_nebula.client.cli.valid_commands import ValidCommands

class NonInteractiveApp:
    """Non-interactive CLI application."""

    def __init__(self):
        os.environ['LANG'] = config.get('locale')
        self.api = Api(config.CONFIG_DIR)
        self.commands = Commands(self.api)
        self.vc = ValidCommands()
        self._h = Help()
        self.__setup_logger()

    def start(self):
        """Start the application."""
        parser = self.__ArgumentParser(description=_tr("Unofficial client for GOG."))
        parser.add_argument('--login',
                help=self._h.help_text_login + ' ' + \
                _tr("If there is a logged-in user keep his credentials and switch user."),
                action='store_true'
        )
        parser.add_argument('--email', help=_tr("Email") + '.',
                type=str, metavar='<' + _tr('email') + '>'
        )
        parser.add_argument('--passwd', help=_tr("Password") + '.',
                type=str, metavar='<' + _tr('password') + '>'
        )
        parser.add_argument('--logout',
                help=self._h.help_text_logout + ' ' + \
                        _tr("And remove the user credentials from the computer."),
                action='store_true'
        )
        parser.add_argument('--user-info', help=self._h.help_text_user, action='store_true')
        parser.add_argument('--show-config',
                help=_tr("Show current configuration."),
                action='store_true'
        )
        parser.add_argument('--os',
                help=_tr("Set preferred OS and save to configuration file."),
                type=str, metavar='<' + _tr("os") + '>'
        )
        parser.add_argument('--locale',
                help=_tr("Set locale and save to configuration file."),
                type=str, metavar='<' + _tr("locale") + '>'
        )
        parser.add_argument('--lang',
                help=_tr("Set preferred language (for downloaded files) and save to configuration file."),
                type=str, metavar='<' + _tr("lang") + '>'
        )
        parser.add_argument('--downloaddir',
                help=_tr("Set download directory and save to configuration file."),
                type=str, metavar='<' + _tr("path") + '>'
        )
        parser.add_argument('--installdir',
                help=_tr("Set installation directory and save to configuration file."),
                type=str, metavar='<' + _tr("path") + '>'
        )
        parser.add_argument('--update', help=self._h.help_text_update, action='store_true')
        parser.add_argument('--list',
                help=self._h.help_text_list.split('\n')[0], action='store_true'
        )
        parser.add_argument('--info',
                help=self._h.help_text_info.split(' - ')[1].capitalize(),
                type=str, metavar='<' + _tr("game") + '>'
        )
        parser.add_argument('--download',
                help=self._h.help_text_download.split(' - ')[1].capitalize(),
                type=str, metavar='<' + _tr("game") + '>'
        )
        parser.add_argument('--install',
                help=self._h.help_text_install.split(' - ')[1].capitalize(),
                type=str, metavar='<' + _tr("game") + '>'
        )
        parser.add_argument('--launch',
                help=self._h.help_text_launch.split(' - ')[1].capitalize(),
                type=str, metavar='<' + _tr("game") + '>'
        )
        parser.add_argument('--uninstall',
                help=self._h.help_text_uninstall.split(' - ')[1].capitalize(),
                type=str, metavar='<' + _tr("game") + '>'
        )
        parser.add_argument('--version',
                help=_tr("Show version."),
                action='store_true'
        )
        args = parser.parse_args()
        if args.logout:
            self.commands.logout(['completely'])
        if not self.api.is_gog_authorized():
            self.login(email=args.email, password=args.passwd)
        elif args.login or args.email:
            self.login(email=args.email, password=args.passwd)
        if args.user_info:
            self.commands.user()
        if args.show_config:
            self.commands.config(['show'])
        if args.os:
            self.commands.config(['set', 'pref_os', args.os])
        if args.locale:
            self.commands.config(['set', 'locale', args.locale])
        if args.lang:
            self.commands.config(['set', 'pref_lang', args.lang])
        if args.downloaddir:
            self.commands.config(['set', 'download_dir', args.downloaddir])
        if args.installdir:
            self.commands.config(['set', 'install_dir', args.installdir])
        if args.update:
            self.commands.update()
        if args.list:
            self.commands.list(use_pager=False)
        if args.info:
            self.commands.info([args.info])
        if args.download:
            self.commands.download([args.download])
        if args.install:
            self.commands.install([args.install])
        if args.launch:
            self.commands.launch([args.launch])
        if args.uninstall:
            self.commands.uninstall([args.uninstall])
        if args.version:
            print(__version__)

    def login(self, email=None, password=None):
        self.api.login(username=email, password=password)
        self.commands.update()

    def __setup_logger(self):
        user_id = self.api.get_user_id()
        if user_id:
            Logger(
                    log_dir=f'{config.CONFIG_DIR}/users/{user_id}',
                    log_name='noninteractive_cli.log',
                    stream_fmt='%(message)s'
            ).setup()
        else:
            Logger(
                    stream_fmt='%(message)s'
            ).setup()
        self.__logger = logging.getLogger(__name__)

    class __ArgumentParser(argparse.ArgumentParser):

        def __add_message(self):
            return _tr("To start an interactive shell, run the program without arguments.") + '\n'

        def print_usage(self, file=None):
            print(self.__add_message())
            if file is None:
                file = sys.stdout
            self._print_message(self.format_usage(), file)

        def print_help(self, file=None):
            print(self.__add_message())
            if file is None:
                file = sys.stdout
            self._print_message(self.format_help(), file)
