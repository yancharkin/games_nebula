from games_nebula.client import config
from games_nebula.client.translator import _tr
from games_nebula.client.cli import ansi
from games_nebula.client.cli.valid_commands import ValidCommands

class Help:
    """Contains help text."""

    def __init__(self):
        self.__ansi_text = ansi.AnsiText(disable=config.get('disable_colors'))
        self.__vc = ValidCommands()
        self.__setup_translation()

    def _is_trnaslation_required(self):
        keys = sorted(list(self.__vc.valid_commands.keys()))
        values = sorted(list(self.__vc.valid_commands.values()))
        if (keys != values) and (config.get('translate_commands') == True):
            return True
        return False

    def __setup_translation(self):
        translate_commands = self._is_trnaslation_required()
        translated_only = config.get('translated_commands_only')
        available_commands = list(self.__vc.valid_commands.values())
        cmdstr_help = "help"
        cmdstr_config = "config"
        cmdstr_set = "set"
        cmdstr_show = "show"
        cmdstr_download = "download"
        cmdstr_info = "info"
        cmdstr_install = "install"
        cmdstr_launch = "launch"
        cmdstr_list = "list"
        cmdstr_all = "all"
        cmdstr_downloaded = "downloaded"
        cmdstr_installed = "installed"
        cmdstr_queue = "queue"
        cmdstr_add = "add"
        cmdstr_clear = "clear"
        cmdstr_download = "download"
        cmdstr_install = "install"
        cmdstr_remove = "remove"
        cmdstr_uninstall = "uninstall"
        if translate_commands:
            _tr_available_commands = list(self.__vc.valid_commands.keys())
            available_commands += _tr_available_commands
            cmdstr_help = f'{cmdstr_help}/' + _tr("help")
            cmdstr_config = f'{cmdstr_config}/' + _tr("config")
            cmdstr_set = f'{cmdstr_set}/' + _tr("set")
            cmdstr_show = f'{cmdstr_show}/' + _tr("show")
            cmdstr_download = f'{cmdstr_download}/' + _tr("download")
            cmdstr_info = f'{cmdstr_info}/' + _tr("info")
            cmdstr_install = f'{cmdstr_install}/' + _tr("install")
            cmdstr_launch = f'{cmdstr_launch}/' + _tr("launch")
            cmdstr_list = f'{cmdstr_list}/' + _tr("list")
            cmdstr_all = f'{cmdstr_all}/' + _tr("all")
            cmdstr_downloaded = f'{cmdstr_downloaded}/' + _tr("downloaded")
            cmdstr_installed = f'{cmdstr_installed}/' + _tr("installed")
            cmdstr_queue = f'{cmdstr_queue}/' + _tr("queue")
            cmdstr_add = f'{cmdstr_add}/' + _tr("add")
            cmdstr_clear = f'{cmdstr_clear}/' + _tr("clear")
            cmdstr_download = f'{cmdstr_download}/' + _tr("download")
            cmdstr_install = f'{cmdstr_install}/' + _tr("install")
            cmdstr_remove = f'{cmdstr_remove}/' + _tr("remove")
            cmdstr_uninstall = f'{cmdstr_uninstall}/' + _tr("uninstall")
            if translated_only:
                available_commands = _tr_available_commands
                cmdstr_help = _tr("help")
                cmdstr_config = _tr("config")
                cmdstr_set = _tr("set")
                cmdstr_show = _tr("show")
                cmdstr_download = _tr("download")
                cmdstr_info = _tr("info")
                cmdstr_install = _tr("install")
                cmdstr_launch = _tr("launch")
                cmdstr_list = _tr("list")
                cmdstr_all = _tr("all")
                cmdstr_downloaded = _tr("downloaded")
                cmdstr_installed = _tr("installed")
                cmdstr_queue = _tr("queue")
                cmdstr_add = _tr("add")
                cmdstr_clear = _tr("clear")
                cmdstr_download = _tr("download")
                cmdstr_install = _tr("install")
                cmdstr_remove = _tr("remove")
                cmdstr_show = _tr("show")
                cmdstr_uninstall = _tr("uninstall")
        available_commands_set = sorted(set(available_commands))
        available_commands_str = ', '.join(available_commands_set)

        self.help_available_commands = _tr("Available commands") + \
                f": {available_commands_str}. " + _tr("Type") + f" '{cmdstr_help} " + \
                _tr("<command>") + "' " + _tr("to get help on the specific <command>.")
        self.help_text_clear = _tr("Clear the terminal screen.")
        self.help_text_config = \
                _tr("View current configuration or change one of the options.") + \
                '\n' + \
                f'  {cmdstr_config} {cmdstr_set} ' + _tr("<option>") + ' - ' + \
                _tr("set value for the <option>.") + \
                '\n' + \
                f'  {cmdstr_config} {cmdstr_show} - ' + \
                _tr("view current configuration.")
        self.help_text_download = f'{cmdstr_download} ' + _tr("<game> - download the <game>.")
        self.help_text_exit = _tr("Quit the application.")
        self.help_text_info = f'{cmdstr_info} ' + _tr("<game> - show information about the <game>.")
        self.help_text_install = f'{cmdstr_install} ' + _tr("<game> - install the <game>.")
        self.help_text_launch = f'{cmdstr_launch} ' + _tr("<game> - launch the <game>.")
        self.help_text_list = _tr("List games.") + '\n' + \
                f'  {cmdstr_list} {cmdstr_all} - ' + \
                _tr("list all owned games.") + '\n' + \
                f'  {cmdstr_list} {cmdstr_downloaded} - ' + \
                _tr("list only downloaded games.") + '\n' + \
                f'  {cmdstr_list} {cmdstr_installed} - ' + \
                _tr("list only installed games.")
        self.help_text_login = _tr("Log in to the GOG account.")
        self.help_text_logout = _tr("Log out from the GOG account.")
        self.help_text_queue = _tr("Manipulate the queue.") + '\n' + \
                f'  {cmdstr_queue} {cmdstr_add} ' + _tr("<game1, game2...>") + ' - ' + \
                _tr("add <game/games> to the queue. Simple regex supported.") + '\n' + \
                f'  {cmdstr_queue} {cmdstr_clear} - ' + \
                _tr("clear the queue.") + '\n' + \
                f'  {cmdstr_queue} {cmdstr_download} - ' + \
                _tr("download games from the queue.") + '\n' + \
                f'  {cmdstr_queue} {cmdstr_install} - ' + \
                _tr("install games from the queue.") + '\n' + \
                f'  {cmdstr_queue} {cmdstr_remove} ' + _tr("<game1, game2...>") + ' - ' + \
                _tr("remove <game/games> from the queue. Simple regex supported.") + '\n' + \
                f'  {cmdstr_queue} {cmdstr_show} - ' + \
                _tr("show the queue.") + '\n' + \
                f'  {cmdstr_queue} {cmdstr_uninstall} - ' + \
                _tr("uninstall games from the queue.")
        self.help_text_restart =_tr("Restart the application.")
        self.help_text_uninstall = f'{cmdstr_uninstall} ' + _tr("<game> - uninstall the <game>.")
        self.help_text_update = _tr("Update information about owned products.")
        self.help_text_user = _tr("Show information about the logged-in user.")

    def __colorize_text(self, text):
        return self.__ansi_text.fcolor_blue + \
                text + \
                self.__ansi_text.reset_all

    def _help(self):
        print(self.__colorize_text(self.help_available_commands))

    def clear(self):
        print(self.__colorize_text(self.help_text_clear))

    def config(self):
        print(self.__colorize_text(self.help_text_config))

    def download(self):
        print(self.__colorize_text(self.help_text_download))

    def exit(self):
        print(self.__colorize_text(self.help_text_exit))

    def info(self):
        print(self.__colorize_text(self.help_text_info))

    def install(self):
        print(self.__colorize_text(self.help_text_install))

    def launch(self):
        print(self.__colorize_text(self.help_text_launch))

    def list(self):
        print(self.__colorize_text(self.help_text_list))

    def login(self):
        print(self.__colorize_text(self.help_text_login))

    def logout(self):
        print(self.__colorize_text(self.help_text_logout))

    def queue(self):
        print(self.__colorize_text(self.help_text_queue))

    def restart(self):
        print(self.__colorize_text(self.help_text_restart))

    def uninstall(self):
        print(self.__colorize_text(self.help_text_uninstall))

    def update(self):
        print(self.__colorize_text(self.help_text_update))

    def user(self):
        print(self.__colorize_text(self.help_text_user))
