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

global_dosbox =  global_config_parser.get('emulation settings', 'dosbox')
global_dosbox_path = global_config_parser.get('emulation settings', 'dosbox_path')
global_dosbox_version = global_config_parser.get('emulation settings', 'dosbox_version')
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

        config_file = self.install_dir + '/' + self.game_name + '/config.ini'
        config_parser = ConfigParser()
        config_parser.read(config_file)

        if not config_parser.has_section('Settings'):
            config_parser.add_section('Settings')

        if not config_parser.has_option('Settings', 'dosbox'):
            self.dosbox = 'global'
            config_parser.set('Settings', 'dosbox', str(self.dosbox))
        else:
            self.dosbox = config_parser.get('Settings', 'dosbox')

        if not config_parser.has_option('Settings', 'dosbox_path'):
            self.dosbox_path = global_dosbox_path
            config_parser.set('Settings', 'dosbox_path', str(self.dosbox_path))
        else:
            self.dosbox_path = config_parser.get('Settings', 'dosbox_path')

        if not config_parser.has_option('Settings', 'dosbox_version'):
            self.dosbox_version = global_dosbox_version
            config_parser.set('Settings', 'dosbox_version', str(self.dosbox_version))
        else:
            self.dosbox_version = config_parser.get('Settings', 'dosbox_version')

        if not config_parser.has_option('Settings', 'own_dosbox_mapperfile'):
            self.own_dosbox_mapperfile = False
            config_parser.set('Settings', 'own_dosbox_mapperfile', str(self.own_dosbox_mapperfile))
        else:
            self.own_dosbox_mapperfile = config_parser.getboolean('Settings', 'own_dosbox_mapperfile')

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

        config_parser.set('Settings', 'dosbox', str(self.dosbox))
        config_parser.set('Settings', 'dosbox_path', str(self.dosbox_path))
        config_parser.set('Settings', 'dosbox_version', str(self.dosbox_version))
        config_parser.set('Settings', 'own_dosbox_mapperfile', str(self.own_dosbox_mapperfile))
        config_parser.set('Settings', 'monitor', str(self.monitor))
        config_parser.set('Settings', 'launcher', str(self.launcher))
        config_parser.set('Settings', 'show_banner', str(self.show_banner))
        config_parser.set('Settings', 'command_before', str(self.command_before))
        config_parser.set('Settings', 'command_after', str(self.command_after))

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
            no_show_all = True,
            visible = self.show_banner
            )

        self.expander = Gtk.Expander(
            label = _("DOSBox"),
            )

        self.frame = Gtk.Frame(
            #label = _("DOSBox"),
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

        self.label_version = Gtk.Label(
            label = _("Version:"),
            halign = Gtk.Align.CENTER
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

        if self.dosbox == 'global':
            self.rbutton_global.set_active(True)
        elif self.dosbox == 'system':
            self.rbutton_sys.set_active(True)
        if self.dosbox == 'path':
            self.rbutton_path.set_label(_("From directory:"))
            self.rbutton_path.set_active(True)

        self.filechooser_button = Gtk.FileChooserButton(
            title = _("Select a directory"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            no_show_all = True
            )
        self.filechooser_button.set_filename(self.dosbox_path)

        self.combobox_version = Gtk.ComboBoxText(
            no_show_all = True
            )

        self.populate_dosbox_versions_combobox()

        self.filechooser_button.connect('file-set', self.cb_filechooser_button)
        self.combobox_version.connect('changed', self.cb_combobox_version)

        self.label_settings = Gtk.Label(
            label = _("Game specific DOSBox settings:"),
            halign = Gtk.Align.CENTER
            )

        self.checkbutton_own_mapper = Gtk.CheckButton(
            label = _("Use own mapperfile"),
            active = self.own_dosbox_mapperfile
            )
        self.checkbutton_own_mapper.connect('toggled', self.cb_checkbutton_own_mapper)

        self.button_remap_keys = Gtk.Button(
            label = _("Remap input"),
            tooltip_text = _("Mapper can be started in game by pressing Ctrl+F1"),
            no_show_all = True
            )
        self.button_remap_keys.connect('clicked', self.cb_button_remap_keys)
        self.button_remap_keys.set_visible(self.own_dosbox_mapperfile)

        self.button_dosbox_settings = Gtk.Button(
            label = _("More settings")
            )
        self.button_dosbox_settings.connect('clicked', self.cb_button_dosbox_settings)

        self.frame_grid.attach(self.label_version, 0, 0, 2, 1)
        self.frame_grid.attach(self.rbutton_global, 0, 1, 2, 1)
        self.frame_grid.attach(self.rbutton_sys, 0, 2, 2, 1)
        self.frame_grid.attach(self.rbutton_path, 0, 3, 2, 1)
        self.frame_grid.attach(self.filechooser_button, 0, 4, 1, 1)
        self.frame_grid.attach(self.combobox_version, 1, 4, 1, 1)
        self.frame_grid.attach(self.label_settings, 0, 5, 2, 1)
        self.frame_grid.attach(self.checkbutton_own_mapper, 0, 6, 1, 1)
        self.frame_grid.attach(self.button_remap_keys, 1, 6, 1, 1)
        self.frame_grid.attach(self.button_dosbox_settings, 0, 7, 2, 1)
        self.frame.add(self.frame_grid)
        self.expander.add(self.frame)

        self.rbutton_global.connect('toggled', self.cb_rbuttons)
        self.rbutton_sys.connect('toggled', self.cb_rbuttons)
        self.rbutton_path.connect('toggled', self.cb_rbuttons)

        if (self.dosbox == 'global') or (self.dosbox == 'system'):
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
            self.combobox_monitor.append_text(output.replace('\n', ''))

        self.combobox_monitor.set_active(self.monitor)

        self.combobox_monitor.connect('changed', self.cb_combobox_monitor)

        self.button_settings = Gtk.Button(
            label = _("Game settings"),
            no_show_all = True
            )
        if not os.path.exists(self.install_dir + '/' + self.game_name + '/dosbox_settings.conf'):
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
            halign = Gtk.Align.START,
            valign = Gtk.Align.START,
            label = _("Always show launcher"),
            active = self.launcher,
            )
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

    def populate_dosbox_versions_combobox(self):

        ver_list = []

        path = self.filechooser_button.get_filename()
        full_list = os.listdir(path)

        for o in full_list:
            if os.path.isdir(path + '/' + o):
                ver_list.append(o)

        ver_list = sorted(ver_list)

        for i in range(len(ver_list)):
            self.combobox_version.append_text(ver_list[i])
            if ver_list[i] == self.dosbox_version:
                self.combobox_version.set_active(i)

    def cb_filechooser_button(self, button):
        self.dosbox_path = button.get_filename()
        self.combobox_version.get_model().clear()
        self.populate_dosbox_versions_combobox()

    def cb_combobox_version(self, combobox):
        self.dosbox_version = combobox.get_active_text()

    def cb_rbuttons(self, button):
        if button.get_name() == 'global':
            self.rbutton_path.set_label(_("From directory"))
            self.filechooser_button.set_visible(False)
            self.combobox_version.set_visible(False)
            self.dosbox = 'global'
        elif button.get_name() == 'system':
            self.rbutton_path.set_label(_("From directory"))
            self.filechooser_button.set_visible(False)
            self.combobox_version.set_visible(False)
            self.dosbox = 'system'
        else:
            self.rbutton_path.set_label(_("From directory:"))
            self.filechooser_button.set_visible(True)
            self.combobox_version.set_visible(True)
            self.dosbox = 'path'

    def cb_combobox_monitor(self, combobox):
        self.monitor = combobox.get_active()

    def cb_button_dosbox_settings(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        dosbox_bin = self.set_dosbox_bin()

        dosbox_version = self.check_dosbox_version(dosbox_bin)

        self.create_link()

        subprocess.call([sys.executable, nebula_dir + '/settings_dosbox.py', \
                self.install_dir + '/' + self.game_name + '/dosbox.conf',
                'local', dosbox_version])

        #~ if (dosbox_version == 'stable') or (dosbox_version == 'svn'):
            #~ os.system('python ' + nebula_dir + '/settings_dosbox.py ' + \
            #~ self.install_dir + '/' + self.game_name + '/dosbox.conf local ' + dosbox_version)
        #~ elif dosbox_version == 'svn_daum':
            #~ os.system('python ' + nebula_dir + '/settings_dosbox_svn_daum.py ' + \
            #~ self.install_dir + '/' + self.game_name + '/dosbox.conf local ' + dosbox_version)

        self.main_window.show()

    def cb_checkbutton_own_mapper(self, button):

        self.own_dosbox_mapperfile = button.get_active()
        self.button_remap_keys.set_visible(button.get_active())

        game_dir = self.install_dir + '/' + self.game_name
        dosbox_conf = game_dir + '/dosbox.conf'

        if button.get_active() == True:

            dosbox_keymap_path = game_dir + '/dosbox_keymap'

            if not os.path.exists(dosbox_conf):
                open(dosbox_conf, 'a').close()

            config_parser = ConfigParser()
            config_parser.read(dosbox_conf)

            if not config_parser.has_section('sdl'):
                config_parser.add_section('sdl')

            config_parser.set('sdl', 'mapperfile', str(dosbox_keymap_path))

            new_config_file = open(dosbox_conf, 'w')
            config_parser.write(new_config_file)
            new_config_file.close()

        else:

            if os.path.exists(dosbox_conf):

                config_parser = ConfigParser()
                config_parser.read(dosbox_conf)

                if (config_parser.has_section('sdl')) and \
                        config_parser.has_option('sdl', 'mapperfile'):

                    config_parser.remove_option('sdl', 'mapperfile')

                if (len(config_parser.sections()) == 1) and \
                        (len(config_parser.options('sdl')) == 0):

                    if os.path.exists(dosbox_conf): os.remove(dosbox_conf)

    def cb_button_remap_keys(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        dosbox_bin = self.set_dosbox_bin()

        with open('/tmp/gn_tmp_dosbox.conf', 'w') as gn_tmp_dosbox_conf:
            gn_tmp_dosbox_conf.write('[autoexec]\n')
            gn_tmp_dosbox_conf.write('exit\n')

        gn_tmp_dosbox_conf.close()

        launch_command = dosbox_bin + ' -conf /tmp/gn_tmp_dosbox.conf' + \
        ' -conf "' + self.install_dir + '/' + self.game_name + '/dosbox.conf"' + \
        ' -startmapper'

        # TODO Make 'SDL_VIDEO_FULLSCREEN_HEAD' optional (?)
        os.system('export SDL_VIDEO_FULLSCREEN_HEAD=0 && ' + launch_command)

        if os.path.exists('/tmp/gn_tmp_dosbox.conf'): os.remove('/tmp/gn_tmp_dosbox.conf')

        self.main_window.show()

    def cb_button_game(self, button):
        self.launch_game()

    def launch_game(self):

        output = self.combobox_monitor.get_active_text().split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        dosbox_bin = self.set_dosbox_bin()

        self.create_link()

        launch_command = dosbox_bin + ' -conf "' + \
        os.getenv('HOME') + '/.games_nebula/config/dosbox.conf"' + \
        ' -conf "' + self.install_dir + '/' + self.game_name + '/dosbox.conf"' + \
        ' -conf "' + self.install_dir + '/' + self.game_name + '/dosbox_game.conf"'

        os.system(self.command_before)
        # FIX Make 'SDL_VIDEO_FULLSCREEN_HEAD' optional (?)
        os.system('export SDL_VIDEO_FULLSCREEN_HEAD=0 && ' + launch_command)
        os.system(self.command_after)

        output = self.monitor_primary.split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.config_save()

        sys.exit()

    def cb_button_settings(self, button):

        output = self.combobox_monitor.get_active_text().split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        dosbox_bin = self.set_dosbox_bin()

        self.create_link()

        launch_command = dosbox_bin + ' -conf "' + \
        os.getenv('HOME') + '/.games_nebula/config/dosbox.conf"' + \
        ' -conf "' + self.install_dir + '/' + self.game_name + '/dosbox.conf"' + \
        ' -conf "' + self.install_dir + '/' + self.game_name + '/dosbox_settings.conf"'

        # FIX Make 'SDL_VIDEO_FULLSCREEN_HEAD' optional (?)
        os.system('export SDL_VIDEO_FULLSCREEN_HEAD=0 && ' + launch_command)

        output = self.monitor_primary.split()[0]
        os.system('xrandr --output '+ output + ' --primary')

        self.main_window.show()

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

    def check_dosbox_version(self, dosbox_bin):

        proc = subprocess.Popen([dosbox_bin, '--version'],stdout=subprocess.PIPE)
        version_line = proc.stdout.readlines()[1].decode('utf-8')

        if 'SVN-Daum' in version_line:
            dosbox_version = 'svn_daum'
        elif 'SVN' in version_line:
            dosbox_version = 'svn'
        else:
            dosbox_version = 'stable'

        return dosbox_version

    def set_dosbox_bin(self):

        if self.dosbox == 'global':
            if global_dosbox == 'system':
                dosbox_bin = 'dosbox'
            if global_dosbox == 'path':
                dosbox_bin = '"' + global_dosbox_path + '/' + global_dosbox_version + '/bin/dosbox"'

        elif self.dosbox == 'system':
            dosbox_bin = 'dosbox'

        elif self.dosbox == 'path':
            dosbox_bin = '"' + self.dosbox_path + '/' + self.dosbox_version + '/bin/dosbox"'

        return dosbox_bin

    def create_link(self):
        link_dir = os.getenv('HOME') + '/.games_nebula/games/.dosbox/'
        link = link_dir + self.game_name
        game_dir = self.install_dir + '/' + self.game_name + '/game'
        if not os.path.exists(link_dir): os.makedirs(link_dir)
        if os.path.exists(link) or os.path.islink(link): os.remove(link)
        os.symlink(game_dir, link)

    def cb_entries(self, entry):
        if entry.get_name() == 'command_before':
            self.command_before = entry.get_text()
        if entry.get_name() == 'command_after':
            self.command_after = entry.get_text()

def main():
    import sys
    app = GUI(sys.argv[1])
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
