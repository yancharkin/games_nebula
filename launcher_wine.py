#!/usr/bin/env python2
# -*- Mode: Python; coding: utf-8; indent-tabs-install_mode: t; c-basic-offset: 4; tab-width: 4 -*-

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

global_wine =  global_config_parser.get('emulation settings', 'wine')
global_wine_path = global_config_parser.get('emulation settings', 'wine_path')
global_wine_version = global_config_parser.get('emulation settings', 'wine_version')
global_monitor = global_config_parser.getint('emulation settings', 'monitor')

goglib_install_dir = global_config_parser.get('goglib preferences', 'goglib_install_dir')
mylib_install_dir = global_config_parser.get('mylib preferences', 'mylib_install_dir')
goglib_download_dir = global_config_parser.get('goglib preferences', 'goglib_download_dir')
mylib_download_dir = global_config_parser.get('mylib preferences', 'mylib_download_dir')

nebula_dir = sys.path[0]
app_icon = GdkPixbuf.Pixbuf.new_from_file(nebula_dir + '/images/icon.png')

gettext.bindtextdomain('games_nebula', nebula_dir + '/locale')
gettext.textdomain('games_nebula')
_ = gettext.gettext

win_ver_dict = {
    'Windows 10' : 'win10',
    'Windows 8.1' : 'win81',
    'Windows 8' : 'win8',
    'Windows 2008 R2' : 'win2008r2',
    'Windows 7' : 'win7',
    'Windows 2008' : 'win2008',
    'Windows Vista' : 'vista',
    'Windows 2003' : 'win2003',
    'Windows XP' : 'winxp',
    'Windows 2000' : 'win2k',
    'Windows ME' : 'winme',
    'Windows 98' : 'win98',
    'Windows 95' : 'win95',
    'Windows NT 4.0' : 'nt40',
    'Windows NT 3.51' : 'nt351',
    'Windows 3.1' : 'win31',
    'Windows 3.0' : 'win30',
    'Windows 2.0' : 'win20'
}

