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

nebula_dir = sys.path[0]
app_icon = GdkPixbuf.Pixbuf.new_from_file(nebula_dir + '/images/icon.png')

gettext.bindtextdomain('games_nebula', nebula_dir + '/locale')
gettext.textdomain('games_nebula')
_ = gettext.gettext

class GUI:

    def __init__(self):
        self.wineprefix_path = os.getenv('WINEPREFIX')
        self.create_main_window()

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

        self.box = Gtk.Box(
            orientation = Gtk.Orientation.VERTICAL,
            margin_top = 5,
            margin_bottom = 5,
            margin_left = 5,
            margin_right = 5,
            spacing = 5,
            )

        self.button_add_remove = Gtk.Button(
            label = _("Add/remove programs")
            )
        self.button_add_remove.connect('clicked', self.cb_button_add_remove)

        self.button_run = Gtk.Button(
            label = _("Run in current prefix...")
            )
        self.button_run.connect('clicked', self.cb_button_run)

        self.button_open_prefix = Gtk.Button(
            label = _("Open prefix in file manager")
            )
        self.button_open_prefix.connect('clicked', self.cb_button_open_prefix)

        self.button_controllers = Gtk.Button(
            label = _("Configure game controllers")
            )
        self.button_controllers.connect('clicked', self.cb_button_controllers)

        self.button_winecfg = Gtk.Button(
            label = _("Wine configuration")
            )
        self.button_winecfg.connect('clicked', self.cb_button_winecfg)

        self.button_winetricks = Gtk.Button(
            label = "Winetricks"
            )
        self.button_winetricks.connect('clicked', self.cb_button_winetricks)

        self.box.pack_start(self.button_add_remove, True, True, 0)
        self.box.pack_start(self.button_run, True, True, 0)
        self.box.pack_start(self.button_open_prefix, True, True, 0)
        self.box.pack_start(self.button_controllers, True, True, 0)
        self.box.pack_start(self.button_winecfg, True, True, 0)
        self.box.pack_start(self.button_winetricks, True, True, 0)

        self.main_window.add(self.box)

        self.main_window.show_all()

    def cb_button_add_remove(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        command = '$WINELOADER uninstaller'
        os.system(command)

        self.main_window.show()

    def cb_button_run(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        dialog = Gtk.FileChooserDialog(
            _("Choose a file to execute"),
            self.main_window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog.set_current_folder(self.wineprefix_path + '/drive_c')

        #filter1 = Gtk.FileFilter()
        #filter1.set_name("DOS/Windows executable")
        #filter1.add_mime_type("application/x-ms-dos-executable")
        #dialog.add_filter(filter1)

        file_filter = Gtk.FileFilter()
        file_filter.set_name("*.exe, *.msi, *.bat")
        file_filter.add_pattern("*.exe")
        file_filter.add_pattern("*.msi")
        file_filter.add_pattern("*.bat")
        dialog.add_filter(file_filter)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:

            file_path = dialog.get_current_folder()

            if '.exe' in dialog.get_filename().split('/')[-1]:
                command = '$WINELOADER "' + dialog.get_filename() + '"'
            elif '.msi' in dialog.get_filename().split('/')[-1]:
                command = '$WINELOADER msiexec /i "' + dialog.get_filename() + '"'
            elif '.bat' in dialog.get_filename().split('/')[-1]:
                command = '$WINELOADER start /unix "' + dialog.get_filename() + '"'

            dialog.destroy()

            while Gtk.events_pending():
                Gtk.main_iteration()

            os.system('cd "' + file_path + '" && ' + command)

        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

        self.main_window.show()

    def cb_button_open_prefix(self, button):

        os.system('xdg-open ' + self.wineprefix_path + '/drive_c')

    def cb_button_controllers(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        command = '$WINELOADER control joy.cpl'
        os.system(command)

        self.main_window.show()

    def cb_button_winecfg(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        command = '$WINELOADER winecfg'
        os.system(command)

        self.main_window.show()

    def cb_button_winetricks(self, button):

        self.main_window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        command = 'winetricks --gui'
        os.system(command)

        self.main_window.show()

def main():
    import sys
    app = GUI()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
