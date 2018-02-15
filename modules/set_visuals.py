import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

try:
    from ConfigParser import ConfigParser as ConfigParser
except:
    from configparser import ConfigParser as ConfigParser

global_config_file = os.getenv('HOME') + '/.games_nebula/config/config.ini'
global_config_parser = ConfigParser()
global_config_parser.read(global_config_file)
gtk_theme = global_config_parser.get('visuals', 'gtk_theme')
gtk_dark = global_config_parser.getboolean('visuals', 'gtk_dark')
icon_theme = global_config_parser.get('visuals', 'icon_theme')
font = global_config_parser.get('visuals','font')
screen = Gdk.Screen.get_default()
gsettings = Gtk.Settings.get_for_screen(screen)
gsettings.set_property('gtk-theme-name', gtk_theme)
gsettings.set_property('gtk-application-prefer-dark-theme', gtk_dark)
gsettings.set_property('gtk-icon-theme-name', icon_theme)
gsettings.set_property('gtk-font-name', font)
