from games_nebula.client import config
from games_nebula.client.translator import _tr

class ValidCommands:
    """All valid CLI application commands."""

    def __init__(self):
        self.translate_commands = config.get('translate_commands')
        self.translated_only = config.get('translated_commands_only')
        self.valid_commands = {
                _tr("clear"): 'clear',
                _tr("config"): 'config',
                _tr("download"): 'download',
                _tr("exit"): 'exit',
                _tr("info"): 'info',
                _tr("install"): 'install',
                _tr("launch"): 'launch',
                _tr("list"): 'list',
                _tr("restart"): 'restart',
                _tr("uninstall"): 'uninstall',
                _tr("update"): 'update',
                _tr("logout"): 'logout',
                _tr("login"): 'login',
                _tr("queue"): 'queue',
                _tr("help"): 'help',
                _tr("user"): 'user'
        }
        self.valid_config_commands = {
                _tr("set"): 'set',
                _tr("show"): 'show'
        }
        self.valid_list_commands = {
                _tr("all"): 'all',
                _tr("downloaded"): 'downloaded',
                _tr("installed"): 'installed'
        }
        self.valid_queue_commands = {
                _tr("add"): 'add',
                _tr("remove"): 'remove',
                _tr("show"): 'show',
                _tr("clear"): 'clear',
                _tr("download"): 'download',
                _tr("install"): 'install',
                _tr("uninstall"): 'uninstall'
        }
        self.valid_logout_commands = {
                _tr("completetely"): 'completetely'
        }
        if self.translate_commands:
            if self.translated_only:
                self.valid_commands_set = set(self.valid_commands.keys())
                self.valid_config_commands_set = set(self.valid_config_commands.keys())
                self.valid_list_commands_set = set(self.valid_list_commands.keys())
                self.valid_queue_commands_set = set(self.valid_queue_commands.keys())
                self.valid_logout_commands_set = set(self.valid_logout_commands.keys())
            else:
                self.valid_commands_set = set(list(self.valid_commands.keys()) + \
                        list(self.valid_commands.values()))
                self.valid_config_commands_set = set(list(self.valid_config_commands.keys()) + \
                        list(self.valid_config_commands.values()))
                self.valid_list_commands_set = set(list(self.valid_list_commands.keys()) + \
                        list(self.valid_list_commands.values()))
                self.valid_queue_commands_set = set(list(self.valid_queue_commands.keys()) + \
                        list(self.valid_queue_commands.values()))
                self.valid_logout_commands_set = set(list(self.valid_logout_commands.keys()) + \
                        list(self.valid_logout_commands.values()))
        else:
            self.valid_commands_set = set(self.valid_commands.values())
            self.valid_config_commands_set = set(self.valid_config_commands.values())
            self.valid_list_commands_set = set(self.valid_list_commands.values())
            self.valid_queue_commands_set = set(self.valid_queue_commands.values())
            self.valid_logout_commands_set = set(self.valid_logout_commands.values())
        self.__all_commands = self.valid_commands.copy()
        self.__all_commands.update(self.valid_config_commands)
        self.__all_commands.update(self.valid_list_commands)
        self.__all_commands.update(self.valid_queue_commands)
        self.__all_commands.update(self.valid_logout_commands)

    def get_cmd_uni_name(self, command):
        """Return command in English even if input command localized."""
        if command in self.__all_commands.keys():
            command = self.__all_commands[command]
        return command
