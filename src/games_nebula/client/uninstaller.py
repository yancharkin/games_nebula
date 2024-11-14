import os
import shutil
import logging

from games_nebula.client import config
from games_nebula.client import is_game_installed
from games_nebula.client.translator import _tr

class Uninstaller:
    def __init__(self, api):
        self.__api = api
        self.__all_games_list = []
        if self.__api.is_available():
            self.__all_games_list = [x['slug'] for x in api.get_games_list()]
        self.__logger = logging.getLogger(__name__)

    def uninstall(self, game_slug):
        """Uninstall a game."""
        game_installed, game_path = is_game_installed(game_slug)
        if game_installed or os.path.exists(os.path.dirname(game_path)):
            self.__logger.info(
                    _tr("Uninstalling") + f" '{game_slug}' " + \
                    _tr("from") + f" '{game_path}'."
            )
            game_path = os.path.split(game_path)[0]
            try:
                shutil.rmtree(game_path)
                game_path = os.path.split(game_path)[0]
                os.removedirs(game_path)
                game_path = os.path.split(game_path)[0]
                os.removedirs(game_path)
            except:
                pass
        elif game_slug in self.__all_games_list:
            self.__logger.info(f"'{game_slug}' " + _tr("not installed."))
        else:
            self.__logger.info(_tr("Invalid identifier") + f": '{game_slug}'.")