class GUI:

    def __init__(self, game_name, exe_path):

        self.game_name = game_name
        self.exe_path = exe_path

        if os.path.exists(goglib_install_dir + '/' + game_name):
            self.install_dir = goglib_install_dir
        elif os.path.exists(mylib_install_dir + '/' + game_name):
            self.install_dir = mylib_install_dir

        if os.path.exists(goglib_download_dir + '/' + game_name):
            self.download_dir = goglib_download_dir
        elif os.path.exists(mylib_download_dir + '/' + game_name):
            self.download_dir = mylib_download_dir
        else:
            self.download_dir = os.getenv('HOME') + '/Downloads'

        self.config_load()

        self.own_prefix_path = self.install_dir + '/' + self.game_name + '/wine_prefix'
        self.common_prefix_path = os.getenv('HOME') + '/.games_nebula/wine_prefix'

        self.create_main_window()


    def config_load(self):

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)

        if not config_parser.has_section('Settings'):
            self.wine = 'global'
            self.wine_path = global_wine_path
            self.wine_version = global_wine_version
            self.monitor = global_monitor
            self.launcher = True
            self.show_banner = True
            self.win_ver = 0
            self.virtual_desktop = False
            self.virtual_desktop_width = ''
            self.virtual_desktop_height = ''
            self.mouse_capture = False
            self.own_prefix = False

            config_parser.add_section('Settings')
            config_parser.set('Settings', 'wine', self.wine)
            config_parser.set('Settings', 'wine_path', self.wine_path)
            config_parser.set('Settings', 'wine_version', self.wine_version)
            config_parser.set('Settings', 'monitor', self.monitor)
            config_parser.set('Settings', 'launcher', self.launcher)
            config_parser.set('Settings', 'show_banner', self.show_banner)
            config_parser.set('Settings', 'win_ver', self.win_ver)
            config_parser.set('Settings', 'virtual_desktop', self.virtual_desktop)
            config_parser.set('Settings', 'virtual_desktop_width', self.virtual_desktop_width)
            config_parser.set('Settings', 'virtual_desktop_height', self.virtual_desktop_height)
            config_parser.set('Settings', 'own_prefix', self.own_prefix)

            new_config_file = open(config_file, 'w')
            config_parser.write(new_config_file)
            new_config_file.close()

        else:
            self.wine = config_parser.get('Settings', 'wine')
            self.wine_path = config_parser.get('Settings', 'wine_path')
            self.wine_version = config_parser.get('Settings', 'wine_version')
            self.monitor = config_parser.getint('Settings', 'monitor')
            self.launcher = config_parser.getboolean('Settings', 'launcher')
            self.show_banner = config_parser.getboolean('Settings', 'show_banner')
            self.win_ver = config_parser.getint('Settings', 'win_ver')
            self.virtual_desktop = config_parser.getboolean('Settings', 'virtual_desktop')
            self.virtual_desktop_width = config_parser.get('Settings', 'virtual_desktop_width')
            self.virtual_desktop_height = config_parser.get('Settings', 'virtual_desktop_height')
            self.mouse_capture = config_parser.getboolean('Settings', 'mouse_capture')
            self.own_prefix = config_parser.getboolean('Settings', 'own_prefix')

    def config_save(self):

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)

        config_parser.set('Settings', 'wine', self.wine)
        config_parser.set('Settings', 'wine_path', self.wine_path)
        config_parser.set('Settings', 'wine_version', self.wine_version)
        config_parser.set('Settings', 'monitor', self.monitor)
        config_parser.set('Settings', 'launcher', self.launcher)
        config_parser.set('Settings', 'show_banner', self.show_banner)
        config_parser.set('Settings', 'win_ver', self.win_ver)
        config_parser.set('Settings', 'virtual_desktop', self.virtual_desktop)
        config_parser.set('Settings', 'virtual_desktop_width', self.virtual_desktop_width)
        config_parser.set('Settings', 'virtual_desktop_height', self.virtual_desktop_height)
        config_parser.set('Settings', 'mouse_capture', self.mouse_capture)
        config_parser.set('Settings', 'own_prefix', self.own_prefix)

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

        self.expander = Gtk.Expander(
            label = _("Wine")
            )

        self.frame = Gtk.Frame(
            #label = _("Wine"),
            label_xalign = 0.5,
            #margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.frame_grid = Gtk.Grid(
            column_homogeneous = True,
            #row_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.rbutton_global = Gtk.RadioButton(
            name = 'global',
            label = _("Global settings")
            )

        self.rbutton_sys = Gtk.RadioButton(
            name = 'system',
            label = _("System version")
            )
        self.rbutton_sys.join_group(self.rbutton_global)

        self.rbutton_path = Gtk.RadioButton(
            name = 'path',
            label = _("From directory")
            )
        self.rbutton_path.join_group(self.rbutton_global)

        if self.wine == 'global':
            self.rbutton_global.set_active(True)
        elif self.wine == 'system':
            self.rbutton_sys.set_active(True)
        if self.wine == 'path':
            self.rbutton_path.set_label(_("From directory:"))
            self.rbutton_path.set_active(True)

        self.filechooser_button = Gtk.FileChooserButton(
            title = _("Select a directory"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            no_show_all = True
            )
        self.filechooser_button.set_filename(self.wine_path)

        self.combobox_version = Gtk.ComboBoxText(
            no_show_all = True
            )

        self.populate_wine_versions_combobox()

        self.filechooser_button.connect('file-set', self.cb_filechooser_button)
        self.combobox_version.connect('changed', self.cb_combobox_version)

        self.label_win_ver = Gtk.Label(
            label = _("Windows version")
            )

        self.combobox_win_ver = Gtk.ComboBoxText()

        self.populate_win_ver_combobox()

        self.combobox_win_ver.connect('changed', self.cb_combobox_win_ver)

        self.checkbutton_prefix = Gtk.CheckButton(
            label = _("Use own wine prefix"),
            active = self.own_prefix
            )
        self.checkbutton_prefix.connect('toggled', self.cb_checkbutton_prefix)

        self.checkbutton_mouse = Gtk.CheckButton(
            label = _("Capture the mouse in fullscreen windows"),
            active = self.mouse_capture
            )
        self.checkbutton_mouse.connect('toggled', self.cb_checkbutton_mouse)

        self.checkbutton_virtual_desktop = Gtk.CheckButton(
            label = _("Emulate a virtual desktop"),
            active = self.virtual_desktop
            )
        self.checkbutton_virtual_desktop.connect('toggled', self.cb_checkbutton_virtual_desktop)

        self.entry_virt_width = Gtk.Entry(
            placeholder_text = _("Width"),
            max_length = 4,
            max_width_chars = 4,
            xalign = 0.5,
            text = self.virtual_desktop_width,
            no_show_all = True
            )
        self.entry_virt_width.set_visible(self.virtual_desktop)
        self.entry_virt_width.connect('changed', self.cb_entry_virt_width)

        self.entry_virt_height = Gtk.Entry(
            placeholder_text = _("Height"),
            max_length = 4,
            max_width_chars = 4,
            xalign = 0.5,
            text = self.virtual_desktop_height,
            no_show_all = True
            )
        self.entry_virt_height.set_visible(self.virtual_desktop)
        self.entry_virt_height.connect('changed', self.cb_entry_virt_height)

        self.label_version = Gtk.Label(
            label = _("Version:"),
            halign = Gtk.Align.CENTER,
            )

        self.label_specific_settings = Gtk.Label(
            label = _("Game specific Wine settings:"),
            halign = Gtk.Align.CENTER,
            )

        self.button_wine_settings = Gtk.Button(
            label = _("Current wine prefix settings")
            )
        self.button_wine_settings.connect('clicked', self.cb_button_wine_settings)

        self.frame_grid.attach(self.label_version, 0, 0, 2, 1)
        self.frame_grid.attach(self.rbutton_global, 0, 1, 2, 1)
        self.frame_grid.attach(self.rbutton_sys, 0, 2, 2, 1)
        self.frame_grid.attach(self.rbutton_path, 0, 3, 2, 1)
        self.frame_grid.attach(self.filechooser_button, 0, 4, 1, 1)
        self.frame_grid.attach(self.combobox_version, 1, 4, 1, 1)
        self.frame_grid.attach(self.label_specific_settings, 0, 5, 2, 1)
        self.frame_grid.attach(self.checkbutton_prefix, 0, 6, 2, 1)
        self.frame_grid.attach(self.checkbutton_mouse, 0, 7, 2, 1)
        self.frame_grid.attach(self.checkbutton_virtual_desktop, 0, 8, 2, 1)
        self.frame_grid.attach(self.entry_virt_width, 0, 9, 1, 1)
        self.frame_grid.attach(self.entry_virt_height, 1, 9, 1, 1)
        self.frame_grid.attach(self.label_win_ver, 0, 10, 1, 1)
        self.frame_grid.attach(self.combobox_win_ver, 1, 10, 1, 1)
        self.frame_grid.attach(self.button_wine_settings, 0, 11, 2, 1)
        self.frame.add(self.frame_grid)
        self.expander.add(self.frame)

        self.rbutton_global.connect('toggled', self.cb_rbuttons)
        self.rbutton_sys.connect('toggled', self.cb_rbuttons)
        self.rbutton_path.connect('toggled', self.cb_rbuttons)

        if (self.wine == 'global') or (self.wine == 'system'):
            self.filechooser_button.set_visible(False)
            self.combobox_version.set_visible(False)
        else:
            self.filechooser_button.set_visible(True)
            self.combobox_version.set_visible(True)

        self.label_monitor = Gtk.Label(
            label = _("Monitor"),
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

        self.button_game = Gtk.Button(
            label = _("Launch game")
            )

        self.button_game.connect('clicked', self.cb_button_game)

        self.checkbutton_show_launcher = Gtk.CheckButton(
            label = _("Always show launcher")
            )

        self.checkbutton_show_launcher.set_active(self.launcher)

        self.checkbutton_show_launcher.connect('clicked', self.cb_checkbutton_show_launcher)

        self.checkbutton_show_banner = Gtk.CheckButton(
            halign = Gtk.Align.END,
            valign = Gtk.Align.START,
            active = self.show_banner
            )

        self.checkbutton_show_banner.connect('toggled', self.cb_checkbutton_show_banner)

        self.grid.attach(self.checkbutton_show_banner, 0, 0, 2, 1)
        self.grid.attach(self.banner, 0, 0, 2, 1)
        self.grid.attach(self.expander, 0, 1, 2, 1)
        self.grid.attach(self.label_monitor, 0, 2, 1, 1)
        self.grid.attach(self.combobox_monitor, 1, 2, 1, 1)
        self.grid.attach(self.button_settings, 0, 3, 2, 1)
        self.grid.attach(self.button_game, 0, 4, 2, 1)
        self.grid.attach(self.checkbutton_show_launcher, 0, 5, 2, 1)
        self.main_window.add(self.grid)

        if self.launcher == True:
            self.main_window.show_all()
        else:
            self.launch_game()

    def populate_win_ver_combobox(self):

        self.combobox_win_ver.append_text(_("Global settings"))
        self.combobox_win_ver.append_text("Windows 10")
        self.combobox_win_ver.append_text("Windows 8.1")
        self.combobox_win_ver.append_text("Windows 8")
        self.combobox_win_ver.append_text("Windows 2008 R2")
        self.combobox_win_ver.append_text("Windows 7")
        self.combobox_win_ver.append_text("Windows 2008")
        self.combobox_win_ver.append_text("Windows Vista")
        self.combobox_win_ver.append_text("Windows 2003")
        self.combobox_win_ver.append_text("Windows XP")

        if self.wine_prefix_arch() != 64:
            self.combobox_win_ver.append_text("Windows 2000")
            self.combobox_win_ver.append_text("Windows ME")
            self.combobox_win_ver.append_text("Windows 98")
            self.combobox_win_ver.append_text("Windows 95")
            self.combobox_win_ver.append_text("Windows NT 4.0")
            self.combobox_win_ver.append_text("Windows NT 3.51")
            self.combobox_win_ver.append_text("Windows 3.1")
            self.combobox_win_ver.append_text("Windows 3.0")
            self.combobox_win_ver.append_text("Windows 2.0")

        self.combobox_win_ver.set_active(self.win_ver)

    def populate_wine_versions_combobox(self):

        ver_list = []

        path = self.filechooser_button.get_filename()
        full_list = os.listdir(path)

        for o in full_list:
            if os.path.isdir(path + '/' + o):
                ver_list.append(o)

        ver_list = sorted(ver_list)

        for i in range(len(ver_list)):
            self.combobox_version.append_text(ver_list[i])
            if ver_list[i] == self.wine_version:
                self.combobox_version.set_active(i)

    def wine_prefix_arch(self):
        if not os.path.exists(os.getenv('HOME') + '/.games_nebula/wine_prefix/drive_c/windows/syswow64'):
            return 32
        else:
            return 64

    def cb_filechooser_button(self, button):
        self.wine_path = button.get_filename()
        self.combobox_version.get_model().clear()
        self.populate_wine_versions_combobox()

    def cb_combobox_version(self, combobox):
        self.wine_version = combobox.get_active_text()

    def cb_rbuttons(self, button):
        if button.get_name() == 'global':
            self.rbutton_path.set_label(_("From directory"))
            self.filechooser_button.set_visible(False)
            self.combobox_version.set_visible(False)
            self.wine = 'global'
        elif button.get_name() == 'system':
            self.rbutton_path.set_label(_("From directory"))
            self.filechooser_button.set_visible(False)
            self.combobox_version.set_visible(False)
            self.wine = 'system'
        else:
            self.rbutton_path.set_label(_("From directory:"))
            self.filechooser_button.set_visible(True)
            self.combobox_version.set_visible(True)
            self.wine = 'path'

    def cb_combobox_monitor(self, combobox):
        self.monitor = combobox.get_active()


    def cb_combobox_win_ver(self, combobox):
        self.win_ver = combobox.get_active()

    def cb_button_wine_settings(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        if self.own_prefix == True:
            wineprefix_path = self.own_prefix_path
        else:
            wineprefix_path = self.common_prefix_path

        if self.wine == 'global':
            if global_wine == 'system':
                wine_path = 'wine'
            if global_wine == 'path':
                wine_path = global_wine_path + '/' + global_wine_version
        elif self.wine == 'system':
            wine_path = 'wine'
        elif self.wine == 'path':
            wine_path = self.wine_path + '/' + self.wine_version

        self.additions_setup(wine_path, wineprefix_path)

        os.system('python ' + nebula_dir + '/settings_wine.py ' + \
        wine_path + ' ' + wineprefix_path)

        self.main_window.show()

    def cb_button_settings(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        if self.own_prefix == True:
            wineprefix_path = self.own_prefix_path
        else:
            wineprefix_path = self.common_prefix_path

        if self.wine == 'global':
            if global_wine == 'system':
                wine_path = 'wine'
            if global_wine == 'path':
                wine_path = global_wine_path + '/' + global_wine_version
        elif self.wine == 'system':
            wine_path = 'wine'
        elif self.wine == 'path':
            wine_path = self.wine_path + '/' + self.wine_version

        self.additions_setup(wine_path, wineprefix_path)

        os.system(self.install_dir + '/' + self.game_name + '/settings.sh ' + \
        self.install_dir + ' ' + wine_path + ' ' + wineprefix_path + ' ' + nebula_dir)

        self.config_save()

        self.exe_path = self.get_new_exe_path()

        os.execl(sys.executable, 'python', __file__, self.game_name, self.exe_path)

    def get_new_exe_path(self):

        start_file = open(self.install_dir + '/' + self.game_name + '/start.sh', 'r')
        start_file_content = start_file.readlines()
        start_file.close()

        for line in start_file_content:
            if 'launcher_wine.py' in line:
                command_list = line.split(' ')
        
        del command_list[0:3]
        exe_path = ' '.join(command_list)

        return exe_path.translate(None, '"')

    def cb_button_game(self, button):
        self.config_save()
        self.launch_game()

    def launch_game(self):

        if self.own_prefix == True:
            wineprefix_path = self.own_prefix_path
        else:
            wineprefix_path = self.common_prefix_path

        output = self.combobox_monitor.get_active_text().split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        if self.wine == 'global':
            if global_wine == 'system':
                wine_bin = 'wine'
                wine_path = 'wine'
            if global_wine == 'path':
                wine_bin = global_wine_path + '/' + global_wine_version + '/bin/wine'
                wineserver_bin = global_wine_path + '/' + global_wine_version + '/bin/wineserver'
                wine_lib = global_wine_path + '/' + global_wine_version + '/lib'
                wine_path = global_wine_path + '/' + global_wine_version

        elif self.wine == 'system':
            wine_bin = 'wine'
            wine_path = 'wine'

        elif self.wine == 'path':
            wine_bin = self.wine_path + '/' + self.wine_version + '/bin/wine'
            wineserver_bin = self.wine_path + '/' + self.wine_version + '/bin/wineserver'
            wine_lib = self.wine_path + '/' + self.wine_version + '/lib'
            wine_path = self.wine_path + '/' + self.wine_version

        win_ver = self.combobox_win_ver.get_active_text()

        if '/' in self.exe_path:
            path_list = list(self.exe_path.split('/'))
            exe_name = path_list[-1]
            path_list.remove(exe_name)
            exe_path_no_exe = "/".join(path_list)
        else:
            exe_name = self.exe_path
            exe_path_no_exe = ''

        if self.combobox_win_ver.get_active_text() != _("Global settings"):
            win_ver_command = '$WINELOADER reg add "HKEY_CURRENT_USER\Software\Wine\AppDefaults\\' + \
                exe_name + '" /v "Version" /t REG_SZ /d ' + win_ver_dict[win_ver] + ' /f'
        else:
            win_ver_command = '$WINELOADER reg delete "HKEY_CURRENT_USER\Software\Wine\AppDefaults\\' + \
                exe_name + '" /f'

        if self.mouse_capture == True:
            mouse_capture_command = "$WINELOADER reg add 'HKEY_CURRENT_USER\Software\Wine\X11 Driver' /v 'GrabFullscreen' /t REG_SZ /d 'Y' /f"
        else:
            mouse_capture_command = "$WINELOADER reg add 'HKEY_CURRENT_USER\Software\Wine\X11 Driver' /v 'GrabFullscreen' /t REG_SZ /d 'N' /f"
        
        arg = ''
        if ' ' in exe_name:
            exe = exe_name.split('.exe ')[0] + '.exe'
            arg = exe_name.split('.exe ')[1]
            exe_name = exe

        if (self.virtual_desktop == True) and (self.virtual_desktop_width != '') \
        and (self.virtual_desktop_height != ''):
            launch_command = '$WINELOADER reg add "HKEY_USERS\S-1-5-21-0-0-0-1000\Control Panel\Colors" /v \
            "Background" /t REG_SZ /d "0 0 0" /f' + \
            ' && $WINELOADER explorer /desktop=' + self.game_name + ',' + \
            self.virtual_desktop_width + 'x' + self.virtual_desktop_height + \
            ' ' + '"' + exe_name + '" "' + arg + '"'
            
        elif self.virtual_desktop == True:
            launch_command = '$WINELOADER reg add "HKEY_USERS\S-1-5-21-0-0-0-1000\Control Panel\Colors" /v \
            "Background" /t REG_SZ /d "0 0 0" /f' + \
            ' && $WINELOADER explorer /desktop=' + self.game_name + ',' + \
            '640x480 ' + '"' + exe_name + '" "' + arg + '"'
        else:
            launch_command = '$WINELOADER "' + exe_name + '" "' + arg + '"'

        if (self.wine == 'path') or (self.wine == 'global' and global_wine == 'path'):

            full_command = 'export WINE=' + wine_bin + ' && ' + \
                'export WINELOADER=' + wine_bin + ' && ' + \
                'export WINESERVER=' + wineserver_bin + ' && ' + \
                'export WINEDLLPATH=' + wine_lib + ' && ' + \
                'export WINEPREFIX=' + wineprefix_path + ' && ' + \
                'cd "' + self.install_dir + '/' + self.game_name + '/game/' + exe_path_no_exe + '" && ' + \
                win_ver_command + '\n' + mouse_capture_command + '\n' + launch_command

        else:

            full_command = 'export WINELOADER=wine && ' + \
                'export WINEPREFIX=' + wineprefix_path + ' && ' + \
                'cd "' + self.install_dir + '/' + self.game_name + '/game/' + exe_path_no_exe + '" && ' + \
                win_ver_command + '\n' + mouse_capture_command + '\n' + launch_command

        self.additions_setup(wine_path, wineprefix_path)

        os.system(full_command)

        output = self.monitor_primary.split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        sys.exit()

    def additions_setup(self, wine_path, wineprefix_path):
        if (os.path.exists(self.install_dir + '/' + self.game_name + '/additions.sh')) and \
         (not os.path.exists(self.install_dir + '/' + self.game_name + '/.configured')):
            os.system(self.install_dir + '/' + self.game_name + '/additions.sh ' + \
            self.install_dir + ' ' + wine_path + ' ' + wineprefix_path + ' ' + self.download_dir)
            os.system('touch ' + self.install_dir + '/' + self.game_name + '/.configured')

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

    def cb_checkbutton_prefix(self, button):

        os.system('rm ' + self.install_dir + '/' + self.game_name + '/.configured')

        if button.get_active() == False:
            self.own_prefix = False
        else:
            self.own_prefix = True

    def cb_checkbutton_virtual_desktop(self, button):
        self.virtual_desktop = button.get_active()
        self.entry_virt_width.set_visible(button.get_active())
        self.entry_virt_height.set_visible(button.get_active())

    def cb_checkbutton_mouse(self, button):
        self.mouse_capture = button.get_active()

    def cb_entry_virt_width(self, entry):
        text = entry.get_text().strip()
        new_text = (''.join([i for i in text if i in '0123456789']))
        entry.set_text(new_text)
        self.virtual_desktop_width = new_text

    def cb_entry_virt_height(self, entry):
        text = entry.get_text().strip()
        new_text = (''.join([i for i in text if i in '0123456789']))
        entry.set_text(new_text)
        self.virtual_desktop_height = new_text

def main():
    import sys
    app = GUI(sys.argv[1], sys.argv[2])
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
