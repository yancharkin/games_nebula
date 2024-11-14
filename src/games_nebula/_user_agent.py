import sys
import platform

from games_nebula import __version__

__python_version = sys.version.split()[0]
__system = platform.system()
__machine = platform.machine()
__pretty_name = None
__user_agent__ = None
try:
    __pretty_name = platform.freedesktop_os_release()['PRETTY_NAME']
except:
    pass
__user_agent__ = ((
        f'GamesNebula/{__version__} ({__system} {__machine}) '
        f'Python-urllib/{__python_version}'
))
if __pretty_name:
    __user_agent__ = ((
        f'GamesNebula/{__version__} ({__system} {__machine}; {__pretty_name}) '
        f'Python-urllib/{__python_version}'
))
