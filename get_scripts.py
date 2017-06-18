#!/usr/bin/env python2
# -*- Mode: Python; coding: utf-8; -*-

import os, sys
import urllib2
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import ConfigParser
import gettext

from modules import mylib_get_data, goglib_get_data

global_config_file = os.getenv('HOME') + '/.games_nebula/config/config.ini'
global_config_parser = ConfigParser.ConfigParser()
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

nebula_dir = sys.path[0]
data_dir = os.getenv('HOME') + '/.games_nebula'
tmp = '/tmp'

gettext.bindtextdomain('games_nebula', nebula_dir + '/locale')
gettext.textdomain('games_nebula')
_ = gettext.gettext

class GUI:

    def __init__(self, lib, overwrite):
        
        self.lib = lib
        
        if overwrite == 'True':
            self.overwrite = True
        else:
            self.overwrite = False
        
        self.scripts_dir = os.getenv('HOME') + '/.games_nebula/scripts/' + self.lib
        self.get_scripts()
    
    def get_scripts(self):

        if self.lib == 'goglib':
            url = 'https://github.com/yancharkin/games_nebula_goglib_scripts/archive/master.zip'
        elif self.lib == 'mylib':
            url = 'https://github.com/yancharkin/games_nebula_mylib_scripts/archive/master.zip'
        
        req = urllib2.Request(url)
        
        try:

            archive_data = urllib2.urlopen(req).read()
            archive_path = tmp + '/' + self.lib + '_scripts.zip'
            archive_file = open(archive_path, 'wb')
            archive_file.write(archive_data)
            archive_file.close()
            
            self.unpack(archive_path)

        except urllib2.URLError as e:
            
            message_dialog = Gtk.MessageDialog(
                None,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                _("Error"),
                )
            message_dialog.format_secondary_text(str(e.reason))

            response = message_dialog.run()
            message_dialog.destroy()

            sys.exit()

        except urllib2.HTTPError as e:
            
            message_dialog = Gtk.MessageDialog(
            None,
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            _("Error"),
            )
            message_dialog.format_secondary_text(str(e.code) + ' ' + str(e.read()))

            response = message_dialog.run()
            message_dialog.destroy()

            sys.exit()

    def unpack(self, archive_path):
        os.system('7z x -aoa -o' + tmp + ' ' + archive_path)
        os.system('rm ' + tmp + '/games_nebula_' + self.lib + '_scripts-master/LICENSE > /dev/null 2>&1')
        
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
            
        git_sctipts = os.listdir(tmp + '/games_nebula_' + self.lib + '_scripts-master')
        existing_scripts = os.listdir(self.scripts_dir)
        
        new_scripts = []
        for script in git_sctipts:
            if script not in existing_scripts:
                new_scripts.append(script)
                if self.overwrite == False:
                    os.system('cp -r ' + tmp + '/games_nebula_' + self.lib + '_scripts-master/' + script \
                                + ' ' + self.scripts_dir)
        if self.overwrite == True:
            os.system('cp -r ' + tmp + '/games_nebula_' + self.lib + '_scripts-master/* ' + self.scripts_dir)
                  
        os.system('rm -r ' + tmp + '/games_nebula_' + self.lib + '_scripts-master')
        os.system('rm ' + tmp + '/' + self.lib + '_scripts.zip > /dev/null 2>&1')
        
        new_scripts = sorted(new_scripts)
        n_new_scripts = len(new_scripts)
        
        if self.lib == 'goglib':
        
            goglib_names = goglib_get_data.games_info(data_dir)[1]
            goglib_titles = goglib_get_data.games_info(data_dir)[2]
            
            name_to_title = {}
            
            for i in range(len(goglib_names)):
                name_to_title[goglib_names[i]] = goglib_titles[i]
            
            new_own_scripts = []
            for game in new_scripts:
                if game in goglib_names:
                    new_own_scripts.append(game)
        
        elif self.lib == 'mylib':
            
            mylib_names = mylib_get_data.games_info(data_dir)[1]
            mylib_titles = mylib_get_data.games_info(data_dir)[2]
            
            name_to_title = {}
            
            for i in range(len(mylib_names)):
                name_to_title[mylib_names[i]] = mylib_titles[i]
        
        message_dialog = Gtk.MessageDialog(
            None,
            0,
            Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,
            _("Completed successfully"),
            )
        message_dialog.set_property('window_position', Gtk.WindowPosition.CENTER_ALWAYS)
        message_dialog.set_property('default-width', 480)
        
        if len(new_scripts) != 0:
            message_dialog.format_secondary_text(_("New scripts downloaded"))
        else:
            message_dialog.format_secondary_text(_("No new scripts in repository"))
        
        content_area = message_dialog.get_content_area()
        content_area.set_property('margin-left', 10)
        content_area.set_property('margin-right', 10)
        content_area.set_property('margin-top', 10)
        content_area.set_property('margin-bottom', 10)
        action_area = message_dialog.get_action_area()
        action_area.set_property('spacing', 10)
        
        expander_new_all = Gtk.Expander(
            label = _("All new scripts (" + str(len(new_scripts)) + "):")
            )
            
        if len(new_scripts) == 0:
            expander_new_all.set_property('no-show-all', True)
            
        scrolled_window1 = Gtk.ScrolledWindow(
            height_request = 240
            )
        
        textbuffer1 = Gtk.TextBuffer()
        
        for i in range(len(new_scripts)):
            iter1 = textbuffer1.get_end_iter()
            textbuffer1.insert(iter1, name_to_title[new_scripts[i]] + '\n')
        
        textview1 = Gtk.TextView(
            buffer = textbuffer1,
            editable = False,
            cursor_visible = False
            )
        
        scrolled_window1.add(textview1)
        expander_new_all.add(scrolled_window1)
        
        content_area.pack_start(expander_new_all, True, True, 0)
        
        if self.lib == 'goglib':

            expander_new_own = Gtk.Expander(
                label = _("Scripts for games you own (" + str(len(new_own_scripts)) + "):")
                )
            
            if len(new_own_scripts) == 0:
                expander_new_own.set_property('no-show-all', True)
            
            scrolled_window_new_own = Gtk.ScrolledWindow(
                height_request = 240
                )
            
            textbuffer_new_own = Gtk.TextBuffer()
            
            for i in range(len(new_own_scripts)):
                iter_new_own = textbuffer_new_own.get_end_iter()
                textbuffer_new_own.insert(iter_new_own, name_to_title[new_own_scripts[i]] + '\n')
            
            textview_new_own = Gtk.TextView(
                buffer = textbuffer_new_own,
                editable = False,
                cursor_visible = False
                )
            
            scrolled_window_new_own.add(textview_new_own)
            expander_new_own.add(scrolled_window_new_own)

            content_area.pack_start(expander_new_own, True, True, 0)

        message_dialog.show_all()
        response = message_dialog.run()
        message_dialog.destroy()

        sys.exit()

def main():
    import sys
    app = GUI(sys.argv[1], sys.argv[2])
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
