import os
import json

class OfflineApi:
    """Class for working with offline collection of JSON files ("local DB")."""

    def __init__(self, config_dir):
        self._config_dir = config_dir
        self._user_info = {}
        self._games_list = []
        self._games_info_details_1 = {}
        self._games_info_details_2 = {}

    def is_available(self, locale='en'):
        """
        Check localdb availability (for a specific locale).
        Return values:
            0: not available
            1: basic info available (excludes: description, dlc info,
                installers, genres, stor page)
            2: all info available
        """
        available = 0
        user_id = self.get_user_id()
        if user_id:
            products_list_path = f'{self._config_dir}/users/{user_id}/products_list.json'
            games_list_path = f'{self._config_dir}/users/{user_id}/games_list.json'
            details_1_path = f'{self._config_dir}/localdb/details1/{locale}/'
            details_2_path = f'{self._config_dir}/localdb/details2/{locale}/'
            if os.path.exists(products_list_path) and os.path.exists(games_list_path):
                available += 1
                if os.path.exists(details_1_path) and os.path.exists(details_2_path):
                    available += 1
        return available

    def get_users(self):
        """Return a set of users authorized on GOG."""
        users = set()
        users_file_path = f'{self._config_dir}/users/users.json'
        if os.path.exists(users_file_path):
            with open(users_file_path, 'r') as f:
                users_dict = json.load(f)['users']
                for key in users_dict.keys():
                    users.add(users_dict[key]['username'])
        return users

    def get_user_id(self):
        """Return ID of the logged in user."""
        user_id = None
        users_file_path = f'{self._config_dir}/users/users.json'
        if os.path.exists(users_file_path):
            with open(users_file_path, 'r') as f:
                user_id = json.load(f)['currentUserId']
        return user_id

    def get_user_info(self):
        """Return info about the logged in user."""
        if not self._user_info:
            user_id = self.get_user_id()
            if user_id:
                user_info_path = f'{self._config_dir}/users/{user_id}/user_info.json'
                with open(user_info_path, 'r') as f:
                    self._user_info = json.load(f)
        return self._user_info

    def get_user_name(self):
        """Return name of the logged in user."""
        return self.get_user_info()['username']

    def get_user_email(self):
        """Return email of the logged in user."""
        return self.get_user_info()['email']

    def get_user_avatar_url(self):
        """Return user's avatar URL."""
        return self.get_user_info()['avatar'] + '.png'

    def get_products_list(self):
        """Return a list of ids of all owned products (games, movies, dlcs, etc.)."""
        products_list = []
        user_id = self.get_user_id()
        if user_id:
            user_dir = f'{self._config_dir}/users/{user_id}'
            products_list_path = f'{user_dir}/products_list.json'
            if os.path.exists(products_list_path):
                with open(products_list_path, 'r') as products_list_f:
                    products_list = json.load(products_list_f)['owned']
        return products_list

    def get_games_list(self, data_type='d'):
        """Return a a list of owned games."""
        if not self._games_list:
            user_id = self.get_user_id()
            if user_id:
                user_dir = f'{self._config_dir}/users/{user_id}'
                games_list_path = f'{user_dir}/games_list.json'
                if os.path.exists(games_list_path):
                    with open(games_list_path, 'r') as games_list_f:
                        self._games_list = json.load(games_list_f)
        return self._games_list

    def get_game_info_basics(self, key):
        """Return dictionary with basic information about the game."""
        if not self._games_list:
            self.get_games_list()
        game_id = self._convert_to_id(key)
        for game_info in self._games_list:
            if game_info['id'] == game_id:
                return game_info

    def get_game_id(self, game_slug):
        """Return game id."""
        return self.get_game_info_basics(game_slug)['id']

    def get_game_slug(self, game_id):
        """Return game slug (short name)."""
        try:
            return self.get_game_info_basics(game_id)['slug']
        except:
            # DLC
            try:
                return self.get_game_info_details_1(game_id)['slug']
            except:
                return None

    def get_game_oses(self, key):
        """Return list of OSes on which the game works."""
        game_id = self._convert_to_id(key)
        works_on = self.get_game_info_basics(game_id)['worksOn']
        return [key for key in works_on.keys() if works_on[key]]

    def get_game_category(self, key):
        """Return game category."""
        game_id = self._convert_to_id(key)
        return self.get_game_info_basics(game_id)['category']

    def get_game_tags(self, key):
        """Return game tags added by user."""
        game_id = self._convert_to_id(key)
        return self.get_game_info_basics(game_id)['tags']

    def get_game_title(self, key, locale='en'):
        """Return game title (full name)."""
        game_id = self._convert_to_id(key)
        try:
            return self.get_game_info_details_1(game_id, locale=locale)['title']
        except:
            try:
                return self.get_game_info_basics(game_id)['title']
            except:
                return None

    def get_game_logo_url(self, key, size='s'):
        """Return game logo URL."""
        sizes = {
                'xs': '_glx_logo.jpg',
                's': '_glx_logo_2x.jpg',
                's2': '_196.jpg', # a bit smaller than logo_2x
                'm': '_product_630.jpg',
                'm2': '_800.jpg', # same height as 630 but wider
                'l': '_product_630_2x.jpg',
                'l2': '_1600.jpg' # same height as 630_2x but wider
        }
        game_id = self._convert_to_id(key)
        try:
            # Works both for games and dlcs
            logo2x = self.get_game_info_details_1(game_id)["images"]["logo2x"]
            logo_url = f'https:{logo2x.split("_glx_logo_2x")[0]}'
        except:
            try:
                # Works only for games
                logo_url = f'https:{self.get_game_info_basics(game_id)["image"]}'
            except:
                # If only basic info available there is no way to get logo_url for DLC
                logo_url = None
        if logo_url:
            logo_url = f'{logo_url}{sizes[size]}'
        return logo_url

    def get_game_icon_url(self, key, size='s'):
        """Return game icon URL."""
        sizes = {
                's': 'sidebarIcon',
                'm': 'sidebarIcon2x',
                'l': 'icon'
        }
        game_id = self._convert_to_id(key)
        try:
            icon_url = self.get_game_info_details_1(game_id)["images"][sizes[size]]
            if icon_url != None:
                return f'https:{icon_url}'
        except:
            return None
        return None

    def get_game_info_details_1(self, key, locale='en'):
        """
        Return dictionary with detailed information about the game.
        Also works for movies.
        """
        game_id = self._convert_to_id(key)
        if (game_id in self._games_info_details_1.keys()) and \
                (locale == self._games_info_details_1[game_id][1]):
            game_info = self._games_info_details_1[game_id][0]
            return game_info
        else:
            details_1_path = f'{self._config_dir}/localdb/details1/{locale}/{game_id}.json'
            if not os.path.exists(details_1_path):
                return {}
            with open(details_1_path, 'r') as game_info_f:
                try:
                    game_info = json.load(game_info_f)
                    self._games_info_details_1[game_id] = (game_info, locale)
                except:
                    return {}
            return game_info

    def get_game_description(self, key, locale='en'):
        """Return game description."""
        game_id = self._convert_to_id(key)
        return self.get_game_info_details_1(game_id, locale=locale)['description']

    def get_game_languages(self, key, locale='en'):
        """Return languages that game supported."""
        game_id = self._convert_to_id(key)
        return self.get_game_info_details_1(game_id, locale=locale)['languages']

    def get_owned_dlcs(self, key):
        """Return the list of the game's DLCs that the user owns."""
        owned_products = self.get_products_list()
        owned_dlcs = []
        if self.get_game_info_details_1(key)['dlcs']:
            all_dlcs = self.get_game_info_details_1(key)['dlcs']['products']
            for dlc in all_dlcs:
                if dlc['id'] in owned_products:
                    owned_dlcs.append(dlc['id'])
        return owned_dlcs

    def get_dlc_slug(self, dlc_id):
        """Return DLC slug."""
        return self.get_game_slug(dlc_id)

    def get_dlc_title(self, dlc_id, locale='en'):
        """Return DLC title."""
        return self.get_game_title(dlc_id, locale=locale)

    def get_installer(self, key, os='linux', lang='en'):
        """
        Return dictionary containing information about an installer
        If possible return data for a given 'os' and 'lang', fallback
        values are 'windows' and 'en'.
        """
        game_id = self._convert_to_id(key)
        try:
            installers = self.get_game_info_details_1(game_id)['downloads']['installers']
        except:
            return None # if offline db not available
        if not installers:
            return None # Some games have no installers ('gwent_the_witcher_card_game')
        while True:
            for installer in installers:
                if installer['os'] == os and installer['language'] == lang:
                    return installer
            for installer in installers:
                if installer['os'] == os and installer['language'] == 'en':
                    return installer
            for installer in installers:
                if installer['os'] == 'windows' and installer['language'] == lang:
                    return installer
            for installer in installers:
                if installer['os'] == 'windows' and installer['language'] == 'en':
                    return installer

    def get_installer_version(self, key, os='linux', lang='en'):
        """Return a version of the game installer."""
        installer = self.get_installer(key, os=os, lang=lang)
        try:
            return installer['version']
        except:
            return None

    def get_installer_total_size(self, key, os='linux', lang='en'):
        """
        Return size of all files in the game installer.
        """
        installer = self.get_installer(key, os=os, lang=lang)
        try:
            return installer['total_size']
        except:
            return 0

    def get_installer_files(self, key, os='linux', lang='en'):
        """Return a list of files in the game installer."""
        installer = self.get_installer(key, os=os, lang=lang)
        return installer['files']

    def get_game_info_details_2(self, key, locale='en'):
        """
        Return dictionary with detailed information about the game.
        Differences with get_game_info_details_1: valid store page link (not
        always the case with first method), publisher, developer, genres (tags),
        system requirements and few more. Doesn't work for movies.
        """
        game_id = self._convert_to_id(key)
        if (game_id in self._games_info_details_2.keys()) and \
                (locale == self._games_info_details_2[game_id][1]):
            game_info = self._games_info_details_2[game_id][0]
            return game_info
        else:
            details_2_path = f'{self._config_dir}/localdb/details2/{locale}/{game_id}.json'
            if not os.path.exists(details_2_path):
                return {}
            with open(details_2_path, 'r') as game_info_f:
                try:
                    game_info = json.load(game_info_f)
                    self._games_info_details_2[game_id] = (game_info, locale)
                except:
                    return {}
            return game_info

    def get_game_genres(self, key, locale='en'):
        """Return list of game genres."""
        game_id = self._convert_to_id(key)
        game_info = self.get_game_info_details_2(game_id, locale=locale)
        try:
            return [genre['name'] for genre in game_info['_embedded']['tags']]
        except:
            return []

    def get_game_publisher(self, key, locale='en'):
        """Return the game publisher."""
        game_id = self._convert_to_id(key)
        game_info = self.get_game_info_details_2(game_id, locale=locale)
        try:
            return game_info['_embedded']['publisher']['name']
        except:
            return ''

    def get_game_developers(self, key, locale='en'):
        """Return the list of game developers"""
        game_id = self._convert_to_id(key)
        game_info = self.get_game_info_details_2(game_id, locale=locale)
        try:
            return [developer['name'] for developer in game_info['_embedded']['developers']]
        except:
            return []

    def get_game_store_page(self, key):
        """Return game store page url."""
        game_id = self._convert_to_id(key)
        try:
            return self.get_game_info_details_2(game_id)['_links']['store']['href']
        except:
            return ''

    #def get_bonus_content(self, key):
    #    game_id = self._convert_to_id(key)
    #    return self.get_game_info_details_1(game_id)['downloads']['bonus_content']

    def _convert_to_id(self, key):
        try:
            key = int(key)
        except:
            pass
        if type(key) == int:
            return key
        elif type(key) == str:
            if not self._games_list:
                self.get_games_list()
            for game_info in self._games_list:
                if game_info['slug'] == key:
                    return game_info['id']

    def _convert_to_lang(self, locale):
        return locale.split('_')[0]

    def _convert_to_locale(self, lang):
        locales = {
                'en': 'en-US',
                'de': 'de-DE',
                'fr': 'fr-FR',
                'pl': 'pl-PL',
                'ru': 'ru-RU',
                'zh': 'zh-Hans'
        }
        if lang not in locales:
            lang = 'en'
        return locales[lang]
