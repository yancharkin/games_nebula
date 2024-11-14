"""Module for working with anyting related to the GOG API."""
import urllib.request
from urllib.parse import quote
import json
import xml.etree.ElementTree as xml_ET
import os
import time

from games_nebula.apis.offlineapi import OfflineApi
from games_nebula import __user_agent__

GALAXY_ID = "46899977096215655"
GALAXY_SECRET = "9d85c43b1482497dbbce61f6e4aa173a433796eeae2ca8c5f6129f2dc4de46d9"
REDIRECT_URL = quote("https://embed.gog.com/on_login_success?origin=client")
AUTH_URL = (
        f'https://auth.gog.com/auth?'
        f'client_id={GALAXY_ID}&'
        f'redirect_uri={REDIRECT_URL}&'
        f'response_type=code&'
        f'layout=client2'
)

class GogToken():
    """Class for working with GOG tokens."""

    def __init__(self, config_dir):
        self.__token_file_path = f'{config_dir}/token.json'
        self._config_dir = config_dir
        self.__expiration = 0
        self.__access_token = None
        if os.path.exists(self.__token_file_path):
            token = self.__load_from_file()
            if 'expire_time' in token:
                if time.time() < token['expire_time']:
                    self.__expiration = token['expire_time']
                    self.__access_token = token['access_token']

    def get(self):
        """Return valid access token. If require, refresh it and save to file."""
        if time.time() > self.__expiration:
            try:
                if os.path.exists(self.__token_file_path):
                    token = self.__load_from_file()
                    refresh_token = token['refresh_token']
                    token = self.__request_refresh(refresh_token)
                else:
                    return None
                self.__access_token = token['access_token']
                self.__expiration = time.time() + token['expires_in'] - 300 # refresh a bit earlier
                token['expire_time'] = self.__expiration
                self.__save_to_file(token)
            except:
                return None
        return self.__access_token

    def get_new(self, login_code):
        """Request new access token using login code, return it and save to a file."""
        if login_code:
            try:
                token = self.__request_new(login_code)
                self.__access_token = token['access_token']
                self.__expiration = time.time() + token['expires_in'] - 300 # refresh a bit earlier
                token['expire_time'] = self.__expiration
                self.__save_to_file(token)
                return self.__access_token
            except Exception as e:
                print(e)
                return None
        return None

    def __load_from_file(self):
        with open(self.__token_file_path, 'r') as token_file:
            token = json.load(token_file)
        return token

    def __save_to_file(self, token):
        if not os.path.exists(self._config_dir):
            os.makedirs(self._config_dir)
        with open(self.__token_file_path, 'w') as token_file:
            json.dump(token, token_file, indent=2, sort_keys=False)

    def __request_new(self, login_code):
        token_url = (
                f'https://auth.gog.com/token'
                f'?client_id={GALAXY_ID}'
                f'&client_secret={GALAXY_SECRET}'
                f'&grant_type=authorization_code'
                f'&code={login_code}'
                f'&redirect_uri={REDIRECT_URL}'
        )
        return self.__request(token_url)

    def __request_refresh(self, refresh_token):
        token_url = (
                f'https://auth.gog.com/token'
                f'?client_id={GALAXY_ID}'
                f'&client_secret={GALAXY_SECRET}'
                f'&grant_type=refresh_token'
                f'&refresh_token={refresh_token}'
        )
        return self.__request(token_url)

    def __request(self, url):
        with urllib.request.urlopen(url) as response:
            token = json.loads(response.read())
            return token

