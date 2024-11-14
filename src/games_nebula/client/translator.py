"""Wrapper around gettext."""
import os
import gettext

if os.path.exists('../data/locale'):
    gettext.bindtextdomain('games_nebula', '../data/locale')
    gettext.bindtextdomain('argparse', '../data/locale') # argparse translation hack
else:
    gettext.bindtextdomain('games_nebula', '/usr/share/locale')
    gettext.bindtextdomain('argparse', '/usr/share/locale')
gettext.textdomain('games_nebula')

def _tr(text):
    return gettext.gettext(text)
