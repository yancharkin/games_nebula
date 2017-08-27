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

sample_commands = {
    _("Disable output"):'xrandr --output <OUTPUT HERE> --off',
    _("Enable output"):'xrandr --output <OUTPUT HERE> --auto',
    _("Output position"):'xrandr --output <OUTPUT HERE> --auto <--left-of | --right-of | --above | --below> <ANOTHER OUTPUT HERE>',
    _("Panning"):'xrandr --output <OUTPUT HERE> --mode <RESOLUTION HERE> --panning <RESOLUTION HERE>',
    _("Reset gamma"):'xgamma -gamma 1'
}

sample_commands_list = sorted(sample_commands)

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

        self.start_gn_exists = os.path.exists(self.install_dir + '/' + self.game_name + '/start_gn.sh')
        self.start_gog_exists = os.path.exists(self.install_dir + '/' + self.game_name + '/start_gog.sh')

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)

        if not config_parser.has_section('Settings'):
            config_parser.add_section('Settings')

        if not config_parser.has_option('Settings', 'launcher_type'):
            if self.start_gog_exists:
                self.launcher_type = 'gog'
            else:
                self.launcher_type = 'gn'
            config_parser.set('Settings', 'launcher_type', self.launcher_type)
        else:
            self.launcher_type = config_parser.get('Settings', 'launcher_type')

        if not config_parser.has_option('Settings', 'monitor'):
            self.monitor = global_monitor
            config_parser.set('Settings', 'monitor', self.monitor)
        else:
            self.monitor = config_parser.getint('Settings', 'monitor')

        if not config_parser.has_option('Settings', 'launcher'):
            self.launcher = True
            config_parser.set('Settings', 'launcher', self.launcher)
        else:
            self.launcher = config_parser.getboolean('Settings', 'launcher')

        if not config_parser.has_option('Settings', 'show_banner'):
            self.show_banner = True
            config_parser.set('Settings', 'show_banner', self.show_banner)
        else:
           self.show_banner = config_parser.getboolean('Settings', 'show_banner')

        if not config_parser.has_option('Settings', 'command_before'):
            self.command_before = ''
            config_parser.set('Settings', 'command_before', self.command_before)
        else:
            self.command_before = config_parser.get('Settings', 'command_before')

        if not config_parser.has_option('Settings', 'command_after'):
            self.command_after = ''
            config_parser.set('Settings', 'command_after', self.command_after)
        else:
            self.command_after = config_parser.get('Settings', 'command_after')

        new_config_file = open(config_file, 'w')
        config_parser.write(new_config_file)
        new_config_file.close()

    def config_save(self):

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)

        config_parser.set('Settings', 'launcher_type', self.launcher_type)
        config_parser.set('Settings', 'monitor', self.monitor)
        config_parser.set('Settings', 'launcher', self.launcher)
        config_parser.set('Settings', 'show_banner', self.show_banner)
        config_parser.set('Settings', 'command_before', self.command_before)
        config_parser.set('Settings', 'command_after', self.command_after)

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

        if os.path.exists(goglib_banners_dir + '/' + self.game_name + '.jpg') and \
                os.path.exists(goglib_install_dir + '/' + self.game_name):
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
            label = _("Primary output:"),
            )
        self.combobox_monitor = Gtk.ComboBoxText()

        for output in self.monitors_list:
            self.combobox_monitor.append_text(output.translate(None, '\n'))
        self.combobox_monitor.set_active(self.monitor)

        self.combobox_monitor.connect('changed', self.cb_combobox_monitor)

        self.button_settings = Gtk.Button(
            label = _("Game settings"),
            no_show_all = True
            )

        if not os.path.exists(self.install_dir + '/' + self.game_name + '/settings.sh'):
            self.button_settings.set_visible(False)
        else:
            self.button_settings.set_visible(True)

        self.button_settings.connect('clicked', self.cb_button_settings)

        self.label_launcher = Gtk.Label(
            label = _("Use:"),
            no_show_all = True
            )

        self.radiobutton_gog_launcher = Gtk.RadioButton(
            label = _("GOG launcher"),
            name = 'gog',
            no_show_all = True
            )
        self.radiobutton_gn_launcher = Gtk.RadioButton(
            label = _("Games Nebula launcher"),
            name = 'gn',
            no_show_all = True
            )
        self.radiobutton_gn_launcher.join_group(self.radiobutton_gog_launcher)

        if self.launcher_type == 'gog':
            self.radiobutton_gog_launcher.set_active(True)
        else:
            self.radiobutton_gn_launcher.set_active(True)

        self.radiobutton_gog_launcher.connect('toggled', self.cb_radiobuttons)
        self.radiobutton_gn_launcher.connect('toggled', self.cb_radiobuttons)

        if self.start_gog_exists and self.start_gn_exists:
            self.label_launcher.set_visible(True)
            self.radiobutton_gn_launcher.set_visible(True)
            self.radiobutton_gog_launcher.set_visible(True)
        else:
            self.label_launcher.set_visible(False)
            self.radiobutton_gn_launcher.set_visible(False)
            self.radiobutton_gog_launcher.set_visible(False)

        expander_before = Gtk.Expander(
            label = _("Execute before launching the game")
            )
        grid_before = Gtk.Grid(
            margin_top = 10,
            row_spacing = 10,
            column_spacing = 5,
            )

        entry_before = Gtk.Entry(
            name = 'command_before',
            hexpand = True,
            text = self.command_before,
            sensitive = False
            )
        entry_before.connect('changed', self.cb_entries)

        def cb_button_edit_before(button):
            if entry_before.get_sensitive():
                entry_before.set_sensitive(False)
            else:
                entry_before.set_sensitive(True)

        img = Gtk.Image.new_from_icon_name("document-new", Gtk.IconSize.SMALL_TOOLBAR)
        button_edit_before = Gtk.Button(
            image = img,
            tooltip_text = _("Edit")
            )
        button_edit_before.connect('clicked', cb_button_edit_before)

        combobox_before = Gtk.ComboBoxText(
            hexpand = True,
            tooltip_text = _("Commands templates")
            )

        for command in sample_commands_list:
            combobox_before.append_text(command)
        combobox_before.set_active(0)

        def cb_button_add_before(button):
            new_command = sample_commands[combobox_before.get_active_text()]
            current_command = entry_before.get_text()
            if current_command == '':
                entry_before.set_text(new_command)
            else:
                entry_before.set_text(current_command + ' && ' + new_command)

        img = Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.SMALL_TOOLBAR)
        button_add_before = Gtk.Button(
            image = img,
            tooltip_text = _("Add command template")
            )
        button_add_before.connect('clicked', cb_button_add_before)

        grid_before.attach(entry_before, 0, 0, 1, 1)
        grid_before.attach(button_edit_before, 1, 0, 1, 1)
        grid_before.attach(combobox_before, 0, 1, 1, 1)
        grid_before.attach(button_add_before, 1, 1, 1, 1)
        expander_before.add(grid_before)

        expander_after = Gtk.Expander(
            label = _("Execute after exiting the game")
            )
        grid_after = Gtk.Grid(
            margin_top = 10,
            row_spacing = 10,
            column_spacing = 5,
            )
        entry_after = Gtk.Entry(
            name = 'command_after',
            hexpand = True,
            text = self.command_after,
            sensitive = False
            )
        entry_after.connect('changed', self.cb_entries)

        def cb_button_edit_after(button):
            if entry_after.get_sensitive():
                entry_after.set_sensitive(False)
            else:
                entry_after.set_sensitive(True)

        img = Gtk.Image.new_from_icon_name("document-new", Gtk.IconSize.SMALL_TOOLBAR)
        button_edit_after = Gtk.Button(
            image = img,
            tooltip_text = _("Edit")
            )
        button_edit_after.connect('clicked', cb_button_edit_after)

        combobox_after = Gtk.ComboBoxText(
            hexpand = True,
            tooltip_text = _("Commands templates")
            )

        for command in sample_commands_list:
            combobox_after.append_text(command)
        combobox_after.set_active(0)

        def cb_button_add_after(button):
            new_command = sample_commands[combobox_after.get_active_text()]
            current_command = entry_after.get_text()
            if current_command == '':
                entry_after.set_text(new_command)
            else:
                entry_after.set_text(current_command + ' && ' + new_command)

        img = Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.SMALL_TOOLBAR)
        button_add_after = Gtk.Button(
            image = img,
            tooltip_text = _("Add command template")
            )
        button_add_after.connect('clicked', cb_button_add_after)

        grid_after.attach(entry_after, 0, 0, 1, 1)
        grid_after.attach(button_edit_after, 1, 0, 1, 1)
        grid_after.attach(combobox_after, 0, 1, 1, 1)
        grid_after.attach(button_add_after, 1, 1, 1, 1)
        expander_after.add(grid_after)

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
        self.grid.attach(expander_before, 0, 1, 2, 1)
        self.grid.attach(expander_after, 0, 2, 2, 1)
        self.grid.attach(self.label_monitor, 0, 3, 1, 1)
        self.grid.attach(self.combobox_monitor, 1, 3, 1, 1)
        self.grid.attach(self.label_launcher, 0, 4, 1, 1)
        self.grid.attach(self.radiobutton_gog_launcher, 1, 4, 1, 1)
        self.grid.attach(self.radiobutton_gn_launcher, 1, 5, 1, 1)
        self.grid.attach(self.button_settings, 0, 6, 2, 1)
        self.grid.attach(self.button_game, 0, 7, 2, 1)
        self.grid.attach(self.checkbutton_show_launcher, 0, 8, 2, 1)
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

        self.switch_monitor('ON')

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        if self.launcher_type == 'gog':
            launch_command = self.install_dir + '/' + self.game_name + '/start_gog.sh'
        else:
            launch_command = self.install_dir + '/' + self.game_name + '/start_gn.sh'

        os.system(self.command_before)
        os.system(launch_command)
        os.system(self.command_after)

        self.switch_monitor('OFF')

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

    def cb_button_settings(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        launch_command = self.install_dir + '/' + self.game_name + '/settings.sh ' + \
        self.install_dir + ' ' + nebula_dir

        os.system(launch_command)

        self.config_save()
        os.execl(sys.executable, 'python', __file__, self.game_name)

    def cb_entries(self, entry):
        if entry.get_name() == 'command_before':
            self.command_before = entry.get_text()
        if entry.get_name() == 'command_after':
            self.command_after = entry.get_text()

    def switch_monitor(self, switch):
        if switch == 'ON':
            output = self.combobox_monitor.get_active_text().split()[0]
            os.system('xrandr --output '+ output + ' --primary')
        elif switch == 'OFF':
            output = self.monitor_primary.split()[0]
            os.system('xrandr --output '+ output + ' --primary')

def main():
    import sys
    app = GUI(sys.argv[1])
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
