import os
import shutil
import sys
import json
import threading
import getpass
import logging
from html.parser import HTMLParser
import http.cookiejar
import urllib.request
from urllib.parse import urlencode

from games_nebula import __user_agent__
from games_nebula.apis import GogApi
from games_nebula.apis import OfflineApi
from games_nebula.apis.gogapi import AUTH_URL
from games_nebula.client.translator import _tr
from games_nebula.client.cli import ansi
from games_nebula.client.utils import convert_from_bytes
from games_nebula.client.utils import reinput

ansi_commands = ansi.AnsiCommands()
ansi_text = ansi.AnsiText()

class Api(OfflineApi):
    """Wrapper around GogApi and OfflienApi."""

    def __init__(self, config_dir, offline_mode=False):
        """
        The constractor for the Api class.
        Arguments:
            offline_mode: force usage of OfflineApi for some methods
            even if GogApi is available

        """
        super().__init__(config_dir)
        self.__logger = logging.getLogger(__name__)
        self._offline_mode = offline_mode
        self.__config_dir = config_dir
        self.__offlineapi = OfflineApi(config_dir)
        user_id = self.__offlineapi.get_user_id()
        if user_id:
            user_dir = f'{config_dir}/users/{user_id}'
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            self.__gogapi = GogApi(user_dir)
        else:
            user_dir = f'{config_dir}/users/tmp_user'
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            self.__gogapi = GogApi(user_dir)
            if self.is_online():
                user_id = self.__gogapi.get_user_id()
                if os.path.exists(f'{config_dir}/users/{user_id}'):
                    shutil.rmtree(f'{config_dir}/users/{user_id}')
                os.rename(user_dir, f'{config_dir}/users/{user_id}')
                self.update_localdb()

    def is_available(self):
        """
        Check if either GogApi or OfflineApi are available.
        Return values:
            0: not available
            1: basic info available (excludes: description, dlc info,
                installers, genres, store page)
            2: all info available
        """
        if self.is_offline_available() == 2:
            return 2
        elif self.is_online():
            return 2
        elif self.is_offline_available() == 1:
            return 1
        return 0

    #def get_user_info(self):
    #    return self.__api_call(sys._getframe().f_code.co_name)

    #def get_user_id(self):
    #    return self.__api_call(sys._getframe().f_code.co_name)

    #def get_products_list(self):
    #    return self.__api_call(sys._getframe().f_code.co_name)

    #def get_games_list(self):
    #    if not self._games_list:
    #        self._games_list = self.__api_call(sys._getframe().f_code.co_name)
    #    return self._games_list

    def get_game_info_details_1(self, key, locale='en'):
        self.__game_info_details_1 = \
                self.__api_call(sys._getframe().f_code.co_name, key=key, locale=locale)
        return self.__game_info_details_1

    def get_game_info_details_2(self, key, locale='en'):
        self.__game_info_details_2 = \
                self.__api_call(sys._getframe().f_code.co_name, key=key, locale=locale)
        return self.__game_info_details_2

    def get_installer_total_size(self, key, os='linux', lang='en', in_bytes=False):
        """
        Return size of all files in the game installer.
        By default convert bytes to largest possible unit and return tuple of
        strings: (size, unit). If in_bytes == True return size in bytes (integer).
        """
        size = self.__api_call(sys._getframe().f_code.co_name, key=key, os=os, lang=lang)
        if in_bytes:
            return size
        return convert_from_bytes(size)

    def get_game_logo_file_path(self, slug, size='s'):
        """Return path to the logo file."""
        return f'{self.__config_dir}/localdb/images/{size}/{slug}.jpg'

    def get_game_icon_file_path(self, slug, size='s'):
        """Return path to the icon file."""
        return f'{self.__config_dir}/localdb/icons/{size}/{slug}.png'

    def is_gog_available(self):
        """Check if GOG server available."""
        return self.__gogapi.is_available()

    def is_gog_authorized(self):
        """Check if a user is authorized on the GOG server."""
        return self.__gogapi.is_authorized()

    def is_online(self):
        """Check if the GOG server is available and if a user is authorized on it."""
        if self.is_gog_available() and self.is_gog_authorized():
            return True
        return False

    def login(self, login_code=None, username=None, password=None):
        """Log into a GOG account."""

        def _login(username=None, password=None, login_code=None):

            class _Html:
                def __init__(self):
                    self.tags = []

                class __HtmlTag:
                    def __init__(self, tag_name, attrs):
                        self._tag_name = tag_name
                        self._attrs = attrs
                        for attr in attrs:
                            setattr(self, f'_{attr[0]}', attr[1])
                    def __getattr__(self, attr):
                        return None

                class __HTMLParser(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self._tags = []
                    def handle_starttag(self, tag, attrs):
                        self._tags.append([tag, attrs])

                def parse(self, text):
                    parser = self.__HTMLParser()
                    parser.feed(text)
                    tags_list = parser._tags
                    parser.close()
                    for t in tags_list:
                        tag = self.__HtmlTag(t[0], t[1])
                        self.tags.append(tag)
                    return self.tags

            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            urllib.request.install_opener(opener)

            req = urllib.request.Request(AUTH_URL)
            req.add_header('User-Agent', __user_agent__)
            resp = urllib.request.urlopen(req)
            data = resp.read().decode('utf-8')
            if "g-recaptcha form__recaptcha" in data:
                self.__logger.info(_tr("Login form contains reCAPTCHA."))
            else:
                if not username or not '@' in username:
                    username = reinput(_tr("Email") + ': ')
                if not password:
                    password = getpass.getpass(_tr("Password") + ': ')
                    ansi_commands.erase_prev_line()
                login_data_1 = {
                    'login[username]': username,
                    'login[password]': password,
                    'login[login_flow]': 'default',
                    'login[_token]': None
                }
                tags = _Html().parse(data)
                for tag in tags:
                    if tag._id == 'login__token':
                        login_data_1['login[_token]'] = tag._value
                if login_data_1['login[_token]']:
                    req = urllib.request.Request(
                            'https://login.gog.com/login_check',
                            urlencode(login_data_1).encode()
                    )
                    req.add_header('User-Agent', __user_agent__)
                    resp = urllib.request.urlopen(req)
                    if 'two_step' in resp.url:
                        two_step_url = resp.url
                        login_data_2 = {
                            'second_step_authentication[send]': '',
                            'second_step_authentication[_token]': None
                        }
                        data = resp.read().decode('utf-8')
                        tags = _Html().parse(data)
                        for tag in tags:
                            if tag._id == 'second_step_authentication__token':
                                login_data_2['second_step_authentication[_token]'] = tag._value
                        if login_data_2['second_step_authentication[_token]']:
                            sc = reinput(
                                    _tr("Enter two-step security code") + ': ',
                                    length=4, numeric=True
                            )
                            login_data_2['second_step_authentication[token][letter_1]'] = sc[0]
                            login_data_2['second_step_authentication[token][letter_2]'] = sc[1]
                            login_data_2['second_step_authentication[token][letter_3]'] = sc[2]
                            login_data_2['second_step_authentication[token][letter_4]'] = sc[3]
                            req = urllib.request.Request(
                                    two_step_url,
                                    urlencode(login_data_2).encode()
                            )
                            req.add_header('User-Agent', __user_agent__)
                            resp = urllib.request.urlopen(req)
                            if 'on_login_success' in resp.url:
                                login_code = resp.url.split('client&code=')[1]
                    elif 'on_login_success' in resp.url:
                        login_code = resp.url.split('client&code=')[1]
                else:
                    self.__logger.error(_tr("Failed to obtain a login token."))

            if not login_code:
                print(_tr(
                    'Failed to log in. '
                    'Try again later or open this link in a browser and authorize:\n'
                    f'{ansi_text.fcolor_blue}{AUTH_URL}{ansi_text.reset_all}\n'
                    'After authorization you will be redirected to a '
                    'blank page. Login code is in the URL of this page '
                    'after "code=".'
                ))
                login_code = reinput(_tr("Paste or input it here") + ': ')
                if not login_code:
                    self.__logger.warning(_tr("Failed to log in."))
                    return

            self.__gogapi.login(login_code=login_code)

        self.logout()

        users_dir = f'{self._config_dir}/users'
        users_file_path = f'{users_dir}/users.json'

        user_id = None
        users_info = {}
        if os.path.exists(users_file_path):
            with open(users_file_path, 'r') as f:
                users_info = json.load(f)
        try:
            for key, value in users_info['users'].items():
                if type(value) == dict:
                    if username in value.values():
                        user_id = key
                        break
                if username == key:
                    user_id = key
                    break
        except:
            pass

        if user_id:
            users_info['currentUserId'] = user_id
            with open(users_file_path, 'w') as f:
                json.dump(users_info, f, indent=2, sort_keys=False)
        if (not user_id) or (not os.path.exists(f'{users_dir}/{user_id}/token.json')):
            _login(username=username, password=password)
        self.__init__(self.__config_dir, offline_mode=self._offline_mode)

    def logout(self, completely=False):
        """Logout from the GOG account."""
        users_dir = f'{self._config_dir}/users'
        users_file_path = f'{users_dir}/users.json'
        users_info = {}
        if os.path.exists(users_file_path):
            with open(users_file_path, 'r') as f:
                users_info = json.load(f)
        users_info['currentUserId'] = None
        if completely:
            user_id = self.get_user_id()
            if user_id:
                user_dir = f'{users_dir}/{user_id}'
                if os.path.exists(user_dir):
                    shutil.rmtree(user_dir)
            users_info['users'].pop(user_id, None)
        with open(users_file_path, 'w') as f:
            json.dump(users_info, f, indent=2, sort_keys=False)
        self.__init__(self.__config_dir, offline_mode=self._offline_mode)

    def update_games_list(self):
        """
        Get a list of owned games (with some info) from the GOG server.
        Includes only games, no packs, movies or dlcs.
        """
        self._games_list = self.__gogapi.update_games_list()
        return self._games_list

    def get_installer_file_info(self, installer_file):
        """
        Return dictionary containing information about the installer_file.
        Works only in online mode.
        """
        return self.__gogapi.get_installer_file_info(installer_file)

    def is_offline_available(self, locale='en'):
        """
        Check localdb availability (for a specific locale).
        Return values:
            0: not available
            1: basic info available (excludes: description, dlc info,
                installers, genres, stor page)
            2: all info available
        """
        return self.__offlineapi.is_available(locale=locale)

    def create_localdb(self, details=False, locale='en', noprint=False):
        """
        Create local DB. Overwrite if already exists.
        Data requested from the GOG server.
        """
        if self.is_online():
            user_info = self.__gogapi.get_user_info()
            user_id = user_info['galaxyUserId']
            user_dir = f'{self._config_dir}/users/{user_id}'
            users_file_path = f'{self._config_dir}/users/users.json'
            users_info = {}
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            if os.path.exists(users_file_path):
                with open(users_file_path, 'r') as f:
                    users_info = json.load(f)
            users_info['currentUserId'] = user_id
            if 'users' not in users_info:
                users_info['users'] = {}
            if user_id not in users_info['users']:
                users_info['users'][user_id] = {}
            users_info['users'][user_id]['username'] = user_info['username']
            users_info['users'][user_id]['email'] = user_info['email']
            with open(users_file_path, 'w') as f:
                json.dump(users_info, f, indent=2, sort_keys=False)
            with open(f'{self._config_dir}/users/{user_id}/user_info.json', 'w') as f:
                json.dump(user_info, f, indent=2, sort_keys=False)
            products_list = self.__gogapi.get_products_list()
            games_list = self.__gogapi.get_games_list()
            with open(f'{user_dir}/products_list.json', 'w') as products_list_f:
                json.dump(
                        {'owned': products_list}, products_list_f,
                        indent=2, sort_keys=False
                )
            with open(f'{user_dir}/games_list.json', 'w') as games_list_f:
                json.dump(games_list, games_list_f, indent=2, sort_keys=False)
            localdb_path = f'{self._config_dir}/localdb'
            if not os.path.exists(localdb_path):
                os.makedirs(localdb_path)
            if details:
                self.__save_details(localdb_path, products_list, locale, noprint)
        else:
            self.__logger.info(_tr("Impossible to create/update local DB in offline mode."))

    def update_localdb(self, details=False, locale='en', noprint=False):
        """
        Try to update localdb.
        Return True if successful or it's already up to date, False - otherwise.
        """
        if not self.is_offline_available():
            if self.is_online():
                try:
                    self.create_localdb(details=details, locale=locale, noprint=noprint)
                    return True
                except:
                    return False
            else:
                return False
        try:
            tmp_list1 = []
            tmp_list2 = []
            details_1_path = f'{self._config_dir}/localdb/details1/{locale}'
            details_2_path = f'{self._config_dir}/localdb/details2/{locale}'
            if os.path.exists(details_1_path):
                tmp_list1 = os.listdir(details_1_path)
            if os.path.exists(details_2_path):
                tmp_list2 = os.listdir(details_2_path)
            if len(tmp_list1) < len(tmp_list2):
                products_list_local = [int(fn.split('.json')[0]) for fn in tmp_list1]
            else:
                products_list_local = [int(fn.split('.json')[0]) for fn in tmp_list2]
            temp_list3 = self.__offlineapi.get_products_list()
            if len(temp_list3) < len(products_list_local):
                products_list_local = temp_list3
            products_list_gog = self.__gogapi.get_products_list()
            if sorted(products_list_local) == sorted(products_list_gog):
                return True
            self.create_localdb(details=False, noprint=noprint)
            if details:
                localdb_path = f'{self._config_dir}/localdb'
                products_list_new = []
                for prod_id in products_list_gog:
                    if prod_id not in products_list_local:
                        products_list_new.append(prod_id)
                self.__save_details(localdb_path, products_list_new, locale, noprint)
            return True
        except:
            return False

    def __save_details(self, localdb_path, products_list, locale, noprint=False):
        def get_details(products_list, locale, details_1_path, details_2_path):
            for prod_id in products_list:
                prod_slug = self.get_game_slug(prod_id)
                if not noprint:
                    ansi_commands.print_on_the_same_line(_tr("Getting info about") + f': {prod_slug}')
                prod_info_1 = self.__gogapi.get_game_info_details_1(prod_id, locale=locale)
                prod_info_2 = self.__gogapi.get_game_info_details_2(prod_id, locale=locale)
                with open(f'{details_1_path}/{prod_id}.json', 'w') as prod_info_f:
                    json.dump(prod_info_1, prod_info_f, indent=2, sort_keys=False)
                with open(f'{details_2_path}/{prod_id}.json', 'w') as prod_info_f:
                    json.dump(prod_info_2, prod_info_f, indent=2, sort_keys=False)

        details_1_path = f'{localdb_path}/details1/{locale}'
        details_2_path = f'{localdb_path}/details2/{locale}'
        if not os.path.exists(details_1_path):
            os.makedirs(details_1_path)
        if not os.path.exists(details_2_path):
            os.makedirs(details_2_path)

        # Split list into chunks
        # https://stackoverflow.com/a/37414115
        products_n  = len(products_list)
        chunks_n = 6
        products_list_chunks = []
        for i in range(chunks_n):
            start_i = i * (products_n // chunks_n) + min(i, products_n % chunks_n)
            end_i =(i+1) * (products_n // chunks_n) + min(i+1, products_n % chunks_n)
            products_list_chunks.append(products_list[start_i:end_i])

        threads = []
        for products_list in products_list_chunks:
            thread = threading.Thread(
                    target=get_details,
                    args=(products_list, locale, details_1_path, details_2_path),
                    daemon=True
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        if not noprint:
            ansi_commands.erase_line()

    def __api_call(self, func_name, *func_args, **func_kwargs):
        try:
            func_return = getattr(self.__offlineapi, func_name)(*func_args, **func_kwargs)
        except:
            func_return = None
        if func_return:
            return func_return
        else:
            if self.is_online() and not self._offline_mode:
                result = getattr(self.__gogapi, func_name)(*func_args, **func_kwargs)
                if func_name == 'get_game_info_details_1' or \
                        func_name == 'get_game_info_details_2':
                    locale = func_kwargs['locale']
                    prod_id = func_kwargs['key']
                    localdb_path = f'{self._config_dir}/localdb'
                    details_1_path = f'{localdb_path}/details1/{locale}'
                    details_2_path = f'{localdb_path}/details2/{locale}'
                    if not os.path.exists(details_1_path):
                        os.makedirs(details_1_path)
                    if not os.path.exists(details_2_path):
                        os.makedirs(details_2_path)
                    if func_name == 'get_game_info_details_1':
                        with open(f'{details_1_path}/{prod_id}.json', 'w') as prod_info_f:
                            json.dump(result, prod_info_f, indent=2, sort_keys=False)
                    if func_name == 'get_game_info_details_2':
                        with open(f'{details_2_path}/{prod_id}.json', 'w') as prod_info_f:
                            json.dump(result, prod_info_f, indent=2, sort_keys=False)
                return result
            else:
                # In offline mode if files for specified 'locale' not available
                # use 'en' files. All info still accurate (except for description,
                # it's in english).
                if func_name == 'get_game_info_details_1':
                    try:
                        return self.__offlineapi.get_game_info_details_1(func_kwargs['key'], locale='en')
                    except:
                        self.__logger.info(_tr("Not available in offline mode."))
                        return None