class GogApi(OfflineApi):
    """Class for working with GOG API."""

    def __init__(self, config_dir):
        super().__init__(config_dir)
        self.__token = GogToken(config_dir)

    def is_available(self):
        """Check if GOG server available."""
        try:
            urllib.request.urlopen('https://api.gog.com/products')
            return True
        except:
            return False

    def get_products_list(self):
        """
        Get a list of ids of all owned products (alway request it from the GOG server).
        Inclues games, movies, dlcs, etc.
        """
        url = 'https://embed.gog.com/user/data/games'
        try:
            return json.loads(self.request(url))['owned']
        except:
            return []

    def get_user_info(self):
        if not self._user_info:
            url = 'https://embed.gog.com/userData.json'
            self._user_info = json.loads(self.request(url))
        return self._user_info

    def get_user_id(self):
        if not self._user_info:
            self.get_user_info()
        try:
            return self._user_info['galaxyUserId']
        except:
            return None

    def get_games_list(self, data_type='d'):
        if not self._games_list:
            return self.update_games_list()
        return self._games_list

    def get_game_info_details_1(self, key, locale='en'):
        game_id = self._convert_to_id(key)
        if (game_id in self._games_info_details_1.keys()) and \
                (locale == self._games_info_details_1[game_id][1]):
            game_info = self._games_info_details_1[game_id][0]
            return game_info
        else:
            try:
                url = (
                        f'https://api.gog.com/products/{game_id}'
                        f'?expand=downloads,description'
                        #f'?expand=downloads,expanded_dlcs,description,screenshots,'
                        #f'videos,related_products,changelog'
                        f'&locale={locale}'
                )
                game_info = json.loads(self.request(url))
                self._games_info_details_1[game_id] = (game_info, locale)
            except:
                game_info = {}
            return game_info

    def get_game_info_details_2(self, key, locale='en'):
        locale = self._convert_to_locale(locale)
        game_id = self._convert_to_id(key)
        if (game_id in self._games_info_details_2.keys()) and \
                (locale == self._games_info_details_2[game_id][1]):
            game_info = self._games_info_details_2[game_id][0]
            return game_info
        else:
            try:
                url = f'https://api.gog.com/v2/games/{game_id}?locale={locale}'
                game_info = json.loads(self.request(url))
                self._games_info_details_2[game_id] = (game_info, locale)
            except:
                game_info = {}
            return game_info

    def request(self, url):
        """Send request to the GOG server."""
        access_token = self.__token.get()
        request = urllib.request.Request(url)
        request.add_header('User-Agent', __user_agent__)
        request.add_header('Authorization', f'Bearer {access_token}')
        response = urllib.request.urlopen(request)
        return response.read()

    def is_authorized(self):
        """Check if user is authorized on the GOG server."""
        if self.__token.get():
            return True
        else:
            return False

    def login(self, login_code=None):
        """Log into a GOG account using login code."""
        if self.is_authorized() or not login_code:
            return
        self.__token.get_new(login_code)

    def update_games_list(self):
        """
        Get a list of owned games (with some info) from the GOG server.
        Includes only games, no packs, movies or dlcs.
        """
        try:
            games = []
            page = 1
            while True:
                url = (
                        f'https://embed.gog.com/account/getFilteredProducts'
                        f'?mediaType=1'
                        f'&sortBy=title'
                        f'&page={page}'
                )
                response = json.loads(self.request(url))
                games_n = response['totalProducts']
                games.extend(response['products'])
                if len(games) == games_n:
                    break
                page += 1
            self._games_list = games
        except:
            pass
        return self._games_list

    def get_installer_file_info(self, installer_file):
        """Return dictionary containing information about the installer_file."""
        response = json.loads(self.request(installer_file['downlink']))
        direct_link = response['downlink']
        checksum_url = response['checksum']
        try:
            # Have to use try ... except
            # At least for a few games (little_big_adventure 1 & 2) request for xml_data
            # failed with: http.client.IncompleteRead: IncompleteRead(0 bytes read, 1 more expected)
            xml_data = self.request(checksum_url)
            xml_root = xml_ET.fromstring(xml_data)
            file_name = xml_root.attrib['name']
            file_md5 = xml_root.attrib['md5']
            size = int(xml_root.attrib['total_size'])
        except:
            file_name = None
            file_md5 = None
            size = installer_file['size'] # not accurate for some reason (:<)
        file_info = {
                'name': file_name,
                'link': direct_link,
                'size': size,
                'md5': file_md5
        }
        return file_info
