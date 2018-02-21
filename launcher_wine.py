import sys, os, subprocess, re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import gettext

try:
    from ConfigParser import ConfigParser as ConfigParser
except:
    from configparser import ConfigParser as ConfigParser

from modules import monitors, paths

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

sample_commands = {
    _("Disable output"):'xrandr --output <OUTPUT HERE> --off',
    _("Enable output"):'xrandr --output <OUTPUT HERE> --auto',
    _("Output position"):'xrandr --output <OUTPUT HERE> --auto <--left-of | --right-of | --above | --below> <ANOTHER OUTPUT HERE>',
    _("Panning"):'xrandr --output <OUTPUT HERE> --mode <RESOLUTION HERE> --panning <RESOLUTION HERE>',
    _("Reset gamma"):'xgamma -gamma 1'
}

sample_commands_list = sorted(sample_commands)

class GUI:

    def __init__(self, game_name, exe_path):

        if exe_path == 'NOEXE':

            game_dir = goglib_install_dir + '/' + game_name

            message_dialog = Gtk.MessageDialog(
                None,
                0,
                Gtk.MessageType.OTHER,
                Gtk.ButtonsType.OK_CANCEL,
                _("Select the correct '.exe' file:")
                )
            message_dialog.set_property('default-width', 480)
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('spacing', 10)

            file_dialog = Gtk.FileChooserDialog(
            _("Select the correct '.exe' file"),
            None,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

            file_dialog.set_current_folder(game_dir + '/game')

            file_filter = Gtk.FileFilter()
            file_filter.set_name(_("DOS/Windows executable"))
            file_filter.add_pattern("*.exe")
            file_filter.add_pattern("*.Exe")
            file_filter.add_pattern("*.EXE")
            file_dialog.add_filter(file_filter)

            filechooserbutton = Gtk.FileChooserButton(
                dialog = file_dialog
                )

            entry = Gtk.Entry(
                placeholder_text = _("Arguments (optional)")
                )

            content_area.pack_start(filechooserbutton, True, True, 0)
            content_area.pack_start(entry, True, True, 0)
            content_area.show_all()

            response = message_dialog.run()

            if response == Gtk.ResponseType.OK:

                file_path = file_dialog.get_current_folder()
                exe_name = file_dialog.get_filename().split('/')[-1]
                arguments = entry.get_text()

                if file_path != '':

                    if file_path == game_dir + '/game':
                        new_exe_path = exe_name
                    else:
                        path1_list = (game_dir + '/game').split('/')
                        path2_list = file_path.split('/')

                        new_exe_path_list = []
                        for directory in path2_list:
                            if directory not in path1_list:
                                new_exe_path_list.append(directory)
                        new_exe_path_list.append(exe_name)

                        new_exe_path = '/'.join(new_exe_path_list)

                    message_dialog.destroy()

                    if arguments != '':
                        start_lines = ['#!/bin/bash\n', \
                        'python "$NEBULA_DIR/launcher_wine.py" ' + game_name + ' "' + \
                        new_exe_path + ' ' + arguments + '"']
                    else:
                        start_lines = ['#!/bin/bash\n', \
                        'python "$NEBULA_DIR/launcher_wine.py" ' + game_name + ' "' + \
                        new_exe_path + '"']

                    start_file = open(game_dir + '/start.sh', 'w')
                    for line in start_lines:
                        start_file.write(line)
                    start_file.close()

                    os.execl(sys.executable, sys.executable, __file__, game_name, new_exe_path)

                else:
                    message_dialog.destroy()
                    sys.exit()

            else:

                message_dialog.destroy()
                sys.exit()

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
        self.set_wineprefix()
        self.create_link()

        self.create_main_window()

    def config_load(self):

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser()
        config_parser.read(config_file)

        if not config_parser.has_section('Settings'):
            config_parser.add_section('Settings')

        if not config_parser.has_option('Settings', 'wine'):
            self.wine = 'global'
            config_parser.set('Settings', 'wine', str(self.wine))
        else:
            self.wine = config_parser.get('Settings', 'wine')

        if not config_parser.has_option('Settings', 'wine_path'):
            self.wine_path = global_wine_path
            config_parser.set('Settings', 'wine_path', str(self.wine_path))
        else:
            self.wine_path = config_parser.get('Settings', 'wine_path')

        if not config_parser.has_option('Settings', 'wine_version'):
            self.wine_version = global_wine_version
            config_parser.set('Settings', 'wine_version', str(self.wine_version))
        else:
            self.wine_version = config_parser.get('Settings', 'wine_version')

        if not config_parser.has_option('Settings', 'monitor'):
            self.monitor = global_monitor
            config_parser.set('Settings', 'monitor', str(self.monitor))
        else:
            self.monitor = config_parser.getint('Settings', 'monitor')

        if not config_parser.has_option('Settings', 'launcher'):
            self.launcher = True
            config_parser.set('Settings', 'launcher', str(self.launcher))
        else:
            self.launcher = config_parser.getboolean('Settings', 'launcher')

        if not config_parser.has_option('Settings', 'show_banner'):
            self.show_banner = True
            config_parser.set('Settings', 'show_banner', str(self.show_banner))
        else:
            self.show_banner = config_parser.getboolean('Settings', 'show_banner')

        if not config_parser.has_option('Settings', 'win_ver'):
            self.win_ver = 0
            config_parser.set('Settings', 'win_ver', str(self.win_ver))
        else:
            self.win_ver = config_parser.getint('Settings', 'win_ver')

        if not config_parser.has_option('Settings', 'virtual_desktop'):
            self.virtual_desktop = False
            config_parser.set('Settings', 'virtual_desktop', str(self.virtual_desktop))
        else:
            self.virtual_desktop = config_parser.getboolean('Settings', 'virtual_desktop')

        if not config_parser.has_option('Settings', 'virtual_desktop_width'):
            self.virtual_desktop_width = ''
            config_parser.set('Settings', 'virtual_desktop_width', str(self.virtual_desktop_width))
        else:
            self.virtual_desktop_width = config_parser.get('Settings', 'virtual_desktop_width')

        if not config_parser.has_option('Settings', 'virtual_desktop_height'):
            self.virtual_desktop_height = ''
            config_parser.set('Settings', 'virtual_desktop_height', str(self.virtual_desktop_height))
        else:
            self.virtual_desktop_height = config_parser.get('Settings', 'virtual_desktop_height')

        if not config_parser.has_option('Settings', 'mouse_capture'):
            self.mouse_capture = False
            config_parser.set('Settings', 'mouse_capture', str(self.mouse_capture))
        else:
            self.mouse_capture = config_parser.getboolean('Settings', 'mouse_capture')

        if not config_parser.has_option('Settings', 'own_prefix'):
            self.own_prefix = False
            config_parser.set('Settings', 'own_prefix', str(self.own_prefix))
        else:
            self.own_prefix = config_parser.getboolean('Settings', 'own_prefix')

        if not config_parser.has_option('Settings', 'winearch'):
            self.winearch = 'win32'
            config_parser.set('Settings', 'winearch', str(self.winearch))
        else:
            self.winearch = config_parser.get('Settings', 'winearch')

        if not config_parser.has_option('Settings', 'command_before'):
            self.command_before = ''
            config_parser.set('Settings', 'command_before', str(self.command_before))
        else:
            self.command_before = config_parser.get('Settings', 'command_before')

        if not config_parser.has_option('Settings', 'command_after'):
            self.command_after = ''
            config_parser.set('Settings', 'command_after', str(self.command_after))
        else:
            self.command_after = config_parser.get('Settings', 'command_after')

        new_config_file = open(config_file, 'w')
        config_parser.write(new_config_file)
        new_config_file.close()

    def config_save(self):

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser()
        config_parser.read(config_file)

        config_parser.set('Settings', 'wine', str(self.wine))
        config_parser.set('Settings', 'wine_path', str(self.wine_path))
        config_parser.set('Settings', 'wine_version', str(self.wine_version))
        config_parser.set('Settings', 'monitor', str(self.monitor))
        config_parser.set('Settings', 'launcher', str(self.launcher))
        config_parser.set('Settings', 'show_banner', str(self.show_banner))
        config_parser.set('Settings', 'win_ver', str(self.win_ver))
        config_parser.set('Settings', 'virtual_desktop', str(self.virtual_desktop))
        config_parser.set('Settings', 'virtual_desktop_width', str(self.virtual_desktop_width))
        config_parser.set('Settings', 'virtual_desktop_height', str(self.virtual_desktop_height))
        config_parser.set('Settings', 'mouse_capture', str(self.mouse_capture))
        config_parser.set('Settings', 'own_prefix', str(self.own_prefix))
        config_parser.set('Settings', 'command_before', str(self.command_before))
        config_parser.set('Settings', 'command_after', str(self.command_after))
        config_parser.set('Settings', 'winearch', str(self.winearch))

        new_config_file = open(config_file, 'w')
        config_parser.write(new_config_file)
        new_config_file.close()

    def get_banner(self):

        goglib_image_path = paths.get_image_path('goglib', self.game_name, 'normal', 'check')
        mylib_image_path = paths.get_image_path('mylib', self.game_name, 'check')

        if os.path.exists(goglib_image_path) and \
                os.path.exists(goglib_install_dir + '/' + self.game_name):
            self.banner_path = goglib_image_path
        else:
            self.banner_path = mylib_image_path

    def quit_app(self, window, event):
        self.config_save()
        Gtk.main_quit()

    def create_main_window(self):

        self.get_banner()
        self.monitors_list, self.monitor_primary = monitors.get_monitors()

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

        self.combobox_winearch = Gtk.ComboBoxText(
            tooltip_text = _("WINEARCH"),
            no_show_all = True
            )
        self.combobox_winearch.connect('changed', self.cb_combobox_winearch)

        self.win64_available()

        self.combobox_winearch.append_text('win32')
        self.combobox_winearch.append_text('win64')

        if self.winearch == 'win32':
            self.combobox_winearch.set_active(0)
        elif self.winearch == 'win64':
            self.combobox_winearch.set_active(1)

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
        self.frame_grid.attach(self.checkbutton_prefix, 0, 6, 1, 1)
        self.frame_grid.attach(self.combobox_winearch, 1, 6, 1, 1)
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

            try:
                self.combobox_monitor.append_text(output.translate(None, '\n'))
            except:
                char_map = str.maketrans('', '', '\n')
                self.combobox_monitor.append_text(output.translate(char_map))

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
        self.grid.attach(expander_before, 0, 2, 2, 1)
        self.grid.attach(expander_after, 0, 3, 2, 1)
        self.grid.attach(self.label_monitor, 0, 4, 1, 1)
        self.grid.attach(self.combobox_monitor, 1, 4, 1, 1)
        self.grid.attach(self.button_settings, 0, 5, 2, 1)
        self.grid.attach(self.button_game, 0, 6, 2, 1)
        self.grid.attach(self.checkbutton_show_launcher, 0, 7, 2, 1)
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

        ver_index = 0
        for i in range(len(ver_list)):
            self.combobox_version.append_text(ver_list[i])
            if ver_list[i] == self.wine_version:
                ver_index = i
        self.combobox_version.set_active(ver_index)

    def wine_prefix_arch(self):
        if not os.path.exists(os.getenv('HOME') + '/.games_nebula/wine_prefix/drive_c/windows/syswow64'):
            return 32
        else:
            return 64

    def cb_filechooser_button(self, button):
        self.wine_path = button.get_filename()
        self.combobox_version.get_model().clear()
        self.populate_wine_versions_combobox()
        self.win64_available()

    def cb_combobox_version(self, combobox):
        self.wine_version = combobox.get_active_text()
        self.win64_available()

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
        self.win64_available()

    def cb_combobox_monitor(self, combobox):
        self.monitor = combobox.get_active()


    def cb_combobox_win_ver(self, combobox):
        self.win_ver = combobox.get_active()

    def cb_button_wine_settings(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        self.set_wineprefix()
        self.create_link()

        self.set_environ()
        self.set_win_ver_command()
        self.set_additions_command()

        launch_command = 'python ' + nebula_dir + '/settings_wine.py'

        full_command = self.win_ver_command + '\n' + \
        self.additions_command + '\n' + \
        launch_command

        os.system(full_command)

        self.main_window.show()

    def cb_button_settings(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        self.set_wineprefix()
        self.create_link()

        self.set_environ()
        self.set_win_ver_command()
        self.set_additions_command()

        launch_command = self.install_dir + '/' + self.game_name + '/settings.sh'

        full_command = self.win_ver_command + '\n' + \
        self.additions_command + '\n' + \
        launch_command

        os.system(full_command)

        self.config_save()

        self.exe_path = self.get_new_exe_path()

        os.execl(sys.executable, sys.executable, __file__, self.game_name, self.exe_path)

    def get_new_exe_path(self):

        start_file = open(self.install_dir + '/' + self.game_name + '/start.sh', 'r')
        start_file_content = start_file.readlines()
        start_file.close()

        for line in start_file_content:
            if 'launcher_wine.py' in line:
                command_list = line.split(' ')

        del command_list[0:3]
        exe_path = ' '.join(command_list)

        try:
            exe_path = exe_path.translate(None, '"\n')
        except:
            char_map = str.maketrans('', '', '"\n')
            exe_path = exe_path.translate(char_map)

        return exe_path

    def get_wine_bin_path(self):

        if self.wine == 'global':
            if global_wine == 'system':
                wine_bin = 'wine'
                wineserver_bin = ''
                wine_lib = ''
            if global_wine == 'path':
                wine_path = global_wine_path + '/' + global_wine_version
                wine_bin = wine_path + '/bin/wine'
                wineserver_bin = wine_path + '/bin/wineserver'
                wine_lib = wine_path + '/lib'
        elif self.wine == 'system':
            wine_bin = 'wine'
            wineserver_bin = ''
            wine_lib = ''
        elif self.wine == 'path':
            wine_path = self.wine_path + '/' + self.wine_version
            wine_bin = wine_path + '/bin/wine'
            wineserver_bin = wine_path + '/bin/wineserver'
            wine_lib = wine_path + '/lib'

        return wine_bin, wineserver_bin, wine_lib

    def cb_button_game(self, button):
        self.config_save()
        self.launch_game()

    def launch_game(self):

        self.switch_monitor('ON')

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        self.set_environ()
        self.set_win_ver_command()
        self.set_mouse_capture_command()
        self.set_additions_command()
        self.set_launch_command()

        exe_name, exe_path_no_exe = self.get_exe_path()
        cd_command =    'cd "' + self.install_dir + '/' + self.game_name + \
                        '/game/' + exe_path_no_exe + '"'

        full_command = cd_command + '\n' + \
        self.win_ver_command + '\n' + \
        self.mouse_capture_command + '\n' + \
        self.additions_command + '\n' + \
        self.launch_command

        os.system(self.command_before)
        os.system(full_command)
        os.system(self.command_after)

        self.switch_monitor('OFF')

        sys.exit()

    def set_additions_command(self):

        self.set_wineprefix()
        self.create_link()

        self.set_environ()

        if (os.path.exists(self.install_dir + '/' + self.game_name + '/additions.sh')) and \
                (not os.path.exists(self.install_dir + '/' + self.game_name + '/.configured')):

            os.system('touch ' + self.install_dir + '/' + self.game_name + '/.configured')
            self.additions_command = self.install_dir + '/' + self.game_name + '/additions.sh'

        else:
            self.additions_command = ''

    def set_environ(self):

        self.set_wineprefix()
        self.create_link()

        wine_bin, \
        wineserver_bin, \
        wine_lib = self.get_wine_bin_path()

        os.environ['WINE'] = wine_bin
        os.environ['WINELOADER'] = wine_bin
        os.environ['WINEPREFIX'] = self.wineprefix

        if (self.wine == 'path') or (self.wine == 'global' and global_wine == 'path'):
            os.environ['WINESERVER'] = wineserver_bin
            os.environ['WINEDLLPATH'] = wine_lib

        os.environ['WINEARCH'] = self.winearch

    def set_win_ver_command(self):

        win_ver = self.combobox_win_ver.get_active_text()

        exe_name, exe_path_no_exe = self.get_exe_path()

        if self.combobox_win_ver.get_active_text() != _("Global settings"):
            self.win_ver_command = '$WINELOADER reg add "HKEY_CURRENT_USER\Software\Wine\AppDefaults\\' + \
                exe_name + '" /v "Version" /t REG_SZ /d ' + win_ver_dict[win_ver] + ' /f'
        else:
            self.win_ver_command = '$WINELOADER reg delete "HKEY_CURRENT_USER\Software\Wine\AppDefaults\\' + \
                exe_name + '" /f'

    def set_launch_command(self):

        exe_name, exe_path_no_exe = self.get_exe_path()

        arg = ''
        if ' ' in exe_name:
            tmp_list = exe_name.split('.exe ')
            if len(tmp_list) > 1:
                exe = exe_name.split('.exe ')[0] + '.exe'
                arg = exe_name.split('.exe ')[1]
                exe_name = exe

        if arg != '':
            if (self.virtual_desktop == True) and (self.virtual_desktop_width != '') \
            and (self.virtual_desktop_height != ''):
                self.launch_command = '$WINELOADER reg add "HKEY_USERS\S-1-5-21-0-0-0-1000\Control Panel\Colors" /v \
                "Background" /t REG_SZ /d "0 0 0" /f' + \
                ' && $WINELOADER explorer /desktop=' + self.game_name + ',' + \
                self.virtual_desktop_width + 'x' + self.virtual_desktop_height + \
                ' ' + '"' + exe_name + '" ' + arg

            elif self.virtual_desktop == True:
                self.launch_command = '$WINELOADER reg add "HKEY_USERS\S-1-5-21-0-0-0-1000\Control Panel\Colors" /v \
                "Background" /t REG_SZ /d "0 0 0" /f' + \
                ' && $WINELOADER explorer /desktop=' + self.game_name + ',' + \
                '640x480 ' + '"' + exe_name + '" ' + arg
            else:
                self.launch_command = '$WINELOADER "' + exe_name + '" ' + arg
        else:
            if (self.virtual_desktop == True) and (self.virtual_desktop_width != '') \
            and (self.virtual_desktop_height != ''):
                self.launch_command = '$WINELOADER reg add "HKEY_USERS\S-1-5-21-0-0-0-1000\Control Panel\Colors" /v \
                "Background" /t REG_SZ /d "0 0 0" /f' + \
                ' && $WINELOADER explorer /desktop=' + self.game_name + ',' + \
                self.virtual_desktop_width + 'x' + self.virtual_desktop_height + \
                ' ' + '"' + exe_name + '"'

            elif self.virtual_desktop == True:
                self.launch_command = '$WINELOADER reg add "HKEY_USERS\S-1-5-21-0-0-0-1000\Control Panel\Colors" /v \
                "Background" /t REG_SZ /d "0 0 0" /f' + \
                ' && $WINELOADER explorer /desktop=' + self.game_name + ',' + \
                '640x480 ' + '"' + exe_name + '"'
            else:
                self.launch_command = '$WINELOADER "' + exe_name + '"'

    def set_mouse_capture_command(self):
        if self.mouse_capture == True:
            self.mouse_capture_command = "$WINELOADER reg add 'HKEY_CURRENT_USER\Software\Wine\X11 Driver' /v 'GrabFullscreen' /t REG_SZ /d 'Y' /f"
        else:
            self.mouse_capture_command = "$WINELOADER reg add 'HKEY_CURRENT_USER\Software\Wine\X11 Driver' /v 'GrabFullscreen' /t REG_SZ /d 'N' /f"

    def set_wineprefix(self):
        if self.own_prefix == True:
            self.wineprefix = self.own_prefix_path
        else:
            self.wineprefix = self.common_prefix_path

    def create_link(self):
        link_dir = self.wineprefix + '/drive_c/Games/'
        link = link_dir + self.game_name
        game_dir = self.install_dir + '/' + self.game_name + '/game'
        os.system('mkdir -p ' + link_dir)
        os.system('rm ' + link + ' > /dev/null 2>&1')
        os.system('ln -s ' + game_dir + ' ' + link)

    def get_exe_path(self):

        if '/' in self.exe_path:
            path_list = list(self.exe_path.split('/'))
            exe_name = path_list[-1]
            path_list.remove(exe_name)
            exe_path_no_exe = "/".join(path_list)
        else:
            exe_name = self.exe_path
            exe_path_no_exe = ''

        return exe_name, exe_path_no_exe

    def switch_monitor(self, switch):
        if switch == 'ON':
            output = self.combobox_monitor.get_active_text().split()[0]
            os.system('xrandr --output '+ output + ' --primary')
        elif switch == 'OFF':
            output = self.monitor_primary.split()[0]
            os.system('xrandr --output '+ output + ' --primary')

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

        os.system('rm ' + self.install_dir + '/' + self.game_name + '/.configured' + ' > /dev/null 2>&1')

        if button.get_active() == False:
            self.own_prefix = False
            self.combobox_winearch.set_visible(False)
        else:
            self.own_prefix = True
            self.win64_available()

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

    def cb_entries(self, entry):
        if entry.get_name() == 'command_before':
            self.command_before = entry.get_text()
        if entry.get_name() == 'command_after':
            self.command_after = entry.get_text()

    def cb_combobox_winearch(self, combobox):
        self.winearch = combobox.get_active_text()

    def win64_available(self):

        wine_bin, \
        wineserver_bin, \
        wine_lib = self.get_wine_bin_path()

        dev_null = open(os.devnull, 'w')
        try:
            proc = subprocess.Popen([wine_bin + '64'], stdout=dev_null, \
                stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
            dev_null.close()
            stdoutdata, stderrdata = proc.communicate()
            if proc.returncode == 1:
                self.combobox_winearch.set_visible(True)
                return True
            else:
                self.combobox_winearch.set_visible(False)
                self.winearch = 'win32'
                return False
        except:
            self.combobox_winearch.set_visible(False)
            self.winearch = 'win32'
            return False

def main():
    import sys
    app = GUI(sys.argv[1], sys.argv[2])
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
