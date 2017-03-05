#!/usr/bin/env python2
# -*- Mode: Python; coding: utf-8; -*-

import sys, os, subprocess, re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import ConfigParser
import gettext

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

global_monitor = global_config_parser.getint('emulation settings', 'monitor')

goglib_install_dir = global_config_parser.get('goglib preferences', 'goglib_install_dir')
mylib_install_dir = global_config_parser.get('mylib preferences', 'mylib_install_dir')

nebula_dir = sys.path[0]
app_icon = GdkPixbuf.Pixbuf.new_from_file(nebula_dir + '/images/icon.png')

gettext.bindtextdomain('games_nebula', nebula_dir + '/locale')
gettext.textdomain('games_nebula')
_ = gettext.gettext

class GUI:

    def __init__(self, game_name):

        self.game_name = game_name

        if os.path.exists(goglib_install_dir + '/' + game_name):
            self.install_dir = goglib_install_dir
        elif os.path.exists(mylib_install_dir + '/' + game_name):
            self.install_dir = mylib_install_dir

        self.config_load()

        self.create_main_window()

    def config_load(self):

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)

        if not config_parser.has_section('Settings'):
            self.launcher_type = 'gog'
            self.monitor = global_monitor
            self.launcher = True
            self.show_banner = True

            config_parser.add_section('Settings')
            config_parser.set('Settings', 'launcher_type', self.launcher_type)
            config_parser.set('Settings', 'monitor', self.monitor)
            config_parser.set('Settings', 'launcher', self.launcher)
            config_parser.set('Settings', 'show_banner', self.show_banner)

            new_config_file = open(config_file, 'w')
            config_parser.write(new_config_file)
            new_config_file.close()

        else:
            self.launcher_type = config_parser.get('Settings', 'launcher_type')
            self.monitor = config_parser.getint('Settings', 'monitor')
            self.launcher = config_parser.getboolean('Settings', 'launcher')
            self.show_banner = config_parser.getboolean('Settings', 'show_banner')

    def config_save(self):

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)
        
        config_parser.set('Settings', 'launcher_type', self.launcher_type)
        config_parser.set('Settings', 'monitor', self.monitor)
        config_parser.set('Settings', 'launcher', self.launcher)
        config_parser.set('Settings', 'show_banner', self.show_banner)

        new_config_file = open(config_file, 'w')
        config_parser.write(new_config_file)
        new_config_file.close()

    def get_monitors(self):

        self.monitors_list = []
        proc = subprocess.Popen(['xrandr'],stdout=subprocess.PIPE)
        for line in proc.stdout.readlines():

            if re.compile(r'\b({0})\b'.format('connected'), flags=re.IGNORECASE).search(line):
                if 'primary' in line:
                    self.monitors_list.append(line.split(' ')[0] + ' ' + line.split(' ')[3].split('+')[0])
                else:
                    self.monitors_list.append(line.split(' ')[0] + ' ' + line.split(' ')[2].split('+')[0])
            if 'primary' in line:
                self.monitor_primary = line.split(' ')[0] + ' ' + line.split(' ')[3].split('+')[0]

    def get_banner(self):

        goglib_banners_dir = os.getenv('HOME') + '/.games_nebula/images/goglib_banners'
        mylib_banners_dir = os.getenv('HOME') + '/.games_nebula/images/mylib_banners'
        if os.path.exists(goglib_banners_dir + '/' + self.game_name + '.jpg'):
            self.banner_path = goglib_banners_dir + '/' + self.game_name + '.jpg'
        else:
            self.banner_path = mylib_banners_dir + '/' + self.game_name + '.jpg'

    def quit_app(self, window, event):
        self.config_save()
        Gtk.main_quit()

    def create_main_window(self):

        self.get_banner()
        self.get_monitors()

        self.main_window = Gtk.Window(
            title = _("Games Nebula"),
            type = Gtk.WindowType.TOPLEVEL,
            window_position = Gtk.WindowPosition.CENTER_ALWAYS,
            resizable = False,
            icon = app_icon,
            )
        self.main_window.connect('delete-event', self.quit_app)

        self.grid = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 10,
            column_spacing = 10,
            column_homogeneous = True,
            )

        self.banner = Gtk.Image(
            file = self.banner_path,
            no_show_all = True
            )

        self.banner.set_visible(self.show_banner)

        self.label_monitor = Gtk.Label(
            label = _("Monitor"),
            )
        self.combobox_monitor = Gtk.ComboBoxText()

        for output in self.monitors_list:
            self.combobox_monitor.append_text(output.translate(None, '\n'))
        self.combobox_monitor.set_active(self.monitor)

        self.combobox_monitor.connect('changed', self.cb_combobox_monitor)
        
        self.label_launcher = Gtk.Label(
            label = _("Use:"),
            )

        self.radiobutton_gog_launcher = Gtk.RadioButton(
            label = _("GOG launcher"),
            name = 'gog'
            )
        self.radiobutton_gn_launcher = Gtk.RadioButton(
            label = _("Games Nebula launcher"),
            name = 'gn'
            )
        self.radiobutton_gn_launcher.join_group(self.radiobutton_gog_launcher)
        
        if self.launcher_type == 'gog':
            self.radiobutton_gog_launcher.set_active(True)
        else:
            self.radiobutton_gn_launcher.set_active(True)
            
        self.radiobutton_gog_launcher.connect('toggled', self.cb_radiobuttons)
        self.radiobutton_gn_launcher.connect('toggled', self.cb_radiobuttons)

        self.button_game = Gtk.Button(
            label = _("Launch game")
            )
        self.button_game.connect('clicked', self.cb_button_game)

        self.checkbutton_show_launcher = Gtk.CheckButton(
            label = _("Always show launcher")
            )

        if self.launcher == True:
            self.checkbutton_show_launcher.set_active(True)
        else:
            self.checkbutton_show_launcher.set_active(False)

        self.checkbutton_show_launcher.connect('clicked', self.cb_checkbutton_show_launcher)

        self.checkbutton_show_banner = Gtk.CheckButton(
            halign = Gtk.Align.END,
            valign = Gtk.Align.START,
            active = self.show_banner
            )

        self.checkbutton_show_banner.connect('toggled', self.cb_checkbutton_show_banner)

        self.grid.attach(self.checkbutton_show_banner, 0, 0, 2, 1)
        self.grid.attach(self.banner, 0, 0, 2, 1)
        self.grid.attach(self.label_monitor, 0, 1, 1, 1)
        self.grid.attach(self.combobox_monitor, 1, 1, 1, 1)
        self.grid.attach(self.label_launcher, 0, 2, 1, 1)
        self.grid.attach(self.radiobutton_gog_launcher, 1, 2, 1, 1)
        self.grid.attach(self.radiobutton_gn_launcher, 1, 3, 1, 1)
        self.grid.attach(self.button_game, 0, 4, 2, 1)
        self.grid.attach(self.checkbutton_show_launcher, 0, 5, 2, 1)
        self.main_window.add(self.grid)

        if self.launcher == True:
            self.main_window.show_all()
        else:
            self.launch_game()

    def cb_combobox_monitor(self, combobox):
        self.monitor = combobox.get_active()

    def cb_button_game(self, button):
        self.launch_game()

    def launch_game(self):

        output = self.combobox_monitor.get_active_text().split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()
        
        if self.launcher_type == 'gog':
            launch_command = self.install_dir + '/' + self.game_name + '/start_gog.sh'
        else:
            launch_command = self.install_dir + '/' + self.game_name + '/start_gn.sh'

        os.system(launch_command)

        output = self.monitor_primary.split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.config_save()

        sys.exit()

    def cb_checkbutton_show_launcher(self, button):
        if button.get_active() == False:
            self.launcher = False
        else:
            self.launcher = True

    def cb_checkbutton_show_banner(self, button):
        if button.get_active() == False:
            self.show_banner = False
            self.banner.set_visible(False)
        else:
            self.show_banner = True
            self.banner.set_visible(True)
    
    def cb_radiobuttons(self, radiobutton):
        if radiobutton.get_active() == True:
            self.launcher_type = radiobutton.get_name()

def main():
    import sys
    app = GUI(sys.argv[1])
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
