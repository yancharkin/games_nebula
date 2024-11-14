"""Module convert platfrom to platform name that used on GOG."""
from sys import platform

if 'linux' in platform:
    platform_name = 'linux'
elif 'darwin' in platform:
    platform_name = 'mac'
elif 'win' in platform:
    platform_name = 'windows'
else:
    platform_name = None
