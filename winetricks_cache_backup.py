import sys, os, subprocess, re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import gettext

try:
    from ConfigParser import ConfigParser as ConfigParser
except:
    from configparser import ConfigParser as ConfigParser

nebula_dir = sys.path[0]
app_icon = GdkPixbuf.Pixbuf.new_from_file(nebula_dir + '/images/icon.png')

gettext.bindtextdomain('games_nebula', nebula_dir + '/locale')
gettext.textdomain('games_nebula')
_ = gettext.gettext

class GUI:

    def __init__(self):
        self.n_files_to_copy = 0
        self.config_load()
        self.create_main_window()

    def config_load(self):

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

        if not global_config_parser.has_section('goglib preferences'):
            global_config_parser.add_section('goglib preferences')

        if not global_config_parser.has_option('goglib preferences', 'goglib_download_dir'):
            goglib_download_dir = os.getenv('HOME') + '/.games_nebula/games/goglib/downloads'
            global_config_parser.set('goglib preferences', 'goglib_download_dir', str(goglib_download_dir))
        else:
            goglib_download_dir = global_config_parser.get('goglib preferences', 'goglib_download_dir')

        if not global_config_parser.has_section('emulation settings'):
            global_config_parser.add_section('emulation settings')

        if not global_config_parser.has_option('emulation settings', 'winetricks_cache'):
            self.winetricks_cache = os.getenv('HOME') + '/.cache/winetricks'
            global_config_parser.set('emulation settings', 'winetricks_cache', str(self.winetricks_cache))
        else:
            self.winetricks_cache = global_config_parser.get('emulation settings', 'winetricks_cache')

        if not global_config_parser.has_option('emulation settings', 'winetricks_cache_backup'):
            self.winetricks_cache_backup = goglib_download_dir + '/_winetricks_cache_backup'
            global_config_parser.set('emulation settings', 'winetricks_cache_backup', str(self.winetricks_cache_backup))
        else:
            self.winetricks_cache_backup = global_config_parser.get('emulation settings', 'winetricks_cache_backup')

        if not os.path.exists(self.winetricks_cache):
            os.system('mkdir -p ' + self.winetricks_cache)

        if not os.path.exists(self.winetricks_cache_backup):
            os.system('mkdir -p ' + self.winetricks_cache_backup)

        config_file = open(os.getenv('HOME') + '/.games_nebula/config/config.ini', 'w')
        global_config_parser.write(config_file)
        config_file.close()

    def config_save(self):

        config_file = os.getenv('HOME') + '/.games_nebula/config/config.ini'
        config_parser = ConfigParser()
        config_parser.read(config_file)

        config_parser.set('emulation settings', 'winetricks_cache', str(self.winetricks_cache))
        config_parser.set('emulation settings', 'winetricks_cache_backup', str(self.winetricks_cache_backup))

        new_config_file = open(os.getenv('HOME') + '/.games_nebula/config/config.ini', 'w')
        config_parser.write(new_config_file)
        new_config_file.close()

    def create_main_window(self):

        self.main_window = Gtk.Window(
            title = "Games Nebula",
            type = Gtk.WindowType.TOPLEVEL,
            window_position = Gtk.WindowPosition.CENTER_ALWAYS,
            resizable = False,
            icon = app_icon,
            #width_request = 180,
            #height_request = 240
            )

        self.main_window.connect('delete-event', Gtk.main_quit)

        grid = Gtk.Grid(
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            row_spacing = 10,
            column_spacing = 10
            )

        label_cache = Gtk.Label(
            label = _("Winetricks cache")
            )

        filechooserbutton_cache = Gtk.FileChooserButton(
            title = _("Winetricks cache"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            )
        filechooserbutton_cache.set_current_folder(self.winetricks_cache)
        filechooserbutton_cache.connect('file-set', self.cb_filechooserbutton_cache)

        label_cache_backup = Gtk.Label(
            label = _("Winetricks cache backup")
            )

        filechooserbutton_cache_backup = Gtk.FileChooserButton(
            title = _("Winetricks cache backup"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            )
        filechooserbutton_cache_backup.set_current_folder(self.winetricks_cache_backup)
        filechooserbutton_cache_backup.connect('file-set', self.cb_filechooserbutton_cache_backup)

        self.button_make_backup = Gtk.Button(
            label = _("Make backup")
            )
        self.button_make_backup.connect('clicked', self.cb_button_make_backup)

        self.button_restore_backup = Gtk.Button(
            label = _("Restore from backup")
            )
        self.button_restore_backup.connect('clicked', self.cb_button_restore_backup)

        self.progressbar = Gtk.ProgressBar(
            hexpand = True,
            show_text = True,
            text = _("Processing..."),
            pulse_step = 0.1,
            no_show_all = True
            )

        grid.attach(label_cache, 0, 0, 1, 1)
        grid.attach(filechooserbutton_cache, 1, 0, 1, 1)
        grid.attach(label_cache_backup, 0, 1, 1, 1)
        grid.attach(filechooserbutton_cache_backup, 1, 1, 1, 1)
        grid.attach(self.button_make_backup, 0, 2, 2, 1)
        grid.attach(self.button_restore_backup, 0, 3, 2, 1)
        grid.attach(self.progressbar, 0, 4, 2, 1)

        self.main_window.add(grid)

        self.main_window.show_all()

    def cb_filechooserbutton_cache(self, filechooserbutton):
        self.winetricks_cache = filechooserbutton.get_filename()

    def cb_filechooserbutton_cache_backup(self, filechooserbutton):
        self.winetricks_cache_backup = filechooserbutton.get_filename()

    def cb_button_make_backup(self, button):

        self.config_save()

        files_cache = os.listdir(self.winetricks_cache)
        files_backup = os.listdir(self.winetricks_cache_backup)

        files_to_copy = list(set(files_cache) - set(files_backup))
        self.n_files_to_copy = len(files_to_copy)

        if self.n_files_to_copy == 0:

            message_dialog = Gtk.MessageDialog(
                self.main_window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                _("Backup is up to date"),
                width_request = 360
                )
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('spacing', 10)

            self.main_window.hide()
            message_dialog.run()
            message_dialog.destroy()
            self.main_window.show()

        else:

            self.button_make_backup.set_visible(False)
            self.button_restore_backup.set_visible(False)
            self.progressbar.set_visible(True)

            for file_name in files_to_copy:
                self.copy_files(file_name, 'make_backup')

    def cb_button_restore_backup(self, button):

        self.config_save()

        files_cache = os.listdir(self.winetricks_cache)
        files_backup = os.listdir(self.winetricks_cache_backup)

        files_to_copy = list(set(files_backup) - set(files_cache))
        self.n_files_to_copy = len(files_to_copy)

        if self.n_files_to_copy == 0:

            message_dialog = Gtk.MessageDialog(
                self.main_window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                _("All files from backup exists in cache"),
                width_request = 360
                )
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('spacing', 10)

            self.main_window.hide()
            message_dialog.run()
            message_dialog.destroy()
            self.main_window.show()

        else:

            self.button_make_backup.set_visible(False)
            self.button_restore_backup.set_visible(False)
            self.progressbar.set_visible(True)

            for file_name in files_to_copy:
                self.copy_files(file_name, 'restore_backup')

    def copy_files(self, file_name, action):

        if action == 'make_backup':
            command = ['cp', '-R', self.winetricks_cache + '/' + file_name, self.winetricks_cache_backup]
        elif action == 'restore_backup':
            command = ['cp', '-R', self.winetricks_cache_backup + '/' + file_name, self.winetricks_cache]

        self.pid, stdin, stdout, stderr = GLib.spawn_async(command,
                                    flags=GLib.SpawnFlags.SEARCH_PATH|GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                                    standard_output=True,
                                    standard_error=True)

        io = GLib.IOChannel(stdout)

        self.source_id_out = io.add_watch(GLib.IO_IN|GLib.IO_HUP,
                             self.watch_process,
                             'copy_files',
                             priority=GLib.PRIORITY_HIGH)

    def watch_process(self, io, condition, process_name):

        if condition is GLib.IO_HUP:

            self.progressbar.pulse()

            self.n_files_to_copy -= 1

            if self.n_files_to_copy == 0:

                message_dialog = Gtk.MessageDialog(
                    self.main_window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    _("Done!"),
                    width_request = 360
                    )
                content_area = message_dialog.get_content_area()
                content_area.set_property('margin-left', 10)
                content_area.set_property('margin-right', 10)
                content_area.set_property('margin-top', 10)
                content_area.set_property('margin-bottom', 10)
                action_area = message_dialog.get_action_area()
                action_area.set_property('spacing', 10)

                self.main_window.hide()
                message_dialog.run()
                message_dialog.destroy()

                Gtk.main_quit()

            return False

        while Gtk.events_pending():
            Gtk.main_iteration_do(False)

        return True

def main():
    import sys
    app = GUI()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
