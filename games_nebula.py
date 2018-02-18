#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; -*-
#
# "Games Nebula"
# Copyright (C) 2016 Ivan Yancharkin <yancharkin@gmail.com>
#
# "Games Nebula" is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# "Games Nebula" is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, subprocess, signal, re
from os.path import isfile, join
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf, InterpType
import gettext

try:
    from ConfigParser import ConfigParser as ConfigParser
except:
    from configparser import ConfigParser as ConfigParser

from modules import mylib_create_banner, mylib_get_data, mylib_tags_create, mylib_tags_get_all, \
mylib_tags_get, goglib_check_authorization, goglib_check_connection, goglib_get_data, \
goglib_get_games_list, goglib_tags_create, goglib_tags_get_all, goglib_tags_get, autosetup, \
monitors

style_provider_1 = Gtk.CssProvider()

css = b"""
.lighter_background {
    background: lighter(@theme_bg_color);
}
"""

style_provider_1.load_from_data(css)

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    style_provider_1,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

transparent_rgba = Gdk.RGBA(
    red = 0,
    green = 0,
    blue = 0,
    alpha = 0,
    )

goglib_game_grids_full_list = []
goglib_game_grids_current_list = []
goglib_games_banners_list = []
goglib_setup_buttons_list = []
goglib_launch_buttons_list = []

mylib_game_grids_full_list = []
mylib_game_grids_current_list = []
mylib_games_banners_list = []
mylib_setup_buttons_list = []
mylib_launch_buttons_list = []

queue_progress_bars_list = []
queue_game_status_list = []
queue_game_image_list = []
queue_game_frame_list = []

goglib_installation_queue = []
mylib_installation_queue = []

goglib_name_to_pid_download_dict = {}
goglib_name_to_pid_unpack_dict = {}
goglib_name_to_pid_install_dict = {}

mylib_name_to_pid_install_dict = {}

nebula_dir = sys.path[0]
data_dir = os.getenv('HOME') + '/.games_nebula'
config_dir = data_dir + '/config'
goglib_tags_file = config_dir + '/goglib_tags.ini'
mylib_tags_file = config_dir + '/mylib_tags.ini'
app_icon = GdkPixbuf.Pixbuf.new_from_file(nebula_dir + '/images/icon.png')

gettext.bindtextdomain('games_nebula', nebula_dir + '/locale')
gettext.textdomain('games_nebula')
_ = gettext.gettext

predefined_tags = [_("Action"), _("Adventure"), _("Demo"), _("Indie"),
                _("Role-playing"), _("Shooter"), _("Simulation"), _("Strategy")]
predefined_tags = sorted(predefined_tags)

def file_exist_in_dir(path):
    return any(isfile(join(path, i)) for i in os.listdir(path))

os.environ['NEBULA_DIR'] = nebula_dir

