"""Allows easily set and get configuration options."""
import os
import json
import locale
import logging

from games_nebula.client.api_wrapper import Api
from games_nebula.client.translator import _tr
from games_nebula.client.utils.platform_name import platform_name

__logger = logging.getLogger(__name__)

CONFIG_DIR = f'{os.getenv("HOME")}/.config/games_nebula'
api = Api(CONFIG_DIR)

if platform_name:
    pref_os = platform_name
else:
    pref_os = 'windows'

__default_locale = 'en_US.UTF-8'
if locale.getlocale()[0] and locale.getlocale()[1]:
    __default_locale = '.'.join(locale.getlocale())

__DEFAULT_CONFIG = {
    'auto_db_update': True,
    'disable_colors': False,
    'download_dir': f'{os.getenv("HOME")}/Games/GOG/installers',
    'force_offline_mode': False,
    'images_size': 's',
    'icons_size': 's',
    'logos_width': 256,
    'install_dir': f'{os.getenv("HOME")}/Games/GOG',
    'keep_installers': True,
    'locale': __default_locale,
    'pref_lang': 'en',
    'pref_os': pref_os,
    'translate_commands': False,
    'translated_commands_only': False
}

if platform_name == 'linux': # and other UNIX-like?
    __DEFAULT_CONFIG.update({
        'use_dosbox': False,
        'use_scummvm': False,
        'use_wine': False
    })

__CONFIG = {}
__USER_ID = None
_USER_CONFIG_DIR = None
__CONFIG_FILE_PATH = None

def __update():
    global __USER_ID
    global _USER_CONFIG_DIR
    global __CONFIG_FILE_PATH
    __USER_ID = api.get_user_id()
    if __USER_ID:
        _USER_CONFIG_DIR = f'{CONFIG_DIR}/users/{__USER_ID}'
    else:
        _USER_CONFIG_DIR = f'{CONFIG_DIR}/users/tmp_user'
    __CONFIG_FILE_PATH = f'{_USER_CONFIG_DIR}/config.json'

def __save():
    global __CONFIG
    __update()
    if __USER_ID:
        try:
            if not os.path.exists(_USER_CONFIG_DIR):
                os.makedirs(_USER_CONFIG_DIR)
            with open(__CONFIG_FILE_PATH, 'w') as config_file:
                json.dump(__CONFIG, config_file, indent=2, sort_keys=False)
        except Exception as e:
            __logger.error(e)

def __load():
    global __CONFIG
    __update()
    if os.path.exists(__CONFIG_FILE_PATH):
        with open(__CONFIG_FILE_PATH, 'r') as config_file:
            __CONFIG = json.load(config_file)
    else:
        __CONFIG = __DEFAULT_CONFIG.copy()
        __save()

def set(option, value):
    """Set configuration option value."""
    global __CONFIG
    if value in ('true', 'True'):
        value = True
    elif value in ('false', 'False'):
        value = False
    if option == 'locale':
        try:
            locale.setlocale(locale.LC_ALL, value)
        except Exception as e:
            e.with_traceback
            __logger.warning(str(e).capitalize())
            return
        os.environ['LANG'] = value
    if (option == 'pref_os') and (value not in ('linux', 'mac', 'windows')):
        __logger.info(_tr("Invalid value for") + f" '{option}': '{value}'.")
        value = pref_os
    if option in __DEFAULT_CONFIG:
        __CONFIG[option] = value
        __save()

def get(option):
    """Get configuration option value."""
    global __CONFIG
    __load()
    try:
        return __CONFIG[option]
    except:
        if option in __DEFAULT_CONFIG:
            return __DEFAULT_CONFIG[option]
        else:
            __logger.info(_tr("Unknown option") + f": '{option}'.")
            return None

def get_all():
    """Return dictionary with all configuration options and their values."""
    global __CONFIG
    __load()
    config = {}
    for option in __DEFAULT_CONFIG:
        if option in __CONFIG:
            config[option] = __CONFIG[option]
        else:
            config[option] = __DEFAULT_CONFIG[option]
    return config

__update()
__load()
