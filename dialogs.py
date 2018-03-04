import sys, os, subprocess, re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf, InterpType
import gettext

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

nebula_dir = sys.path[0]

app_icon = GdkPixbuf.Pixbuf.new_from_file(nebula_dir + '/images/icon.png')

gettext.bindtextdomain('games_nebula', nebula_dir + '/locale')
gettext.textdomain('games_nebula')
_ = gettext.gettext

class GUI:

    def __init__(self, dialog_type, argument1):

        if dialog_type == 'question':
            print(self.create_question(argument1))
            sys.exit()
        elif dialog_type == 'list':
            print(self.create_list(argument1))
            sys.exit()
        elif dialog_type == 'progress':
            self.create_progress(argument1)
        else:
            print(_("Unknown dialog type: ") + dialog_type)
            sys.exit()

    def create_question(self, option_name):

        message_dialog = Gtk.MessageDialog(
            None,
            0,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO,
            _("Install") + " " + option_name + "?"
            )
        message_dialog.set_default_size(360, 120)

        content_area = message_dialog.get_content_area()
        content_area.set_property('margin_top', 10)
        content_area.set_property('margin_bottom', 10)
        content_area.set_property('margin_left', 10)
        content_area.set_property('margin_right', 10)

        action_area = message_dialog.get_action_area()
        action_area.set_spacing(10)

        response = message_dialog.run()
        message_dialog.destroy()

        if response == Gtk.ResponseType.YES:
            return 'Yes'
        elif response == Gtk.ResponseType.NO:
            return 'No'

    def create_list(self, options_list):

        message_dialog = Gtk.MessageDialog(
            None,
            0,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.OK,
            _("Choose version:")
            )
        message_dialog.set_default_size(360, 0)

        content_area = message_dialog.get_content_area()
        content_area.set_property('margin_top', 10)
        content_area.set_property('margin_bottom', 10)
        content_area.set_property('margin_left', 10)
        content_area.set_property('margin_right', 10)

        options_list = options_list.split(', ')

        def cb_radiobutton(radiobutton):
            self.option = radiobutton.get_label()

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing = 10
            )

        radiobutton1 = Gtk.RadioButton(
            label = options_list[0]
            )
        radiobutton1.connect('clicked', cb_radiobutton)
        box.pack_start(radiobutton1, True, True, 0)

        for i in range(1, len(options_list)):
            radiobutton = Gtk.RadioButton(
                label = options_list[i]
                )
            radiobutton.connect('clicked', cb_radiobutton)
            radiobutton.join_group(radiobutton1)
            box.pack_start(radiobutton, True, True, 0)

        content_area.pack_start(box, True, True, 0)

        self.option = options_list[0]

        message_dialog.show_all()
        response = message_dialog.run()
        message_dialog.destroy()

        return self.option

    def create_progress(self, command_string):

        message_text = _("Processing...")

        window_progress = Gtk.Window(
            title = "Games Nebula",
            icon = app_icon,
            type = Gtk.WindowType.TOPLEVEL,
            window_position = Gtk.WindowPosition.CENTER_ALWAYS,
            resizable = False
            )

        box = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            spacing = 10
            )

        pic = app_icon.scale_simple(32, 32, InterpType.BILINEAR)

        image = Gtk.Image(
            pixbuf = pic,
            margin_left = 10,
            margin_right = 10
            )

        label = Gtk.Label(
            label = message_text,
            margin_right = 10,
            margin_top = 20,
            margin_bottom = 20
            )

        box.pack_start(image, True, True, 0)
        box.pack_start(label, True, True, 0)

        window_progress.add(box)

        window_progress.show_all()

        def watch_process(io, condition, process_name):

            if condition is not GLib.IO_IN:
                sys.exit()

            while Gtk.events_pending():
                Gtk.main_iteration_do(False)

            line = io.readline()
            print(line.replace('\n', ''))

            return True

        if ' ' in command_string:
            command = command_string.split(' ')
        else:
            command = []
            command.append(command_string)

        pid, stdin, stdout, stderr = GLib.spawn_async(command,
                flags=GLib.SpawnFlags.SEARCH_PATH|GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                standard_output=True,
                standard_error=True)

        io = GLib.IOChannel(stdout)

        self.source_id_out = io.add_watch(GLib.IO_IN|GLib.IO_HUP,
                                 watch_process,
                                 'run_command',
                                 priority=GLib.PRIORITY_HIGH)

def main():
    import sys
    app = GUI(sys.argv[1], sys.argv[2])

    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