class GUI:

    def __init__(self):

        self.create_loading_window()

        while Gtk.events_pending():
            Gtk.main_iteration()

        self.goglib_box_width = 1
        self.mylib_box_width = 1
        self.last_active_tab = None
        self.goglib_now_installing = None
        self.mylib_now_installing = None
        self.download_canceled = False
        self.unpack_canceled = False
        self.goglib_new_games_list = []
        self.detached_tabs_names = []
        self.additional_windows_list = []
        self.additional_notebooks_list = []

        self.monitors_list, self.monitor_primary = monitors.get_monitors()
        self.config_load()
        self.parse_goglib_colors()
        self.parse_mylib_colors()

        if self.goglib_tab_at_start and not self.goglib_offline_mode_at_start:
            self.goglib_authorized = goglib_check_authorization.goglib_authorized()
            if self.goglib_authorized == False:
                self.goglib_offline_mode = True
                if goglib_check_connection.goglib_available():
                    self.create_login_window()
                else:

                    self.loading_window.hide()

                    while Gtk.events_pending():
                        Gtk.main_iteration()

                    message_dialog = Gtk.MessageDialog(
                        None,
                        0,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        _("GOG.com unavailable")
                        )
                    message_dialog.format_secondary_text(_("Check your internet connection.\nStarting in offline mode."))
                    content_area = message_dialog.get_content_area()
                    content_area.set_property('margin-left', 10)
                    content_area.set_property('margin-right', 10)
                    content_area.set_property('margin-top', 10)
                    content_area.set_property('margin-bottom', 10)

                    message_dialog.run()
                    message_dialog.destroy()

                    self.goglib_offline_mode = True
                    self.create_main_window()
                    self.timer()
            else:
                self.goglib_offline_mode = False
                self.create_main_window()
                self.timer()
        else:
            self.goglib_offline_mode = True
            self.create_main_window()
            self.timer()

    def create_loading_window(self):

        self.loading_window = Gtk.Window(
            title = "Games Nebula",
            icon = app_icon,
            type = Gtk.WindowType.POPUP,
            window_position = Gtk.WindowPosition.CENTER_ALWAYS,
            resizable = False
            )

        self.box_loading_window = Gtk.Box()

        loading_icon = app_icon.scale_simple(32, 32, InterpType.BILINEAR)

        self.image_loading = Gtk.Image(
            pixbuf = loading_icon,
            margin_left = 10,
            margin_right = 10
            )

        self.label_loading = Gtk.Label(
            label = _("Launching 'Games Nebula'"),
            margin_right = 10,
            margin_left = 10,
            margin_top = 20,
            margin_bottom = 20
            )

        self.box_loading_window.pack_start(self.image_loading, True, True, 0)
        self.box_loading_window.pack_start(self.label_loading, True, True, 0)
        self.loading_window.add(self.box_loading_window)
        self.loading_window.show_all()

    def create_login_window(self):

        self.loading_window.destroy()

        while Gtk.events_pending():
            Gtk.main_iteration()

        os.system(sys.executable + ' ' + nebula_dir + '/pygogauth.py')
        os.execl(sys.executable, sys.executable, *sys.argv)

    def create_main_window(self):

        self.main_window = Gtk.Window(
            title = "Games Nebula",
            type = Gtk.WindowType.TOPLEVEL,
            window_position = Gtk.WindowPosition.CENTER,
            icon = app_icon,
            )
        self.main_window.connect('delete-event', self.quit_app)
        self.main_window.connect('key-press-event', self.shortcuts)

        workarea_width, workarea_height = self.get_monitor_workarea(self.main_window)
        self.main_window.set_property('default_width', workarea_width)
        self.main_window.set_property('default_height', workarea_height)

        self.notebook = Gtk.Notebook(
            show_tabs = self.show_tabs
            )
        self.notebook.set_group_name('games_nebula')
        self.notebook.connect('create-window', self.detach_tab)

        self.button_add_tab = Gtk.Button(
            image = Gtk.Image(stock=Gtk.STOCK_ADD),
            visible = True,
            relief = Gtk.ReliefStyle.NONE,
            tooltip_text = _("Add tabs")
            )
        self.button_add_tab.connect('clicked', self.cb_button_add_tab)
        self.notebook.set_action_widget(self.button_add_tab, Gtk.PackType.START)

        if self.goglib_offline_mode:
            img = Gtk.Image.new_from_icon_name("network-offline", Gtk.IconSize.SMALL_TOOLBAR)
            online_status_icon = img
            online_tooltip = _("Offline - click to go online")
        else:
            img = Gtk.Image.new_from_icon_name("network-idle", Gtk.IconSize.SMALL_TOOLBAR)
            online_status_icon = img
            online_tooltip = _("Online - click to go offline")

        self.button_online_status = Gtk.Button(
            image = online_status_icon,
            visible = False,
            no_show_all = True,
            relief = Gtk.ReliefStyle.NONE,
            tooltip_text = online_tooltip
            )
        self.button_online_status.connect('clicked', self.cb_button_online_status)

        img = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.SMALL_TOOLBAR)
        self.button_update_goglib = Gtk.Button(
            image = img,
            visible = False,
            no_show_all = True,
            relief = Gtk.ReliefStyle.NONE,
            tooltip_text = _("Update GOG library")
            )
        self.button_update_goglib.connect('clicked', self.cb_button_update_goglib)

        self.box_action_widgets_end = Gtk.Box()
        self.box_action_widgets_end.pack_start(self.button_online_status, True, True, 0)
        self.box_action_widgets_end.pack_start(self.button_update_goglib, True, True, 0)
        self.box_action_widgets_end.show_all()
        self.notebook.set_action_widget(self.box_action_widgets_end, Gtk.PackType.END)

        self.spinner_update = Gtk.Spinner(
            active = True,
            visible = True,
            margin_left = 10,
            margin_right = 10,
            )

        self.notebook.show_all()

        if self.gogcom_tab_at_start == True:
            self.create_gogcom_tab()

        if self.goglib_tab_at_start == True:
            self.create_goglib_tab_content()

        if self.mylib_tab_at_start == True:
            self.create_mylib_tab()

        self.create_settings_tab()
        self.create_queue_tab()

        self.main_window.add(self.notebook)

        self.notebook.connect('switch-page', self.notebook_page_switched)

        self.main_window.show_all()
        self.loading_window.hide()

    def notebook_page_switched(self, notebook, widget, arg):

        # Automatically check for new games (not a good idea)
        #~ if (widget.get_name() == 'goglib_tab') and (self.last_active_tab == 'gogcom_tab'):
            #~ if self.goglib_offline_mode:
                #~ if goglib_authorized:
                    #~ os.execl(sys.executable, sys.executable, *sys.argv)
            #~ else:
                #~ for i in range (self.notebook.get_n_pages()):
                    #~ try:
                        #~ if self.notebook.get_nth_page(i) == self.unauthorized_grid:
                            #~ if goglib_authorized:
                                #~ os.execl(sys.executable, sys.executable, *sys.argv)
                    #~ except:
                        #~ pass
        #~ if (self.last_active_tab == 'gogcom_tab') and goglib_authorized:
            #~ self.check_for_new_games()

        if self.last_active_tab == 'settings_tab':
            self.config_save()

        if widget.get_name() != 'goglib_tab':
            self.button_update_goglib.set_visible(False)
            self.button_online_status.set_visible(False)
        else:
            self.button_online_status.set_visible(True)
            if not self.goglib_offline_mode:
                self.button_update_goglib.set_visible(True)

        self.last_active_tab = widget.get_name()

    def check_for_new_games(self):

        self.goglib_new_games_list = []
        self.goglib_updated_games_list = []

        command = ['lgogdownloader', '--exclude', '1,2,4,8,16,32','--list']

        pid, stdin, stdout, stderr = GLib.spawn_async(
            command,
            flags=GLib.SpawnFlags.SEARCH_PATH|GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            standard_output=True,
            standard_error=True
            )

        io = GLib.IOChannel(stdout)

        self.source_id_out = io.add_watch(
            GLib.IO_IN|GLib.IO_HUP,
            self.watch_process,
            'check_for_new_games',
            priority=GLib.PRIORITY_HIGH
            )

    def quit_app(self, window, event):
        self.config_save()
        Gtk.main_quit()

    def create_goglib_tab_empty(self):

        self.unauthorized_grid = Gtk.Grid(
            name = 'goglib_tab',
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.CENTER,
            row_spacing = 10,
            column_spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.unauthorized_message = Gtk.Label(
            label = _("You are not authorized on GOG.COM and can't download games."),
            wrap = True,
            )

        self.unauthorized_grid.attach(self.unauthorized_message, 0, 0, 1, 1)

        if os.path.exists(os.getenv('HOME') + '/.games_nebula/config/games_list'):
            self.button_start_offline = Gtk.Button(
                label = _("Start in offline mode"),
                halign = Gtk.Align.CENTER
                )

            self.button_start_offline.connect('clicked', self.goglib_start_offline_mode)

            self.unauthorized_grid.attach(self.button_start_offline, 0, 1, 1, 1)

        self.unauthorized_tab_box = Gtk.Box(
            spacing = 10,
            )

        self.unauthorized_tab_label = Gtk.Label(
            label = _("GOG LIBRARY")
            )

        self.unauthorized_tab_close_button = Gtk.Button(
            name = "Downloads",
            image = Gtk.Image(stock=Gtk.STOCK_CLOSE),
            relief = Gtk.ReliefStyle.NONE,
            focus_on_click = False,
            )

        self.unauthorized_tab_close_button.connect('clicked', self.close_tab, self.unauthorized_grid)

        self.unauthorized_tab_box.pack_start(self.unauthorized_tab_label, True, True, 0)
        self.unauthorized_tab_box.pack_start(self.unauthorized_tab_close_button, True, True, 0)
        self.unauthorized_tab_box.show_all()

        self.notebook.append_page(self.unauthorized_grid, self.unauthorized_tab_box)
        self.notebook.set_tab_reorderable(self.unauthorized_grid, True)
        self.notebook.set_tab_detachable(self.unauthorized_grid, True)

    def goglib_start_offline_mode(self, button):
        self.goglib_offline_mode = True
        self.button_online_status.set_property('tooltip_text', _("Offline - click to go online"))
        self.button_online_status.set_property('image', self.icon_network_offline)
        self.notebook.detach_tab(self.unauthorized_grid)
        self.create_goglib_tab_content()
        self.main_window.show_all()
        new_active_page = self.notebook.page_num(self.box_goglib_page)
        self.notebook.set_current_page(new_active_page)

    def goglib_offline_available_games(self):

        available_distrs = os.listdir(self.goglib_download_dir)
        available_offline = []

        for game_name in self.goglib_games_list:
            start_path = self.goglib_install_dir + '/' + game_name + '/start.sh'
            if os.path.exists(start_path) or (game_name in available_distrs):
                available_offline.append(game_name)

        self.goglib_available_games = list(available_offline)

    def create_goglib_tab_content(self):

        if not os.path.exists(config_dir + '/games_list'):

            if not self.goglib_offline_mode:

                goglib_get_games_list.goglib_get_games_list()

            elif self.goglib_offline_mode:

                message_dialog = Gtk.MessageDialog(
                    self.main_window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    _("Error"),
                    )
                message_dialog.format_secondary_text(_("File '") +
                os.getenv('HOME') + '/.games_nebula/config/games_list' + _("' is missing.\n") +
                _("'GOG LIBRARY' tab will be disabled."))
                content_area = message_dialog.get_content_area()
                content_area.set_property('margin-left', 10)
                content_area.set_property('margin-right', 10)
                content_area.set_property('margin-top', 10)
                content_area.set_property('margin-bottom', 10)
                action_area = message_dialog.get_action_area()
                action_area.set_property('spacing', 10)

                self.loading_window.hide()
                message_dialog.run()
                message_dialog.destroy()

                if (self.mylib_tab_at_start == False) and \
                        (self.gogcom_tab_at_start == False) and \
                        (self.queue_tab_at_start == False) and \
                        (self.settings_tab_at_start == False):

                    self.create_settings_tab()
                    self.notebook.append_page(self.scrolledwindow_settings, self.box_settings_tab)
                    self.notebook.set_tab_detachable(self.scrolledwindow_settings, True)
                    self.notebook.set_tab_reorderable(self.scrolledwindow_settings, True)
                    self.notebook.set_tab_detachable(self.scrolledwindow_settings, True)

                return

        self.number_of_games, \
        self.goglib_games_list, \
        self.list_titles, \
        self.list_icons,\
        self.available_scripts = goglib_get_data.games_info(data_dir)

        if self.goglib_offline_mode == True:
            self.goglib_offline_available_games()
        else:
            self.goglib_available_games = self.goglib_games_list

        self.goglib_number_of_games_to_show = self.number_of_games
        self.goglib_shown_games_list = list(self.goglib_games_list)
        self.goglib_status_filter_list = list(self.goglib_games_list)
        self.goglib_tags1_filter_list = list(self.goglib_games_list)
        self.goglib_tags2_filter_list = list(self.goglib_games_list)
        self.goglib_tags3_filter_list = list(self.goglib_games_list)
        self.goglib_tags4_filter_list = list(self.goglib_games_list)
        self.goglib_search_filter_list = list(self.goglib_games_list)

        self.all_tags = goglib_tags_get_all.goglib_tags_get_all(goglib_tags_file)

        self.goglib_dict_name_to_title = {}
        for i in range(self.number_of_games):
            self.goglib_dict_name_to_title[self.goglib_games_list[i]] = self.list_titles[i]

        self.box_goglib_page = Gtk.Box(
            orientation = Gtk.Orientation.VERTICAL,
            homogeneous = False,
            name = 'goglib_tab',
            )

        self.box_goglib_filters = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            homogeneous = False,
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            spacing = 10
            )

        self.goglib_tab_search_entry = Gtk.SearchEntry(
            placeholder_text = _("Search"),
            halign = Gtk.Align.FILL,
            )
        self.goglib_tab_search_entry.connect('search-changed', self.goglib_search_filter)

        self.combobox_goglib_status = Gtk.ComboBoxText(
            tooltip_text = _("Status filter"),
            name = 'combobox_goglib_status'
            )

        self.status_list = [_("No filter"), _("Installed"), _("Unavailable")]

        for i in range(len(self.status_list)):
            self.combobox_goglib_status.append_text(self.status_list[i])
            if self.status_list[i] == self.status_filter:
                self.combobox_goglib_status.set_active(i)
        self.combobox_goglib_status.connect('changed', self.cb_combobox_goglib_status)
        self.combobox_goglib_status.connect('button-press-event', self.cb2_comboboxes_filters)

        if self.goglib_filter_color_indication == True:
            goglib_combobox_status_cell_view = self.combobox_goglib_status.get_child()
            if self.goglib_status_filter_type == 'include':
                goglib_combobox_status_cell_view.set_background_rgba(self.goglib_include_rgba)
            elif self.goglib_status_filter_type == 'exclude':
                goglib_combobox_status_cell_view.set_background_rgba(self.goglib_exclude_rgba)

        self.combobox_goglib_tags1 = Gtk.ComboBoxText(
            tooltip_text = _("Tags filter 1"),
            name = 'combobox_goglib_tags1'
            )
        self.combobox_goglib_tags1.append_text(_("No filter"))
        for i in range(len(self.all_tags)):
            if self.all_tags[i] != '':
                self.combobox_goglib_tags1.append_text(self.all_tags[i])
            if self.all_tags[i] == self.goglib_tags_filter1:
                self.combobox_goglib_tags1.set_active(i + 1)

        if self.goglib_tags_filter1 not in self.all_tags:
            self.combobox_goglib_tags1.set_active(0)

        self.combobox_goglib_tags1.append_text(_("No tags"))

        self.combobox_goglib_tags1.connect('changed', self.cb_combobox_goglib_tags1)
        self.combobox_goglib_tags1.connect('button-press-event', self.cb2_comboboxes_filters)

        if self.goglib_filter_color_indication == True:
            goglib_combobox_tags1_cell_view = self.combobox_goglib_tags1.get_child()
            if self.goglib_tags_filter1_type == 'include':
                goglib_combobox_tags1_cell_view.set_background_rgba(self.goglib_include_rgba)
            elif self.goglib_tags_filter1_type == 'exclude':
                goglib_combobox_tags1_cell_view.set_background_rgba(self.goglib_exclude_rgba)

        self.combobox_goglib_tags2 = Gtk.ComboBoxText(
            tooltip_text = _("Tags filter 2"),
            no_show_all = True,
            name = 'combobox_goglib_tags2'
            )
        self.combobox_goglib_tags2.append_text(_("No filter"))
        for i in range(len(self.all_tags)):
            if self.all_tags[i] != '':
                self.combobox_goglib_tags2.append_text(self.all_tags[i])
            if self.all_tags[i] == self.goglib_tags_filter2:
                self.combobox_goglib_tags2.set_active(i + 1)

        if self.goglib_tags_filter2 not in self.all_tags:
            self.combobox_goglib_tags2.set_active(0)

        self.combobox_goglib_tags2.append_text(_("No tags"))

        self.combobox_goglib_tags2.connect('changed', self.cb_combobox_goglib_tags2)
        self.combobox_goglib_tags2.connect('button-press-event', self.cb2_comboboxes_filters)

        if self.goglib_filter_color_indication == True:
            goglib_combobox_tags2_cell_view = self.combobox_goglib_tags2.get_child()
            if self.goglib_tags_filter2_type == 'include':
                goglib_combobox_tags2_cell_view.set_background_rgba(self.goglib_include_rgba)
            elif self.goglib_tags_filter2_type == 'exclude':
                goglib_combobox_tags2_cell_view.set_background_rgba(self.goglib_exclude_rgba)

        self.combobox_goglib_tags3 = Gtk.ComboBoxText(
            tooltip_text = _("Tags filter 3"),
            no_show_all = True,
            name = 'combobox_goglib_tags3'
            )
        self.combobox_goglib_tags3.append_text(_("No filter"))
        for i in range(len(self.all_tags)):
            if self.all_tags[i] != '':
                self.combobox_goglib_tags3.append_text(self.all_tags[i])
            if self.all_tags[i] == self.goglib_tags_filter3:
                self.combobox_goglib_tags3.set_active(i + 1)

        if self.goglib_tags_filter3 not in self.all_tags:
            self.combobox_goglib_tags3.set_active(0)

        self.combobox_goglib_tags3.append_text(_("No tags"))

        self.combobox_goglib_tags3.connect('changed', self.cb_combobox_goglib_tags3)
        self.combobox_goglib_tags3.connect('button-press-event', self.cb2_comboboxes_filters)

        if self.goglib_filter_color_indication == True:
            goglib_combobox_tags3_cell_view = self.combobox_goglib_tags3.get_child()
            if self.goglib_tags_filter3_type == 'include':
                goglib_combobox_tags3_cell_view.set_background_rgba(self.goglib_include_rgba)
            elif self.goglib_tags_filter3_type == 'exclude':
                goglib_combobox_tags3_cell_view.set_background_rgba(self.goglib_exclude_rgba)

        self.combobox_goglib_tags4 = Gtk.ComboBoxText(
            tooltip_text = _("Tags filter 4"),
            no_show_all = True,
            name = 'combobox_goglib_tags4'
            )
        self.combobox_goglib_tags4.append_text(_("No filter"))
        for i in range(len(self.all_tags)):
            if self.all_tags[i] != '':
                self.combobox_goglib_tags4.append_text(self.all_tags[i])
            if self.all_tags[i] == self.goglib_tags_filter4:
                self.combobox_goglib_tags4.set_active(i + 1)

        if self.goglib_tags_filter4 not in self.all_tags:
            self.combobox_goglib_tags4.set_active(0)

        self.combobox_goglib_tags4.append_text(_("No tags"))

        self.combobox_goglib_tags4.connect('changed', self.cb_combobox_goglib_tags4)
        self.combobox_goglib_tags4.connect('button-press-event', self.cb2_comboboxes_filters)

        if self.goglib_filter_color_indication == True:
            goglib_combobox_tags4_cell_view = self.combobox_goglib_tags4.get_child()
            if self.goglib_tags_filter4_type == 'include':
                goglib_combobox_tags4_cell_view.set_background_rgba(self.goglib_include_rgba)
            elif self.goglib_tags_filter4_type == 'exclude':
                goglib_combobox_tags4_cell_view.set_background_rgba(self.goglib_exclude_rgba)

        self.button_goglib_add_tag_filter = Gtk.Button(
            name = 'add',
            image = Gtk.Image(stock=Gtk.STOCK_ADD),
            no_show_all = True,
            tooltip_text = _("Add tags filter")
            )
        self.button_goglib_add_tag_filter.connect('clicked', self.goglib_tag_filters_number_changed)

        self.button_goglib_remove_tag_filter = Gtk.Button(
            name = 'remove',
            image = Gtk.Image(stock=Gtk.STOCK_REMOVE),
            tooltip_text = _("Remove tags filter"),
            no_show_all = True,
            )
        self.button_goglib_remove_tag_filter.connect('clicked', self.goglib_tag_filters_number_changed)

        self.adjustment_goglib_scale_banner = Gtk.Adjustment(self.scale_level, 0.4, 1, 0.1, 0.3)
        self.adjustment_goglib_scale_banner.connect('value-changed', self.cb_adjustment_goglib_scale_banner)
        self.scl_banners = Gtk.Scale(
            tooltip_text = _("Scale"),
            orientation = Gtk.Orientation.HORIZONTAL,
            halign = Gtk.Align.END,
            valign = Gtk.Align.CENTER,
            width_request = 150,
            draw_value = False,
            show_fill_level = True,
            adjustment = self.adjustment_goglib_scale_banner,
            )

        self.box_goglib_filters.pack_start(self.goglib_tab_search_entry, True, True, 0)
        self.box_goglib_filters.pack_start(self.combobox_goglib_status, False, False, 0)
        self.box_goglib_filters.pack_start(self.combobox_goglib_tags1, False, False, 0)
        self.box_goglib_filters.pack_start(self.combobox_goglib_tags2, False, False, 0)
        self.box_goglib_filters.pack_start(self.combobox_goglib_tags3, False, False, 0)
        self.box_goglib_filters.pack_start(self.combobox_goglib_tags4, False, False, 0)
        self.box_goglib_filters.pack_start(self.button_goglib_remove_tag_filter, False, False, 0)
        self.box_goglib_filters.pack_start(self.button_goglib_add_tag_filter, False, False, 0)
        self.box_goglib_filters.pack_start(self.scl_banners, False, False, 0)

        self.scrolledwindow_goglib = Gtk.ScrolledWindow()

        self.grid_goglib = Gtk.Grid(
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            hexpand = True,
            column_homogeneous = True,
            row_spacing = 30,
            margin_top = 30,
            margin_bottom = 30,
            )

        self.scrolledwindow_goglib.add(self.grid_goglib)

        for i in range(0, self.goglib_number_of_games_to_show):

            gtk_grid_game = Gtk.Grid(
                name = self.goglib_shown_games_list[i],
                halign = Gtk.Align.CENTER,
                row_spacing = 1,
                column_spacing = 1,
                )
            goglib_game_grids_full_list.append(gtk_grid_game)
            goglib_game_grids_current_list.append(gtk_grid_game)

            gtk_button_setup = Gtk.Button(
                name = self.goglib_shown_games_list[i],
                label = _("Install")
                )
            goglib_setup_buttons_list.append(gtk_button_setup)
            gtk_button_setup.connect('clicked', self.goglib_setup_game)

            image_goglib_banner = Gtk.Image(
                name = self.goglib_shown_games_list[i],
                tooltip_text = self.list_titles[i],
                )

            goglib_games_banners_list.append(image_goglib_banner)

            banner_event_box = Gtk.EventBox()
            banner_event_box.add(image_goglib_banner)

            banner_event_box.connect('button-press-event', self.goglib_banner_clicked)

            gtk_button_launch = Gtk.Button(
                name = self.goglib_shown_games_list[i],
                label = _("Launch")
                )
            gtk_button_launch.connect('clicked', self.goglib_launch_game)
            goglib_launch_buttons_list.append(gtk_button_launch)

            if os.path.exists(self.goglib_install_dir + '/' + self.goglib_shown_games_list[i] + '/start.sh'):
                gtk_button_setup.set_label(_("Remove"))
                gtk_button_launch.set_sensitive(True)
            else:
                gtk_button_setup.set_label(_("Install"))
                gtk_button_launch.set_sensitive(False)

            gtk_grid_game.attach(banner_event_box, 0, 0, 2, 1)
            gtk_grid_game.attach(gtk_button_setup, 0, 1, 1, 1)
            gtk_grid_game.attach(gtk_button_launch, 1, 1, 1, 1)

            max_pixbuf_width = self.scale_level * (518 + 60)
            number_of_columns = int(self.goglib_box_width / max_pixbuf_width)
            self.grid_autoresize(number_of_columns)

        self.box_goglib_installation_status = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            visible = False,
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            hexpand = True,
            )

        self.progressbar_goglib = Gtk.ProgressBar(
            hexpand = True,
            show_text = True,
            text = ' ',
            pulse_step = 0.05
            )

        self.box_goglib_installation_status.pack_start(self.progressbar_goglib, False, False, 0)

        self.scrolledwindow_filters = Gtk.ScrolledWindow()
        self.scrolledwindow_filters.add(self.box_goglib_filters)

        self.box_goglib_page.pack_start(self.scrolledwindow_filters, False, False, 0)
        self.box_goglib_page.pack_start(self.scrolledwindow_goglib, True, True, 0)
        self.box_goglib_page.pack_start(self.box_goglib_installation_status, False, False, 0)

        self.box_goglib_tab = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            spacing = 10
            )

        self.label_goglib_tab = Gtk.Label(
            label = _("GOG LIBRARY")
            )

        self.button_close_goglib_tab = Gtk.Button(
            image = Gtk.Image(stock=Gtk.STOCK_CLOSE),
            relief = Gtk.ReliefStyle.NONE,
            focus_on_click = False,
            )
        self.button_close_goglib_tab.connect('clicked', self.close_tab, self.box_goglib_page)


        self.box_goglib_tab.pack_start(self.label_goglib_tab, True, True, 0)
        self.box_goglib_tab.pack_start(self.button_close_goglib_tab, False, False, 0)

        self.box_goglib_tab.show_all()

        self.notebook.append_page(self.box_goglib_page, self.box_goglib_tab)
        self.notebook.set_tab_reorderable(self.box_goglib_page, True)
        self.notebook.set_tab_detachable(self.box_goglib_page, True)

        self.cb_combobox_goglib_status(self.combobox_goglib_status)
        self.cb_combobox_goglib_tags1(self.combobox_goglib_tags1)
        self.cb_combobox_goglib_tags2(self.combobox_goglib_tags2)
        self.cb_combobox_goglib_tags3(self.combobox_goglib_tags3)
        self.cb_combobox_goglib_tags4(self.combobox_goglib_tags4)
        self.goglib_tags_visibility()
        self.update_goglib_interface()

        # Automatically check for new games (not a good idea for now)
        #~ self.check_for_new_games()
        #~ self.timer_check_for_new_games()

    def create_mylib_tab(self):

        self.mylib_number_of_games, \
        self.mylib_games_list, \
        self.mylib_list_titles  = mylib_get_data.games_info(data_dir)

        self.mylib_number_of_games_to_show = self.mylib_number_of_games
        self.mylib_shown_games_list = list(self.mylib_games_list)
        self.mylib_status_filter_list = list(self.mylib_games_list)
        self.mylib_tags1_filter_list = list(self.mylib_games_list)
        self.mylib_tags2_filter_list = list(self.mylib_games_list)
        self.mylib_tags3_filter_list = list(self.mylib_games_list)
        self.mylib_tags4_filter_list = list(self.mylib_games_list)
        self.mylib_search_filter_list = list(self.mylib_games_list)

        mylib_tags_file = config_dir + '/mylib_tags.ini'
        self.mylib_all_tags = mylib_tags_get_all.mylib_tags_get_all(mylib_tags_file)

        self.mylib_dict_name_to_title = {}
        for i in range(self.mylib_number_of_games):
            self.mylib_dict_name_to_title[self.mylib_games_list[i]] = self.mylib_list_titles[i]

        self.box_mylib_page = Gtk.Box(
            orientation = Gtk.Orientation.VERTICAL,
            homogeneous = False,
            name = 'mylib_tab',
            )

        self.mylib_filters_box = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            homogeneous = False,
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            spacing = 10
            )

        self.mylib_tab_search_entry = Gtk.SearchEntry(
            placeholder_text = _("Search"),
            halign = Gtk.Align.FILL,
            )
        self.mylib_tab_search_entry.connect('search-changed', self.mylib_search_filter)

        self.combobox_mylib_status = Gtk.ComboBoxText(
            tooltip_text = _("Status filter"),
            name = 'combobox_mylib_status'
            )

        self.mylib_status_list = [_("No filter"), _("Installed")]

        for i in range(len(self.mylib_status_list)):
            self.combobox_mylib_status.append_text(self.mylib_status_list[i])
            if self.mylib_status_list[i] == self.mylib_status_filter:
                self.combobox_mylib_status.set_active(i)

        self.combobox_mylib_status.connect('changed', self.cb_combobox_mylib_status)
        self.combobox_mylib_status.connect('button-press-event', self.cb2_comboboxes_filters)

        if self.mylib_filter_color_indication == True:
            mylib_combobox_status_cell_view = self.combobox_mylib_status.get_child()
            if self.mylib_status_filter_type == 'include':
                mylib_combobox_status_cell_view.set_background_rgba(self.mylib_include_rgba)
            elif self.mylib_status_filter_type == 'exclude':
                mylib_combobox_status_cell_view.set_background_rgba(self.mylib_exclude_rgba)

        self.combobox_mylib_tags1 = Gtk.ComboBoxText(
            tooltip_text = _("Tags filter 1"),
            name = 'combobox_mylib_tags1'
            )
        self.combobox_mylib_tags1.append_text(_("No filter"))

        for i in range(len(self.mylib_all_tags)):
            if self.mylib_all_tags[i] != '':
                self.combobox_mylib_tags1.append_text(self.mylib_all_tags[i])
            if self.mylib_all_tags[i] == self.mylib_tags_filter1:
                self.combobox_mylib_tags1.set_active(i + 1)

        if self.mylib_tags_filter1 not in self.mylib_all_tags:
            self.combobox_mylib_tags1.set_active(0)

        self.combobox_mylib_tags1.append_text(_("No tags"))

        self.combobox_mylib_tags1.connect('changed', self.cb_combobox_mylib_tags1)
        self.combobox_mylib_tags1.connect('button-press-event', self.cb2_comboboxes_filters)

        if self.mylib_filter_color_indication == True:
            mylib_combobox_tags1_cell_view = self.combobox_mylib_tags1.get_child()
            if self.mylib_tags_filter1_type == 'include':
                mylib_combobox_tags1_cell_view.set_background_rgba(self.mylib_include_rgba)
            elif self.mylib_tags_filter1_type == 'exclude':
                mylib_combobox_tags1_cell_view.set_background_rgba(self.mylib_exclude_rgba)

        self.combobox_mylib_tags2 = Gtk.ComboBoxText(
            tooltip_text = _("Tags filter 2"),
            no_show_all = True,
            name = 'combobox_mylib_tags2'
            )
        self.combobox_mylib_tags2.append_text(_("No filter"))

        for i in range(len(self.mylib_all_tags)):
            if self.mylib_all_tags[i] != '':
                self.combobox_mylib_tags2.append_text(self.mylib_all_tags[i])
            if self.mylib_all_tags[i] == self.mylib_tags_filter2:
                self.combobox_mylib_tags2.set_active(i + 1)

        if self.mylib_tags_filter2 not in self.mylib_all_tags:
            self.combobox_mylib_tags2.set_active(0)

        self.combobox_mylib_tags2.append_text(_("No tags"))

        self.combobox_mylib_tags2.connect('changed', self.cb_combobox_mylib_tags2)
        self.combobox_mylib_tags2.connect('button-press-event', self.cb2_comboboxes_filters)

        if self.mylib_filter_color_indication == True:
            mylib_combobox_tags2_cell_view = self.combobox_mylib_tags2.get_child()
            if self.mylib_tags_filter2_type == 'include':
                mylib_combobox_tags2_cell_view.set_background_rgba(self.mylib_include_rgba)
            elif self.mylib_tags_filter2_type == 'exclude':
                mylib_combobox_tags2_cell_view.set_background_rgba(self.mylib_exclude_rgba)

        self.combobox_mylib_tags3 = Gtk.ComboBoxText(
            tooltip_text = _("Tags filter 3"),
            no_show_all = True,
            name = 'combobox_mylib_tags3'
            )
        self.combobox_mylib_tags3.append_text(_("No filter"))

        for i in range(len(self.mylib_all_tags)):
            if self.mylib_all_tags[i] != '':
                self.combobox_mylib_tags3.append_text(self.mylib_all_tags[i])
            if self.mylib_all_tags[i] == self.mylib_tags_filter3:
                self.combobox_mylib_tags3.set_active(i + 1)

        if self.mylib_tags_filter3 not in self.mylib_all_tags:
            self.combobox_mylib_tags3.set_active(0)

        self.combobox_mylib_tags3.append_text(_("No tags"))

        self.combobox_mylib_tags3.connect('changed', self.cb_combobox_mylib_tags3)
        self.combobox_mylib_tags3.connect('button-press-event', self.cb2_comboboxes_filters)

        if self.mylib_filter_color_indication == True:
            mylib_combobox_tags3_cell_view = self.combobox_mylib_tags3.get_child()
            if self.mylib_tags_filter3_type == 'include':
                mylib_combobox_tags3_cell_view.set_background_rgba(self.mylib_include_rgba)
            elif self.mylib_tags_filter3_type == 'exclude':
                mylib_combobox_tags3_cell_view.set_background_rgba(self.mylib_exclude_rgba)

        self.combobox_mylib_tags4 = Gtk.ComboBoxText(
            tooltip_text = _("Tags filter 4"),
            no_show_all = True,
            name = 'combobox_mylib_tags4'
            )
        self.combobox_mylib_tags4.append_text(_("No filter"))

        for i in range(len(self.mylib_all_tags)):
            if self.mylib_all_tags[i] != '':
                self.combobox_mylib_tags4.append_text(self.mylib_all_tags[i])
            if self.mylib_all_tags[i] == self.mylib_tags_filter4:
                self.combobox_mylib_tags4.set_active(i + 1)

        if self.mylib_tags_filter4 not in self.mylib_all_tags:
            self.combobox_mylib_tags4.set_active(0)

        self.combobox_mylib_tags4.append_text(_("No tags"))

        self.combobox_mylib_tags4.connect('changed', self.cb_combobox_mylib_tags4)
        self.combobox_mylib_tags4.connect('button-press-event', self.cb2_comboboxes_filters)

        if self.mylib_filter_color_indication == True:
            mylib_combobox_tags4_cell_view = self.combobox_mylib_tags4.get_child()
            if self.mylib_tags_filter4_type == 'include':
                mylib_combobox_tags4_cell_view.set_background_rgba(self.mylib_include_rgba)
            elif self.mylib_tags_filter4_type == 'exclude':
                mylib_combobox_tags4_cell_view.set_background_rgba(self.mylib_exclude_rgba)

        self.button_mylib_tagfilter_add = Gtk.Button(
            name = 'add',
            image = Gtk.Image(stock=Gtk.STOCK_ADD),
            no_show_all = True,
            tooltip_text = _("Add tags filter")
            )
        self.button_mylib_tagfilter_add.connect('clicked', self.mylib_tagfilters_number_changed)

        self.button_mylib_tagfilter_remove = Gtk.Button(
            name = 'remove',
            image = Gtk.Image(stock=Gtk.STOCK_REMOVE),
            tooltip_text = _("Remove tags filter"),
            no_show_all = True,
            )
        self.button_mylib_tagfilter_remove.connect('clicked', self.mylib_tagfilters_number_changed)

        self.adjustment_mylib_scale_banner = Gtk.Adjustment(self.mylib_scale_level, 0.4, 1, 0.1, 0.3)
        self.adjustment_mylib_scale_banner.connect('value-changed', self.cb_adjustment_mylib_scale_banner)
        self.mylib_scl_banners = Gtk.Scale(
            tooltip_text = _("Scale"),
            orientation = Gtk.Orientation.HORIZONTAL,
            halign = Gtk.Align.END,
            valign = Gtk.Align.CENTER,
            width_request = 150,
            draw_value = False,
            show_fill_level = True,
            adjustment = self.adjustment_mylib_scale_banner,
            )

        self.mylib_filters_box.pack_start(self.mylib_tab_search_entry, True, True, 0)
        self.mylib_filters_box.pack_start(self.combobox_mylib_status, False, False, 0)
        self.mylib_filters_box.pack_start(self.combobox_mylib_tags1, False, False, 0)
        self.mylib_filters_box.pack_start(self.combobox_mylib_tags2, False, False, 0)
        self.mylib_filters_box.pack_start(self.combobox_mylib_tags3, False, False, 0)
        self.mylib_filters_box.pack_start(self.combobox_mylib_tags4, False, False, 0)
        self.mylib_filters_box.pack_start(self.button_mylib_tagfilter_remove, False, False, 0)
        self.mylib_filters_box.pack_start(self.button_mylib_tagfilter_add, False, False, 0)
        self.mylib_filters_box.pack_start(self.mylib_scl_banners, False, False, 0)

        self.mylib_tab_scrolled_window = Gtk.ScrolledWindow()

        self.mylib_tab_grid = Gtk.Grid(
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            hexpand = True,
            column_homogeneous = True,
            row_spacing = 30,
            margin_top = 30,
            margin_bottom = 30,
            )

        self.mylib_tab_scrolled_window.add(self.mylib_tab_grid)

        for i in range(0, self.mylib_number_of_games_to_show):

            mylib_game_grid = Gtk.Grid(
                name = self.mylib_shown_games_list[i],
                halign = Gtk.Align.CENTER,
                row_spacing = 1,
                column_spacing = 1,
                )
            mylib_game_grids_full_list.append(mylib_game_grid)
            mylib_game_grids_current_list.append(mylib_game_grid)

            mylib_setup_button = Gtk.Button(
                name = self.mylib_shown_games_list[i],
                )
            mylib_setup_button.set_label(_("Install"))
            mylib_setup_buttons_list.append(mylib_setup_button)
            mylib_setup_button.connect('clicked', self.mylib_setup_game)

            if not os.path.exists(data_dir + '/images/mylib_banners/' + self.mylib_shown_games_list[i] + '.jpg'):
                mylib_create_banner.mylib_create_banner(self.mylib_shown_games_list[i])

            pixbuf = GdkPixbuf.Pixbuf.new_from_file(data_dir + '/images/mylib_banners/' + self.mylib_shown_games_list[i] + '.jpg')
            pixbuf = pixbuf.scale_simple(518 * self.mylib_scale_level, 240 * self.mylib_scale_level, InterpType.BILINEAR)

            mylib_game_banner = Gtk.Image(
                name = self.mylib_shown_games_list[i],
                tooltip_text = self.mylib_list_titles[i],
                pixbuf = pixbuf
                )

            mylib_games_banners_list.append(mylib_game_banner)

            mylib_game_banner_event_box = Gtk.EventBox()
            mylib_game_banner_event_box.add(mylib_game_banner)

            mylib_game_banner_event_box.connect('button-press-event', self.mylib_banner_clicked)

            mylib_launch_button = Gtk.Button(
                name = self.mylib_shown_games_list[i],
                label = _("Launch")
                )
            mylib_launch_button.connect('clicked', self.mylib_launch_game)
            mylib_launch_buttons_list.append(mylib_launch_button)

            if os.path.exists(self.mylib_install_dir + '/' + self.mylib_shown_games_list[i] + '/start.sh'):
                mylib_setup_button.set_label(_("Remove"))
                mylib_launch_button.set_sensitive(True)
            else:
                mylib_setup_button.set_label(_("Install"))
                mylib_launch_button.set_sensitive(False)

            mylib_game_grid.attach(mylib_game_banner_event_box, 0, 0, 2, 1)
            mylib_game_grid.attach(mylib_setup_button, 0, 1, 1, 1)
            mylib_game_grid.attach(mylib_launch_button, 1, 1, 1, 1)

            max_pixbuf_width = self.mylib_scale_level * (518 + 60)
            number_of_columns = int(self.mylib_box_width / max_pixbuf_width)
            self.mylib_grid_autoresize(number_of_columns)

        self.mylib_installation_status_box = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            visible = False,
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            hexpand = True,
            )

        self.mylib_tab_progressbar = Gtk.ProgressBar(
            hexpand = True,
            show_text = True,
            text = ' ',
            pulse_step = 0.5
            )

        self.scrolledwindow_mylib_filters = Gtk.ScrolledWindow()
        self.scrolledwindow_mylib_filters.add(self.mylib_filters_box)

        self.box_mylib_page.pack_start(self.scrolledwindow_mylib_filters, False, False, 0)
        self.box_mylib_page.pack_start(self.mylib_tab_scrolled_window, True, True, 0)
        self.box_mylib_page.pack_start(self.mylib_installation_status_box, False, False, 0)

        self.mylib_installation_status_box.pack_start(self.mylib_tab_progressbar, False, False, 0)

        self.box_mylib_tab = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            spacing = 10
            )

        self.label_mylib_tab = Gtk.Label(
            label = _("MY LIBRARY")
            )

        self.button_close_mylib_tab = Gtk.Button(
            image = Gtk.Image(stock=Gtk.STOCK_CLOSE),
            relief = Gtk.ReliefStyle.NONE,
            focus_on_click = False,
            )
        self.button_close_mylib_tab.connect('clicked', self.close_tab, self.box_mylib_page)

        self.box_mylib_tab.pack_start(self.label_mylib_tab, True, True, 0)
        self.box_mylib_tab.pack_start(self.button_close_mylib_tab, False, False, 0)
        self.box_mylib_tab.show_all()

        self.notebook.append_page(self.box_mylib_page, self.box_mylib_tab)
        self.notebook.set_tab_reorderable(self.box_mylib_page, True)
        self.notebook.set_tab_detachable(self.box_mylib_page, True)

        self.cb_combobox_mylib_status(self.combobox_mylib_status)
        self.cb_combobox_mylib_tags1(self.combobox_mylib_tags1)
        self.cb_combobox_mylib_tags2(self.combobox_mylib_tags2)
        self.cb_combobox_mylib_tags3(self.combobox_mylib_tags3)
        self.cb_combobox_mylib_tags4(self.combobox_mylib_tags4)
        self.mylib_tags_visibility()
        self.update_mylib_interface()

    def cb_button_add_tab(self, button):
        self.add_tab()

    def cb_button_update_goglib(self, button):
        self.box_action_widgets_end.remove(self.button_update_goglib)
        self.box_action_widgets_end.pack_end(self.spinner_update, True, True, 0)
        self.check_for_new_games()

    def add_tab(self):

        checkbuttons_list = []

        tabs_to_add_names = {
                'goglib_tab':_("GOG LIBRARY"),
                'mylib_tab':_("MY LIBRARY"),
                'gogcom_tab':_("GOG.COM"),
                'queue_tab':_("QUEUE"),
                'settings_tab':_("SETTINGS")
                }

        for i in range(self.notebook.get_n_pages()):
            del tabs_to_add_names[self.notebook.get_nth_page(i).get_name()]

        if len(self.detached_tabs_names) != 0:
            for name in self.detached_tabs_names:
                del tabs_to_add_names[name]

        if len(tabs_to_add_names) != 0:

            message_dialog = Gtk.MessageDialog(
                self.main_window,
                0,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.OK_CANCEL,
                _("Add tabs"),
                )
            message_dialog.format_secondary_text(_("Choose tabs you want to add:"))
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('spacing', 10)

            for tab in sorted(tabs_to_add_names):
                checkbutton = Gtk.CheckButton(
                    name = tab,
                    label = tabs_to_add_names[tab]
                    )
                checkbuttons_list.append(checkbutton)
                content_area.pack_start(checkbutton, True, True, 0)

            message_dialog.show_all()
            message_dialog_response = message_dialog.run()
            message_dialog.destroy()

            if message_dialog_response == Gtk.ResponseType.OK:

                for button in checkbuttons_list:
                    if button.get_active():
                        if button.get_name() == 'goglib_tab':
                            try:
                                self.notebook.append_page(self.unauthorized_grid, self.unauthorized_tab_box)
                                self.notebook.set_tab_reorderable(self.unauthorized_grid, True)
                                self.notebook.set_tab_detachable(self.unauthorized_grid, True)
                            except:
                                try:
                                    self.notebook.append_page(self.box_goglib_page, self.box_goglib_tab)
                                    self.notebook.set_tab_reorderable(self.box_goglib_page, True)
                                    self.notebook.set_tab_detachable(self.box_goglib_page, True)
                                except:
                                    self.create_goglib_tab_content()

                        if button.get_name() == 'mylib_tab':
                            try:
                                self.notebook.append_page(self.box_mylib_page, self.box_mylib_tab)
                                self.notebook.set_tab_reorderable(self.box_mylib_page, True)
                                self.notebook.set_tab_detachable(self.box_mylib_page, True)
                            except:
                                self.create_mylib_tab()

                        if button.get_name() == 'gogcom_tab':
                            try:
                                self.notebook.append_page(self.gogcom_tab_scrolled_window, self.gogcom_tab_box)
                                self.notebook.set_tab_reorderable(self.gogcom_tab_scrolled_window, True)
                                self.notebook.set_tab_detachable(self.gogcom_tab_scrolled_window, True)
                            except:
                                self.create_gogcom_tab()

                        if button.get_name() == 'queue_tab':
                            self.notebook.append_page(self.queue_tab_scrolled_window, self.queue_tab)
                            self.notebook.set_tab_reorderable(self.queue_tab_scrolled_window, True)
                            self.notebook.set_tab_detachable(self.queue_tab_scrolled_window, True)

                        if button.get_name() == 'settings_tab':
                            self.notebook.append_page(self.scrolledwindow_settings, self.box_settings_tab)
                            self.notebook.set_tab_reorderable(self.scrolledwindow_settings, True)
                            self.notebook.set_tab_detachable(self.scrolledwindow_settings, True)

                self.set_new_page_active()

            self.main_window.show_all()

    def create_gogcom_tab(self):

        gi.require_version('WebKit2', '4.0')
        from gi.repository import WebKit2
        import webbrowser

        self.webkit = WebKit2
        self.webbrowser = webbrowser

        self.setup_cookies()

        self.webpage = self.webkit.WebView()
        self.webpage.load_uri('https://www.gog.com')

        self.gogcom_tab_scrolled_window = Gtk.ScrolledWindow(
            name = 'gogcom_tab'
            )

        self.gogcom_tab_scrolled_window.add(self.webpage)
        self.check_gogcom_tab()

        self.gogcom_tab_box = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            spacing = 10
            )

        self.gogcom_tab_label = Gtk.Label(
            label = _("GOG.COM")
            )

        self.gogcom_tab_close_button = Gtk.Button(
            image = Gtk.Image(stock=Gtk.STOCK_CLOSE),
            relief = Gtk.ReliefStyle.NONE,
            focus_on_click = False,
            )

        self.gogcom_tab_close_button.connect('clicked', self.close_tab, self.gogcom_tab_scrolled_window)

        self.gogcom_tab_box.pack_start(self.gogcom_tab_label, True, True, 0)
        self.gogcom_tab_box.pack_start(self.gogcom_tab_close_button, False, False, 0)

        self.gogcom_tab_box.show_all()

        self.notebook.append_page(self.gogcom_tab_scrolled_window, self.gogcom_tab_box)
        self.notebook.set_tab_reorderable(self.gogcom_tab_scrolled_window, True)
        self.notebook.set_tab_detachable(self.gogcom_tab_scrolled_window, True)

    def create_settings_tab(self):

        self.scrolledwindow_settings = Gtk.ScrolledWindow(
            name = 'settings_tab'
            )

        self.box_settings = Gtk.Box(
            orientation = Gtk.Orientation.VERTICAL,
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.START,
            spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.grid_common_settings = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            )

        img_app_bg = Gtk.Image()
        img_app_bg_ctx = img_app_bg.get_style_context()
        img_app_bg_ctx.add_class('lighter_background')

        self.label_tabs_at_start = Gtk.Label(
            label = _("Tabs at startup")
            )

        self.label_goglib_tab_at_start = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("GOG LIBRARY"),
            margin_top = 10,
            margin_left = 10,
            )

        self.switch_goglib_tab_at_start = Gtk.Switch(
            name = 'goglib',
            halign = Gtk.Align.END,
            margin_top = 10,
            margin_right = 10,
            active = self.goglib_tab_at_start,
            )

        self.switch_goglib_tab_at_start.connect('state-set', self.cb_switch_goglib_tab_at_start)

        self.label_mylib_tab_at_start = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("MY LIBRARY"),
            margin_left = 10,
            )

        self.switch_mylib_tab_at_start = Gtk.Switch(
            halign = Gtk.Align.END,
            margin_right = 10,
            active = self.mylib_tab_at_start,
            )
        self.switch_mylib_tab_at_start.connect('state-set', self.cb_switch_mylib_tab_at_start)

        if self.goglib_tab_at_start == False:
            self.switch_mylib_tab_at_start.set_active(True)
            self.switch_mylib_tab_at_start.set_sensitive(False)

        self.label_gogcom_tab_at_start = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("GOG.COM"),
            margin_left = 10,
            )

        self.switch_gogcom_tab_at_start = Gtk.Switch(
            halign = Gtk.Align.END,
            margin_right = 10,
            active = self.gogcom_tab_at_start
            )
        self.switch_gogcom_tab_at_start.connect('state-set', self.cb_switch_gogcom_tab_at_start)

        self.label_queue_tab_at_start = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("QUEUE"),
            margin_left = 10,
            )

        self.switch_queue_tab_at_start = Gtk.Switch(
            halign = Gtk.Align.END,
            margin_right = 10,
            active = self.queue_tab_at_start,
            )
        self.switch_queue_tab_at_start.connect('state-set', self.cb_switch_queue_tab_at_start)

        self.label_settings_tab_at_start = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("SETTINGS"),
            margin_bottom = 10,
            margin_left = 10,
            )

        self.switch_settings_tab_at_start = Gtk.Switch(
            halign = Gtk.Align.END,
            margin_bottom = 10,
            margin_right = 10,
            active = self.settings_tab_at_start,
            )
        self.switch_settings_tab_at_start.connect('state-set', self.cb_switch_settings_tab_at_start)

        self.grid_common_settings.attach(self.label_tabs_at_start, 0, 0, 4, 1)
        self.grid_common_settings.attach(self.label_goglib_tab_at_start, 0, 1, 2, 1)
        self.grid_common_settings.attach(self.switch_goglib_tab_at_start, 2, 1, 2, 1)
        self.grid_common_settings.attach(self.label_mylib_tab_at_start, 0, 2, 2, 1)
        self.grid_common_settings.attach(self.switch_mylib_tab_at_start, 2, 2, 2, 1)
        self.grid_common_settings.attach(self.label_gogcom_tab_at_start, 0, 3, 2, 1)
        self.grid_common_settings.attach(self.switch_gogcom_tab_at_start, 2, 3, 2, 1)
        self.grid_common_settings.attach(self.label_queue_tab_at_start, 0, 4, 2, 1)
        self.grid_common_settings.attach(self.switch_queue_tab_at_start, 2, 4, 2, 1)
        self.grid_common_settings.attach(self.label_settings_tab_at_start, 0, 5, 2, 1)
        self.grid_common_settings.attach(self.switch_settings_tab_at_start, 2, 5, 2, 1)
        self.grid_common_settings.attach(img_app_bg, 0, 1, 4, 5)

        self.grid_goglib_preferences = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            )

        image_goglib_preferences_bg = Gtk.Image()
        image_goglib_preferences_bg_ctx = image_goglib_preferences_bg.get_style_context()
        image_goglib_preferences_bg_ctx.add_class('lighter_background')

        self.label_goglib_preferences = Gtk.Label(
            label = _("GOG library preferences"),
            margin_left = 10,
            )

        self.label_goglib_preferred_language = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Preferred language"),
            margin_top = 10,
            margin_left = 10,
            )

        self.combobox_preferred_language = Gtk.ComboBoxText(
            margin_top = 10,
            margin_right = 10,
            )

        for lang in self.lang_list:
            self.combobox_preferred_language.append_text(lang)

        for i in range(len(self.lang_list)):
            if self.lang_list[i] == self.goglib_lang:
                self.combobox_preferred_language.set_active(i)

        self.combobox_preferred_language.connect('changed', self.cb_combobox_preferred_language)

        self.label_goglib_keep_installers = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Keep installers"),
            margin_left = 10,
            )

        self.switch_goglib_keep_installers = Gtk.Switch(
            halign = Gtk.Align.END,
            margin_right = 10,
            active = self.goglib_keep_installers
            )
        self.switch_goglib_keep_installers.connect('state-set', self.cb_switch_goglib_keep_installers)

        if self.goglib_download_extras:
            self.switch_goglib_keep_installers.set_active(True)
            self.switch_goglib_keep_installers.set_sensitive(False)
        else:
            self.switch_goglib_keep_installers.set_sensitive(True)

        self.label_goglib_download_extras = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Download extras"),
            margin_left = 10,
            )

        self.switch_goglib_download_extras = Gtk.Switch(
            halign = Gtk.Align.END,
            margin_right = 10,
            active = self.goglib_download_extras
            )
        self.switch_goglib_download_extras.connect('state-set', self.cb_switch_goglib_download_extras)

        self.label_goglib_offline_mode = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Start in offline mode"),
            margin_left = 10,
            )

        self.switch_goglib_offline_mode = Gtk.Switch(
            halign = Gtk.Align.END,
            margin_right = 10,
            active = self.goglib_offline_mode
            )
        self.switch_goglib_offline_mode.connect('state-set', self.cb_switch_goglib_offline_mode)

        self.label_goglib_download_dir = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Downloads directory"),
            margin_left = 10,
            )

        self.filechooserbutton_goglib_download_dir = Gtk.FileChooserButton(
            title = _("Select a directory"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            margin_right = 10,
            )
        self.filechooserbutton_goglib_download_dir.set_current_folder(self.goglib_download_dir)
        self.filechooserbutton_goglib_download_dir.connect('file-set', self.cb_filechooserbutton_goglib_download_dir)

        self.label_goglib_install_dir = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Installation directory"),
            margin_left = 10,
            )

        self.filechooserbutton_goglib_install_dir = Gtk.FileChooserButton(
            name = 'goglib_install_dir',
            title = _("Select a directory"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            margin_right = 10,
            )
        self.filechooserbutton_goglib_install_dir.set_current_folder(self.goglib_install_dir)
        self.filechooserbutton_goglib_install_dir.connect('file-set', self.cb_filechooserbutton_goglib_install_dir)

        self.button_goglib_scripts = Gtk.Button(
            label = _("Download"),
            name = 'goglib'
            )
        self.button_goglib_scripts.connect('clicked', self.cb_button_get_scripts)

        self.checkbutton_goglib_scripts = Gtk.CheckButton(
            label = _("Overwrite existing scripts"),
            name = 'goglib',
            active = self.goglib_scripts_overwrite
            )
        self.checkbutton_goglib_scripts.connect('clicked', self.cb_checkbutton_scripts_overwrite)

        self.grid_goglib_scripts = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.grid_goglib_scripts.attach(self.button_goglib_scripts, 0, 0, 1, 1)
        self.grid_goglib_scripts.attach(self.checkbutton_goglib_scripts, 0, 1, 1, 1)

        self.frame_goglib_scripts = Gtk.Frame(
            label = _("Installation scripts"),
            label_xalign = 0.5,
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            )
        self.frame_goglib_scripts.add(self.grid_goglib_scripts)

        self.label_goglib_status_filter_behavior = Gtk.Label(
            label = _("Status filter behaivior:"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_goglib_status_filter_include = Gtk.RadioButton(
            label = _("Include"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_goglib_status_filter_exclude = Gtk.RadioButton(
            label = _("Exclude"),
            halign = Gtk.Align.END,
            )
        self.radiobutton_goglib_status_filter_exclude.join_group(self.radiobutton_goglib_status_filter_include)

        if self.goglib_status_filter_type == 'include':
            self.radiobutton_goglib_status_filter_include.set_active(True)
        elif self.goglib_status_filter_type == 'exclude':
            self.radiobutton_goglib_status_filter_exclude.set_active(True)
        self.radiobutton_goglib_status_filter_include.connect('toggled', self.cb_radiobutton_goglib_status_filter_include)

        self.label_goglib_tag1_behavior = Gtk.Label(
            label = _("Tags filter 1 behaivior:"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_goglib_tag1_include = Gtk.RadioButton(
            label = _("Include"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_goglib_tag1_exclude = Gtk.RadioButton(
            label = _("Exclude"),
            halign = Gtk.Align.END,
            )
        self.radiobutton_goglib_tag1_exclude.join_group(self.radiobutton_goglib_tag1_include)

        if self.goglib_tags_filter1_type == 'include':
            self.radiobutton_goglib_tag1_include.set_active(True)
        elif self.goglib_tags_filter1_type == 'exclude':
            self.radiobutton_goglib_tag1_exclude.set_active(True)
        self.radiobutton_goglib_tag1_include.connect('toggled', self.cb_radiobutton_goglib_tag1_include)

        self.label_goglib_tag2_behavior = Gtk.Label(
            label = _("Tags filter 2 behaivior:"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_goglib_tag2_include = Gtk.RadioButton(
            label = _("Include"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_goglib_tag2_exclude = Gtk.RadioButton(
            label = _("Exclude"),
            halign = Gtk.Align.END,
            )
        self.radiobutton_goglib_tag2_exclude.join_group(self.radiobutton_goglib_tag2_include)

        if self.goglib_tags_filter2_type == 'include':
            self.radiobutton_goglib_tag2_include.set_active(True)
        elif self.goglib_tags_filter2_type == 'exclude':
            self.radiobutton_goglib_tag2_exclude.set_active(True)
        self.radiobutton_goglib_tag2_include.connect('toggled', self.cb_radiobutton_goglib_tag2_include)

        self.label_goglib_tag3_behavior = Gtk.Label(
            label = _("Tags filter 3 behaivior:"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_goglib_tag3_include = Gtk.RadioButton(
            label = _("Include"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_goglib_tag3_exclude = Gtk.RadioButton(
            label = _("Exclude"),
            halign = Gtk.Align.END,
            )
        self.radiobutton_goglib_tag3_exclude.join_group(self.radiobutton_goglib_tag3_include)

        if self.goglib_tags_filter3_type == 'include':
            self.radiobutton_goglib_tag3_include.set_active(True)
        elif self.goglib_tags_filter3_type == 'exclude':
            self.radiobutton_goglib_tag3_exclude.set_active(True)
        self.radiobutton_goglib_tag3_include.connect('toggled', self.cb_radiobutton_goglib_tag3_include)

        self.label_goglib_tag4_behavior = Gtk.Label(
            label = _("Tags filter 4 behaivior:"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_goglib_tag4_include = Gtk.RadioButton(
            label = _("Include"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_goglib_tag4_exclude = Gtk.RadioButton(
            label = _("Exclude"),
            halign = Gtk.Align.END,
            )
        self.radiobutton_goglib_tag4_exclude.join_group(self.radiobutton_goglib_tag4_include)

        if self.goglib_tags_filter4_type == 'include':
            self.radiobutton_goglib_tag4_include.set_active(True)
        elif self.goglib_tags_filter4_type == 'exclude':
            self.radiobutton_goglib_tag4_exclude.set_active(True)
        self.radiobutton_goglib_tag4_include.connect('toggled', self.cb_radiobutton_goglib_tag4_include)

        self.label_goglib_filter_color_indication = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Filters color indication"),
            )
        self.switch_goglib_filter_color_indication = Gtk.Switch(
            active = self.goglib_filter_color_indication,
            halign = Gtk.Align.END,
            )
        self.switch_goglib_filter_color_indication.connect('state-set', self.cb_switch_goglib_filter_color_indication)

        self.label_goglib_colors = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Include/exclude colors:"),
            )

        self.colorbutton_goglib_include = Gtk.ColorButton(
            tooltip_text = _("Include"),
            use_alpha = True
            )
        self.colorbutton_goglib_include.set_rgba(self.goglib_include_rgba)
        self.colorbutton_goglib_include.connect('color-set', self.cb_colorbutton_goglib_include)

        self.colorbutton_goglib_exclude = Gtk.ColorButton(
            tooltip_text = _("Exclude"),
            use_alpha = True
            )
        self.colorbutton_goglib_exclude.set_rgba(self.goglib_exclude_rgba)
        self.colorbutton_goglib_exclude.connect('color-set', self.cb_colorbutton_goglib_exclude)

        self.grid_goglib_filters = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )
        self.grid_goglib_filters.attach(self.label_goglib_status_filter_behavior, 0, 0, 2, 1)
        self.grid_goglib_filters.attach(self.radiobutton_goglib_status_filter_include, 2, 0, 1, 1)
        self.grid_goglib_filters.attach(self.radiobutton_goglib_status_filter_exclude, 3, 0, 1, 1)
        self.grid_goglib_filters.attach(self.label_goglib_tag1_behavior, 0, 1, 2, 1)
        self.grid_goglib_filters.attach(self.radiobutton_goglib_tag1_include, 2, 1, 1, 1)
        self.grid_goglib_filters.attach(self.radiobutton_goglib_tag1_exclude, 3, 1, 1, 1)
        self.grid_goglib_filters.attach(self.label_goglib_tag2_behavior, 0, 2, 2, 1)
        self.grid_goglib_filters.attach(self.radiobutton_goglib_tag2_include, 2, 2, 1, 1)
        self.grid_goglib_filters.attach(self.radiobutton_goglib_tag2_exclude, 3, 2, 1, 1)
        self.grid_goglib_filters.attach(self.label_goglib_tag3_behavior, 0, 3, 2, 1)
        self.grid_goglib_filters.attach(self.radiobutton_goglib_tag3_include, 2, 3, 1, 1)
        self.grid_goglib_filters.attach(self.radiobutton_goglib_tag3_exclude, 3, 3, 1, 1)
        self.grid_goglib_filters.attach(self.label_goglib_tag4_behavior, 0, 4, 2, 1)
        self.grid_goglib_filters.attach(self.radiobutton_goglib_tag4_include, 2, 4, 1, 1)
        self.grid_goglib_filters.attach(self.radiobutton_goglib_tag4_exclude, 3, 4, 1, 1)
        self.grid_goglib_filters.attach(self.label_goglib_filter_color_indication, 0, 5, 2, 1)
        self.grid_goglib_filters.attach(self.switch_goglib_filter_color_indication, 2, 5, 2, 1)
        self.grid_goglib_filters.attach(self.label_goglib_colors, 0, 6, 2, 1)
        self.grid_goglib_filters.attach(self.colorbutton_goglib_include, 2, 6, 1, 1)
        self.grid_goglib_filters.attach(self.colorbutton_goglib_exclude, 3, 6, 1, 1)

        self.frame_goglib_filters = Gtk.Frame(
            label = _("Filters"),
            label_xalign = 0.5,
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            )
        self.frame_goglib_filters.add(self.grid_goglib_filters)

        self.grid_goglib_preferences.attach(self.label_goglib_preferences, 0, 0, 4, 1)
        self.grid_goglib_preferences.attach(self.label_goglib_preferred_language, 0, 1, 2, 1)
        self.grid_goglib_preferences.attach(self.combobox_preferred_language, 2, 1, 2, 1)
        self.grid_goglib_preferences.attach(self.label_goglib_keep_installers, 0, 2, 2, 1)
        self.grid_goglib_preferences.attach(self.switch_goglib_keep_installers, 2, 2, 2, 1)
        self.grid_goglib_preferences.attach(self.label_goglib_download_extras, 0, 3, 2, 1)
        self.grid_goglib_preferences.attach(self.switch_goglib_download_extras, 2, 3, 2, 1)
        self.grid_goglib_preferences.attach(self.label_goglib_offline_mode, 0, 4, 2, 1)
        self.grid_goglib_preferences.attach(self.switch_goglib_offline_mode, 2, 4, 2, 1)
        self.grid_goglib_preferences.attach(self.label_goglib_download_dir, 0, 5, 2, 1)
        self.grid_goglib_preferences.attach(self.filechooserbutton_goglib_download_dir, 2, 5, 2, 1)
        self.grid_goglib_preferences.attach(self.label_goglib_install_dir, 0, 6, 2, 1)
        self.grid_goglib_preferences.attach(self.filechooserbutton_goglib_install_dir, 2, 6, 2, 1)
        self.grid_goglib_preferences.attach(self.frame_goglib_scripts, 0, 7, 4, 1)
        self.grid_goglib_preferences.attach(self.frame_goglib_filters, 0, 8, 4, 1)
        self.grid_goglib_preferences.attach(image_goglib_preferences_bg, 0, 1, 4, 8)

        self.grid_mylib_preferences = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            )

        imgage_mylib_preferences_bg = Gtk.Image()
        imgage_mylib_preferences_bg_ctx = imgage_mylib_preferences_bg.get_style_context()
        imgage_mylib_preferences_bg_ctx.add_class('lighter_background')

        self.label_mylib_preferences = Gtk.Label(
            label = _("My library preferences"),
            margin_left = 10,
            )

        self.label_mylib_keep_installers = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Keep installers"),
            margin_left = 10,
            )

        self.switch_mylib_keep_installers = Gtk.Switch(
            halign = Gtk.Align.END,
            margin_top = 10,
            margin_right = 10,
            active = self.mylib_keep_installers,
            )
        self.switch_mylib_keep_installers.connect('state-set', self.cb_switch_mylib_keep_installers)


        self.label_mylib_download_dir = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Downloads directory"),
            margin_left = 10,
            )

        self.filechooserbutton_mylib_download_dir = Gtk.FileChooserButton(
            title = _("Select a directory"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            margin_right = 10,
            )
        self.filechooserbutton_mylib_download_dir.set_current_folder(self.mylib_download_dir)
        self.filechooserbutton_mylib_download_dir.connect('file-set', self.cb_filechooserbutton_mylib_download_dir)

        self.label_mylib_install_dir = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Installation directory"),
            margin_left = 10,
            margin_bottom = 10,
            )

        self.filechooserbutton_mylib_install_dir = Gtk.FileChooserButton(
            title = _("Select a directory"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            margin_right = 10,
            margin_bottom = 10,
            )
        self.filechooserbutton_mylib_install_dir.set_current_folder(self.mylib_install_dir)
        self.filechooserbutton_mylib_install_dir.connect('file-set', self.cb_filechooserbutton_mylib_install_dir)

        self.button_mylib_scripts = Gtk.Button(
            label = _("Download"),
            name = 'mylib'
            )
        self.button_mylib_scripts.connect('clicked', self.cb_button_get_scripts)

        self.checkbutton_mylib_scripts = Gtk.CheckButton(
            label = _("Overwrite existing scripts"),
            name = 'mylib',
            active = self.mylib_scripts_overwrite
            )
        self.checkbutton_mylib_scripts.connect('clicked', self.cb_checkbutton_scripts_overwrite)

        self.grid_mylib_scripts = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.grid_mylib_scripts.attach(self.button_mylib_scripts, 0, 0, 1, 1)
        self.grid_mylib_scripts.attach(self.checkbutton_mylib_scripts, 0, 1, 1, 1)

        self.frame_mylib_scripts = Gtk.Frame(
            label = _("Installation scripts"),
            label_xalign = 0.5,
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            )
        self.frame_mylib_scripts.add(self.grid_mylib_scripts)

        self.label_mylib_status_filter_behavior = Gtk.Label(
            label = _("Status filter behaivior:"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_mylib_status_filter_include = Gtk.RadioButton(
            label = _("Include"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_mylib_status_filter_exclude = Gtk.RadioButton(
            label = _("Exclude"),
            halign = Gtk.Align.END,
            )
        self.radiobutton_mylib_status_filter_exclude.join_group(self.radiobutton_mylib_status_filter_include)

        if self.mylib_status_filter_type == 'include':
            self.radiobutton_mylib_status_filter_include.set_active(True)
        elif self.mylib_status_filter_type == 'exclude':
            self.radiobutton_mylib_status_filter_exclude.set_active(True)
        self.radiobutton_mylib_status_filter_include.connect('toggled', self.cb_radiobutton_mylib_status_filter_include)

        self.label_mylib_tag1_behavior = Gtk.Label(
            label = _("Tags filter 1 behaivior:"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_mylib_tag1_include = Gtk.RadioButton(
            label = _("Include"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_mylib_tag1_exclude = Gtk.RadioButton(
            label = _("Exclude"),
            halign = Gtk.Align.END,
            )
        self.radiobutton_mylib_tag1_exclude.join_group(self.radiobutton_mylib_tag1_include)

        if self.mylib_tags_filter1_type == 'include':
            self.radiobutton_mylib_tag1_include.set_active(True)
        elif self.mylib_tags_filter1_type == 'exclude':
            self.radiobutton_mylib_tag1_exclude.set_active(True)
        self.radiobutton_mylib_tag1_include.connect('toggled', self.cb_radiobutton_mylib_tag1_include)

        self.label_mylib_tag2_behavior = Gtk.Label(
            label = _("Tags filter 2 behaivior:"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_mylib_tag2_include = Gtk.RadioButton(
            label = _("Include"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_mylib_tag2_exclude = Gtk.RadioButton(
            label = _("Exclude"),
            halign = Gtk.Align.END,
            )
        self.radiobutton_mylib_tag2_exclude.join_group(self.radiobutton_mylib_tag2_include)

        if self.mylib_tags_filter2_type == 'include':
            self.radiobutton_mylib_tag2_include.set_active(True)
        elif self.mylib_tags_filter2_type == 'exclude':
            self.radiobutton_mylib_tag2_exclude.set_active(True)
        self.radiobutton_mylib_tag2_include.connect('toggled', self.cb_radiobutton_mylib_tag2_include)

        self.label_mylib_tag3_behavior = Gtk.Label(
            label = _("Tags filter 3 behaivior:"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_mylib_tag3_include = Gtk.RadioButton(
            label = _("Include"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_mylib_tag3_exclude = Gtk.RadioButton(
            label = _("Exclude"),
            halign = Gtk.Align.END,
            )
        self.radiobutton_mylib_tag3_exclude.join_group(self.radiobutton_mylib_tag3_include)

        if self.mylib_tags_filter3_type == 'include':
            self.radiobutton_mylib_tag3_include.set_active(True)
        elif self.mylib_tags_filter3_type == 'exclude':
            self.radiobutton_mylib_tag3_exclude.set_active(True)
        self.radiobutton_mylib_tag3_include.connect('toggled', self.cb_radiobutton_mylib_tag3_include)

        self.label_mylib_tag4_behavior = Gtk.Label(
            label = _("Tags filter 4 behaivior:"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_mylib_tag4_include = Gtk.RadioButton(
            label = _("Include"),
            halign = Gtk.Align.START,
            )
        self.radiobutton_mylib_tag4_exclude = Gtk.RadioButton(
            label = _("Exclude"),
            halign = Gtk.Align.END,
            )
        self.radiobutton_mylib_tag4_exclude.join_group(self.radiobutton_mylib_tag4_include)

        if self.mylib_tags_filter4_type == 'include':
            self.radiobutton_mylib_tag4_include.set_active(True)
        elif self.mylib_tags_filter4_type == 'exclude':
            self.radiobutton_mylib_tag4_exclude.set_active(True)
        self.radiobutton_mylib_tag4_include.connect('toggled', self.cb_radiobutton_mylib_tag4_include)

        self.label_mylib_filter_color_indication = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Filters color indication"),
            )
        self.switch_mylib_filter_color_indication = Gtk.Switch(
            active = self.mylib_filter_color_indication,
            halign = Gtk.Align.END,
            )
        self.switch_mylib_filter_color_indication.connect('state-set', self.cb_switch_mylib_filter_color_indication)

        self.label_mylib_colors = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Include/exclude colors:"),
            )

        self.colorbutton_mylib_include = Gtk.ColorButton(
            tooltip_text = _("Include"),
            use_alpha = True
            )
        self.colorbutton_mylib_include.set_rgba(self.mylib_include_rgba)
        self.colorbutton_mylib_include.connect('color-set', self.cb_colorbutton_mylib_include)

        self.colorbutton_mylib_exclude = Gtk.ColorButton(
            tooltip_text = _("Exclude"),
            use_alpha = True
            )
        self.colorbutton_mylib_exclude.set_rgba(self.mylib_exclude_rgba)
        self.colorbutton_mylib_exclude.connect('color-set', self.cb_colorbutton_mylib_exclude)

        self.grid_mylib_filters = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )
        self.grid_mylib_filters.attach(self.label_mylib_status_filter_behavior, 0, 0, 2, 1)
        self.grid_mylib_filters.attach(self.radiobutton_mylib_status_filter_include, 2, 0, 1, 1)
        self.grid_mylib_filters.attach(self.radiobutton_mylib_status_filter_exclude, 3, 0, 1, 1)
        self.grid_mylib_filters.attach(self.label_mylib_tag1_behavior, 0, 1, 2, 1)
        self.grid_mylib_filters.attach(self.radiobutton_mylib_tag1_include, 2, 1, 1, 1)
        self.grid_mylib_filters.attach(self.radiobutton_mylib_tag1_exclude, 3, 1, 1, 1)
        self.grid_mylib_filters.attach(self.label_mylib_tag2_behavior, 0, 2, 2, 1)
        self.grid_mylib_filters.attach(self.radiobutton_mylib_tag2_include, 2, 2, 1, 1)
        self.grid_mylib_filters.attach(self.radiobutton_mylib_tag2_exclude, 3, 2, 1, 1)
        self.grid_mylib_filters.attach(self.label_mylib_tag3_behavior, 0, 3, 2, 1)
        self.grid_mylib_filters.attach(self.radiobutton_mylib_tag3_include, 2, 3, 1, 1)
        self.grid_mylib_filters.attach(self.radiobutton_mylib_tag3_exclude, 3, 3, 1, 1)
        self.grid_mylib_filters.attach(self.label_mylib_tag4_behavior, 0, 4, 2, 1)
        self.grid_mylib_filters.attach(self.radiobutton_mylib_tag4_include, 2, 4, 1, 1)
        self.grid_mylib_filters.attach(self.radiobutton_mylib_tag4_exclude, 3, 4, 1, 1)
        self.grid_mylib_filters.attach(self.label_mylib_filter_color_indication, 0, 5, 2, 1)
        self.grid_mylib_filters.attach(self.switch_mylib_filter_color_indication, 2, 5, 2, 1)
        self.grid_mylib_filters.attach(self.label_mylib_colors, 0, 6, 2, 1)
        self.grid_mylib_filters.attach(self.colorbutton_mylib_include, 2, 6, 1, 1)
        self.grid_mylib_filters.attach(self.colorbutton_mylib_exclude, 3, 6, 1, 1)

        self.frame_mylib_filters = Gtk.Frame(
            label = _("Filters"),
            label_xalign = 0.5,
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            )
        self.frame_mylib_filters.add(self.grid_mylib_filters)

        self.grid_mylib_preferences.attach(self.label_mylib_preferences, 0, 0, 4, 1)
        self.grid_mylib_preferences.attach(self.label_mylib_keep_installers, 0, 1, 2, 1)
        self.grid_mylib_preferences.attach(self.switch_mylib_keep_installers, 2, 1, 2, 1)
        self.grid_mylib_preferences.attach(self.label_mylib_download_dir, 0, 2, 2, 1)
        self.grid_mylib_preferences.attach(self.filechooserbutton_mylib_download_dir, 2, 2, 2, 1)
        self.grid_mylib_preferences.attach(self.label_mylib_install_dir, 0, 3, 2, 1)
        self.grid_mylib_preferences.attach(self.filechooserbutton_mylib_install_dir, 2, 3, 2, 1)
        self.grid_mylib_preferences.attach(self.frame_mylib_scripts, 0, 4, 4, 1)
        self.grid_mylib_preferences.attach(self.frame_mylib_filters, 0, 5, 4, 1)
        self.grid_mylib_preferences.attach(imgage_mylib_preferences_bg, 0, 1, 4, 5)

        self.grid_visuals = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            )

        image_visuals_bg = Gtk.Image()
        image_visuals_bg_ctx = image_visuals_bg.get_style_context()
        image_visuals_bg_ctx.add_class('lighter_background')

        self.label_visuals = Gtk.Label(
            label = _("Visuals")
            )

        self.label_gtk_theme = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("GTK+ theme"),
            margin_top = 10,
            margin_left = 10,
            )

        self.combobox_gtk_theme = Gtk.ComboBoxText(
            margin_top = 10,
            margin_right = 10,
            )

        self.label_dark_theme = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Dark variant"),
            margin_left = 10,
            )

        self.switch_dark_theme = Gtk.Switch(
            halign = Gtk.Align.END,
            margin_right = 10,
            active = self.gtk_dark,
            )
        self.switch_dark_theme.connect('state-set', self.cb_switch_dark_theme)

        self.label_icon_theme = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Icon theme"),
            margin_left = 10,
            )

        self.combobox_icon_theme = Gtk.ComboBoxText(
            margin_right = 10,
            )

        self.label_font = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Font"),
            margin_bottom = 10,
            margin_left = 10,
            )

        self.fontbutton = Gtk.FontButton(
            margin_bottom = 10,
            margin_right = 10,
            font = self.font
            )
        self.fontbutton.connect('font-set', self.cb_fontbutton)

        self.populate_themes_comboboxes()
        self.combobox_gtk_theme.connect('changed', self.cb_combobox_gtk_theme)
        self.combobox_icon_theme.connect('changed', self.cb_combobox_icon_theme)

        self.grid_visuals.attach(self.label_visuals, 0, 0, 4, 1)
        self.grid_visuals.attach(self.label_gtk_theme, 0, 1, 2, 1)
        self.grid_visuals.attach(self.combobox_gtk_theme, 2, 1, 2, 1)
        self.grid_visuals.attach(self.label_dark_theme, 0, 2, 2, 1)
        self.grid_visuals.attach(self.switch_dark_theme, 2, 2, 2, 1)
        self.grid_visuals.attach(self.label_icon_theme, 0, 3, 2, 1)
        self.grid_visuals.attach(self.combobox_icon_theme, 2, 3, 2, 1)
        self.grid_visuals.attach(self.label_font, 0, 4, 2, 1)
        self.grid_visuals.attach(self.fontbutton, 2, 4, 2, 1)
        self.grid_visuals.attach(image_visuals_bg, 0, 1, 4, 4)

        self.grid_emulation = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            )

        image_emulation_bg = Gtk.Image()
        image_emulation_bg_ctx = image_emulation_bg.get_style_context()
        image_emulation_bg_ctx.add_class('lighter_background')

        self.label_emulation = Gtk.Label(
            label = _("Emulators settings")
            )

        self.label_monitor = Gtk.Label(
            halign = Gtk.Align.START,
            label = _("Monitor"),
            margin_top = 10,
            margin_left = 10,
            )

        self.combobox_monitor = Gtk.ComboBoxText(
            margin_top = 10,
            margin_right = 10,
            )

        for output in self.monitors_list:
            try:
                self.combobox_monitor.append_text(output.translate(None, '\n'))
            except:
                char_map = str.maketrans('', '', '\n')
                self.combobox_monitor.append_text(output.translate(char_map))

        self.combobox_monitor.set_active(self.monitor)

        self.combobox_monitor.connect('changed', self.cb_combobox_monitor)

        self.frame_wine_settings = Gtk.Frame(
            label = _("Wine"),
            label_xalign = 0.5,
            margin_left = 10,
            margin_right = 10,
            )

        self.grid_wine_settings = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.radiobutton_wine_settings_sys = Gtk.RadioButton(
            name = 'system',
            label = _("System version")
            )

        self.radiobutton_wine_settings_dir = Gtk.RadioButton(
            name = 'path',
            label = _("From directory")
            )

        self.radiobutton_wine_settings_dir.join_group(self.radiobutton_wine_settings_sys)

        self.filechooserbutton_wine = Gtk.FileChooserButton(
            title = _("Select a directory"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            no_show_all = True,
            )
        self.filechooserbutton_wine.set_filename(self.wine_path)
        self.filechooserbutton_wine.connect('file-set', self.cb_filechooserbutton_wine)

        self.combobox_wine_version = Gtk.ComboBoxText(
            no_show_all = True,
            )
        self.populate_wine_version_combobox()
        self.combobox_wine_version.connect('changed', self.cb_combobox_wine_version)

        checkbutton_own_prefix = Gtk.CheckButton(
            label = _("Own wineprefix for every game"),
            active = self.own_prefix
            )
        checkbutton_own_prefix.connect('clicked', self.cb_checkbutton_own_prefix)

        self.button_winetricks_cache = Gtk.Button(
            label = _("Backup/Restore winetricks cache")
            )
        self.button_winetricks_cache.connect('clicked', self.cb_button_winetricks_cache)

        self.button_wine_settings = Gtk.Button(
            label = _("Wine settings")
            )
        self.button_wine_settings.connect('clicked', self.cb_button_wine_settings)

        self.label_winearch = Gtk.Label(
            label = _("Winearch:"),
            no_show_all = True
            )

        self.combobox_winearch = Gtk.ComboBoxText(
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

        self.grid_wine_settings.attach(self.radiobutton_wine_settings_sys, 0, 0, 4, 1)
        self.grid_wine_settings.attach(self.radiobutton_wine_settings_dir, 0, 1, 4, 1)
        self.grid_wine_settings.attach(self.filechooserbutton_wine, 0, 2, 2, 1)
        self.grid_wine_settings.attach(self.combobox_wine_version, 2, 2, 2, 1)
        self.grid_wine_settings.attach(self.label_winearch, 0, 3, 2, 1)
        self.grid_wine_settings.attach(self.combobox_winearch, 2, 3, 2, 1)
        self.grid_wine_settings.attach(checkbutton_own_prefix, 0, 4, 4, 1)
        self.grid_wine_settings.attach(self.button_winetricks_cache, 0, 5, 4, 1)
        self.grid_wine_settings.attach(self.button_wine_settings, 0, 6, 4, 1)

        self.frame_wine_settings.add(self.grid_wine_settings)
        self.radiobutton_wine_settings_sys.connect('toggled', self.cb_radiobutton_wine_settings)
        self.radiobutton_wine_settings_dir.connect('toggled', self.cb_radiobutton_wine_settings)

        if self.wine == 'system':
            self.radiobutton_wine_settings_sys.set_active(True)
            self.radiobutton_wine_settings_dir.set_label(_("From directory"))
            self.filechooserbutton_wine.set_visible(False)
            self.combobox_wine_version.set_visible(False)
        if self.wine == 'path':
            self.radiobutton_wine_settings_dir.set_active(True)
            self.radiobutton_wine_settings_dir.set_label(_("From directory:"))
            self.filechooserbutton_wine.set_visible(True)
            self.combobox_wine_version.set_visible(True)

        self.frame_dosbox_settings = Gtk.Frame(
            label = _("DOSBox"),
            label_xalign = 0.5,
            margin_left = 10,
            margin_right = 10,
            )

        self.grid_dosbox_settings = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.radiobutton_dosbox_settings_sys = Gtk.RadioButton(
            name = 'system',
            label = _("System version")
            )

        self.radiobutton_dosbox_settings_dir = Gtk.RadioButton(
            name = 'path',
            label = _("From directory"),
            )

        self.radiobutton_dosbox_settings_dir.join_group(self.radiobutton_dosbox_settings_sys)

        self.filechooserbutton_dosbox = Gtk.FileChooserButton(
            title = _("Select a directory"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            no_show_all = True
            )
        self.filechooserbutton_dosbox.set_filename(self.dosbox_path)
        self.filechooserbutton_dosbox.connect('file-set', self.cb_filechooserbutton_dosbox)

        self.combobox_dosbox_version = Gtk.ComboBoxText(
            no_show_all = True
            )
        self.combobox_dosbox_version.connect('changed', self.cb_combobox_dosbox_version)

        self.populate_dosbox_version_combobox()

        self.button_dosbox_settings = Gtk.Button(
            label = _("DOSBox settings")
            )

        self.button_dosbox_settings.connect('clicked', self.cb_button_dosbox_settings)

        self.grid_dosbox_settings.attach(self.radiobutton_dosbox_settings_sys, 0, 0, 4, 1)
        self.grid_dosbox_settings.attach(self.radiobutton_dosbox_settings_dir, 0, 1, 2, 1)
        self.grid_dosbox_settings.attach(self.filechooserbutton_dosbox, 0, 2, 2, 1)
        self.grid_dosbox_settings.attach(self.combobox_dosbox_version, 2, 2, 2, 1)
        self.grid_dosbox_settings.attach(self.button_dosbox_settings, 0, 3, 4, 1)

        self.frame_dosbox_settings.add(self.grid_dosbox_settings)

        self.radiobutton_dosbox_settings_sys.connect('toggled', self.cb_radiobutton_dosbox_settings)
        self.radiobutton_dosbox_settings_dir.connect('toggled', self.cb_radiobutton_dosbox_settings)

        if self.dosbox == 'system':
            self.radiobutton_dosbox_settings_dir.set_label(_("From directory"))
            self.radiobutton_dosbox_settings_sys.set_active(True)
            self.filechooserbutton_dosbox.set_visible(False)
            self.combobox_dosbox_version.set_visible(False)
        if self.dosbox == 'path':
            self.radiobutton_dosbox_settings_dir.set_label(_("From directory:"))
            self.radiobutton_dosbox_settings_dir.set_active(True)
            self.filechooserbutton_dosbox.set_visible(True)
            self.combobox_dosbox_version.set_visible(True)

        self.frame_scummvm_settings = Gtk.Frame(
            label = _("ScummVM"),
            label_xalign = 0.5,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.grid_scummvm_settings = Gtk.Grid(
            column_homogeneous = True,
            row_spacing = 10,
            column_spacing = 10,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 10,
            margin_right = 10,
            )

        self.radiobutton_scummvm_settings_sys = Gtk.RadioButton(
            name = 'system',
            label = _("System version")
            )

        self.radiobutton_scummvm_settings_dir = Gtk.RadioButton(
            name = 'path',
            label = _("From directory:")
            )

        self.radiobutton_scummvm_settings_dir.join_group(self.radiobutton_scummvm_settings_sys)

        self.filechooserbutton_scummvm = Gtk.FileChooserButton(
            title = _("Select a directory"),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            no_show_all = True
            )
        self.filechooserbutton_scummvm.set_filename(self.scummvm_path)
        self.filechooserbutton_scummvm.connect('file-set', self.cb_filechooserbutton_scummvm)

        self.combobox_scummvm_version = Gtk.ComboBoxText(
            no_show_all = True
            )
        self.combobox_scummvm_version.connect('changed', self.cb_combobox_scummvm_version)

        self.populate_scummvm_version_combobox()

        self.button_scummvm_settings = Gtk.Button(
            label = _("ScummVM settings")
            )

        self.button_scummvm_settings.connect('clicked', self.cb_button_scummvm_settings)

        self.grid_scummvm_settings.attach(self.radiobutton_scummvm_settings_sys, 0, 0, 4, 1)
        self.grid_scummvm_settings.attach(self.radiobutton_scummvm_settings_dir, 0, 1, 2, 1)
        self.grid_scummvm_settings.attach(self.filechooserbutton_scummvm, 0, 2, 2, 1)
        self.grid_scummvm_settings.attach(self.combobox_scummvm_version, 2, 2, 2, 1)
        self.grid_scummvm_settings.attach(self.button_scummvm_settings, 0, 3, 4, 1)

        self.frame_scummvm_settings.add(self.grid_scummvm_settings)

        self.radiobutton_scummvm_settings_sys.connect('toggled', self.cb_radiobutton_scummvm_settings)
        self.radiobutton_scummvm_settings_dir.connect('toggled', self.cb_radiobutton_scummvm_settings)

        if self.scummvm == 'system':
            self.radiobutton_scummvm_settings_dir.set_label(_("From directory"))
            self.radiobutton_scummvm_settings_sys.set_active(True)
            self.filechooserbutton_scummvm.set_visible(False)
            self.combobox_scummvm_version.set_visible(False)
        if self.scummvm == 'path':
            self.radiobutton_scummvm_settings_dir.set_label(_("From directory:"))
            self.radiobutton_scummvm_settings_dir.set_active(True)
            self.filechooserbutton_scummvm.set_visible(True)
            self.combobox_scummvm_version.set_visible(True)

        self.grid_emulation.attach(self.label_emulation, 0, 0, 4, 1)
        self.grid_emulation.attach(self.label_monitor, 0, 1, 2, 1)
        self.grid_emulation.attach(self.combobox_monitor, 2, 1, 2, 1)
        self.grid_emulation.attach(self.frame_wine_settings, 0, 2, 4, 1)
        self.grid_emulation.attach(self.frame_dosbox_settings, 0, 3, 4, 1)
        self.grid_emulation.attach(self.frame_scummvm_settings, 0, 4, 4, 1)
        self.grid_emulation.attach(image_emulation_bg, 0, 1, 4, 4)

        self.box_settings.pack_start(self.grid_common_settings, True, True, 0)
        self.box_settings.pack_start(self.grid_goglib_preferences, True, True, 0)
        self.box_settings.pack_start(self.grid_mylib_preferences, True, True, 0)
        self.box_settings.pack_start(self.grid_visuals, True, True, 0)
        self.box_settings.pack_start(self.grid_emulation, True, True, 0)

        self.box_settings_tab = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            spacing = 10
            )

        self.label_settings_tab = Gtk.Label(
            label = _("SETTINGS")
            )

        self.button_close_settings_tab = Gtk.Button(
            image = Gtk.Image(stock=Gtk.STOCK_CLOSE),
            relief = Gtk.ReliefStyle.NONE,
            focus_on_click = False,
            )
        self.button_close_settings_tab.connect('clicked', self.close_tab, self.scrolledwindow_settings)

        self.box_settings_tab.pack_start(self.label_settings_tab, True, True, 0)
        self.box_settings_tab.pack_start(self.button_close_settings_tab, False, False, 0)

        self.box_settings_tab.show_all()

        self.scrolledwindow_settings.add(self.box_settings)

        if self.settings_tab_at_start == True:
            self.notebook.append_page(self.scrolledwindow_settings, self.box_settings_tab)
            self.notebook.set_tab_detachable(self.scrolledwindow_settings, True)
            self.notebook.set_tab_reorderable(self.scrolledwindow_settings, True)
            self.notebook.set_tab_detachable(self.scrolledwindow_settings, True)

    def setup_cookies(self):

        if not os.path.exists(os.getenv('HOME') + '/.config/lgogdownloader'):
            os.makedirs(os.getenv('HOME') + '/.config/lgogdownloader')

        cookiejar = os.getenv('HOME') + '/.config/lgogdownloader/cookies.txt'
        context = self.webkit.WebContext.get_default()
        cookie_manager = context.get_cookie_manager();
        cookie_manager.set_persistent_storage(cookiejar, self.webkit.CookiePersistentStorage.TEXT);

    def create_queue_tab(self):

        self.queue_tab_scrolled_window = Gtk.ScrolledWindow(
            name = 'queue_tab'
            )

        self.queue_tab_box = Gtk.Box(
            spacing = 20,
            margin_top = 20,
            margin_bottom = 20,
            margin_left = 20,
            margin_right = 20,
            orientation = Gtk.Orientation.VERTICAL
            )

        self.queue_tab = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            spacing = 10
            )

        self.queue_tab_label = Gtk.Label(
            label = _("QUEUE")
            )

        self.queue_tab_close_button = Gtk.Button(
            name = "Downloads",
            image = Gtk.Image(stock=Gtk.STOCK_CLOSE),
            relief = Gtk.ReliefStyle.NONE,
            focus_on_click = False,
            )

        self.queue_tab_close_button.connect('clicked', self.close_tab, self.queue_tab_scrolled_window)

        self.queue_tab.pack_start(self.queue_tab_label, True, True, 0)
        self.queue_tab.pack_start(self.queue_tab_close_button, False, False, 0)

        self.queue_tab.show_all()

        self.queue_tab_scrolled_window.add(self.queue_tab_box)

        if self.queue_tab_at_start:
            self.notebook.append_page(self.queue_tab_scrolled_window, self.queue_tab)
            self.notebook.set_tab_reorderable(self.queue_tab_scrolled_window, True)
            self.notebook.set_tab_detachable(self.queue_tab_scrolled_window, True)

    def mylib_create_queue_tab_content(self, game_name):

        queue_game_frame = Gtk.Frame(
            name = game_name,
            )
        queue_game_frame_list.append(queue_game_frame)

        queue_game_grid = Gtk.Grid(
            )

        queue_game_background = Gtk.Image()
        queue_game_background_ctx = queue_game_background.get_style_context()
        queue_game_background_ctx.add_class('lighter_background')

        queue_game_image = Gtk.Image(
            name = game_name,
            margin_top = 20,
            margin_bottom = 20,
            margin_left = 20,
            )

        pixbuf_width = (self.mylib_box_width -  60) / 5
        scale_level = float(pixbuf_width)/518
        pixbuf_height = 240 * scale_level

        for i in range(self.mylib_number_of_games_to_show):
            if self.mylib_shown_games_list[i] == game_name:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(data_dir + '/images/mylib_banners/' + game_name + '.jpg')
                pixbuf = pixbuf.scale_simple(pixbuf_width, pixbuf_height, InterpType.BILINEAR)
                queue_game_image.set_from_pixbuf(pixbuf)

        queue_game_image_list.append(queue_game_image)

        queue_game_label = Gtk.Label(
            vexpand = False,
            hexpand = True,
            wrap = True,
            margin_left = 20,
            label = self.mylib_dict_name_to_title[game_name],
            )

        queue_game_progress_bar = Gtk.ProgressBar(
            margin_left = 20,
            vexpand = False,
            show_text = True,
            text = ' ',
            hexpand = True,
            name = game_name,
            pulse_step = 0.05
            )
        queue_progress_bars_list.append(queue_game_progress_bar)

        queue_game_status = Gtk.Label(
            margin_left = 20,
            vexpand = False,
            name = game_name,
            hexpand = True,
            wrap = True,
            label = ' '
            )
        queue_game_status_list.append(queue_game_status)

        queue_game_remove = Gtk.Button(
            image = Gtk.Image(stock=Gtk.STOCK_CLOSE),
            relief = Gtk.ReliefStyle.NONE,
            focus_on_click = False,
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.CENTER,
            margin_right = 10,
            margin_left = 10,
            name = game_name,
            )
        queue_game_remove.connect('clicked', self.remove_from_installation_queue)

        queue_game_grid.attach(queue_game_image, 0, 0, 1, 3)
        queue_game_grid.attach(queue_game_label, 1, 0, 1, 1)
        queue_game_grid.attach(queue_game_progress_bar, 1, 1, 1, 1)
        queue_game_grid.attach(queue_game_status, 1, 2, 1, 1)
        queue_game_grid.attach(queue_game_remove, 2, 0, 1, 3)
        queue_game_grid.attach(queue_game_background, 0, 0, 3, 3)

        queue_game_frame.add(queue_game_grid)

        self.queue_tab_box.add(queue_game_frame)
        self.queue_tab_box.show_all()

    def create_queue_tab_content(self, game_name):

        queue_game_frame = Gtk.Frame(
            name = game_name,
            )
        queue_game_frame_list.append(queue_game_frame)

        queue_game_grid = Gtk.Grid()

        queue_game_background = Gtk.Image()
        queue_game_background_ctx = queue_game_background.get_style_context()
        queue_game_background_ctx.add_class('lighter_background')

        queue_game_image = Gtk.Image(
            name = game_name,
            margin_top = 20,
            margin_bottom = 20,
            margin_left = 20,
            )

        pixbuf_width = (self.goglib_box_width -  60) / 5
        scale_level = float(pixbuf_width)/518
        pixbuf_height = 240 * scale_level

        for i in range(self.goglib_number_of_games_to_show):
            if self.goglib_shown_games_list[i] == game_name:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(data_dir + '/images/goglib_banners/' + game_name + '.jpg')
                pixbuf = pixbuf.scale_simple(pixbuf_width, pixbuf_height, InterpType.BILINEAR)
                queue_game_image.set_from_pixbuf(pixbuf)

        queue_game_image_list.append(queue_game_image)

        queue_game_label = Gtk.Label(
            vexpand = False,
            hexpand = True,
            wrap = True,
            margin_left = 20,
            #wrap_mode = Pango.WrapMode.WORD,
            label = self.goglib_dict_name_to_title[game_name],
            )

        queue_game_progress_bar = Gtk.ProgressBar(
            margin_left = 20,
            vexpand = False,
            show_text = True,
            text = ' ',
            hexpand = True,
            name = game_name,
            pulse_step = 0.05
            )
        queue_progress_bars_list.append(queue_game_progress_bar)

        queue_game_status = Gtk.Label(
            margin_left = 20,
            vexpand = False,
            name = game_name,
            hexpand = True,
            wrap = True,
            #wrap_mode = Pango.WrapMode.WORD,
            label = ' '
            )
        queue_game_status_list.append(queue_game_status)

        queue_game_remove = Gtk.Button(
            image = Gtk.Image(stock=Gtk.STOCK_CLOSE),
            relief = Gtk.ReliefStyle.NONE,
            focus_on_click = False,
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.CENTER,
            margin_right = 10,
            margin_left = 10,
            name = game_name,
            )
        queue_game_remove.connect('clicked', self.remove_from_installation_queue)

        queue_game_grid.attach(queue_game_image, 0, 0, 1, 3)
        queue_game_grid.attach(queue_game_label, 1, 0, 1, 1)
        queue_game_grid.attach(queue_game_progress_bar, 1, 1, 1, 1)
        queue_game_grid.attach(queue_game_status, 1, 2, 1, 1)
        queue_game_grid.attach(queue_game_remove, 2, 0, 1, 3)
        queue_game_grid.attach(queue_game_background, 0, 0, 3, 3)

        queue_game_frame.add(queue_game_grid)

        self.queue_tab_box.add(queue_game_frame)
        self.queue_tab_box.show_all()

    def queue_tab_exists(self):

        for i in range (self.notebook.get_n_pages()):
            if self.notebook.get_nth_page(i) == self.queue_tab_scrolled_window:
                return True

        return False

    def append_queue_tab(self):
        self.notebook.append_page(self.queue_tab_scrolled_window, self.queue_tab)
        self.notebook.set_tab_reorderable(self.queue_tab_scrolled_window, True)
        self.notebook.set_tab_detachable(self.queue_tab_scrolled_window, True)
        self.notebook.show_all()
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)

    def goglib_page_exists(self):

        for i in range (self.notebook.get_n_pages()):
            if self.notebook.get_nth_page(i).get_name() == 'goglib_tab':
                return True

        return False

    def mylib_page_exists(self):

        for i in range (self.notebook.get_n_pages()):
            if self.notebook.get_nth_page(i).get_name() == 'mylib_tab':
                return True

        return False

    def close_tab(self, button, widget):

        if widget.get_name() not in self.detached_tabs_names:

            page_number = self.notebook.page_num(widget)
            self.notebook.remove_page(page_number)

        else:
            for notebook in self.additional_notebooks_list:
                for i in range(notebook.get_n_pages()):
                    if widget.get_name() == notebook.get_nth_page(i).get_name():
                        notebook.remove_page(i)

    def check_gogcom_tab(self):

        current_uri = self.webpage.get_uri()

        if (current_uri != None) and not (current_uri.startswith('https://www.gog.com')):
            self.webpage.go_back()
            self.webbrowser.open_new(current_uri)

        GObject.timeout_add(1000, self.check_gogcom_tab)

    def mylib_grid_autoresize(self, number_of_columns):

        self.mylib_grid_unattach()
        column_indexes = []

        for j in range(number_of_columns):

            for i in range(j, self.mylib_number_of_games_to_show, number_of_columns):
                column_indexes.append(i)

            for i in range(0, self.mylib_number_of_games_to_show):
                if i in column_indexes:
                    self.mylib_tab_grid.attach(mylib_game_grids_current_list[i], j, int(i / number_of_columns), 1, 1)

            column_indexes = []

    def mylib_grid_unattach(self):
        for mylib_game_grid in mylib_game_grids_current_list:
            self.mylib_tab_grid.remove(mylib_game_grid)

    def grid_autoresize(self, number_of_columns):

        self.grid_unattach()
        column_indexes = []

        for j in range(number_of_columns):

            for i in range(j, self.goglib_number_of_games_to_show, number_of_columns):
                column_indexes.append(i)

            for i in range(0, self.goglib_number_of_games_to_show):
                if i in column_indexes:
                    self.grid_goglib.attach(goglib_game_grids_current_list[i], j, int(i / number_of_columns), 1, 1)

            column_indexes = []

    def grid_unattach(self):
        for gtk_grid_game in goglib_game_grids_current_list:
            self.grid_goglib.remove(gtk_grid_game)

    def update_mylib_grid(self):

        max_pixbuf_width = self.mylib_scale_level * (518 + 90)

        number_of_columns = int(self.mylib_box_width / max_pixbuf_width)

        new_pixbuf_width = self.mylib_scale_level * 518
        new_pixbuf_height = self.mylib_scale_level * 240

        for i in range(0, self.mylib_number_of_games_to_show):

            if (os.path.exists(self.mylib_install_dir + '/' + self.mylib_shown_games_list[i] + '/start.sh')) and \
                    (mylib_setup_buttons_list[i].get_name() not in mylib_installation_queue):

                mylib_setup_buttons_list[i].set_label(_("Remove"))
                mylib_setup_buttons_list[i].set_sensitive(True)
                mylib_launch_buttons_list[i].set_sensitive(True)
            else:
                mylib_launch_buttons_list[i].set_sensitive(False)

                if mylib_setup_buttons_list[i].get_name() not in \
                                    mylib_name_to_pid_install_dict:
                    if mylib_setup_buttons_list[i].get_name() not in mylib_installation_queue:
                        mylib_setup_buttons_list[i].set_label(_("Install"))
                        mylib_setup_buttons_list[i].set_sensitive(True)
                    else:
                        mylib_setup_buttons_list[i].set_label(_("In queue"))
                        mylib_setup_buttons_list[i].set_sensitive(False)
                else:
                    mylib_setup_buttons_list[i].set_label(_("Installing"))
                    mylib_setup_buttons_list[i].set_sensitive(False)

            pixbuf= GdkPixbuf.Pixbuf.new_from_file(data_dir + '/images/mylib_banners/' + self.mylib_shown_games_list[i] + '.jpg')

            pixbuf = pixbuf.scale_simple(new_pixbuf_width, new_pixbuf_height, InterpType.BILINEAR)

            mylib_games_banners_list[i].set_from_pixbuf(pixbuf)
            mylib_games_banners_list[i].set_name(self.mylib_shown_games_list[i])
            mylib_setup_buttons_list[i].set_name(self.mylib_shown_games_list[i])
            mylib_launch_buttons_list[i].set_name(self.mylib_shown_games_list[i])

            mylib_games_banners_list[i].set_property('tooltip_text', \
                                    self.mylib_dict_name_to_title[self.mylib_shown_games_list[i]])

        if self.mylib_number_of_games_to_show < number_of_columns:
            self.mylib_tab_grid.set_property('halign', Gtk.Align.START)
            column_spacing = (self.mylib_box_width  - (new_pixbuf_width * number_of_columns)) / (number_of_columns)
            self.mylib_tab_grid.set_property('column_spacing', column_spacing + 1)
            self.mylib_tab_grid.set_property('margin_left', (column_spacing/2) + 1)
        else:
            self.mylib_tab_grid.set_property('halign', Gtk.Align.FILL)
            self.mylib_tab_grid.set_property('column_spacing', 0)
            self.mylib_tab_grid.set_property('margin_left', 0)

        self.mylib_grid_autoresize(number_of_columns)
        self.mylib_tab_grid.show_all()

    def update_goglib_grid(self):

        max_pixbuf_width = self.scale_level * (518 + 90)

        number_of_columns = int(self.goglib_box_width / max_pixbuf_width)

        new_pixbuf_width = self.scale_level * 518
        new_pixbuf_height = self.scale_level * 240

        for i in range(0, self.goglib_number_of_games_to_show):

            if self.goglib_shown_games_list[i] not in self.goglib_available_games:
                # TODO (?) Do not read images from file everytime, use pixbuf (create at start)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(data_dir + '/images/goglib_banners/unavailable/' + self.goglib_shown_games_list[i] + '.jpg')
                goglib_setup_buttons_list[i].set_sensitive(False)
                goglib_launch_buttons_list[i].set_sensitive(False)
            else:
                goglib_setup_buttons_list[i].set_sensitive(True)
                pixbuf= GdkPixbuf.Pixbuf.new_from_file(data_dir + '/images/goglib_banners/' + self.goglib_shown_games_list[i] + '.jpg')

            pixbuf = pixbuf.scale_simple(new_pixbuf_width, new_pixbuf_height, InterpType.BILINEAR)

            goglib_games_banners_list[i].set_from_pixbuf(pixbuf)
            goglib_games_banners_list[i].set_name(self.goglib_shown_games_list[i])
            goglib_setup_buttons_list[i].set_name(self.goglib_shown_games_list[i])
            goglib_launch_buttons_list[i].set_name(self.goglib_shown_games_list[i])

            if os.path.exists(self.goglib_install_dir + '/' + self.goglib_shown_games_list[i] + '/start.sh'):
                goglib_setup_buttons_list[i].set_label(_("Remove"))
                goglib_setup_buttons_list[i].set_sensitive(True)
                goglib_launch_buttons_list[i].set_sensitive(True)
            else:
                goglib_launch_buttons_list[i].set_sensitive(False)

                if goglib_setup_buttons_list[i].get_name() not in \
                        (goglib_name_to_pid_download_dict or goglib_name_to_pid_install_dict \
                        or goglib_name_to_pid_unpack_dict):

                    if goglib_setup_buttons_list[i].get_name() not in goglib_installation_queue:
                        goglib_setup_buttons_list[i].set_label(_("Install"))
                        if goglib_setup_buttons_list[i].get_name() in self.goglib_available_games:
                            goglib_setup_buttons_list[i].set_sensitive(True)
                        else:
                            goglib_setup_buttons_list[i].set_sensitive(False)
                    else:
                        goglib_setup_buttons_list[i].set_sensitive(False)
                        goglib_setup_buttons_list[i].set_label(_("In queue"))
                else:
                    goglib_setup_buttons_list[i].set_label(_("Installing"))
                    goglib_setup_buttons_list[i].set_sensitive(False)

            goglib_games_banners_list[i].set_property('tooltip_text', \
                                    self.goglib_dict_name_to_title[self.goglib_shown_games_list[i]])

        if self.goglib_number_of_games_to_show < number_of_columns:
            self.grid_goglib.set_property('halign', Gtk.Align.START)
            column_spacing = (self.goglib_box_width  - (new_pixbuf_width * number_of_columns)) / (number_of_columns)
            self.grid_goglib.set_property('column_spacing', column_spacing + 1)
            self.grid_goglib.set_property('margin_left', (column_spacing/2) + 1)
        else:
            self.grid_goglib.set_property('halign', Gtk.Align.FILL)
            self.grid_goglib.set_property('column_spacing', 0)
            self.grid_goglib.set_property('margin_left', 0)

        self.grid_autoresize(number_of_columns)
        self.grid_goglib.show_all()

    def update_goglib(self):

        self.window_update_message = Gtk.Window(
            title = _("Changes in library"),
            type = Gtk.WindowType.POPUP,
            window_position = Gtk.WindowPosition.CENTER_ALWAYS,
            resizable = False,
            icon = app_icon,
        )

        self.box_update_message = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL
        )

        self.label_update_message = Gtk.Label(
            label = _("Updating GOG library..."),
            margin_right = 10,
            margin_top = 20,
            margin_bottom = 20,
        )

        self.spinner_update_message = Gtk.Spinner(
            active = True,
            visible = True,
            margin_left = 10,
            width_request = 48,
            height_request = 48
        )

        self.box_update_message.pack_start(self.spinner_update_message, True, True, 0)
        self.box_update_message.pack_start(self.label_update_message, True, True, 0)

        self.window_update_message.add(self.box_update_message)

        self.main_window.hide()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        self.window_update_message.show_all()

        command = ['lgogdownloader', '--exclude', '1,2,4,8,16,32','--list-details']

        pid, stdin, stdout, stderr = GLib.spawn_async(command,
                flags=GLib.SpawnFlags.SEARCH_PATH|GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                standard_output=True,
                standard_error=True)

        io = GLib.IOChannel(stdout)

        self.source_id_out = io.add_watch(GLib.IO_IN|GLib.IO_HUP,
                                 self.watch_process,
                                 'update_goglib',
                                 priority=GLib.PRIORITY_HIGH)

    def update_mylib_interface(self):

        if (len(mylib_installation_queue) > 0) and (mylib_installation_queue[0] != self.mylib_now_installing):
            self.mylib_now_installing  = mylib_installation_queue[0]
            self.mylib_install_game(mylib_installation_queue[0])

            for button in mylib_setup_buttons_list:
                if button.get_name() == self.mylib_now_installing:
                    button.set_label(_("Installing"))

        if self.mylib_filters_box.get_allocation().height != 1:
            self.scrolledwindow_mylib_filters.set_property('height_request', \
            self.mylib_filters_box.get_allocation().height + 20)


        if (self.box_mylib_page.get_allocation().width != self.mylib_box_width):

            self.mylib_box_width = self.box_mylib_page.get_allocation().width

            self.update_mylib_grid()

            self.update_queue_banners()

        if (len(mylib_installation_queue) == 0):
            self.mylib_installation_status_box.set_visible(False)
        else:
            self.mylib_installation_status_box.set_visible(True)

        GObject.timeout_add(1000, self.update_mylib_interface)

    def update_goglib_interface(self):

        if (len(self.goglib_new_games_list) != 0) and self.main_window.get_visible():
            self.update_goglib()

        if (len(goglib_installation_queue) > 0) and (goglib_installation_queue[0] != self.goglib_now_installing):
            self.goglib_now_installing = goglib_installation_queue[0]
            self.goglib_download_game(goglib_installation_queue[0])

            for button in goglib_setup_buttons_list:
                if button.get_name() == self.goglib_now_installing:
                    button.set_label(_("Installing"))

        if self.box_goglib_filters.get_allocation().height != 1:
            self.scrolledwindow_filters.set_property('height_request', \
            self.box_goglib_filters.get_allocation().height + 20)

        if (self.box_goglib_page.get_allocation().width != self.goglib_box_width):

            self.goglib_box_width = self.box_goglib_page.get_allocation().width

            self.update_goglib_grid()

            self.update_queue_banners()

        if (len(goglib_installation_queue) == 0):
            self.box_goglib_installation_status.set_visible(False)
        else:
            self.box_goglib_installation_status.set_visible(True)

        GObject.timeout_add(1000, self.update_goglib_interface)

    def update_queue_banners(self):

        if self.goglib_box_width != 1:
            new_downloads_pixbuf_width = (self.goglib_box_width -  60) / 5
        else:
            new_downloads_pixbuf_width = (self.mylib_box_width -  60) / 5

        downloads_pixbuf_scale_level = float(new_downloads_pixbuf_width)/518
        new_downloads_pixbuf_height = 240 * downloads_pixbuf_scale_level

        if queue_game_image_list:
            for i in range(0, len(queue_game_image_list)):

                if os.path.exists(data_dir + '/images/goglib_banners/' + queue_game_image_list[i].get_name() + '.jpg'):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(data_dir + '/images/goglib_banners/' + queue_game_image_list[i].get_name() + '.jpg')
                else:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(data_dir + '/images/mylib_banners/' + queue_game_image_list[i].get_name() + '.jpg')

                pixbuf = pixbuf.scale_simple(new_downloads_pixbuf_width, new_downloads_pixbuf_height, InterpType.BILINEAR)
                queue_game_image_list[i].set_from_pixbuf(pixbuf)

    #~ def timer_check_for_new_games(self):
        #~ self.check_for_new_games()
        #~ GObject.timeout_add(30000, self.timer_check_for_new_games)

    def timer(self):

        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window_notebook = window.get_child()
                if window_notebook != None:
                    window_notebook_n_pages = window_notebook.get_n_pages()
                    for i in range(window_notebook_n_pages):
                        page_name = window_notebook.get_nth_page(i).get_name()
                        if page_name not in self.detached_tabs_names:
                            self.detached_tabs_names.append(page_name)

        if (len(self.detached_tabs_names) + self.notebook.get_n_pages()) == 5:
            self.button_add_tab.set_visible(False)
        else:
            self.button_add_tab.set_visible(True)

        GObject.timeout_add(1000, self.timer)

    def config_load(self):

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(data_dir + '/games'):
            os.makedirs(data_dir + '/games')
        if not os.path.exists(data_dir + '/games/mylib'):
            os.makedirs(data_dir + '/games/mylib')
        if not os.path.exists(data_dir + '/games/mylib/downloads'):
            os.makedirs(data_dir + '/games/mylib/downloads')
        if not os.path.exists(data_dir + '/games/mylib/installed'):
            os.makedirs(data_dir + '/games/mylib/installed')
        if not os.path.exists(data_dir + '/games/goglib'):
            os.makedirs(data_dir + '/games/goglib')
        if not os.path.exists(data_dir + '/games/goglib/downloads'):
            os.makedirs(data_dir + '/games/goglib/downloads')
        if not os.path.exists(data_dir + '/games/goglib/installed'):
            os.makedirs(data_dir + '/games/goglib/installed')
        if not os.path.exists(data_dir + '/config'):
            os.makedirs(data_dir + '/config')
        if not os.path.exists(data_dir + '/scripts'):
            os.makedirs(data_dir + '/scripts')
            os.system('cp -R ' + nebula_dir + '/scripts/* ' + data_dir + '/scripts/')
        if not os.path.exists(data_dir + '/images'):
            os.makedirs(data_dir + '/images')
            os.system('cp -R ' + nebula_dir + '/images/goglib_banners ' + data_dir + '/images/')
            os.system('cp -R ' + nebula_dir + '/images/mylib_banners ' + data_dir + '/images/')

        if not os.path.exists(data_dir + '/scripts/goglib'):
            os.makedirs(data_dir + '/scripts/goglib')
        if not os.path.exists(data_dir + '/scripts/mylib'):
            os.makedirs(data_dir + '/scripts/mylib')

        self.config_parser = ConfigParser()
        self.config_parser.read(config_dir + '/config.ini')

        # tabs at startup
        if not self.config_parser.has_section('tabs at startup'):
            self.config_parser.add_section('tabs at startup')

        if not self.config_parser.has_option('tabs at startup', 'goglib'):
            self.goglib_tab_at_start = True
            self.config_parser.set('tabs at startup', 'goglib', str(self.goglib_tab_at_start))
        else:
            self.goglib_tab_at_start = self.config_parser.getboolean('tabs at startup', 'goglib')

        if not self.config_parser.has_option('tabs at startup', 'mylib'):
            self.mylib_tab_at_start = False
            self.config_parser.set('tabs at startup', 'mylib', str(self.mylib_tab_at_start))
        else:
            self.mylib_tab_at_start = self.config_parser.getboolean('tabs at startup', 'mylib')

        if not self.config_parser.has_option('tabs at startup', 'gogcom'):
            self.gogcom_tab_at_start = False
            self.config_parser.set('tabs at startup', 'gogcom', str(self.gogcom_tab_at_start))
        else:
            self.gogcom_tab_at_start = self.config_parser.getboolean('tabs at startup', 'gogcom')

        if not self.config_parser.has_option('tabs at startup', 'queue'):
            self.queue_tab_at_start = False
            self.config_parser.set('tabs at startup', 'queue', str(self.queue_tab_at_start))
        else:
            self.queue_tab_at_start = self.config_parser.getboolean('tabs at startup', 'queue')

        if not self.config_parser.has_option('tabs at startup', 'settings'):
            self.settings_tab_at_start = True
            self.config_parser.set('tabs at startup', 'settings', str(self.settings_tab_at_start))
        else:
            self.settings_tab_at_start = self.config_parser.getboolean('tabs at startup', 'settings')

        if not self.config_parser.has_option('tabs at startup', 'show_tabs'):
            self.show_tabs = True
            self.config_parser.set('tabs at startup', 'show_tabs', str(self.show_tabs))
        else:
            self.show_tabs = self.config_parser.getboolean('tabs at startup', 'show_tabs')


        # goglib gui preferences
        if not self.config_parser.has_section('goglib gui preferences'):
            self.config_parser.add_section('goglib gui preferences')

        if not self.config_parser.has_option('goglib gui preferences', 'scale_level'):
            self.scale_level = 0.5
            self.config_parser.set('goglib gui preferences', 'scale_level', str(self.scale_level))
        else:
            self.scale_level = self.config_parser.getfloat('goglib gui preferences', 'scale_level')

        if not self.config_parser.has_option('goglib gui preferences', 'status_filter'):
            self.status_filter = _("No filter")
            self.config_parser.set('goglib gui preferences', 'status_filter', str(self.status_filter))
        else:
            self.status_filter = self.config_parser.get('goglib gui preferences', 'status_filter')

        if not self.config_parser.has_option('goglib gui preferences', 'tag_filters'):
            self.goglib_tf_number = 1
            self.config_parser.set('goglib gui preferences', 'tag_filters', str(self.goglib_tf_number))
        else:
            self.goglib_tf_number = self.config_parser.getint('goglib gui preferences', 'tag_filters')

        if not self.config_parser.has_option('goglib gui preferences', 'tags_filter1'):
            self.goglib_tags_filter1 = _("No filter")
            self.config_parser.set('goglib gui preferences', 'tags_filter1', str(self.goglib_tags_filter1))
        else:
            self.goglib_tags_filter1 = self.config_parser.get('goglib gui preferences', 'tags_filter1')

        if not self.config_parser.has_option('goglib gui preferences', 'tags_filter2'):
            self.goglib_tags_filter2 = _("No filter")
            self.config_parser.set('goglib gui preferences', 'tags_filter2', str(self.goglib_tags_filter2))
        else:
            self.goglib_tags_filter2 = self.config_parser.get('goglib gui preferences', 'tags_filter2')

        if not self.config_parser.has_option('goglib gui preferences', 'tags_filter3'):
            self.goglib_tags_filter3 = _("No filter")
            self.config_parser.set('goglib gui preferences', 'tags_filter3', str(self.goglib_tags_filter3))
        else:
            self.goglib_tags_filter3 = self.config_parser.get('goglib gui preferences', 'tags_filter3')

        if not self.config_parser.has_option('goglib gui preferences', 'tags_filter4'):
            self.goglib_tags_filter4 = _("No filter")
            self.config_parser.set('goglib gui preferences', 'tags_filter4', str(self.goglib_tags_filter4))
        else:
            self.goglib_tags_filter4 = self.config_parser.get('goglib gui preferences', 'tags_filter4')

        if not self.config_parser.has_option('goglib gui preferences', 'filter_color_indication'):
            self.goglib_filter_color_indication = True
            self.config_parser.set('goglib gui preferences', 'filter_color_indication', str(self.goglib_filter_color_indication))
        else:
            self.goglib_filter_color_indication = self.config_parser.getboolean('goglib gui preferences', 'filter_color_indication')

        if not self.config_parser.has_option('goglib gui preferences', 'status_filter_type'):
            self.goglib_status_filter_type = 'include'
            self.config_parser.set('goglib gui preferences', 'status_filter_type', str(self.goglib_status_filter_type))
        else:
            self.goglib_status_filter_type = self.config_parser.get('goglib gui preferences', 'status_filter_type')

        if not self.config_parser.has_option('goglib gui preferences', 'tags_filter1_type'):
            self.goglib_tags_filter1_type = 'include'
            self.config_parser.set('goglib gui preferences', 'tags_filter1_type', str(self.goglib_tags_filter1_type))
        else:
            self.goglib_tags_filter1_type = self.config_parser.get('goglib gui preferences', 'tags_filter1_type')

        if not self.config_parser.has_option('goglib gui preferences', 'tags_filter2_type'):
            self.goglib_tags_filter2_type = 'include'
            self.config_parser.set('goglib gui preferences', 'tags_filter2_type', str(self.goglib_tags_filter2_type))
        else:
            self.goglib_tags_filter2_type = self.config_parser.get('goglib gui preferences', 'tags_filter2_type')

        if not self.config_parser.has_option('goglib gui preferences', 'tags_filter3_type'):
            self.goglib_tags_filter3_type = 'exclude'
            self.config_parser.set('goglib gui preferences', 'tags_filter3_type', str(self.goglib_tags_filter3_type))
        else:
            self.goglib_tags_filter3_type = self.config_parser.get('goglib gui preferences', 'tags_filter3_type')

        if not self.config_parser.has_option('goglib gui preferences', 'tags_filter4_type'):
            self.goglib_tags_filter4_type = 'exclude'
            self.config_parser.set('goglib gui preferences', 'tags_filter4_type', str(self.goglib_tags_filter4_type))
        else:
            self.goglib_tags_filter4_type = self.config_parser.get('goglib gui preferences', 'tags_filter4_type')

        if not self.config_parser.has_option('goglib gui preferences', 'goglib_include_color'):
            self.goglib_include_color = 'rgba(128,255,128,0.2)'
            self.config_parser.set('goglib gui preferences', 'goglib_include_color', str(self.goglib_include_color))
        else:
            self.goglib_include_color = self.config_parser.get('goglib gui preferences', 'goglib_include_color')

        if not self.config_parser.has_option('goglib gui preferences', 'goglib_exclude_color'):
            self.goglib_exclude_color = 'rgba(255,128,128,0.2)'
            self.config_parser.set('goglib gui preferences', 'goglib_exclude_color', str(self.goglib_exclude_color))
        else:
            self.goglib_exclude_color = self.config_parser.get('goglib gui preferences', 'goglib_exclude_color')

        # mylib gui preferences
        if not self.config_parser.has_section('mylib gui preferences'):
            self.config_parser.add_section('mylib gui preferences')

        if not self.config_parser.has_option('mylib gui preferences', 'scale_level'):
            self.mylib_scale_level = 0.5
            self.config_parser.set('mylib gui preferences', 'scale_level', str(self.mylib_scale_level))
        else:
            self.mylib_scale_level = self.config_parser.getfloat('mylib gui preferences', 'scale_level')

        if not self.config_parser.has_option('mylib gui preferences', 'status_filter'):
            self.mylib_status_filter = _("No filter")
            self.config_parser.set('mylib gui preferences', 'status_filter', str(self.mylib_status_filter))
        else:
            self.mylib_status_filter = self.config_parser.get('mylib gui preferences', 'status_filter')

        if not self.config_parser.has_option('mylib gui preferences', 'tag_filters'):
            self.mylib_tf_number = 1
            self.config_parser.set('mylib gui preferences', 'tag_filters', str(self.mylib_tf_number))
        else:
            self.mylib_tf_number = self.config_parser.getint('mylib gui preferences', 'tag_filters')

        if not self.config_parser.has_option('mylib gui preferences', 'tags_filter1'):
            self.mylib_tags_filter1 = _("No filter")
            self.config_parser.set('mylib gui preferences', 'tags_filter1', str(self.mylib_tags_filter1))
        else:
            self.mylib_tags_filter1 = self.config_parser.get('mylib gui preferences', 'tags_filter1')

        if not self.config_parser.has_option('mylib gui preferences', 'tags_filter2'):
            self.mylib_tags_filter2 = _("No filter")
            self.config_parser.set('mylib gui preferences', 'tags_filter2', str(self.mylib_tags_filter2))
        else:
            self.mylib_tags_filter2 = self.config_parser.get('mylib gui preferences', 'tags_filter2')

        if not self.config_parser.has_option('mylib gui preferences', 'tags_filter3'):
            self.mylib_tags_filter3 = _("No filter")
            self.config_parser.set('mylib gui preferences', 'tags_filter3', str(self.mylib_tags_filter3))
        else:
            self.mylib_tags_filter3 = self.config_parser.get('mylib gui preferences', 'tags_filter3')

        if not self.config_parser.has_option('mylib gui preferences', 'tags_filter4'):
            self.mylib_tags_filter4 = _("No filter")
            self.config_parser.set('mylib gui preferences', 'tags_filter4', str(self.mylib_tags_filter4))
        else:
            self.mylib_tags_filter4 = self.config_parser.get('mylib gui preferences', 'tags_filter4')

        if not self.config_parser.has_option('mylib gui preferences', 'filter_color_indication'):
            self.mylib_filter_color_indication = True
            self.config_parser.set('mylib gui preferences', 'filter_color_indication', str(self.mylib_filter_color_indication))
        else:
            self.mylib_filter_color_indication = self.config_parser.getboolean('mylib gui preferences', 'filter_color_indication')

        if not self.config_parser.has_option('mylib gui preferences', 'status_filter_type'):
            self.mylib_status_filter_type = 'include'
            self.config_parser.set('mylib gui preferences', 'status_filter_type', str(self.mylib_status_filter_type))
        else:
            self.mylib_status_filter_type = self.config_parser.get('mylib gui preferences', 'status_filter_type')

        if not self.config_parser.has_option('mylib gui preferences', 'tags_filter1_type'):
            self.mylib_tags_filter1_type = 'include'
            self.config_parser.set('mylib gui preferences', 'tags_filter1_type', str(self.mylib_tags_filter1_type))
        else:
            self.mylib_tags_filter1_type = self.config_parser.get('mylib gui preferences', 'tags_filter1_type')

        if not self.config_parser.has_option('mylib gui preferences', 'tags_filter2_type'):
            self.mylib_tags_filter2_type = 'include'
            self.config_parser.set('mylib gui preferences', 'tags_filter2_type', str(self.mylib_tags_filter2_type))
        else:
            self.mylib_tags_filter2_type = self.config_parser.get('mylib gui preferences', 'tags_filter2_type')

        if not self.config_parser.has_option('mylib gui preferences', 'tags_filter3_type'):
            self.mylib_tags_filter3_type = 'exclude'
            self.config_parser.set('mylib gui preferences', 'tags_filter3_type', str(self.mylib_tags_filter3_type))
        else:
            self.mylib_tags_filter3_type = self.config_parser.get('mylib gui preferences', 'tags_filter3_type')

        if not self.config_parser.has_option('mylib gui preferences', 'tags_filter4_type'):
            self.mylib_tags_filter4_type = 'exclude'
            self.config_parser.set('mylib gui preferences', 'tags_filter4_type', str(self.mylib_tags_filter4_type))
        else:
            self.mylib_tags_filter4_type = self.config_parser.get('mylib gui preferences', 'tags_filter4_type')

        if not self.config_parser.has_option('mylib gui preferences', 'mylib_include_color'):
            self.mylib_include_color = 'rgba(128,255,128,0.2)'
            self.config_parser.set('mylib gui preferences', 'mylib_include_color', str(self.mylib_include_color))
        else:
            self.mylib_include_color = self.config_parser.get('mylib gui preferences', 'mylib_include_color')

        if not self.config_parser.has_option('mylib gui preferences', 'mylib_exclude_color'):
            self.mylib_exclude_color = 'rgba(255,128,128,0.2)'
            self.config_parser.set('mylib gui preferences', 'mylib_exclude_color', str(self.mylib_exclude_color))
        else:
            self.mylib_exclude_color = self.config_parser.get('mylib gui preferences', 'mylib_exclude_color')

        # gog languages
        if not self.config_parser.has_section('gog languages'):
            self.config_parser.add_section('gog languages')
            self.config_parser.set('gog languages', 'english', '1')
            self.config_parser.set('gog languages', 'deutsch', '2')
            self.config_parser.set('gog languages', 'français', '4')
            self.config_parser.set('gog languages', 'polski', '8')
            self.config_parser.set('gog languages', 'русский', '16')
            self.config_parser.set('gog languages', '中文', '32')
            self.config_parser.set('gog languages', 'čeština', '64')
            self.config_parser.set('gog languages', 'español', '128')
            self.config_parser.set('gog languages', 'magyar', '256')
            self.config_parser.set('gog languages', 'italiano', '512')
            self.config_parser.set('gog languages', '日本語', '1024')
            self.config_parser.set('gog languages', 'türkçe', '2048')
            self.config_parser.set('gog languages', 'português', '4096')
            self.config_parser.set('gog languages', '한국어', '8192')
            self.config_parser.set('gog languages', 'nederlands', '16384')
            self.config_parser.set('gog languages', 'svenska', '32768')
            self.config_parser.set('gog languages', 'norsk', '65536')
            self.config_parser.set('gog languages', 'dansk', '131072')
            self.config_parser.set('gog languages', 'suomi', '262144')
            self.config_parser.set('gog languages', 'slovenčina', '1048576')

            self.lang_index = {
                'english' : '1',
                'deutsch' : '2',
                'français' : '4',
                'polski' : '8',
                'русский' : '16',
                '中文' : '32',
                'čeština' : '64',
                'español' : '128',
                'magyar' : '256',
                'italiano' : '512',
                '日本語' : '1024',
                'türkçe' : '2048',
                'português' : '4096',
                '한국어' : '8192',
                'nederlands' : '16384',
                'svenska' : '32768',
                'norsk' : '65536',
                'dansk' : '131072',
                'suomi' : '262144',
                'slovenčina' : '1048576',
                }

            self.lang_list = []
            for lang in self.lang_index:
                self.lang_list.append(lang)
            self.lang_list = sorted(self.lang_list)

        else:

            self.lang_list = []
            self.lang_index = {}

            for lang in self.config_parser.options('gog languages'):
                self.lang_list.append(lang)
                self.lang_list = sorted(self.lang_list)
                self.lang_index[lang] = self.config_parser.get('gog languages', lang)

        # gog library preferences
        if not self.config_parser.has_section('goglib preferences'):
            self.config_parser.add_section('goglib preferences')

        if not self.config_parser.has_option('goglib preferences', 'goglib_lang'):
            self.goglib_lang = 'english'
            self.config_parser.set('goglib preferences', 'goglib_lang', str(self.goglib_lang))
        else:
            self.goglib_lang =  self.config_parser.get('goglib preferences', 'goglib_lang')

        if not self.config_parser.has_option('goglib preferences', 'goglib_keep_installers'):
            self.goglib_keep_installers = True
            self.config_parser.set('goglib preferences', 'goglib_keep_installers', str(self.goglib_keep_installers))
        else:
            self.goglib_keep_installers = self.config_parser.getboolean('goglib preferences', 'goglib_keep_installers')

        if not self.config_parser.has_option('goglib preferences', 'goglib_download_extras'):
            self.goglib_download_extras = False
            self.config_parser.set('goglib preferences', 'goglib_download_extras', str(self.goglib_download_extras))
        else:
            self.goglib_download_extras = self.config_parser.getboolean('goglib preferences', 'goglib_download_extras')

        if not self.config_parser.has_option('goglib preferences', 'goglib_offline_mode_at_start'):
            self.goglib_offline_mode_at_start = False
            self.config_parser.set('goglib preferences', 'goglib_offline_mode_at_start', str(self.goglib_offline_mode_at_start))
        else:
            self.goglib_offline_mode_at_start = self.config_parser.getboolean('goglib preferences', 'goglib_offline_mode_at_start')

        if not self.config_parser.has_option('goglib preferences', 'goglib_download_dir'):
            self.goglib_download_dir = data_dir + '/games/goglib/downloads'
            self.config_parser.set('goglib preferences', 'goglib_download_dir', str(self.goglib_download_dir))
        else:
            self.goglib_download_dir = self.config_parser.get('goglib preferences', 'goglib_download_dir')

        if not self.config_parser.has_option('goglib preferences', 'goglib_install_dir'):
            self.goglib_install_dir = data_dir + '/games/goglib/installed'
            self.config_parser.set('goglib preferences', 'goglib_install_dir', str(self.goglib_install_dir))
        else:
            self.goglib_install_dir = self.config_parser.get('goglib preferences', 'goglib_install_dir')

        if not self.config_parser.has_option('goglib preferences', 'goglib_scripts_overwrite'):
            self.goglib_scripts_overwrite = False
            self.config_parser.set('goglib preferences', 'goglib_scripts_overwrite', str(self.goglib_scripts_overwrite))
        else:
            self.goglib_scripts_overwrite = self.config_parser.getboolean('goglib preferences', 'goglib_scripts_overwrite')

        # mylib library preferences
        if not self.config_parser.has_section('mylib preferences'):
            self.config_parser.add_section('mylib preferences')

        if not self.config_parser.has_option('mylib preferences', 'mylib_keep_installers'):
            self.mylib_keep_installers = True
            self.config_parser.set('mylib preferences', 'mylib_keep_installers', str(self.mylib_keep_installers))
        else:
            self.mylib_keep_installers = self.config_parser.getboolean('mylib preferences', 'mylib_keep_installers')

        if not self.config_parser.has_option('mylib preferences', 'mylib_download_dir'):
            self.mylib_download_dir = data_dir + '/games/mylib/downloads'
            self.config_parser.set('mylib preferences', 'mylib_download_dir', str(self.mylib_download_dir))
        else:
            self.mylib_download_dir = self.config_parser.get('mylib preferences', 'mylib_download_dir')

        if not self.config_parser.has_option('mylib preferences', 'mylib_install_dir'):
            self.mylib_install_dir = data_dir + '/games/mylib/installed'
            self.config_parser.set('mylib preferences', 'mylib_install_dir', str(self.mylib_install_dir))
        else:
            self.mylib_install_dir = self.config_parser.get('mylib preferences', 'mylib_install_dir')

        if not self.config_parser.has_option('mylib preferences', 'mylib_scripts_overwrite'):
            self.mylib_scripts_overwrite = False
            self.config_parser.set('mylib preferences', 'mylib_scripts_overwrite', str(self.mylib_scripts_overwrite))
        else:
            self.mylib_scripts_overwrite = self.config_parser.getboolean('mylib preferences', 'mylib_scripts_overwrite')

        # visuals
        if not self.config_parser.has_section('visuals'):
            self.get_system_visuals()
            self.config_parser.add_section('visuals')
            self.config_parser.set('visuals', 'gtk_theme', str(self.gtk_theme))
            self.config_parser.set('visuals', 'gtk_dark', str(self.gtk_dark))
            self.config_parser.set('visuals', 'icon_theme', str(self.icon_theme))
            self.config_parser.set('visuals', 'font', str(self.font))
        else:
            self.gtk_theme = self.config_parser.get('visuals', 'gtk_theme')
            self.gtk_dark = self.config_parser.getboolean('visuals', 'gtk_dark')
            self.icon_theme = self.config_parser.get('visuals', 'icon_theme')
            self.font = self.config_parser.get('visuals','font')

        # emulation settings
        if not self.config_parser.has_section('emulation settings'):
            self.config_parser.add_section('emulation settings')

        if not self.config_parser.has_option('emulation settings', 'monitor'):
            self.monitor = 0
            self.config_parser.set('emulation settings', 'monitor', str(self.monitor))
        else:
            self.monitor = self.config_parser.getint('emulation settings', 'monitor')

        if not self.config_parser.has_option('emulation settings', 'wine'):
            self.wine = 'system'
            self.config_parser.set('emulation settings', 'wine', str(self.wine))
        else:
            self.wine =  self.config_parser.get('emulation settings', 'wine')

        if not self.config_parser.has_option('emulation settings', 'wine_path'):
            self.wine_path = ''
            self.config_parser.set('emulation settings', 'wine_path', str(self.wine_path))
        else:
            self.wine_path = self.config_parser.get('emulation settings', 'wine_path')

        if not self.config_parser.has_option('emulation settings', 'wine_version'):
            self.wine_version = ''
            self.config_parser.set('emulation settings', 'wine_version', str(self.wine_version))
        else:
            self.wine_version = self.config_parser.get('emulation settings', 'wine_version')

        if not self.config_parser.has_option('emulation settings', 'own_prefix'):
            self.own_prefix = False
            self.config_parser.set('emulation settings', 'own_prefix', str(self.own_prefix))
        else:
            self.own_prefix = self.config_parser.getboolean('emulation settings', 'own_prefix')

        if not self.config_parser.has_option('emulation settings', 'winearch'):
            self.winearch = 'win32'
            self.config_parser.set('emulation settings', 'winearch', str(self.winearch))
        else:
            self.winearch = self.config_parser.get('emulation settings', 'winearch')

        if not self.config_parser.has_option('emulation settings', 'dosbox'):
            self.dosbox = 'system'
            self.config_parser.set('emulation settings', 'dosbox', str(self.dosbox))
        else:
            self.dosbox =  self.config_parser.get('emulation settings', 'dosbox')

        if not self.config_parser.has_option('emulation settings', 'dosbox_path'):
            self.dosbox_path = ''
            self.config_parser.set('emulation settings', 'dosbox_path', str(self.dosbox_path))
        else:
            self.dosbox_path = self.config_parser.get('emulation settings', 'dosbox_path')

        if not self.config_parser.has_option('emulation settings', 'dosbox_version'):
            self.dosbox_version = ''
            self.config_parser.set('emulation settings', 'dosbox_version', str(self.dosbox_version))
        else:
            self.dosbox_version = self.config_parser.get('emulation settings', 'dosbox_version')

        if not self.config_parser.has_option('emulation settings', 'scummvm'):
            self.scummvm = 'system'
            self.config_parser.set('emulation settings', 'scummvm', str(self.scummvm))
        else:
            self.scummvm =  self.config_parser.get('emulation settings', 'scummvm')

        if not self.config_parser.has_option('emulation settings', 'scummvm_path'):
            self.scummvm_path = ''
            self.config_parser.set('emulation settings', 'scummvm_path', str(self.scummvm_path))
        else:
            self.scummvm_path = self.config_parser.get('emulation settings', 'scummvm_path')

        if not self.config_parser.has_option('emulation settings', 'scummvm_version'):
            self.scummvm_version = ''
            self.config_parser.set('emulation settings', 'scummvm_version', str(self.scummvm_version))
        else:
            self.scummvm_version = self.config_parser.get('emulation settings', 'scummvm_version')

        config_file = open(config_dir + '/config.ini', 'w')
        self.config_parser.write(config_file)
        config_file.close()

        if self.wine == 'path':
            self.wine_dir = self.wine_path + '/' + self.wine_version
        if self.wine == 'system':
            self.wine_dir = '/usr'
        if self.dosbox == 'path':
            self.dosbox_dir = self.dosbox_path + '/' + self.dosbox_version
        if self.dosbox == 'system':
            self.dosbox_dir = '/usr/bin'
        if self.scummvm == 'path':
            self.scummvm_dir = self.scummvm_path + '/' + self.scummvm_version + '/bin'
        if self.scummvm == 'system':
            self.scummvm_dir = '/usr/games'

        self.set_visuals()

    def config_save(self):

        # tabs at startup
        self.config_parser.set('tabs at startup', 'goglib', str(self.goglib_tab_at_start))
        self.config_parser.set('tabs at startup', 'mylib', str(self.mylib_tab_at_start))
        self.config_parser.set('tabs at startup', 'gogcom', str(self.gogcom_tab_at_start))
        self.config_parser.set('tabs at startup', 'queue', str(self.queue_tab_at_start))
        self.config_parser.set('tabs at startup', 'settings', str(self.settings_tab_at_start))
        self.config_parser.set('tabs at startup', 'show_tabs', str(self.show_tabs))

        # goglib gui preferences

        self.config_parser.set('goglib gui preferences', 'scale_level', str(self.scale_level))
        self.config_parser.set('goglib gui preferences', 'status_filter', str(self.status_filter))
        self.config_parser.set('goglib gui preferences', 'tag_filters', str(self.goglib_tf_number))
        self.config_parser.set('goglib gui preferences', 'tags_filter1', str(self.goglib_tags_filter1))
        self.config_parser.set('goglib gui preferences', 'tags_filter2', str(self.goglib_tags_filter2))
        self.config_parser.set('goglib gui preferences', 'tags_filter3', str(self.goglib_tags_filter3))
        self.config_parser.set('goglib gui preferences', 'tags_filter4', str(self.goglib_tags_filter4))

        self.config_parser.set('goglib gui preferences', 'filter_color_indication', str(self.goglib_filter_color_indication))
        self.config_parser.set('goglib gui preferences', 'status_filter_type', str(self.goglib_status_filter_type))
        self.config_parser.set('goglib gui preferences', 'tags_filter1_type', str(self.goglib_tags_filter1_type))
        self.config_parser.set('goglib gui preferences', 'tags_filter2_type', str(self.goglib_tags_filter2_type))
        self.config_parser.set('goglib gui preferences', 'tags_filter3_type', str(self.goglib_tags_filter3_type))
        self.config_parser.set('goglib gui preferences', 'tags_filter4_type', str(self.goglib_tags_filter4_type))
        self.config_parser.set('goglib gui preferences', 'goglib_include_color', str(self.goglib_include_color))
        self.config_parser.set('goglib gui preferences', 'goglib_exclude_color', str(self.goglib_exclude_color))

        # mylib gui preferences

        self.config_parser.set('mylib gui preferences', 'scale_level', str(self.mylib_scale_level))
        self.config_parser.set('mylib gui preferences', 'status_filter', str(self.mylib_status_filter))
        self.config_parser.set('mylib gui preferences', 'tag_filters', str(self.mylib_tf_number))
        self.config_parser.set('mylib gui preferences', 'tags_filter1', str(self.mylib_tags_filter1))
        self.config_parser.set('mylib gui preferences', 'tags_filter2', str(self.mylib_tags_filter2))
        self.config_parser.set('mylib gui preferences', 'tags_filter3', str(self.mylib_tags_filter3))
        self.config_parser.set('mylib gui preferences', 'tags_filter4', str(self.mylib_tags_filter4))

        self.config_parser.set('mylib gui preferences', 'filter_color_indication', str(self.mylib_filter_color_indication))
        self.config_parser.set('mylib gui preferences', 'status_filter_type', str(self.mylib_status_filter_type))
        self.config_parser.set('mylib gui preferences', 'tags_filter1_type', str(self.mylib_tags_filter1_type))
        self.config_parser.set('mylib gui preferences', 'tags_filter2_type', str(self.mylib_tags_filter2_type))
        self.config_parser.set('mylib gui preferences', 'tags_filter3_type', str(self.mylib_tags_filter3_type))
        self.config_parser.set('mylib gui preferences', 'tags_filter4_type', str(self.mylib_tags_filter4_type))
        self.config_parser.set('mylib gui preferences', 'mylib_include_color', str(self.mylib_include_color))
        self.config_parser.set('mylib gui preferences', 'mylib_exclude_color', str(self.mylib_exclude_color))

        # goglib preferences

        self.config_parser.set('goglib preferences', 'goglib_lang', str(self.goglib_lang))
        self.config_parser.set('goglib preferences', 'goglib_keep_installers', str(self.goglib_keep_installers))
        self.config_parser.set('goglib preferences', 'goglib_download_extras', str(self.goglib_download_extras))
        self.config_parser.set('goglib preferences', 'goglib_offline_mode_at_start', str(self.goglib_offline_mode_at_start))
        self.config_parser.set('goglib preferences', 'goglib_download_dir', str(self.goglib_download_dir))
        self.config_parser.set('goglib preferences', 'goglib_install_dir', str(self.goglib_install_dir))
        self.config_parser.set('goglib preferences', 'goglib_scripts_overwrite', str(self.goglib_scripts_overwrite))

        # mylib preferences

        self.config_parser.set('mylib preferences', 'mylib_keep_installers', str(self.mylib_keep_installers))
        self.config_parser.set('mylib preferences', 'mylib_download_dir', str(self.mylib_download_dir))
        self.config_parser.set('mylib preferences', 'mylib_install_dir', str(self.mylib_install_dir))
        self.config_parser.set('mylib preferences', 'mylib_scripts_overwrite', str(self.mylib_scripts_overwrite))

        # visuals
        self.config_parser.set('visuals', 'gtk_theme', str(self.gtk_theme))
        self.config_parser.set('visuals', 'gtk_dark', str(self.gtk_dark))
        self.config_parser.set('visuals', 'icon_theme', str(self.icon_theme))
        self.config_parser.set('visuals', 'font', str(self.font))

        # emulation settings
        self.config_parser.set('emulation settings', 'monitor', str(self.monitor))
        self.config_parser.set('emulation settings', 'wine', str(self.wine))
        self.config_parser.set('emulation settings', 'wine_path', str(self.wine_path))
        self.config_parser.set('emulation settings', 'wine_version', str(self.wine_version))
        self.config_parser.set('emulation settings', 'own_prefix', str(self.own_prefix))
        self.config_parser.set('emulation settings', 'winearch', str(self.winearch))
        self.config_parser.set('emulation settings', 'dosbox', str(self.dosbox))
        self.config_parser.set('emulation settings', 'dosbox_path', str(self.dosbox_path))
        self.config_parser.set('emulation settings', 'dosbox_version', str(self.dosbox_version))
        self.config_parser.set('emulation settings', 'scummvm', str(self.scummvm))
        self.config_parser.set('emulation settings', 'scummvm_path', str(self.scummvm_path))
        self.config_parser.set('emulation settings', 'scummvm_version', str(self.scummvm_version))

        config_file = open(config_dir + '/config.ini', 'w')
        self.config_parser.write(config_file)
        config_file.close()

    def get_system_visuals(self):

        screen = Gdk.Screen.get_default()
        gsettings = Gtk.Settings.get_for_screen(screen)

        self.gtk_theme = gsettings.get_property('gtk-theme-name')
        self.gtk_dark = gsettings.get_property('gtk-application-prefer-dark-theme')
        self.icon_theme = gsettings.get_property('gtk-icon-theme-name')
        self.font = gsettings.get_property('gtk-font-name')

    def set_visuals(self):

        screen = Gdk.Screen.get_default()
        gsettings = Gtk.Settings.get_for_screen(screen)

        gsettings.set_property('gtk-theme-name', self.gtk_theme)
        gsettings.set_property('gtk-application-prefer-dark-theme', self.gtk_dark)
        gsettings.set_property('gtk-icon-theme-name', self.icon_theme)
        gsettings.set_property('gtk-font-name', self.font)

        self.config_save()

    def populate_wine_version_combobox(self):

        ver_list = []

        path = self.filechooserbutton_wine.get_filename()
        full_list = os.listdir(path)

        for o in full_list:
            if os.path.isdir(path + '/' + o):
                ver_list.append(o)

        ver_list = sorted(ver_list)

        ver_index = 0
        for i in range(len(ver_list)):
            self.combobox_wine_version.append_text(ver_list[i])
            if ver_list[i] == self.wine_version:
                ver_index = i
        self.combobox_wine_version.set_active(ver_index)

    def populate_dosbox_version_combobox(self):

        ver_list = []

        path = self.filechooserbutton_dosbox.get_filename()
        full_list = os.listdir(path)

        for o in full_list:
            if os.path.isdir(path + '/' + o):
                ver_list.append(o)

        ver_list = sorted(ver_list)

        for i in range(len(ver_list)):
            self.combobox_dosbox_version.append_text(ver_list[i])
            if ver_list[i] == self.dosbox_version:
                self.combobox_dosbox_version.set_active(i)

    def populate_scummvm_version_combobox(self):

        ver_list = []

        path = self.filechooserbutton_scummvm.get_filename()
        full_list = os.listdir(path)

        for o in full_list:
            if os.path.isdir(path + '/' + o):
                ver_list.append(o)

        ver_list = sorted(ver_list)

        for i in range(len(ver_list)):
            self.combobox_scummvm_version.append_text(ver_list[i])
            if ver_list[i] == self.scummvm_version:
                self.combobox_scummvm_version.set_active(i)

    def populate_themes_comboboxes(self):

        themes_dir = '/usr/share/themes'
        icons_dir = '/usr/share/icons'
        themes = sorted(os.listdir(themes_dir))
        icon_themes = sorted(os.listdir(icons_dir))
        valid_themes = []
        valid_icon_themes = []

        for theme in themes:
            if os.path.exists(themes_dir + '/' + theme + '/gtk-3.0'):
                self.combobox_gtk_theme.append_text(theme)
                valid_themes.append(theme)

        for icon_theme in icon_themes:
            if os.path.exists(icons_dir + '/' + icon_theme + '/icon-theme.cache'):
                self.combobox_icon_theme.append_text(icon_theme)
                valid_icon_themes.append(icon_theme)

        for i in range(len(valid_themes)):
            if valid_themes[i] == self.gtk_theme:
                self.combobox_gtk_theme.set_active(i)

        for i in range(len(valid_icon_themes)):
            if valid_icon_themes[i] == self.icon_theme:
                self.combobox_icon_theme.set_active(i)

    def cb_combobox_goglib_tags1(self, combobox):

        self.goglib_tags_filter1 = combobox.get_active_text()

        self.goglib_tags1_filter_list = []

        filter = combobox.get_active_text()

        if filter == _("No filter"):
            self.goglib_tags1_filter_list = list(self.goglib_games_list)
        else:
            for game_name in self.goglib_games_list:
                game_tags = goglib_tags_get.goglib_tags_get(game_name, goglib_tags_file)

                if filter == _("No tags"):
                    if self.goglib_tags_filter1_type == 'include':
                        if len(game_tags) == 0:
                            self.goglib_tags1_filter_list.append(game_name)
                    elif self.goglib_tags_filter1_type == 'exclude':
                        if len(game_tags) != 0:
                            self.goglib_tags1_filter_list.append(game_name)
                else:
                    if self.goglib_tags_filter1_type == 'include':
                        if filter in game_tags:
                            self.goglib_tags1_filter_list.append(game_name)
                    elif self.goglib_tags_filter1_type == 'exclude':
                        if filter not in game_tags:
                            self.goglib_tags1_filter_list.append(game_name)

        self.goglib_apply_filters()

    def cb_combobox_mylib_tags1(self, combobox):

        self.mylib_tags_filter1 = combobox.get_active_text()

        self.mylib_tags1_filter_list = []

        filter = combobox.get_active_text()

        if filter == _("No filter"):
            self.mylib_tags1_filter_list = list(self.mylib_games_list)
        else:
            for game_name in self.mylib_games_list:
                game_tags = mylib_tags_get.mylib_tags_get(game_name, mylib_tags_file)

                if filter == _("No tags"):
                    if self.mylib_tags_filter1_type == 'include':
                        if len(game_tags) == 0:
                            self.mylib_tags1_filter_list.append(game_name)
                    elif self.mylib_tags_filter1_type == 'exclude':
                        if len(game_tags) != 0:
                            self.mylib_tags1_filter_list.append(game_name)
                else:
                    if self.mylib_tags_filter1_type == 'include':
                        if filter in game_tags:
                            self.mylib_tags1_filter_list.append(game_name)
                    elif self.mylib_tags_filter1_type == 'exclude':
                        if filter not in game_tags:
                            self.mylib_tags1_filter_list.append(game_name)

        self.mylib_apply_filters()

    def cb_combobox_goglib_tags2(self, combobox):

        self.goglib_tags_filter2 = combobox.get_active_text()

        self.goglib_tags2_filter_list = []

        filter = combobox.get_active_text()

        if filter == _("No filter"):
            self.goglib_tags2_filter_list = list(self.goglib_games_list)
        else:
            for game_name in self.goglib_games_list:
                game_tags = goglib_tags_get.goglib_tags_get(game_name, goglib_tags_file)

                if filter == _("No tags"):
                    if self.goglib_tags_filter2_type == 'include':
                        if len(game_tags) == 0:
                            self.goglib_tags2_filter_list.append(game_name)
                    elif self.goglib_tags_filter2_type == 'exclude':
                        if len(game_tags) != 0:
                            self.goglib_tags2_filter_list.append(game_name)
                else:
                    if self.goglib_tags_filter2_type == 'include':
                        if filter in game_tags:
                            self.goglib_tags2_filter_list.append(game_name)
                    elif self.goglib_tags_filter2_type == 'exclude':
                        if filter not in game_tags:
                            self.goglib_tags2_filter_list.append(game_name)

        self.goglib_apply_filters()

    def cb_combobox_mylib_tags2(self, combobox):

        self.mylib_tags_filter2 = combobox.get_active_text()

        self.mylib_tags2_filter_list = []

        filter = combobox.get_active_text()

        if filter == _("No filter"):
            self.mylib_tags2_filter_list = list(self.mylib_games_list)
        else:
            for game_name in self.mylib_games_list:
                game_tags = mylib_tags_get.mylib_tags_get(game_name, mylib_tags_file)

                if filter == _("No tags"):
                    if self.mylib_tags_filter2_type == 'include':
                        if len(game_tags) == 0:
                            self.mylib_tags2_filter_list.append(game_name)
                    elif self.mylib_tags_filter2_type == 'exclude':
                        if len(game_tags) != 0:
                            self.mylib_tags2_filter_list.append(game_name)
                else:
                    if self.mylib_tags_filter2_type == 'include':
                        if filter in game_tags:
                            self.mylib_tags2_filter_list.append(game_name)
                    elif self.mylib_tags_filter2_type == 'exclude':
                        if filter not in game_tags:
                            self.mylib_tags2_filter_list.append(game_name)

        self.mylib_apply_filters()

    def cb_combobox_goglib_tags3(self, combobox):

        self.goglib_tags_filter3 = combobox.get_active_text()

        self.goglib_tags3_filter_list = []

        filter = combobox.get_active_text()

        if filter == _("No filter"):
            self.goglib_tags3_filter_list = list(self.goglib_games_list)
        else:
            for game_name in self.goglib_games_list:
                game_tags = goglib_tags_get.goglib_tags_get(game_name, goglib_tags_file)

                if filter == _("No tags"):
                    if self.goglib_tags_filter3_type == 'include':
                        if len(game_tags) == 0:
                            self.goglib_tags3_filter_list.append(game_name)
                    elif self.goglib_tags_filter3_type == 'exclude':
                        if len(game_tags) != 0:
                            self.goglib_tags3_filter_list.append(game_name)
                else:
                    if self.goglib_tags_filter3_type == 'include':
                        if filter in game_tags:
                            self.goglib_tags3_filter_list.append(game_name)
                    elif self.goglib_tags_filter3_type == 'exclude':
                        if filter not in game_tags:
                            self.goglib_tags3_filter_list.append(game_name)

        self.goglib_apply_filters()

    def cb_combobox_mylib_tags3(self, combobox):

        self.mylib_tags_filter3 = combobox.get_active_text()

        self.mylib_tags3_filter_list = []

        filter = combobox.get_active_text()

        if filter == _("No filter"):
            self.mylib_tags3_filter_list = list(self.mylib_games_list)
        else:
            for game_name in self.mylib_games_list:
                game_tags = mylib_tags_get.mylib_tags_get(game_name, mylib_tags_file)

                if filter == _("No tags"):
                    if self.mylib_tags_filter3_type == 'include':
                        if len(game_tags) == 0:
                            self.mylib_tags3_filter_list.append(game_name)
                    elif self.mylib_tags_filter3_type == 'exclude':
                        if len(game_tags) != 0:
                            self.mylib_tags3_filter_list.append(game_name)
                else:
                    if self.mylib_tags_filter3_type == 'include':
                        if filter in game_tags:
                            self.mylib_tags3_filter_list.append(game_name)
                    elif self.mylib_tags_filter3_type == 'exclude':
                        if filter not in game_tags:
                            self.mylib_tags3_filter_list.append(game_name)

        self.mylib_apply_filters()

    def cb_combobox_goglib_tags4(self, combobox):

        self.goglib_tags_filter4 = combobox.get_active_text()

        self.goglib_tags4_filter_list = []

        filter = combobox.get_active_text()

        if filter == _("No filter"):
            self.goglib_tags4_filter_list = list(self.goglib_games_list)
        else:
            for game_name in self.goglib_games_list:
                game_tags = goglib_tags_get.goglib_tags_get(game_name, goglib_tags_file)

                if filter == _("No tags"):
                    if self.goglib_tags_filter4_type == 'include':
                        if len(game_tags) == 0:
                            self.goglib_tags4_filter_list.append(game_name)
                    elif self.goglib_tags_filter4_type == 'exclude':
                        if len(game_tags) != 0:
                            self.goglib_tags4_filter_list.append(game_name)
                else:
                    if self.goglib_tags_filter4_type == 'include':
                        if filter in game_tags:
                            self.goglib_tags4_filter_list.append(game_name)
                    elif self.goglib_tags_filter4_type == 'exclude':
                        if filter not in game_tags:
                            self.goglib_tags4_filter_list.append(game_name)

        self.goglib_apply_filters()

    def cb_combobox_mylib_tags4(self, combobox):

        self.mylib_tags_filter4 = combobox.get_active_text()

        self.mylib_tags4_filter_list = []

        filter = combobox.get_active_text()

        if filter == _("No filter"):
            self.mylib_tags4_filter_list = list(self.mylib_games_list)
        else:
            for game_name in self.mylib_games_list:
                game_tags = mylib_tags_get.mylib_tags_get(game_name, mylib_tags_file)

                if filter == _("No tags"):
                    if self.mylib_tags_filter4_type == 'include':
                        if len(game_tags) == 0:
                            self.mylib_tags4_filter_list.append(game_name)
                    elif self.mylib_tags_filter4_type == 'exclude':
                        if len(game_tags) != 0:
                            self.mylib_tags4_filter_list.append(game_name)
                else:
                    if self.mylib_tags_filter4_type == 'include':
                        if filter in game_tags:
                            self.mylib_tags4_filter_list.append(game_name)
                    elif self.mylib_tags_filter4_type == 'exclude':
                        if filter not in game_tags:
                            self.mylib_tags4_filter_list.append(game_name)

        self.mylib_apply_filters()

    def goglib_search_filter(self, search_bar):

        self.goglib_search_filter_list = []

        filter = search_bar.get_text()

        for game_name in self.goglib_games_list:

            # Find sequence of characters in the beggining of the string
            if bool(re.match(filter, self.goglib_dict_name_to_title[game_name], re.I)):
                self.goglib_search_filter_list.append(game_name)
            # Find sequence of characters anywere in the string
            if len(filter) > 1:
                if filter.lower() in self.goglib_dict_name_to_title[game_name].lower():
                    self.goglib_search_filter_list.append(game_name)

        self.goglib_apply_filters()

    def mylib_search_filter(self, search_bar):

        self.mylib_search_filter_list = []

        filter = search_bar.get_text()

        for game_name in self.mylib_games_list:

            # Find sequence of characters in the beggining of the string
            if bool(re.match(filter, self.mylib_dict_name_to_title[game_name], re.I)):
                self.mylib_search_filter_list.append(game_name)
            # Find sequence of characters anywere in the string
            if len(filter) > 1:
                if filter.lower() in self.mylib_dict_name_to_title[game_name].lower():
                    self.mylib_search_filter_list.append(game_name)

        self.mylib_apply_filters()

    def cb_combobox_goglib_status(self, combobox):

        self.status_filter = combobox.get_active_text()

        self.goglib_status_filter_list = []

        filter = combobox.get_active_text()

        if filter == _("No filter"):
            self.goglib_status_filter_list = list(self.goglib_games_list)
        if filter == _("Installed"):
            for game_name in self.goglib_games_list:

                if self.goglib_status_filter_type == 'include':

                    if os.path.exists(self.goglib_install_dir + '/' + game_name + '/start.sh') and \
                            (game_name not in goglib_installation_queue):

                        self.goglib_status_filter_list.append(game_name)

                elif self.goglib_status_filter_type == 'exclude':
                    if not os.path.exists(self.goglib_install_dir + '/' + game_name + '/start.sh')  and \
                            (game_name not in goglib_installation_queue):

                        self.goglib_status_filter_list.append(game_name)

        if filter == _("Unavailable"):
            for game_name in self.goglib_games_list:
                if self.goglib_status_filter_type == 'include':
                    if game_name not in self.goglib_available_games:
                        self.goglib_status_filter_list.append(game_name)
                elif self.goglib_status_filter_type == 'exclude':
                    if game_name in self.goglib_available_games:
                        self.goglib_status_filter_list.append(game_name)

        self.goglib_apply_filters()


    def cb_combobox_mylib_status(self, combobox):

        self.mylib_status_filter = combobox.get_active_text()

        self.mylib_status_filter_list = []

        filter = combobox.get_active_text()

        if filter == _("No filter"):
            self.mylib_status_filter_list = list(self.mylib_games_list)
        if filter == _("Installed"):
            for game_name in self.mylib_games_list:

                if self.mylib_status_filter_type == 'include':

                    if (os.path.exists(self.mylib_install_dir + '/' + game_name + '/start.sh')) and \
                            (game_name not in mylib_installation_queue):

                        self.mylib_status_filter_list.append(game_name)

                elif self.mylib_status_filter_type == 'exclude':
                    if not os.path.exists(self.mylib_install_dir + '/' + game_name + '/start.sh'):
                        self.mylib_status_filter_list.append(game_name)

        self.mylib_apply_filters()

    def goglib_apply_filters(self):

        self.final_list = []

        for game_name in self.goglib_games_list:
            if (game_name in self.goglib_tags1_filter_list) and \
                    (game_name in self.goglib_tags2_filter_list) and \
                    (game_name in self.goglib_tags3_filter_list) and \
                    (game_name in self.goglib_tags4_filter_list) and \
                    (game_name in self.goglib_status_filter_list) and \
                    (game_name in self.goglib_search_filter_list):
                self.final_list.append(game_name)

        self.grid_unattach()

        self.goglib_shown_games_list = list(self.final_list)
        self.goglib_number_of_games_to_show = len(self.goglib_shown_games_list)

        goglib_game_grids_current_list  = []

        for game_grid in goglib_game_grids_full_list:
            if game_grid.get_name() in self.goglib_shown_games_list:
                goglib_game_grids_current_list.append(game_grid)

        self.update_goglib_grid()

    def mylib_apply_filters(self):

        self.mylib_final_list = []

        for game_name in self.mylib_games_list:
            if (game_name in self.mylib_tags1_filter_list) and \
                        (game_name in self.mylib_tags2_filter_list) and \
                        (game_name in self.mylib_tags3_filter_list) and \
                        (game_name in self.mylib_tags4_filter_list) and \
                        (game_name in self.mylib_status_filter_list) and \
                        (game_name in self.mylib_search_filter_list):

                self.mylib_final_list.append(game_name)

        self.mylib_grid_unattach()

        self.mylib_shown_games_list = list(self.mylib_final_list)
        self.mylib_number_of_games_to_show = len(self.mylib_shown_games_list)

        mylib_game_grids_current_list  = []

        for game_grid in mylib_game_grids_full_list:
            if game_grid.get_name() in self.mylib_shown_games_list:
                mylib_game_grids_current_list.append(game_grid)

        self.update_mylib_grid()

    def goglib_tag_filters_number_changed(self, button):

        action = button.get_name()

        if action == 'add':
            self.goglib_tf_number += 1
        if action == 'remove':
            self.goglib_tf_number -= 1

        self.goglib_tags_visibility()

    def mylib_tagfilters_number_changed(self, button):

        action = button.get_name()

        if action == 'add':
            self.mylib_tf_number += 1
        if action == 'remove':
            self.mylib_tf_number -= 1

        self.mylib_tags_visibility()

    def goglib_tags_visibility(self):
        if self.goglib_tf_number == 1:
            self.button_goglib_remove_tag_filter.set_visible(False)
            self.button_goglib_add_tag_filter.set_visible(True)
            self.combobox_goglib_tags2.set_visible(False)
            self.combobox_goglib_tags2.set_active(0)
            self.combobox_goglib_tags3.set_visible(False)
            self.combobox_goglib_tags3.set_active(0)
            self.combobox_goglib_tags4.set_visible(False)
            self.combobox_goglib_tags4.set_active(0)
        if self.goglib_tf_number == 2:
            self.button_goglib_remove_tag_filter.set_visible(True)
            self.button_goglib_add_tag_filter.set_visible(True)
            self.combobox_goglib_tags2.set_visible(True)
            self.combobox_goglib_tags3.set_visible(False)
            self.combobox_goglib_tags3.set_active(0)
            self.combobox_goglib_tags4.set_visible(False)
            self.combobox_goglib_tags4.set_active(0)
        if self.goglib_tf_number == 3:
            self.button_goglib_remove_tag_filter.set_visible(True)
            self.button_goglib_add_tag_filter.set_visible(True)
            self.combobox_goglib_tags2.set_visible(True)
            self.combobox_goglib_tags3.set_visible(True)
            self.combobox_goglib_tags4.set_visible(False)
            self.combobox_goglib_tags4.set_active(0)
        if self.goglib_tf_number == 4:
            self.button_goglib_remove_tag_filter.set_visible(True)
            self.button_goglib_add_tag_filter.set_visible(False)
            self.combobox_goglib_tags2.set_visible(True)
            self.combobox_goglib_tags3.set_visible(True)
            self.combobox_goglib_tags4.set_visible(True)

    def mylib_tags_visibility(self):
        if self.mylib_tf_number == 1:
            self.button_mylib_tagfilter_remove.set_visible(False)
            self.button_mylib_tagfilter_add.set_visible(True)
            self.combobox_mylib_tags2.set_visible(False)
            self.combobox_mylib_tags2.set_active(0)
            self.combobox_mylib_tags3.set_visible(False)
            self.combobox_mylib_tags3.set_active(0)
            self.combobox_mylib_tags4.set_visible(False)
            self.combobox_mylib_tags4.set_active(0)
        if self.mylib_tf_number == 2:
            self.button_mylib_tagfilter_remove.set_visible(True)
            self.button_mylib_tagfilter_add.set_visible(True)
            self.combobox_mylib_tags2.set_visible(True)
            self.combobox_mylib_tags3.set_visible(False)
            self.combobox_mylib_tags3.set_active(0)
            self.combobox_mylib_tags4.set_visible(False)
            self.combobox_mylib_tags4.set_active(0)
        if self.mylib_tf_number == 3:
            self.button_mylib_tagfilter_remove.set_visible(True)
            self.button_mylib_tagfilter_add.set_visible(True)
            self.combobox_mylib_tags2.set_visible(True)
            self.combobox_mylib_tags3.set_visible(True)
            self.combobox_mylib_tags4.set_visible(False)
            self.combobox_mylib_tags4.set_active(0)
        if self.mylib_tf_number == 4:
            self.button_mylib_tagfilter_remove.set_visible(True)
            self.button_mylib_tagfilter_add.set_visible(False)
            self.combobox_mylib_tags2.set_visible(True)
            self.combobox_mylib_tags3.set_visible(True)
            self.combobox_mylib_tags4.set_visible(True)

    def cb_adjustment_goglib_scale_banner(self, adjustment):

        self.scale_level = adjustment.get_value()

        self.update_goglib_grid()

    def cb_adjustment_mylib_scale_banner(self, adjustment):

        self.mylib_scale_level = adjustment.get_value()

        self.update_mylib_grid()

    def goglib_banner_clicked(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            game_name = widget.get_children()[0].get_name()

            current_tags_list = goglib_tags_get.goglib_tags_get(game_name, goglib_tags_file)

            current_tags_str = str1 = ','.join(current_tags_list)

            message_dialog = Gtk.MessageDialog(
                self.main_window,
                0,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK_CANCEL,
                '"' + self.goglib_dict_name_to_title[game_name] + '" ' + _("tags:"),
                )
            message_dialog.set_property('default-width', 480)
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            content_area.set_property('spacing', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('margin_top', 10)
            action_area.set_property('spacing', 10)

            entry = Gtk.Entry(
                text = current_tags_str,
                placeholder_text = _("Use commas to separate tags."),
                width_request = 100,
                sensitive = False,
                tooltip_text = _("Current tags")
                )

            def cb_button_edit_tags(button):
                if entry.get_sensitive():
                    entry.set_sensitive(False)
                else:
                    entry.set_sensitive(True)

            img = Gtk.Image.new_from_icon_name("document-new", Gtk.IconSize.SMALL_TOOLBAR)
            button_edit_tags = Gtk.Button(
                image = img,
                tooltip_text = _("Edit")
                )
            button_edit_tags.connect('clicked', cb_button_edit_tags)

            box0 = Gtk.Box(spacing = 5)

            box0.pack_start(entry, True, True, 0)
            box0.pack_start(button_edit_tags, False, False, 0)

            combobox_existing_tags = Gtk.ComboBoxText(no_show_all=True)
            for tag in self.all_tags:
                if tag not in predefined_tags:
                    combobox_existing_tags.append_text(tag)
            combobox_existing_tags.set_active(0)

            def cb_button_remove_existing_tags(button):
                current_tags = entry.get_text()
                tag_to_remove = combobox_existing_tags.get_active_text()
                if tag_to_remove in current_tags:
                    tmp_list = current_tags.split(',')
                    tmp_list.remove(tag_to_remove)
                    net_tags_string = ','.join(tmp_list)
                    entry.set_text(net_tags_string)

            img = Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.SMALL_TOOLBAR)
            button_remove_existing_tags = Gtk.Button(
                image = img,
                no_show_all = True,
                tooltip_text = _("Remove from current tags")
                )
            button_remove_existing_tags.connect('clicked', cb_button_remove_existing_tags)

            def cb_button_add_existing_tags(button):
                current_tags = entry.get_text()
                new_tag = combobox_existing_tags.get_active_text()
                if new_tag not in current_tags:
                    if len(current_tags) == 0:
                        entry.set_text(new_tag)
                    else:
                        entry.set_text(current_tags + ',' + new_tag)

            img = Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.SMALL_TOOLBAR)
            button_add_existing_tags = Gtk.Button(
                image = img,
                no_show_all = True,
                tooltip_text = _("Add to current tags")
                )
            button_add_existing_tags.connect('clicked', cb_button_add_existing_tags)

            label_existing_tags = Gtk.Label(
                label=_("Existing tags:"),
                xalign = 0,
                no_show_all = True
                )
            box1 = Gtk.Box(spacing = 5)

            if len(self.all_tags) == 0:
                label_existing_tags.set_visible(False)
                combobox_existing_tags.set_visible(False)
                button_remove_existing_tags.set_visible(False)
                button_add_existing_tags.set_visible(False)
            else:
                label_existing_tags.set_visible(True)
                combobox_existing_tags.set_visible(True)
                button_remove_existing_tags.set_visible(True)
                button_add_existing_tags.set_visible(True)

            box1.pack_start(combobox_existing_tags, True, True, 0)
            box1.pack_start(button_remove_existing_tags, False, False, 0)
            box1.pack_start(button_add_existing_tags, False, False, 0)

            combobox_predefined_tags = Gtk.ComboBoxText()
            for tag in predefined_tags:
                combobox_predefined_tags.append_text(tag)
            combobox_predefined_tags.set_active(0)

            def cb_button_remove_predefined_tags(button):
                current_tags = entry.get_text()
                tag_to_remove = combobox_predefined_tags.get_active_text()
                if tag_to_remove in current_tags:
                    tmp_list = current_tags.split(',')
                    tmp_list.remove(tag_to_remove)
                    net_tags_string = ','.join(tmp_list)
                    entry.set_text(net_tags_string)

            img = Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.SMALL_TOOLBAR)
            button_remove_predefined_tags = Gtk.Button(
                image = img,
                tooltip_text = _("Remove from current tags")
                )
            button_remove_predefined_tags.connect('clicked', cb_button_remove_predefined_tags)

            def cb_button_add_predefined_tags(button):
                current_tags = entry.get_text()
                new_tag = combobox_predefined_tags.get_active_text()
                if new_tag not in current_tags:
                    if len(current_tags) == 0:
                        entry.set_text(new_tag)
                    else:
                        entry.set_text(current_tags + ',' + new_tag)

            img = Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.SMALL_TOOLBAR)
            button_add_predefined_tags = Gtk.Button(
                image = img,
                tooltip_text = _("Add to current tags")
                )
            button_add_predefined_tags.connect('clicked', cb_button_add_predefined_tags)

            label_predefined_tags = Gtk.Label(
                label=_("Predefined tags:"),
                xalign = 0
                )
            box2 = Gtk.Box(spacing=5)
            box2.pack_start(combobox_predefined_tags, True, True, 0)
            box2.pack_start(button_remove_predefined_tags, False, False, 0)
            box2.pack_start(button_add_predefined_tags, False, False, 0)

            content_area.pack_start(box0, True, True, 0)
            content_area.pack_start(label_existing_tags, True, True, 0)
            content_area.pack_start(box1, True, True, 0)
            content_area.pack_start(label_predefined_tags, True, True, 0)
            content_area.pack_start(box2, True, True, 0)

            message_dialog.show_all()
            message_dialog_response = message_dialog.run()

            if message_dialog_response == Gtk.ResponseType.OK:

                new_tags = entry.get_text()

                if new_tags != '':

                    new_tags_list = new_tags.split(',')

                    update_combobox = False

                    for tag in new_tags_list:
                        if tag not in self.all_tags:
                            update_combobox = True

                    goglib_tags_create.goglib_tags_create(game_name, new_tags, goglib_tags_file)
                    self.all_tags = goglib_tags_get_all.goglib_tags_get_all(goglib_tags_file)

                    if update_combobox == True:

                        self.combobox_goglib_tags1.get_model().clear()
                        self.combobox_goglib_tags2.get_model().clear()
                        self.combobox_goglib_tags3.get_model().clear()
                        self.combobox_goglib_tags4.get_model().clear()

                        self.combobox_goglib_tags1.append_text(_("No filter"))
                        self.combobox_goglib_tags2.append_text(_("No filter"))
                        self.combobox_goglib_tags3.append_text(_("No filter"))
                        self.combobox_goglib_tags4.append_text(_("No filter"))
                        self.combobox_goglib_tags1.set_active(0)
                        self.combobox_goglib_tags2.set_active(0)
                        self.combobox_goglib_tags3.set_active(0)
                        self.combobox_goglib_tags4.set_active(0)
                        for tag in self.all_tags:
                            if tag != '':
                                self.combobox_goglib_tags1.append_text(tag)
                                self.combobox_goglib_tags2.append_text(tag)
                                self.combobox_goglib_tags3.append_text(tag)
                                self.combobox_goglib_tags4.append_text(tag)
                        self.combobox_goglib_tags1.append_text(_("No tags"))
                        self.combobox_goglib_tags2.append_text(_("No tags"))
                        self.combobox_goglib_tags3.append_text(_("No tags"))
                        self.combobox_goglib_tags4.append_text(_("No tags"))

                    self.cb_combobox_goglib_tags1(self.combobox_goglib_tags1)
                    self.cb_combobox_goglib_tags2(self.combobox_goglib_tags2)
                    self.cb_combobox_goglib_tags3(self.combobox_goglib_tags3)
                    self.cb_combobox_goglib_tags4(self.combobox_goglib_tags4)

                if new_tags == '':
                    goglib_tags_create.goglib_tags_create(game_name, new_tags, goglib_tags_file)
                    self.cb_combobox_goglib_tags1(self.combobox_goglib_tags1)
                    self.cb_combobox_goglib_tags2(self.combobox_goglib_tags2)
                    self.cb_combobox_goglib_tags3(self.combobox_goglib_tags3)
                    self.cb_combobox_goglib_tags4(self.combobox_goglib_tags4)

            message_dialog.destroy()

    def mylib_banner_clicked(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            game_name = widget.get_children()[0].get_name()

            current_tags_list = mylib_tags_get.mylib_tags_get(game_name, mylib_tags_file)

            current_tags_str = str1 = ','.join(current_tags_list)

            message_dialog = Gtk.MessageDialog(
                self.main_window,
                0,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK_CANCEL,
                '"' + self.mylib_dict_name_to_title[game_name] + '" ' + _("tags:"),
                )
            message_dialog.set_property('default-width', 480)
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            content_area.set_property('spacing', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('margin_top', 10)
            action_area.set_property('spacing', 10)

            entry = Gtk.Entry(
                text = current_tags_str,
                placeholder_text = _("Use comma to separate tags."),
                width_request = 100,
                sensitive = False,
                tooltip_text = _("Current tags")
                )

            def cb_button_edit_tags(button):
                if entry.get_sensitive():
                    entry.set_sensitive(False)
                else:
                    entry.set_sensitive(True)

            img = Gtk.Image.new_from_icon_name("document-new", Gtk.IconSize.SMALL_TOOLBAR)
            button_edit_tags = Gtk.Button(
                image = img,
                tooltip_text = _("Edit")
                )
            button_edit_tags.connect('clicked', cb_button_edit_tags)

            box0 = Gtk.Box(spacing = 5)

            box0.pack_start(entry, True, True, 0)
            box0.pack_start(button_edit_tags, False, False, 0)

            combobox_existing_tags = Gtk.ComboBoxText(no_show_all=True)
            for tag in self.mylib_all_tags:
                if tag not in predefined_tags:
                    combobox_existing_tags.append_text(tag)
            combobox_existing_tags.set_active(0)

            def cb_button_remove_existing_tags(button):
                current_tags = entry.get_text()
                tag_to_remove = combobox_existing_tags.get_active_text()
                if tag_to_remove in current_tags:
                    tmp_list = current_tags.split(',')
                    tmp_list.remove(tag_to_remove)
                    net_tags_string = ','.join(tmp_list)
                    entry.set_text(net_tags_string)

            img = Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.SMALL_TOOLBAR)
            button_remove_existing_tags = Gtk.Button(
                image = img,
                no_show_all = True,
                tooltip_text = _("Remove from current tags")
                )
            button_remove_existing_tags.connect('clicked', cb_button_remove_existing_tags)

            def cb_button_add_existing_tags(button):
                current_tags = entry.get_text()
                new_tag = combobox_existing_tags.get_active_text()
                if new_tag not in current_tags:
                    if len(current_tags) == 0:
                        entry.set_text(new_tag)
                    else:
                        entry.set_text(current_tags + ',' + new_tag)

            img = Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.SMALL_TOOLBAR)
            button_add_existing_tags = Gtk.Button(
                image = img,
                no_show_all = True,
                tooltip_text = _("Add to current tags")
                )
            button_add_existing_tags.connect('clicked', cb_button_add_existing_tags)

            label_existing_tags = Gtk.Label(
                label=_("Existing tags:"),
                xalign = 0,
                no_show_all = True
                )
            box1 = Gtk.Box(spacing = 5)

            if len(self.mylib_all_tags) == 0:
                label_existing_tags.set_visible(False)
                combobox_existing_tags.set_visible(False)
                button_remove_existing_tags.set_visible(False)
                button_add_existing_tags.set_visible(False)
            else:
                label_existing_tags.set_visible(True)
                combobox_existing_tags.set_visible(True)
                button_remove_existing_tags.set_visible(True)
                button_add_existing_tags.set_visible(True)

            box1.pack_start(combobox_existing_tags, True, True, 0)
            box1.pack_start(button_remove_existing_tags, False, False, 0)
            box1.pack_start(button_add_existing_tags, False, False, 0)

            combobox_predefined_tags = Gtk.ComboBoxText()
            for tag in predefined_tags:
                combobox_predefined_tags.append_text(tag)
            combobox_predefined_tags.set_active(0)

            def cb_button_remove_predefined_tags(button):
                current_tags = entry.get_text()
                tag_to_remove = combobox_predefined_tags.get_active_text()
                if tag_to_remove in current_tags:
                    tmp_list = current_tags.split(',')
                    tmp_list.remove(tag_to_remove)
                    net_tags_string = ','.join(tmp_list)
                    entry.set_text(net_tags_string)

            img = Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.SMALL_TOOLBAR)
            button_remove_predefined_tags = Gtk.Button(
                image = img,
                tooltip_text = _("Remove from current tags")
                )
            button_remove_predefined_tags.connect('clicked', cb_button_remove_predefined_tags)

            def cb_button_add_predefined_tags(button):
                current_tags = entry.get_text()
                new_tag = combobox_predefined_tags.get_active_text()
                if new_tag not in current_tags:
                    if len(current_tags) == 0:
                        entry.set_text(new_tag)
                    else:
                        entry.set_text(current_tags + ',' + new_tag)


            img = Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.SMALL_TOOLBAR)
            button_add_predefined_tags = Gtk.Button(
                image = img,
                tooltip_text = _("Add to current tags")
                )
            button_add_predefined_tags.connect('clicked', cb_button_add_predefined_tags)

            label_predefined_tags = Gtk.Label(
                label=_("Predefined tags:"),
                xalign = 0
                )
            box2 = Gtk.Box(spacing=5)
            box2.pack_start(combobox_predefined_tags, True, True, 0)
            box2.pack_start(button_remove_predefined_tags, False, False, 0)
            box2.pack_start(button_add_predefined_tags, False, False, 0)

            content_area.pack_start(box0, True, True, 0)
            content_area.pack_start(label_existing_tags, True, True, 0)
            content_area.pack_start(box1, True, True, 0)
            content_area.pack_start(label_predefined_tags, True, True, 0)
            content_area.pack_start(box2, True, True, 0)

            message_dialog.show_all()
            message_dialog_response = message_dialog.run()

            if message_dialog_response == Gtk.ResponseType.OK:

                new_tags = entry.get_text()

                if new_tags != '':

                    new_tags_list = new_tags.split(',')

                    update_combobox = False

                    for tag in new_tags_list:
                        if tag not in self.mylib_all_tags:
                            update_combobox = True

                    mylib_tags_create.mylib_tags_create(game_name, new_tags, mylib_tags_file)
                    self.mylib_all_tags = mylib_tags_get_all.mylib_tags_get_all(mylib_tags_file)

                    if update_combobox == True:

                        self.combobox_mylib_tags1.get_model().clear()
                        self.combobox_mylib_tags2.get_model().clear()
                        self.combobox_mylib_tags3.get_model().clear()
                        self.combobox_mylib_tags4.get_model().clear()

                        self.combobox_mylib_tags1.append_text(_("No filter"))
                        self.combobox_mylib_tags2.append_text(_("No filter"))
                        self.combobox_mylib_tags3.append_text(_("No filter"))
                        self.combobox_mylib_tags4.append_text(_("No filter"))
                        self.combobox_mylib_tags1.set_active(0)
                        self.combobox_mylib_tags2.set_active(0)
                        self.combobox_mylib_tags3.set_active(0)
                        self.combobox_mylib_tags4.set_active(0)
                        for tag in self.mylib_all_tags:
                            if tag != '':
                                self.combobox_mylib_tags1.append_text(tag)
                                self.combobox_mylib_tags2.append_text(tag)
                                self.combobox_mylib_tags3.append_text(tag)
                                self.combobox_mylib_tags4.append_text(tag)
                        self.combobox_mylib_tags1.append_text(_("No tags"))
                        self.combobox_mylib_tags2.append_text(_("No tags"))
                        self.combobox_mylib_tags3.append_text(_("No tags"))
                        self.combobox_mylib_tags4.append_text(_("No tags"))

                    self.cb_combobox_mylib_tags1(self.combobox_mylib_tags1)
                    self.cb_combobox_mylib_tags2(self.combobox_mylib_tags2)
                    self.cb_combobox_mylib_tags3(self.combobox_mylib_tags3)
                    self.cb_combobox_mylib_tags4(self.combobox_mylib_tags4)

                if new_tags == '':
                    mylib_tags_create.mylib_tags_create(game_name, new_tags, mylib_tags_file)
                    self.cb_combobox_mylib_tags1(self.combobox_mylib_tags1)
                    self.cb_combobox_mylib_tags2(self.combobox_mylib_tags2)
                    self.cb_combobox_mylib_tags3(self.combobox_mylib_tags3)
                    self.cb_combobox_mylib_tags4(self.combobox_mylib_tags4)

            message_dialog.destroy()

    def remove_from_installation_queue(self, button):

        game_name = button.get_name()

        self.download_canceled = False
        self.unpack_canceled = False

        if game_name in goglib_name_to_pid_download_dict:

            self.download_canceled = True

            os.kill(goglib_name_to_pid_download_dict[game_name], signal.SIGTERM)

            if self.goglib_keep_installers == False:
                if os.path.exists(self.goglib_download_dir + '/' + game_name):
                    os.system('rm -R -f ' + self.goglib_download_dir + '/' + game_name)

            for i in range(self.goglib_number_of_games_to_show):
                if goglib_setup_buttons_list[i].get_name() == game_name:
                    goglib_setup_buttons_list[i].set_label(_("Install"))
                    goglib_setup_buttons_list[i].set_sensitive(True)

        elif game_name in goglib_name_to_pid_unpack_dict:

            self.unpack_canceled = True

            os.kill(goglib_name_to_pid_unpack_dict[game_name], signal.SIGTERM)

            if self.goglib_keep_installers == False:
                if os.path.exists(self.goglib_download_dir + '/' + game_name):
                    os.system('rm -R -f ' + self.goglib_download_dir + '/' + game_name)

            if os.path.exists(self.goglib_install_dir + '/' + game_name):
                os.system('rm -R -f ' + self.goglib_install_dir + '/' + game_name)

            for i in range(self.goglib_number_of_games_to_show):
                if goglib_setup_buttons_list[i].get_name() == game_name:
                    goglib_setup_buttons_list[i].set_label(_("Install"))
                    goglib_setup_buttons_list[i].set_sensitive(True)

        elif game_name in goglib_name_to_pid_install_dict:
            os.kill(goglib_name_to_pid_install_dict[game_name], signal.SIGTERM)

            if self.goglib_keep_installers == False:
                if os.path.exists(self.goglib_download_dir + '/' + game_name):
                    os.system('rm -R -f ' + self.goglib_download_dir + '/' + game_name)

            if os.path.exists(self.goglib_install_dir + '/' + game_name):
                os.system('rm -R -f ' + self.goglib_install_dir + '/' + game_name)

            for i in range(self.goglib_number_of_games_to_show):
                if goglib_setup_buttons_list[i].get_name() == game_name:
                    goglib_setup_buttons_list[i].set_label(_("Install"))
                    goglib_setup_buttons_list[i].set_sensitive(True)

        elif game_name in goglib_installation_queue:

            goglib_installation_queue.remove(game_name)

            if not os.path.exists(self.goglib_install_dir + '/' + game_name + '/start.sh'):
                for i in range(self.goglib_number_of_games_to_show):
                    if goglib_setup_buttons_list[i].get_name() == game_name:
                        goglib_setup_buttons_list[i].set_label(_("Install"))
                        goglib_setup_buttons_list[i].set_sensitive(True)

        elif game_name in mylib_name_to_pid_install_dict:

            os.kill(mylib_name_to_pid_install_dict[game_name], signal.SIGTERM)
            del mylib_name_to_pid_install_dict[mylib_installation_queue[0]]
            mylib_installation_queue.remove(game_name)
            self.mylib_now_installing = None

            if self.mylib_keep_installers == False:
                if os.path.exists(self.mylib_download_dir + '/' + game_name):
                    os.system('rm -R -f ' + self.goglib_download_dir + '/' + game_name)

            if os.path.exists(self.mylib_install_dir + '/' + game_name):
                os.system('rm -R -f ' + self.mylib_install_dir + '/' + game_name)

            for i in range(self.mylib_number_of_games_to_show):
                if mylib_setup_buttons_list[i].get_name() == game_name:
                    mylib_setup_buttons_list[i].set_label(_("Install"))
                    mylib_setup_buttons_list[i].set_sensitive(True)

        elif game_name in mylib_installation_queue:

            del mylib_name_to_pid_install_dict[mylib_installation_queue[0]]
            mylib_installation_queue.remove(game_name)
            self.mylib_now_installing = None

            if not os.path.exists(self.mylib_install_dir + '/' + game_name + '/start.sh'):
                for i in range(self.mylib_number_of_games_to_show):
                    if mylib_setup_buttons_list[i].get_name() == game_name:
                        mylib_setup_buttons_list[i].set_label(_("Install"))
                        mylib_setup_buttons_list[i].set_sensitive(True)


        for frame in queue_game_frame_list:
            if frame.get_name() == game_name:
                frame.destroy()

    def mylib_launch_game(self, button):

        self.switch_monitor('ON')

        self.main_window.hide()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        game_name = button.get_name()

        self.set_environ(game_name, self.mylib_download_dir, self.mylib_install_dir)

        start_path = self.mylib_install_dir + '/' + game_name + '/start.sh'
        os.system('chmod +x ' + start_path)
        os.system(start_path)

        self.switch_monitor('OFF')

        self.main_window.show()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.show()

    def goglib_launch_game(self, button):

        self.switch_monitor('ON')

        self.main_window.hide()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        game_name = button.get_name()

        self.set_environ(game_name, self.goglib_download_dir, self.goglib_install_dir)

        start_file_path = self.goglib_install_dir + '/' + game_name + '/start.sh'
        os.system('chmod +x ' + start_file_path)
        os.system(start_file_path)

        self.switch_monitor('OFF')

        self.main_window.show()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.show()

    def mylib_setup_game(self, button):

        game_name = button.get_name()

        if not os.path.exists(self.mylib_install_dir + '/' + game_name + '/start.sh'):

            if len(mylib_installation_queue) == 0:
                button.set_label(_("Installing"))
            else:
                button.set_label(_("In queue"))
            button.set_sensitive(False)

            if len(queue_game_frame_list) != 0:
                for frame in queue_game_frame_list:
                        if frame.get_name() == game_name:
                            frame.destroy()

            self.mylib_create_queue_tab_content(game_name)
            mylib_installation_queue.append(game_name)

        else:

            message_dialog = Gtk.MessageDialog(
                self.main_window,
                0,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO
                )
            message_dialog.format_secondary_text(_("Are you sure you want to remove\n'") +
            self.mylib_dict_name_to_title[game_name] + "'?")
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('spacing', 10)

            content_area_label = content_area.get_children()[0].get_children()[0].get_children()[1]
            content_area_label.set_property('justify', Gtk.Justification.CENTER)

            message_dialog_response = message_dialog.run()

            if message_dialog_response == Gtk.ResponseType.YES:

                os.system('rm -R -f ' + self.mylib_install_dir + '/' + game_name)

                dosbox_game_path = os.getenv('HOME') + '/.games_nebula/games/.dosbox/' + game_name
                os.system('rm -R -f ' + dosbox_game_path)
                wine_game_path = os.getenv('HOME') + '/.games_nebula/wine_prefix/drive_c/Games/' + game_name
                os.system('rm -R -f ' + wine_game_path)

                if os.path.exists(data_dir + '/scripts/mylib/' + game_name + '/uninstall'):
                    self.set_environ(game_name, self.mylib_download_dir, self.mylib_install_dir)
                    uninstall_command = (data_dir + '/scripts/mylib/' + game_name + '/uninstall')
                    os.system(uninstall_command)

                button.set_label(_("Install"))

                for button in mylib_launch_buttons_list:
                    if button.get_name() == game_name:
                        button.set_sensitive(False)

                self.cb_combobox_mylib_status(self.combobox_mylib_status)

            message_dialog.destroy()

    def goglib_setup_game(self, button):

        game_name = button.get_name()

        if not os.path.exists(self.goglib_install_dir + '/' + game_name + '/start.sh'):

            if len(goglib_installation_queue) == 0:
                button.set_label(_("Installing"))
            else:
                button.set_label(_("In queue"))
            button.set_sensitive(False)

            if len(queue_game_frame_list) != 0:
                for frame in queue_game_frame_list:
                        if frame.get_name() == game_name:
                            frame.destroy()

            self.create_queue_tab_content(game_name)
            goglib_installation_queue.append(game_name)

        else:

            message_dialog = Gtk.MessageDialog(
                self.main_window,
                0,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                )
            message_dialog.format_secondary_text(_("Are you sure you want to remove\n'") +
            self.goglib_dict_name_to_title[game_name] + "'?")
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('spacing', 10)

            content_area_label = content_area.get_children()[0].get_children()[0].get_children()[1]
            content_area_label.set_property('justify', Gtk.Justification.CENTER)

            message_dialog_response = message_dialog.run()

            if message_dialog_response == Gtk.ResponseType.YES:

                os.system('rm -R -f ' + self.goglib_install_dir + '/' + game_name)

                dosbox_game_path = os.getenv('HOME') + '/.games_nebula/games/.dosbox/' + game_name
                os.system('rm -R -f ' + dosbox_game_path)
                wine_game_path = os.getenv('HOME') + '/.games_nebula/wine_prefix/drive_c/Games/' + game_name
                os.system('rm -R -f ' + wine_game_path)

                if os.path.exists(data_dir + '/scripts/goglib/' + game_name + '/uninstall'):

                    self.set_environ(game_name, self.goglib_download_dir, self.goglib_install_dir)

                    uninstall_command = (data_dir + '/scripts/goglib/' + game_name + '/uninstall')
                    os.system(uninstall_command)

                button.set_label(_("Install"))

                for button in goglib_launch_buttons_list:
                    if button.get_name() == game_name:
                        button.set_sensitive(False)

                self.cb_combobox_goglib_status(self.combobox_goglib_status)

            message_dialog.destroy()

            if self.goglib_offline_mode:

                available_distrs = os.listdir(self.goglib_download_dir)

                if game_name not in available_distrs:
                    self.goglib_available_games.remove(game_name)

                self.update_goglib_grid()

    def goglib_download_game(self, game_name):

        if self.goglib_offline_mode:
            self.goglib_unpack_game(goglib_installation_queue[0])

        else:

            if not self.queue_tab_exists():
                self.append_queue_tab()

            self.progressbar_goglib.set_text(_("Downloading..."))

            if not os.path.exists(self.goglib_download_dir + '/' +  game_name):
                    os.makedirs(self.goglib_download_dir + '/' +  game_name)

            self.preferred_language = self.lang_index[self.goglib_lang]

            if self.goglib_download_extras == False:
                command = ['lgogdownloader', '--download', '--ignore-dlc-count', '--platform', '4,1', \
                            '--language', self.preferred_language + ',1,', '--game', game_name + '$', \
                            '--directory=' + self.goglib_download_dir + '/', '--exclude', '2,4,16']
            elif self.goglib_download_extras == True:
                command = ['lgogdownloader', '--download', '--ignore-dlc-count', '--platform', '4,1', \
                            '--language', self.preferred_language + ',1,', '--game', game_name + '$', \
                            '--directory=' + self.goglib_download_dir + '/', '--exclude', '4,16']

            goglib_name_to_pid_download_dict[game_name], stdin, stdout, stderr = GLib.spawn_async(command,
                    flags=GLib.SpawnFlags.SEARCH_PATH|GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                    standard_output=True,
                    standard_error=True)

            io = GLib.IOChannel(stdout)

            self.source_id_out = io.add_watch(GLib.IO_IN|GLib.IO_HUP,
                                    self.watch_process,
                                    'goglib_download_game',
                                    priority=GLib.PRIORITY_HIGH)

    def mylib_install_game(self, game_name):

        if not self.queue_tab_exists():
            self.append_queue_tab()

        if not os.path.exists(self.mylib_install_dir):
            os.makedirs(self.mylib_install_dir)

        game_dir = self.mylib_install_dir + '/' + game_name

        if not os.path.exists(game_dir):
            os.makedirs(game_dir)

        self.mylib_tab_progressbar.set_text(_("Installing..."))

        self.set_environ(game_name, self.mylib_download_dir, self.mylib_install_dir)
        os.environ['KEEP_INSTALLERS'] = str(self.mylib_keep_installers)
        autosetup.autosetup('mylib', self.mylib_install_dir, game_name)

        settings_py_path = os.getenv('HOME') + '/.games_nebula/scripts/mylib/' + game_name + '/settings.py'
        if os.path.exists(settings_py_path):
            os.system('cp ' + settings_py_path + ' ' + game_dir)
            os.system('echo "Writing settings.sh"')
            settings_lines = ['#!/bin/bash\n',
            'python "$INSTALL_DIR/' + game_name + '/settings.py"']
            settings_file = open(game_dir + '/settings.sh', 'w')
            for line in settings_lines:
                settings_file.write(line)
            settings_file.close()
            os.system('chmod +x ' + game_dir + '/settings.sh')

        if self.own_prefix:
            config_file = open(game_dir + '/config.ini', 'w')
            config_file.write('[Settings]\n')
            config_file.write('own_prefix = True')
            config_file.close()

        command = [data_dir + '/scripts/mylib/' + game_name + '/setup']

        mylib_name_to_pid_install_dict[game_name], stdin, stdout, stderr = GLib.spawn_async(command,
                flags=GLib.SpawnFlags.SEARCH_PATH|GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                standard_output=True,
                standard_error=True)

        io = GLib.IOChannel(stdout)

        self.source_id_out = io.add_watch(GLib.IO_IN|GLib.IO_HUP,
                                 self.watch_process,
                                 'mylib_install_game',
                                 priority=GLib.PRIORITY_HIGH)

    def goglib_unpack_game(self, game_name):

        if not self.queue_tab_exists():
            self.append_queue_tab()

        if not os.path.exists(self.goglib_install_dir):
            os.makedirs(self.goglib_install_dir)

        if not os.path.exists(self.goglib_install_dir + '/' + game_name):
            os.makedirs(self.goglib_install_dir + '/' + game_name)

        self.progressbar_goglib.set_text(_("Installing..."))

        files_list = os.listdir(self.goglib_download_dir + '/' + game_name)
        files_list = sorted(files_list)

        self.installer_type = 'none'
        number_of_installers = 0
        versions = []

        for line in files_list:

            if '.sh' in line:
                self.installer_type = 'sh'
                versions.append(line)
                number_of_installers += 1
            elif '.exe' in line:
                self.installer_type = 'exe'
                versions.append(line)
                number_of_installers += 1

        versions = sorted(versions)

        if number_of_installers > 0:

            if self.installer_type == 'sh':
                command = ['unzip', '-o', \
                        self.goglib_download_dir + '/' + game_name + '/' + versions[-1], \
                        '-d', self.goglib_install_dir + '/' + game_name + '/tmp']

            elif self.installer_type == 'exe':
                command = ['innoextract', '--gog', \
                        self.goglib_download_dir + '/' + game_name + '/' + versions[-1], \
                        '-d', self.goglib_install_dir + '/' + game_name + '/tmp']

        elif number_of_installers == 0:
            self.goglib_install_game(goglib_installation_queue[0])
            return

        goglib_name_to_pid_unpack_dict[game_name], stdin, stdout, stderr = GLib.spawn_async(command,
                flags=GLib.SpawnFlags.SEARCH_PATH|GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                standard_output=True,
                standard_error=True)

        io = GLib.IOChannel(stdout)

        self.source_id_out = io.add_watch(GLib.IO_IN|GLib.IO_HUP,
                                 self.watch_process,
                                 'goglib_unpack_game',
                                 priority=GLib.PRIORITY_HIGH)

    def goglib_install_game(self, game_name):

        setup_sctipt_exists = os.path.exists(data_dir + '/scripts/goglib/' + game_name + '/setup')

        if not self.queue_tab_exists():
            self.append_queue_tab()

        if self.installer_type == 'sh':

            game_dir = self.goglib_install_dir + '/' + game_name
            files_path = game_dir + '/tmp/data/noarch/'
            files_to_move = os.listdir(files_path)

            files_to_move_lower = [file_name.lower() for file_name in files_to_move]

            if 'dosbox' in files_to_move_lower:

                files_path = game_dir + '/tmp/data/noarch/data/'
                files_to_move = os.listdir(files_path)
                os.system('mv ' + game_dir + '/tmp/data/noarch/*_single.conf ' +
                game_dir + '/dosbox_game.conf')

                if '_settings.conf' in ' '.join(files_to_move):
                    settings_conf_exists = True
                    os.system('mv ' + game_dir + '/tmp/data/noarch/*_settings.conf ' +
                    game_dir + '/dosbox_settings.conf')
                else:
                    settings_conf_exists = False

                def update_conf_file(file_path):

                    file_to_change = open(file_path, 'r')
                    file_content = file_to_change.readlines()
                    file_to_change.close()

                    c_mount_command = 'mount c ' + os.getenv('HOME') + \
                    '/.games_nebula/games/.dosbox/' + game_name + '\n'
                    d_imgmount_command = 'imgmount d ' + os.getenv('HOME') + \
                    '/.games_nebula/games/.dosbox/' + game_name + '/'
                    d_mount_command = 'mount d ' + os.getenv('HOME') + \
                    '/.games_nebula/games/.dosbox/' + game_name + '/'

                    for i in range(len(file_content)):
                        if 'mount c' in file_content[i].lower():
                            file_content[i] = c_mount_command + 'c:\n'

                        if 'imgmount d' in file_content[i].lower():
                            tmp_list = file_content[i].split(' ')[2:]
                            tmp_list[0] = tmp_list[0].strip('"\\.')
                            iso = ' '.join(tmp_list)
                            if tmp_list[0] not in files_to_move:
                                iso = iso.lower()
                            file_content[i] = d_imgmount_command + iso + 'cls\n'
                        elif 'mount d' in file_content[i].lower():
                            tmp_list = file_content[i].split(' ')[2:]
                            tmp_list[0] = tmp_list[0].strip('"\\.')
                            data_dir = ' '.join(tmp_list)
                            if tmp_list[0] not in files_to_move:
                                data_dir = data_dir.lower()
                            file_content[i] = d_mount_command + data_dir + 'cls\n'

                    file_to_change = open(file_path, 'w')
                    for line in file_content:
                        file_to_change.write(line)
                    file_to_change.close()

                update_conf_file(game_dir + '/dosbox_game.conf')
                if settings_conf_exists:
                    update_conf_file(game_dir + '/dosbox_settings.conf')

                start_lines = ['#!/bin/bash\n',
                'python "$NEBULA_DIR/launcher_dosbox.py" ' + game_name]

                start_file = open(game_dir + '/start.sh', 'w')
                for line in start_lines:
                    start_file.write(line)
                start_file.close()
                os.system('chmod +x ' + game_dir + '/start.sh')

                os.system('mkdir -p ' + game_dir + '/game')
                command = []
                for f in files_to_move:
                    command.extend(('mv', files_path + f, game_dir + '/game'))

            elif 'scummvm' in files_to_move_lower:

                for file_name in files_to_move:
                    if '.ini' in file_name.lower():
                        ini_file = file_name
                        scummvm_name = file_name.split('.')[0].lower()

                files_path = game_dir + '/tmp/data/noarch/data/'
                files_to_move = os.listdir(files_path)

                os.system('mv ' + game_dir + '/tmp/data/noarch/' + ini_file +
                ' ' + game_dir + '/scummvmrc')

                start_lines = ['#!/bin/bash\n',
                'python "$NEBULA_DIR/launcher_scummvm.py" ' + game_name + ' ' + scummvm_name]

                start_file = open(game_dir + '/start.sh', 'w')
                for line in start_lines:
                    start_file.write(line)
                start_file.close()
                os.system('chmod +x ' + game_dir + '/start.sh')

                os.system('mkdir -p ' + game_dir + '/game')
                command = []
                for f in files_to_move:
                    command.extend(('mv', files_path + f, game_dir + '/game'))

            else:

                command = []
                for f in files_to_move:
                    command.extend(('mv', files_path + f, game_dir))

        elif self.installer_type == 'exe':

            game_dir = self.goglib_install_dir + '/' + game_name
            tmp_game_path = game_dir + '/tmp/game/'
            tmp_app_path = game_dir + '/tmp/app/'

            tmp_game_files_n = 0
            if os.path.exists(tmp_game_path):
                tmp_game_files = os.listdir(tmp_game_path)
                tmp_game_files_n = len(tmp_game_files)

            tmp_app_files_n = 0
            if os.path.exists(tmp_app_path):
                tmp_app_files = os.listdir(tmp_app_path)
                tmp_app_files_n = len(tmp_app_files)

            if tmp_game_files_n > tmp_app_files_n:
                files_path = tmp_game_path
                files_to_move = list(tmp_game_files)
                game_data_dir = '/tmp/game/'
            else:
                files_path = tmp_app_path
                files_to_move = list(tmp_app_files)
                game_data_dir = '/tmp/app/'

            files_to_move_lower = [file_name.lower() for file_name in files_to_move]

            if 'dosbox' in files_to_move_lower:
                os.system('mv ' + game_dir + game_data_dir + '*_single.conf ' +
                game_dir + '/dosbox_game.conf')

                if '_settings.conf' in ' '.join(files_to_move):
                    settings_conf_exists = True
                    os.system('mv ' + game_dir + game_data_dir + '*_settings.conf ' +
                    game_dir + '/dosbox_settings.conf')
                else:
                    settings_conf_exists = False

                def update_conf_file(file_path):

                    file_to_change = open(file_path, 'r')
                    file_content = file_to_change.readlines()
                    file_to_change.close()

                    c_mount_command = 'mount c ' + os.getenv('HOME') + \
                    '/.games_nebula/games/.dosbox/' + game_name + '\n'
                    d_imgmount_command = 'imgmount d ' + os.getenv('HOME') + \
                    '/.games_nebula/games/.dosbox/' + game_name + '/'
                    d_mount_command = 'mount d ' + os.getenv('HOME') + \
                    '/.games_nebula/games/.dosbox/' + game_name + '/'

                    for i in range(len(file_content)):
                        if 'mount c' in file_content[i].lower():
                            file_content[i] = c_mount_command + 'c:\n'

                        if 'imgmount d' in file_content[i].lower():
                            tmp_list = file_content[i].split(' ')[2:]
                            tmp_list[0] = tmp_list[0].strip('"\\.')
                            iso = ' '.join(tmp_list)
                            if tmp_list[0] not in files_to_move:
                                iso = iso.lower()
                            file_content[i] = d_imgmount_command + iso + 'cls\n'
                        elif 'mount d' in file_content[i].lower():
                            tmp_list = file_content[i].split(' ')[2:]
                            tmp_list[0] = tmp_list[0].strip('"\\.')
                            data_dir = ' '.join(tmp_list)
                            if tmp_list[0] not in files_to_move:
                                data_dir = data_dir.lower()
                            file_content[i] = d_mount_command + data_dir + 'cls\n'

                    file_to_change = open(file_path, 'w')
                    for line in file_content:
                        file_to_change.write(line)
                    file_to_change.close()

                update_conf_file(game_dir + '/dosbox_game.conf')
                if settings_conf_exists:
                    update_conf_file(game_dir + '/dosbox_settings.conf')

                start_lines = ['#!/bin/bash\n',
                'python "$NEBULA_DIR/launcher_dosbox.py" ' + game_name]

                start_file = open(game_dir + '/start.sh', 'w')
                for line in start_lines:
                    start_file.write(line)
                start_file.close()
                os.system('chmod +x ' + game_dir + '/start.sh')

            elif 'scummvm' in files_to_move_lower:

                for file_name in files_to_move:
                    if '.ini' in file_name.lower():
                        ini_file = file_name
                        scummvm_name = file_name.split('.')[0].lower()

                os.system('mv ' + game_dir + game_data_dir + ini_file + ' ' +
                game_dir + '/scummvmrc')

                start_lines = ['#!/bin/bash\n',
                'python "$NEBULA_DIR/launcher_scummvm.py" ' + game_name + ' ' + scummvm_name]

                start_file = open(game_dir + '/start.sh', 'w')
                for line in start_lines:
                    start_file.write(line)
                start_file.close()
                os.system('chmod +x ' + game_dir + '/start.sh')

            else:

                if self.own_prefix:
                    config_file = open(game_dir + '/config.ini', 'w')
                    config_file.write('[Settings]\n')
                    config_file.write('own_prefix = True')
                    config_file.close()

                files_in_game_dir = os.listdir(game_dir + game_data_dir)
                n_exe = 0
                for file_name in files_in_game_dir:
                    if '.exe' in file_name.lower():
                        exe_name =  '"' + file_name + '"'
                        n_exe += 1
                if n_exe != 1:
                    exe_name = 'NOEXE'

                start_lines = ['#!/bin/bash\n',
                'python "$NEBULA_DIR/launcher_wine.py" ' + game_name + ' ' + exe_name]
                start_file = open(game_dir + '/start.sh', 'w')
                for line in start_lines:
                    start_file.write(line)
                start_file.close()
                os.system('chmod +x ' + game_dir + '/start.sh')

            os.system('mkdir -p ' + game_dir + '/game')
            command = []
            for f in files_to_move:
                command.extend(('mv', files_path + f, game_dir + '/game'))

        else:
            if not os.path.exists(data_dir + '/scripts/goglib/' + game_name + '/setup'):

                message_dialog = Gtk.MessageDialog(
                    self.main_window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    _("Error")
                    )
                message_dialog.format_secondary_text(_("Impossible to install."))
                message_dialog.set_property('default-width', 480)
                content_area = message_dialog.get_content_area()
                content_area.set_property('margin-left', 10)
                content_area.set_property('margin-right', 10)
                content_area.set_property('margin-top', 10)
                content_area.set_property('margin-bottom', 10)
                action_area = message_dialog.get_action_area()
                action_area.set_property('spacing', 10)

                message_dialog.run()
                message_dialog.destroy()

                os.system('rm -R -f ' + self.goglib_install_dir + '/' + game_name)
                command = ['echo', 'Impossible to install']

            else:
                command = ['echo', 'Running script...']

        settings_py_path = os.getenv('HOME') + '/.games_nebula/scripts/goglib/' + game_name + '/settings.py'
        if os.path.exists(settings_py_path):
            os.system('cp ' + settings_py_path + ' ' + game_dir)
            os.system('echo "Writing settings.sh"')
            settings_lines = ['#!/bin/bash\n',
            'python "$INSTALL_DIR/' + game_name + '/settings.py"']
            settings_file = open(game_dir + '/settings.sh', 'w')
            for line in settings_lines:
                settings_file.write(line)
            settings_file.close()
            os.system('chmod +x ' + game_dir + '/settings.sh')

        goglib_name_to_pid_install_dict[game_name], stdin, stdout, stderr = GLib.spawn_async(command,
                flags=GLib.SpawnFlags.SEARCH_PATH|GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                standard_output=True,
                standard_error=True)

        io = GLib.IOChannel(stdout)

        self.source_id_out = io.add_watch(GLib.IO_IN|GLib.IO_HUP,
                                 self.watch_process,
                                 'goglib_install_game',
                                 priority=GLib.PRIORITY_HIGH)

    def run_goglib_setup_script(self, game_name):

        self.progressbar_goglib.set_text(_("Executing script..."))

        self.set_environ(game_name, self.goglib_download_dir, self.goglib_install_dir)

        command = [data_dir + '/scripts/goglib/' + game_name + '/setup']

        goglib_name_to_pid_install_dict[game_name], stdin, stdout, stderr = GLib.spawn_async(command,
                flags=GLib.SpawnFlags.SEARCH_PATH|GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                standard_output=True,
                standard_error=True)

        io = GLib.IOChannel(stdout)

        self.source_id_out = io.add_watch(GLib.IO_IN|GLib.IO_HUP,
                                 self.watch_process,
                                 'run_goglib_setup_script',
                                 priority=GLib.PRIORITY_HIGH)

    def watch_process(self, io, condition, process_name):

        if condition is GLib.IO_HUP:

            if process_name == 'goglib_download_game':
                game_name = goglib_installation_queue[0]
                GLib.source_remove(self.source_id_out)
                #GLib.source_remove(self.source_id_err)

                if self.download_canceled == False:

                    self.goglib_unpack_game(game_name)

                    for downloads_game_status in queue_game_status_list:
                        if downloads_game_status.get_name() == game_name:
                            downloads_game_status.set_label(' ')

                    del goglib_name_to_pid_download_dict[game_name]

                else:
                    del goglib_name_to_pid_download_dict[game_name]
                    del goglib_installation_queue[0]
                    self.goglib_now_installing = None
                    self.download_canceled = False

                return False

            if process_name == 'goglib_unpack_game':
                game_name = goglib_installation_queue[0]
                GLib.source_remove(self.source_id_out)

                if self.unpack_canceled == False:

                    #GLib.source_remove(self.source_id_out)
                    #GLib.source_remove(self.source_id_err)

                    self.goglib_install_game(game_name)

                    del goglib_name_to_pid_unpack_dict[game_name]

                else:
                    del goglib_name_to_pid_unpack_dict[game_name]
                    del goglib_installation_queue[0]
                    self.goglib_now_installing = None
                    self.unpack_canceled = False

                return False

            if process_name == 'goglib_install_game':
                game_name = goglib_installation_queue[0]
                GLib.source_remove(self.source_id_out)
                #GLib.source_remove(self.source_id_err)

                self.set_environ(game_name, self.goglib_download_dir, self.goglib_install_dir)
                autosetup.autosetup('goglib', self.goglib_install_dir, game_name)

                if os.path.exists(data_dir + '/scripts/goglib/' + game_name + '/setup'):
                    self.run_goglib_setup_script(game_name)
                else:
                    game_dir = self.goglib_install_dir + '/' + game_name
                    start_file_path = game_dir + '/start.sh'
                    dosbox_game_conf_path = game_dir + '/dosbox_game.conf'
                    scummvmrc_path = game_dir + '/scummvmrc'

                    if (self.installer_type == 'sh') and \
                            (not os.path.exists(dosbox_game_conf_path)) and \
                            (not os.path.exists(scummvmrc_path)):

                        is_wine_wrapper = False
                        game_dir_content = os.listdir(game_dir + '/game')
                        for file_name in game_dir_content:
                            if '.exe' in file_name.lower():
                                is_wine_wrapper = True

                        if not is_wine_wrapper:

                            start_gog_path = game_dir + '/start_gog.sh'
                            if not os.path.exists(start_gog_path):
                                os.system('mv ' + start_file_path + ' ' + start_gog_path)

                            start_lines = ['#!/bin/bash\n',
                            'python "$NEBULA_DIR/launcher_native.py" ' + game_name]

                            start_file = open(start_file_path, 'w')
                            for line in start_lines:
                                start_file.write(line)
                            start_file.close()
                            os.system('chmod +x ' + start_file_path)

                    for progress_bar in queue_progress_bars_list:
                        if progress_bar.get_name() == game_name:
                            progress_bar.set_fraction(1)
                            progress_bar.set_text(_("Done"))

                    #Destroy frame when finished
                    #~ for frame in queue_game_frame_list:
                       #~ if frame.get_name() == game_name:
                           #~ frame.destroy()

                    os.system('rm -R -f ' + self.goglib_install_dir + '/' + game_name + '/tmp')

                    if self.goglib_keep_installers == False:
                        os.system('rm -R -f ' + self.goglib_download_dir + '/' + game_name)

                    self.update_queue_banners()

                    del goglib_name_to_pid_install_dict[game_name]
                    del goglib_installation_queue[0]

                    self.cb_combobox_goglib_status(self.combobox_goglib_status)

                    self.goglib_now_installing = None

                return False

            if process_name == 'run_goglib_setup_script':
                game_name = goglib_installation_queue[0]
                GLib.source_remove(self.source_id_out)
                #GLib.source_remove(self.source_id_err)

                for progress_bar in queue_progress_bars_list:
                    if progress_bar.get_name() == game_name:
                        progress_bar.set_fraction(1)
                        progress_bar.set_text(_("Done"))

                #Destroy frame when finished
                #~ for frame in queue_game_frame_list:
                   #~ if frame.get_name() == game_name:
                       #~ frame.destroy()

                os.system('rm -R -f ' + self.goglib_install_dir + '/' + game_name + '/tmp')

                if self.goglib_keep_installers == False:
                    os.system('rm -R -f ' + self.goglib_download_dir + '/' + game_name)

                self.update_queue_banners()

                del goglib_name_to_pid_install_dict[game_name]
                del goglib_installation_queue[0]

                self.cb_combobox_goglib_status(self.combobox_goglib_status)

                self.goglib_now_installing = None

                return False

            if process_name == 'mylib_install_game':
                game_name = mylib_installation_queue[0]
                GLib.source_remove(self.source_id_out)
                #GLib.source_remove(self.source_id_err)

                for progress_bar in queue_progress_bars_list:
                    if progress_bar.get_name() == game_name:
                        progress_bar.set_fraction(1)
                        progress_bar.set_text(_("Done"))

                if self.mylib_keep_installers == False:
                    if os.path.exists(self.mylib_download_dir + '/' + game_name):
                        os.system('rm -R -f ' + self.mylib_download_dir + '/' + game_name)

                self.update_queue_banners()

                del mylib_name_to_pid_install_dict[game_name]
                del mylib_installation_queue[0]

                self.cb_combobox_mylib_status(self.combobox_mylib_status)

                self.mylib_now_installing = None

                return False

            if process_name == 'check_for_new_games':

                self.box_action_widgets_end.remove(self.spinner_update)
                self.box_action_widgets_end.pack_end(self.button_update_goglib, True, True, 0)

                if len(self.goglib_new_games_list) == 0:

                    message_dialog = Gtk.MessageDialog(
                        self.main_window,
                        0,
                        Gtk.MessageType.INFO,
                        Gtk.ButtonsType.OK,
                        _("No new games in library.")
                        )
                    content_area = message_dialog.get_content_area()
                    content_area.set_property('margin-left', 10)
                    content_area.set_property('margin-right', 10)
                    content_area.set_property('margin-top', 10)
                    content_area.set_property('margin-bottom', 10)
                    message_dialog.run()
                    message_dialog.destroy()

                GLib.source_remove(self.source_id_out)
                return False

            if process_name == 'update_goglib':
                GLib.source_remove(self.source_id_out)

                # FIX Workaround for situation when lgogdownloader return 'Unable to read...'
                if len(self.goglib_updated_games_list) > 1:

                    updated_file = open(config_dir + '/games_list', 'w')
                    for line in self.goglib_updated_games_list:
                        updated_file.write(line)
                    updated_file.close()

                    self.config_save()
                    os.execl(sys.executable, sys.executable, *sys.argv)

                return False

        line = io.readline()

        if (process_name != 'check_for_new_games' ) and (process_name != 'update_goglib'):
            try:
                print(line.translate(None, '\n'))
            except:
                char_map = str.maketrans('', '', '\n')
                print(line.translate(char_map))

        if self.goglib_page_exists():
            self.progressbar_goglib.pulse()
        if self.mylib_page_exists():
            self.mylib_tab_progressbar.pulse()

        if process_name == 'goglib_download_game':

            if '%' in line:
                mb_downloaded = line.split('@')[0].split(' ')[-2]
                speed = line.split('@')[1].split(' ')[1]
                try:
                    eta = line.split('@')[1].split(' ')[3].translate(None, '\n')
                except:
                    char_map = str.maketrans('', '', '\n')
                    eta = line.split('@')[1].split(' ')[3].translate(char_map)

                try:
                    percentage = line.split('%', 1)[0].translate(None, ' %\n')
                except:
                    char_map = str.maketrans('', '', '%\n')
                    percentage = line.split('%', 1)[0].translate(char_map)

                for progress_bar in queue_progress_bars_list:
                    if progress_bar.get_name() == goglib_installation_queue[0]:
                        progress_bar.set_fraction((float(percentage))/100)
                        progress_bar.set_text(_("Downloading..."))

                for downloads_game_status in queue_game_status_list:
                    if downloads_game_status.get_name() == goglib_installation_queue[0]:
                        downloads_game_status.set_label(
                        "Downloaded: " + mb_downloaded + \
                        " Speed: " + speed + \
                        " ETA: " + eta
                        )

        if process_name == 'goglib_unpack_game':

            for progress_bar in queue_progress_bars_list:
                    if progress_bar.get_name() == goglib_installation_queue[0]:
                        progress_bar.pulse()
                        progress_bar.set_text(_("Installing..."))

        if process_name == 'goglib_install_game':

            for progress_bar in queue_progress_bars_list:
                    if progress_bar.get_name() == goglib_installation_queue[0]:
                        progress_bar.pulse()
                        progress_bar.set_text(_("Installing..."))

        if process_name == 'run_goglib_setup_script':

            for progress_bar in queue_progress_bars_list:
                    if progress_bar.get_name() == goglib_installation_queue[0]:
                        progress_bar.pulse()
                        progress_bar.set_text(_("Executing script..."))

        if process_name == 'mylib_install_game':

            for progress_bar in queue_progress_bars_list:
                    if progress_bar.get_name() == mylib_installation_queue[0]:
                        progress_bar.set_text(_("Installing..."))
                        progress_bar.pulse()
                        progress_bar.set_pulse_step(0.1)

        if process_name == 'check_for_new_games':
            if '\n' in line:
                try:
                    game_name = line.split(' ')[0].translate(None, '\n')
                except:
                    char_map = str.maketrans('', '', '\n')
                    game_name = line.split(' ')[0].translate(char_map)
                if '\x1b[32m' in game_name:
                    game_name = game_name.split('\x1b[32m')[1]
                if  game_name not in self.goglib_games_list:
                    self.goglib_new_games_list.append(game_name)

        if process_name == 'update_goglib':
            self.goglib_updated_games_list.append(line)

        while Gtk.events_pending():
            Gtk.main_iteration_do(False)

        return True

    def cb_radiobutton_wine_settings(self, button):
        if button.get_name() == 'system':
            self.radiobutton_wine_settings_dir.set_label(_("From directory"))
            self.filechooserbutton_wine.set_visible(False)
            self.combobox_wine_version.set_visible(False)
            self.wine = 'system'
        else:
            self.radiobutton_wine_settings_dir.set_label(_("From directory:"))
            self.filechooserbutton_wine.set_visible(True)
            self.combobox_wine_version.set_visible(True)
            self.wine = 'path'
        self.win64_available()

    def cb_checkbutton_own_prefix(self, checkbutton):
        self.own_prefix = checkbutton.get_active()

    def cb_button_wine_settings(self, button):

        self.main_window.hide()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        if self.wine == 'system':
            os.environ['WINELOADER'] = 'wine'
        elif self.wine == 'path':
            wine_path = self.wine_path + '/' + self.wine_version
            os.environ['WINE'] = wine_path + '/bin/wine'
            os.environ['WINELOADER'] = wine_path + '/bin/wine'
            os.environ['WINESERVER'] = wine_path + '/bin/wineserver'
            os.environ['WINEDLLPATH'] = wine_path + '/lib'

        os.environ['WINEPREFIX'] = os.getenv('HOME') + '/.games_nebula/wine_prefix'

        os.system('python ' + nebula_dir + '/settings_wine.py')

        self.main_window.show()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.show()

    def cb_button_winetricks_cache(self, button):

        self.main_window.hide()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        os.system(sys.executable + ' ' + nebula_dir + '/winetricks_cache_backup.py')

        self.main_window.show()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.show()

    def cb_button_scummvm_settings(self, button):

        self.main_window.hide()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        if self.scummvm == 'path':
            self.scummvm_dir = self.scummvm_path + '/' + self.scummvm_version + '/bin'
            os.system(self.scummvm_dir + '/scummvm -F -c ' + config_dir + '/scummvmrc')
        if self.scummvm == 'system':
            os.system('scummvm -F -c ' + config_dir + '/scummvmrc')

        self.main_window.show()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.show()

    def cb_checkbutton_scripts_overwrite(self, checkbutton):
        if checkbutton.get_name() == 'goglib':
            self.goglib_scripts_overwrite = checkbutton.get_active()
        elif checkbutton.get_name() == 'mylib':
            self.mylib_scripts_overwrite = checkbutton.get_active()

    def cb_button_get_scripts(self, button):

        lib = button.get_name()

        if lib == 'goglib':
            overwrite = self.checkbutton_goglib_scripts.get_active()
        elif lib == 'mylib':
            overwrite = self.checkbutton_mylib_scripts.get_active()

        self.main_window.hide()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        mylib_has_new_scripts = os.system('python ' + nebula_dir + '/get_scripts.py ' + lib + ' ' + str(overwrite))

        # Ugly but works
        if mylib_has_new_scripts == 0:
            print("No new scripts.")
        else:
            print("New scripts downloaded!")
            os.execl(sys.executable, sys.executable, *sys.argv)

        self.main_window.show()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.show()

    def cb_button_dosbox_settings(self, button):

        self.main_window.hide()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        if self.dosbox == 'system':
            dosbox_bin = 'dosbox'
        elif self.dosbox == 'path':
            dosbox_bin = self.dosbox_path + '/' + self.dosbox_version + '/bin/dosbox'

        dosbox_version = self.check_dosbox_version(dosbox_bin)

        dosbox_global_config = os.getenv('HOME') + '/.games_nebula/config/dosbox.conf'

        os.system('python ' + nebula_dir + '/settings_dosbox.py ' \
        + dosbox_global_config + ' global ' + dosbox_version)

        # TODO Use if special config tool for svn-daum build exists (settings_dosbox_svn_daum.py)
        #~ if (dosbox_version == 'stable') or (dosbox_version == 'svn'):
            #~ os.system('python ' + nebula_dir + '/settings_dosbox.py ' + \
            #~ dosbox_global_config + ' global ' + dosbox_version)
        #~ elif dosbox_version == 'svn_daum':
            #~ os.system('python ' + nebula_dir + '/dosbox_settings_svn_daum.py ' + \
            #~ dosbox_global_config + ' global ' + dosbox_version)

        self.main_window.show()
        if len(self.additional_windows_list) != 0:
            for window in self.additional_windows_list:
                window.show()

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

    def cb_radiobutton_dosbox_settings(self, button):
        if button.get_name() == 'system':
            self.radiobutton_dosbox_settings_dir.set_label(_("From directory"))
            self.filechooserbutton_dosbox.set_visible(False)
            self.combobox_dosbox_version.set_visible(False)
            self.dosbox = 'system'
        else:
            self.radiobutton_dosbox_settings_dir.set_label(_("From directory:"))
            self.filechooserbutton_dosbox.set_visible(True)
            self.combobox_dosbox_version.set_visible(True)
            self.dosbox = 'path'

    def cb_radiobutton_scummvm_settings(self, button):
        if button.get_name() == 'system':
            self.radiobutton_scummvm_settings_dir.set_label(_("From directory"))
            self.filechooserbutton_scummvm.set_visible(False)
            self.combobox_scummvm_version.set_visible(False)
            self.scummvm = 'system'
        else:
            self.radiobutton_scummvm_settings_dir.set_label(_("From directory:"))
            self.filechooserbutton_scummvm.set_visible(True)
            self.combobox_scummvm_version.set_visible(True)
            self.scummvm = 'path'

    def cb_combobox_wine_version(self, combobox):
        self.wine_version = combobox.get_active_text()
        self.win64_available()

    def cb_combobox_dosbox_version(self, combobox):
        self.dosbox_version = combobox.get_active_text()

    def cb_combobox_scummvm_version(self, combobox):
        self.scummvm_version = combobox.get_active_text()

    def cb_switch_goglib_tab_at_start(self, switch, event):

        self.goglib_tab_at_start = switch.get_active()

        if switch.get_active() == False:
            self.switch_mylib_tab_at_start.set_active(True)
            self.switch_mylib_tab_at_start.set_sensitive(False)
        else:
            self.switch_mylib_tab_at_start.set_sensitive(True)

    def cb_switch_mylib_tab_at_start(self, switch, event):

        self.mylib_tab_at_start = switch.get_active()

    def cb_switch_gogcom_tab_at_start(self, switch, event):
        self.gogcom_tab_at_start = switch.get_active()

    def cb_switch_queue_tab_at_start(self, switch, event):
        self.queue_tab_at_start = switch.get_active()

    def cb_switch_settings_tab_at_start(self, switch, event):
        self.settings_tab_at_start = switch.get_active()

    def cb_filechooserbutton_goglib_download_dir(self, button):
        self.goglib_download_dir = button.get_filename()

    def cb_filechooserbutton_goglib_install_dir(self, button):

        new_goglib_install_dir = button.get_filename()

        if new_goglib_install_dir != self.goglib_install_dir:

            message_dialog = Gtk.MessageDialog(
                self.main_window,
                0,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                _("Installation directory changed")
                )
            message_dialog.format_secondary_text(_("Do you really want to change installation directory?\n" + \
                "All your installed games will be moved to the new location.\nProceed?"))
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('spacing', 10)

            message_dialog_response = message_dialog.run()

            if message_dialog_response == Gtk.ResponseType.YES:

                os.system('mv -f ' + self.goglib_install_dir + '/* ' + \
                new_goglib_install_dir + ' && rmdir ' + self.goglib_install_dir)

                os.system('rm ' + new_goglib_install_dir + '/*/.configured > /dev/null 2>&1')

                self.goglib_install_dir = new_goglib_install_dir

            elif message_dialog_response == Gtk.ResponseType.NO:

                button.set_filename(self.goglib_install_dir)

            message_dialog.destroy()

        #~ self.goglib_status_filter_list = []
        #~ for game_name in self.goglib_games_list:
           #~ if os.path.exists(self.goglib_install_dir + '/' + game_name + '/start.sh'):
               #~ self.goglib_status_filter_list.append(game_name)
        #~ self.goglib_apply_filters()

    def cb_filechooserbutton_mylib_download_dir(self, button):
        self.mylib_download_dir = button.get_filename()

    def cb_filechooserbutton_mylib_install_dir(self, button):

        new_mylib_install_dir = button.get_filename()

        if new_mylib_install_dir != self.mylib_install_dir:

            message_dialog = Gtk.MessageDialog(
                self.main_window,
                0,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                _("Installation directory changed")
                )
            message_dialog.format_secondary_text(_("Do you really want to change installation directory?\n" + \
                "All your installed games will be moved to the new location.\nProceed?"))
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('spacing', 10)

            message_dialog_response = message_dialog.run()

            if message_dialog_response == Gtk.ResponseType.YES:

                os.system('mv -f ' + self.mylib_install_dir + '/* ' + \
                new_mylib_install_dir + ' && rmdir ' + self.mylib_install_dir)

                os.system('rm ' + new_mylib_install_dir + '/*/.configured > /dev/null 2>&1')

                self.mylib_install_dir = new_mylib_install_dir

            elif message_dialog_response == Gtk.ResponseType.NO:

                button.set_filename(self.mylib_install_dir)

            message_dialog.destroy()

    def cb_combobox_preferred_language(self, combobox):
        self.goglib_lang = combobox.get_active_text()

    def cb_switch_goglib_keep_installers(self, switch, event):
        self.goglib_keep_installers = switch.get_active()

    def cb_switch_goglib_offline_mode(self, switch, event):
        self.goglib_start_offline_mode = switch.get_active()

    def cb_switch_goglib_download_extras(self, switch, event):

        self.goglib_download_extras = switch.get_active()

        if switch.get_active():
            self.switch_goglib_keep_installers.set_active(True)
            self.switch_goglib_keep_installers.set_sensitive(False)
        else:
            self.switch_goglib_keep_installers.set_sensitive(True)

    def cb_switch_mylib_keep_installers(self, switch, event):
        self.mylib_keep_installers = switch.get_active()

    def cb_fontbutton(self, button):
        self.font = button.get_font_name()
        self.set_visuals()

    def cb_combobox_gtk_theme(self, combobox):
        self.gtk_theme = combobox.get_active_text()
        self.set_visuals()

    def cb_combobox_icon_theme(self, combobox):
        self.icon_theme = combobox.get_active_text()
        self.set_visuals()

    def cb_switch_dark_theme(self, switch, event):
        self.gtk_dark = switch.get_active()
        self.set_visuals()

    def cb_combobox_monitor(self, combobox):
        self.monitor = combobox.get_active()

    def cb_filechooserbutton_wine(self, button):
        self.wine_path = button.get_filename()
        self.combobox_wine_version.get_model().clear()
        self.populate_wine_version_combobox()
        self.win64_available()

    def cb_filechooserbutton_dosbox(self, button):
        self.dosbox_path = button.get_filename()
        self.combobox_dosbox_version.get_model().clear()
        self.populate_dosbox_version_combobox()

    def cb_filechooserbutton_scummvm(self, button):
        self.scummvm_path = button.get_filename()
        self.combobox_scummvm_version.get_model().clear()
        self.populate_scummvm_version_combobox()

    def cb_radiobutton_goglib_status_filter_include(self, button):
        if button.get_active() == True:
            self.goglib_status_filter_type = 'include'
        else:
            self.goglib_status_filter_type = 'exclude'
        self.set_goglib_filters_color_indication()

        self.cb_combobox_goglib_status(self.combobox_goglib_status)

    def cb_radiobutton_goglib_tag1_include(self, button):
        if button.get_active() == True:
            self.goglib_tags_filter1_type = 'include'
        else:
            self.goglib_tags_filter1_type = 'exclude'
        self.set_goglib_filters_color_indication()

        self.cb_combobox_goglib_tags1(self.combobox_goglib_tags1)

    def cb_radiobutton_goglib_tag2_include(self, button):
        if button.get_active() == True:
            self.goglib_tags_filter2_type = 'include'
        else:
            self.goglib_tags_filter2_type = 'exclude'
        self.set_goglib_filters_color_indication()

        self.cb_combobox_goglib_tags2(self.combobox_goglib_tags2)

    def cb_radiobutton_goglib_tag3_include(self, button):
        if button.get_active() == True:
            self.goglib_tags_filter3_type = 'include'
        else:
            self.goglib_tags_filter3_type = 'exclude'
        self.set_goglib_filters_color_indication()

        self.cb_combobox_goglib_tags3(self.combobox_goglib_tags3)

    def cb_radiobutton_goglib_tag4_include(self, button):
        if button.get_active() == True:
            self.goglib_tags_filter4_type = 'include'
        else:
            self.goglib_tags_filter4_type = 'exclude'
        self.set_goglib_filters_color_indication()

        self.cb_combobox_goglib_tags4(self.combobox_goglib_tags4)

    def cb_switch_goglib_filter_color_indication(self, switch, event):

        self.goglib_filter_color_indication = switch.get_active()
        self.set_goglib_filters_color_indication()

    def set_goglib_filters_color_indication(self):

        self.cb_combobox_goglib_status(self.combobox_goglib_status)
        self.goglib_apply_filters()

        goglib_combobox_status_cell_view = self.combobox_goglib_status.get_child()
        goglib_combobox_tags1_cell_view = self.combobox_goglib_tags1.get_child()
        goglib_combobox_tags2_cell_view = self.combobox_goglib_tags2.get_child()
        goglib_combobox_tags3_cell_view = self.combobox_goglib_tags3.get_child()
        goglib_combobox_tags4_cell_view = self.combobox_goglib_tags4.get_child()

        if self.goglib_filter_color_indication == True:

            if self.goglib_status_filter_type == 'include':
                goglib_combobox_status_cell_view.set_background_rgba(self.goglib_include_rgba)
            elif self.goglib_status_filter_type == 'exclude':
                goglib_combobox_status_cell_view.set_background_rgba(self.goglib_exclude_rgba)

            if self.goglib_tags_filter1_type == 'include':
                goglib_combobox_tags1_cell_view.set_background_rgba(self.goglib_include_rgba)
            elif self.goglib_tags_filter1_type == 'exclude':
                goglib_combobox_tags1_cell_view.set_background_rgba(self.goglib_exclude_rgba)

            if self.goglib_tags_filter2_type == 'include':
                goglib_combobox_tags2_cell_view.set_background_rgba(self.goglib_include_rgba)
            elif self.goglib_tags_filter2_type == 'exclude':
                goglib_combobox_tags2_cell_view.set_background_rgba(self.goglib_exclude_rgba)

            if self.goglib_tags_filter3_type == 'include':
                goglib_combobox_tags3_cell_view.set_background_rgba(self.goglib_include_rgba)
            elif self.goglib_tags_filter3_type == 'exclude':
                goglib_combobox_tags3_cell_view.set_background_rgba(self.goglib_exclude_rgba)

            if self.goglib_tags_filter4_type == 'include':
                goglib_combobox_tags4_cell_view.set_background_rgba(self.goglib_include_rgba)
            elif self.goglib_tags_filter4_type == 'exclude':
                goglib_combobox_tags4_cell_view.set_background_rgba(self.goglib_exclude_rgba)

        else:

            goglib_combobox_status_cell_view.set_background_rgba(transparent_rgba)
            goglib_combobox_tags1_cell_view.set_background_rgba(transparent_rgba)
            goglib_combobox_tags2_cell_view.set_background_rgba(transparent_rgba)
            goglib_combobox_tags3_cell_view.set_background_rgba(transparent_rgba)
            goglib_combobox_tags4_cell_view.set_background_rgba(transparent_rgba)

    def cb_radiobutton_mylib_status_filter_include(self, button):
        if button.get_active() == True:
            self.mylib_status_filter_type = 'include'
        else:
            self.mylib_status_filter_type = 'exclude'
        self.set_mylib_filters_color_indication()

        self.cb_combobox_mylib_status(self.combobox_mylib_status)

    def cb_radiobutton_mylib_tag1_include(self, button):
        if button.get_active() == True:
            self.mylib_tags_filter1_type = 'include'
        else:
            self.mylib_tags_filter1_type = 'exclude'
        self.set_mylib_filters_color_indication()

        self.cb_combobox_mylib_tags1(self.combobox_mylib_tags1)

    def cb_radiobutton_mylib_tag2_include(self, button):
        if button.get_active() == True:
            self.mylib_tags_filter2_type = 'include'
        else:
            self.mylib_tags_filter2_type = 'exclude'
        self.set_mylib_filters_color_indication()

        self.cb_combobox_mylib_tags2(self.combobox_mylib_tags2)

    def cb_radiobutton_mylib_tag3_include(self, button):
        if button.get_active() == True:
            self.mylib_tags_filter3_type = 'include'
        else:
            self.mylib_tags_filter3_type = 'exclude'
        self.set_mylib_filters_color_indication()

        self.cb_combobox_mylib_tags3(self.combobox_mylib_tags3)

    def cb_radiobutton_mylib_tag4_include(self, button):
        if button.get_active() == True:
            self.mylib_tags_filter4_type = 'include'
        else:
            self.mylib_tags_filter4_type = 'exclude'
        self.set_mylib_filters_color_indication()

        self.cb_combobox_mylib_tags4(self.combobox_mylib_tags4)

    def cb_switch_mylib_filter_color_indication(self, switch, event):

        self.mylib_filter_color_indication = switch.get_active()
        self.set_mylib_filters_color_indication()

    def cb_button_online_status(self, button):

        if self.goglib_offline_mode:
            self.goglib_offline_mode_at_start = False
        else:
            self.goglib_offline_mode_at_start = True

        self.config_save()

        os.execl(sys.executable, sys.executable, *sys.argv)

    def set_mylib_filters_color_indication(self):

        self.mylib_apply_filters()

        mylib_combobox_status_cell_view = self.combobox_mylib_status.get_child()
        mylib_combobox_tags1_cell_view = self.combobox_mylib_tags1.get_child()
        mylib_combobox_tags2_cell_view = self.combobox_mylib_tags2.get_child()
        mylib_combobox_tags3_cell_view = self.combobox_mylib_tags3.get_child()
        mylib_combobox_tags4_cell_view = self.combobox_mylib_tags4.get_child()

        if self.mylib_filter_color_indication == True:

            if self.mylib_status_filter_type == 'include':
                mylib_combobox_status_cell_view.set_background_rgba(self.mylib_include_rgba)
            elif self.mylib_status_filter_type == 'exclude':
                mylib_combobox_status_cell_view.set_background_rgba(self.mylib_exclude_rgba)

            if self.mylib_tags_filter1_type == 'include':
                mylib_combobox_tags1_cell_view.set_background_rgba(self.mylib_include_rgba)
            elif self.mylib_tags_filter1_type == 'exclude':
                mylib_combobox_tags1_cell_view.set_background_rgba(self.mylib_exclude_rgba)

            if self.mylib_tags_filter2_type == 'include':
                mylib_combobox_tags2_cell_view.set_background_rgba(self.mylib_include_rgba)
            elif self.mylib_tags_filter2_type == 'exclude':
                mylib_combobox_tags2_cell_view.set_background_rgba(self.mylib_exclude_rgba)

            if self.mylib_tags_filter3_type == 'include':
                mylib_combobox_tags3_cell_view.set_background_rgba(self.mylib_include_rgba)
            elif self.mylib_tags_filter3_type == 'exclude':
                mylib_combobox_tags3_cell_view.set_background_rgba(self.mylib_exclude_rgba)

            if self.mylib_tags_filter4_type == 'include':
                mylib_combobox_tags4_cell_view.set_background_rgba(self.mylib_include_rgba)
            elif self.mylib_tags_filter4_type == 'exclude':
                mylib_combobox_tags4_cell_view.set_background_rgba(self.mylib_exclude_rgba)

        else:

            mylib_combobox_status_cell_view.set_background_rgba(transparent_rgba)
            mylib_combobox_tags1_cell_view.set_background_rgba(transparent_rgba)
            mylib_combobox_tags2_cell_view.set_background_rgba(transparent_rgba)
            mylib_combobox_tags3_cell_view.set_background_rgba(transparent_rgba)
            mylib_combobox_tags4_cell_view.set_background_rgba(transparent_rgba)

    def cb_colorbutton_goglib_include(self, button):
        self.goglib_include_color = button.get_rgba().to_string()
        self.parse_goglib_colors()
        self.set_goglib_filters_color_indication()

    def cb_colorbutton_goglib_exclude(self, button):
        self.goglib_exclude_color = button.get_rgba().to_string()
        self.parse_goglib_colors()
        self.set_goglib_filters_color_indication()

    def cb_colorbutton_mylib_include(self, button):
        self.mylib_include_color = button.get_rgba().to_string()
        self.parse_mylib_colors()
        self.set_mylib_filters_color_indication()

    def cb_colorbutton_mylib_exclude(self, button):
        self.mylib_exclude_color = button.get_rgba().to_string()
        self.parse_mylib_colors()
        self.set_mylib_filters_color_indication()

    def parse_goglib_colors(self):
        self.goglib_include_rgba = Gdk.RGBA()
        self.goglib_include_rgba.parse(self.goglib_include_color)
        self.goglib_exclude_rgba = Gdk.RGBA()
        self.goglib_exclude_rgba.parse(self.goglib_exclude_color)

    def parse_mylib_colors(self):
        self.mylib_include_rgba = Gdk.RGBA()
        self.mylib_include_rgba.parse(self.mylib_include_color)
        self.mylib_exclude_rgba = Gdk.RGBA()
        self.mylib_exclude_rgba.parse(self.mylib_exclude_color)

    def win64_available(self):

        if self.wine == 'system':
            wine_bin = 'wine64'
        elif self.wine == 'path':
            wine_bin = self.wine_path + '/' + self.wine_version + '/bin/wine64'

        dev_null = open(os.devnull, 'w')
        try:
            proc = subprocess.Popen([wine_bin], stdout=dev_null, \
                stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
            dev_null.close()
            stdoutdata, stderrdata = proc.communicate()
            if proc.returncode == 1:
                self.label_winearch.set_visible(True)
                self.combobox_winearch.set_visible(True)
                return True
            else:
                self.label_winearch.set_visible(False)
                self.combobox_winearch.set_visible(False)
                self.winearch = 'win32'
                return False
        except:
            self.label_winearch.set_visible(False)
            self.combobox_winearch.set_visible(False)
            self.winearch = 'win32'
            return False

    def cb_combobox_winearch(self, combobox):
        self.winearch = combobox.get_active_text()

    def switch_monitor(self, switch):
        if switch == 'ON':
            output = self.combobox_monitor.get_active_text().split()[0]
            os.system('xrandr --output '+ output + ' --primary')
        elif switch == 'OFF':
            output = self.monitor_primary.split()[0]
            os.system('xrandr --output '+ output + ' --primary')

    def detach_tab(self, notebook, page_content, x, y):

        def remove_additional_page(notebook, page_content, page_num, window):
            self.detached_tabs_names.remove(page_content.get_name())
            if notebook.get_n_pages() == 0:
                self.additional_windows_list.remove(window)
                window.destroy()

        def additional_window_destroyed(window, event, notebook):
            if notebook.get_n_pages() != 0:
                for i in range(notebook.get_n_pages()):
                    self.detached_tabs_names.remove(notebook.get_nth_page(i).get_name())
                    notebook.remove_page(i)
            window.remove(notebook)
            self.additional_windows_list.remove(window)

        tab_label = notebook.get_tab_label(page_content)

        additional_window = Gtk.Window(
            title = "Games Nebula",
            type = Gtk.WindowType.TOPLEVEL,
            window_position = Gtk.WindowPosition.CENTER,
            default_width = 800,
            default_height = 600,
            icon = app_icon,
            )
        additional_window.connect('key-press-event', self.shortcuts)
        self.additional_windows_list.append(additional_window)

        workarea_width, workarea_height = self.get_monitor_workarea(additional_window)
        additional_window.set_property('default_width', workarea_width)
        additional_window.set_property('default_height', workarea_height)

        additional_notebook = Gtk.Notebook(
            show_tabs = self.show_tabs
            )
        additional_notebook.set_group_name('games_nebula')
        self.additional_notebooks_list.append(additional_notebook)
        additional_window.add(additional_notebook)

        additional_notebook.connect('create-window', self.detach_tab)
        additional_notebook.connect('page-removed', remove_additional_page, additional_window)
        additional_window.connect('delete-event', additional_window_destroyed, additional_notebook)

        additional_window.show_all()

        notebook.detach_tab(page_content)
        additional_notebook.append_page(page_content, tab_label)
        additional_notebook.set_tab_detachable(page_content, True)
        additional_notebook.set_tab_reorderable(page_content, True)

        self.detached_tabs_names.append(page_content.get_name())

    def get_monitor_workarea(self, window):

        x = window.get_position().root_x
        y = window.get_position().root_y

        try:
            display = Gdk.Display.get_default()
            current_monitor = display.get_monitor_at_point(x, y)
            workarea_width = current_monitor.get_workarea().width
            workarea_height = current_monitor.get_workarea().height
        except:
            # TODO For GTK before 3.22. Remove when not needed anymore
            screen = Gdk.Screen.get_default()
            current_monitor_number = screen.get_monitor_at_point(x, y)
            workarea_width = screen.get_monitor_workarea(current_monitor_number).width
            workarea_height = screen.get_monitor_workarea(current_monitor_number).height

        return workarea_width, workarea_height

    def get_event_scancode(self, event):

        try:
            key_scancode = event.get_scancode()
        except:
            # TODO For GTK before 3.22. Remove when not needed anymore
            keycode = event.get_keycode()
            key_scancode = keycode[1]

        return key_scancode

    def set_new_page_active(self):

        last_page_number = self.notebook.get_n_pages() - 1

        if self.notebook.get_current_page() != last_page_number:
            self.notebook.set_current_page(last_page_number)
        else:
            return

        GObject.timeout_add(100, self.set_new_page_active)

    # Switch behavior and reset filters by RMB and LMB

    def cb2_comboboxes_filters(self, combobox, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:

            if combobox.get_name() == 'combobox_goglib_status':
                if event.button == 3:
                    if self.goglib_status_filter_type == 'include':
                        self.goglib_status_filter_type = 'exclude'
                        self.radiobutton_goglib_status_filter_exclude.set_active(True)
                    elif self.goglib_status_filter_type == 'exclude':
                        self.goglib_status_filter_type = 'include'
                        self.radiobutton_goglib_status_filter_include.set_active(True)
                    self.set_goglib_filters_color_indication()
                    self.cb_combobox_goglib_status(self.combobox_goglib_status)
                elif event.button == 2:
                    self.combobox_goglib_status.set_active(0)

            if combobox.get_name() == 'combobox_goglib_tags1':
                if event.button == 3:
                    if self.goglib_tags_filter1_type == 'include':
                        self.goglib_tags_filter1_type = 'exclude'
                        self.radiobutton_goglib_tag1_exclude.set_active(True)
                    elif self.goglib_tags_filter1_type == 'exclude':
                        self.goglib_tags_filter1_type = 'include'
                        self.radiobutton_goglib_tag1_include.set_active(True)
                    self.set_goglib_filters_color_indication()
                    self.cb_combobox_goglib_tags1(self.combobox_goglib_tags1)
                elif event.button == 2:
                    self.combobox_goglib_tags1.set_active(0)

            if combobox.get_name() == 'combobox_goglib_tags2':
                if event.button == 3:
                    if self.goglib_tags_filter2_type == 'include':
                        self.goglib_tags_filter2_type = 'exclude'
                        self.radiobutton_goglib_tag2_exclude.set_active(True)
                    elif self.goglib_tags_filter2_type == 'exclude':
                        self.goglib_tags_filter2_type = 'include'
                        self.radiobutton_goglib_tag2_include.set_active(True)
                    self.set_goglib_filters_color_indication()
                    self.cb_combobox_goglib_tags2(self.combobox_goglib_tags2)
                elif event.button == 2:
                    self.combobox_goglib_tags2.set_active(0)

            if combobox.get_name() == 'combobox_goglib_tags3':
                if event.button == 3:
                    if self.goglib_tags_filter3_type == 'include':
                        self.goglib_tags_filter3_type = 'exclude'
                        self.radiobutton_goglib_tag3_exclude.set_active(True)
                    elif self.goglib_tags_filter3_type == 'exclude':
                        self.goglib_tags_filter3_type = 'include'
                        self.radiobutton_goglib_tag3_include.set_active(True)
                    self.set_goglib_filters_color_indication()
                    self.cb_combobox_goglib_tags3(self.combobox_goglib_tags3)
                elif event.button == 2:
                    self.combobox_goglib_tags3.set_active(0)

            if combobox.get_name() == 'combobox_goglib_tags4':
                if event.button == 3:
                    if self.goglib_tags_filter4_type == 'include':
                        self.goglib_tags_filter4_type = 'exclude'
                        self.radiobutton_goglib_tag4_exclude.set_active(True)
                    elif self.goglib_tags_filter4_type == 'exclude':
                        self.goglib_tags_filter4_type = 'include'
                        self.radiobutton_goglib_tag4_include.set_active(True)
                    self.set_goglib_filters_color_indication()
                    self.cb_combobox_goglib_tags4(self.combobox_goglib_tags4)
                elif event.button == 2:
                    self.combobox_goglib_tags4.set_active(0)

            if combobox.get_name() == 'combobox_mylib_status':
                if event.button == 3:
                    if self.mylib_status_filter_type == 'include':
                        self.mylib_status_filter_type = 'exclude'
                        self.radiobutton_mylib_status_filter_exclude.set_active(True)
                    elif self.mylib_status_filter_type == 'exclude':
                        self.mylib_status_filter_type = 'include'
                        self.radiobutton_mylib_status_filter_include.set_active(True)
                    self.set_mylib_filters_color_indication()
                    self.cb_combobox_mylib_status(self.combobox_mylib_status)
                elif event.button == 2:
                    self.combobox_mylib_status.set_active(0)

            if combobox.get_name() == 'combobox_mylib_tags1':
                if event.button == 3:
                    if self.mylib_tags_filter1_type == 'include':
                        self.mylib_tags_filter1_type = 'exclude'
                        self.radiobutton_mylib_tag1_exclude.set_active(True)
                    elif self.mylib_tags_filter1_type == 'exclude':
                        self.mylib_tags_filter1_type = 'include'
                        self.radiobutton_mylib_tag1_include.set_active(True)
                    self.set_mylib_filters_color_indication()
                    self.cb_combobox_mylib_tags1(self.combobox_mylib_tags1)
                elif event.button == 2:
                    self.combobox_mylib_tags1.set_active(0)

            if combobox.get_name() == 'combobox_mylib_tags2':
                if event.button == 3:
                    if self.mylib_tags_filter2_type == 'include':
                        self.mylib_tags_filter2_type = 'exclude'
                        self.radiobutton_mylib_tag2_exclude.set_active(True)
                    elif self.mylib_tags_filter2_type == 'exclude':
                        self.mylib_tags_filter2_type = 'include'
                        self.radiobutton_mylib_tag2_include.set_active(True)
                    self.set_mylib_filters_color_indication()
                    self.cb_combobox_mylib_tags2(self.combobox_mylib_tags2)
                elif event.button == 2:
                    self.combobox_mylib_tags2.set_active(0)

            if combobox.get_name() == 'combobox_mylib_tags3':
                if event.button == 3:
                    if self.mylib_tags_filter3_type == 'include':
                        self.mylib_tags_filter3_type = 'exclude'
                        self.radiobutton_mylib_tag3_exclude.set_active(True)
                    elif self.mylib_tags_filter3_type == 'exclude':
                        self.mylib_tags_filter3_type = 'include'
                        self.radiobutton_mylib_tag3_include.set_active(True)
                    self.set_mylib_filters_color_indication()
                    self.cb_combobox_mylib_tags3(self.combobox_mylib_tags3)
                elif event.button == 2:
                    self.combobox_mylib_tags3.set_active(0)

            if combobox.get_name() == 'combobox_mylib_tags4':
                if event.button == 3:
                    if self.mylib_tags_filter4_type == 'include':
                        self.mylib_tags_filter4_type = 'exclude'
                        self.radiobutton_mylib_tag4_exclude.set_active(True)
                    elif self.mylib_tags_filter4_type == 'exclude':
                        self.mylib_tags_filter4_type = 'include'
                        self.radiobutton_mylib_tag4_include.set_active(True)
                    self.set_mylib_filters_color_indication()
                    self.cb_combobox_mylib_tags4(self.combobox_mylib_tags4)
                elif event.button == 2:
                    self.combobox_mylib_tags4.set_active(0)

    def shortcuts(self, current_window, event):

        key_scancode = self.get_event_scancode(event)

        # Hide/show tabs (Shift + T)
        if (key_scancode == 28) and (event.state & Gdk.ModifierType.SHIFT_MASK):

            notebook = current_window.get_child()

            if notebook.get_show_tabs() == True:
                notebook.set_show_tabs(False)
                self.show_tabs = False
            else:
                notebook.set_show_tabs(True)
                self.show_tabs = True

        # Fullscreen/unfullscreen (Ctrl + F)
        if (key_scancode == 41) and (event.state & Gdk.ModifierType.CONTROL_MASK):

            current_window_gdk = current_window.get_window()
            window_state = current_window_gdk.get_state()

            fullscreen_state = Gdk.WindowState.FULLSCREEN

            if window_state & fullscreen_state != fullscreen_state:
                current_window.fullscreen()
            else:
                current_window.unfullscreen()

        # Next tab (Ctrl + Tab)
        if (key_scancode == 23) and (event.state & Gdk.ModifierType.CONTROL_MASK):
            notebook = current_window.get_child()

            if notebook.get_current_page() != (notebook.get_n_pages() - 1):
                notebook.next_page()
            else:
                notebook.set_current_page(0)

        # Previous tab (Shift + Tab)
        if (key_scancode == 23) and (event.state & Gdk.ModifierType.SHIFT_MASK):
            notebook = current_window.get_child()

            if notebook.get_current_page() != 0:
                notebook.prev_page()
            else:
                notebook.set_current_page((notebook.get_n_pages() - 1))

        # Close tab (Ctrl + W)
        if (key_scancode == 25) and (event.state & Gdk.ModifierType.CONTROL_MASK):
            notebook = current_window.get_child()
            page_number = notebook.get_current_page()
            notebook.remove_page(page_number)

        # Add tab (Ctrl + T)
        if (key_scancode == 28) and (event.state & Gdk.ModifierType.CONTROL_MASK):
            self.add_tab()

        # Search entry focus (Ctrl + S)
        if (key_scancode == 39) and (event.state & Gdk.ModifierType.CONTROL_MASK):

            notebook = current_window.get_child()
            current_page_n = notebook.get_current_page()
            current_page_content = notebook.get_nth_page(current_page_n)
            search_entry = current_page_content.get_children()[0].get_child().get_child().get_children()[0]
            search_entry.grab_focus()

        # Quit (Ctrl + Q)
        if (key_scancode == 24) and (event.state & Gdk.ModifierType.CONTROL_MASK):
            message_dialog = Gtk.MessageDialog(
                self.main_window,
                0,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.OK_CANCEL,
                _("Quit application?")
                )
            content_area = message_dialog.get_content_area()
            content_area.set_property('margin-left', 10)
            content_area.set_property('margin-right', 10)
            content_area.set_property('margin-top', 10)
            content_area.set_property('margin-bottom', 10)
            action_area = message_dialog.get_action_area()
            action_area.set_property('spacing', 10)

            self.main_window.hide()
            response = message_dialog.run()
            message_dialog.destroy()
            self.main_window.show()

            if response == Gtk.ResponseType.OK:
                self.config_save()
                Gtk.main_quit()

    def set_environ(self, game_name, download_dir, install_dir):

        if self.wine == 'system':
            wine_path = 'wine'
        elif self.wine == 'path':
            wine_path = self.wine_path + '/' + self.wine_version

        os.environ['WINEARCH'] = self.winearch
        os.environ['DOWNLOAD_DIR'] = download_dir
        os.environ['INSTALL_DIR'] = install_dir
        os.environ['WINE_PATH'] = wine_path
        os.environ['GAME_NAME'] = game_name
        os.environ['START_FILE'] = install_dir + '/' + game_name + '/start.sh'
        os.environ['START_GOG_FILE'] = install_dir + '/' + game_name + '/start_gog.sh'
        os.environ['START_GN_FILE'] = install_dir + '/' + game_name + '/start_gn.sh'
        os.environ['SETTINGS_FILE'] = install_dir + '/' + game_name + '/settings.sh'
        os.environ['ADDITIONS_FILE'] = install_dir + '/' + game_name + '/additions.sh'
        os.environ['DOSBOX_GAME_CONF'] = install_dir + '/' + game_name + '/dosbox_game.conf'
        os.environ['DOSBOX_SETTINGS_CONF'] = install_dir + '/' + game_name + '/dosbox_settings.conf'

def main():
    app = GUI()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
