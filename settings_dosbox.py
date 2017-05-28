#!/usr/bin/env python2
# -*- Mode: Python; coding: utf-8; indent-tabs-install_mode: t; c-basic-offset: 4; tab-width: 4 -*-

import sys, os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GdkPixbuf
import ConfigParser
import gettext

nebula_dir = sys.path[0]
app_icon = GdkPixbuf.Pixbuf.new_from_file(nebula_dir + '/images/icon.png')

gettext.bindtextdomain('games_nebula', nebula_dir + '/locale')
gettext.textdomain('games_nebula')
_ = gettext.gettext

class GUI:

    def __init__(self, config_path, config_type, dosbox_version):

        self.get_global_settings()

        self.config_path = config_path
        self.config_type = config_type
        self.dosbox_version = dosbox_version

        if self.config_type == 'global':
            self.dosbox_config_global_load(self.config_path)
        elif self.config_type == 'local':
            global_config_path = os.getenv('HOME') + '/.games_nebula/config/dosbox.conf'
            self.dosbox_config_global_load(global_config_path)
            self.dosbox_config_local_load(self.config_path)

        self.set_dosbox_config_vars()

        self.create_main_window()

    def create_main_window(self):

        self.main_window = Gtk.Window(
            title = _("Games Nebula"),
            type = Gtk.WindowType.TOPLEVEL,
            window_position = Gtk.WindowPosition.CENTER_ALWAYS,
            #resizable = False,
            default_width = 800,
            default_height = 600,
            icon = app_icon,
            )
        self.main_window.connect('delete-event', self.quit_app)

#################################################################
        self.grid_sdl = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600
            )

        self.label_fullscreen = Gtk.Label(
            label = _("Fullscreen"),
            halign = Gtk.Align.START,
            tooltip_text = _("Start dosbox directly in fullscreen. (Press ALT-Enter to go back)")
            )

        self.switch_fullscreen = Gtk.Switch(
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.sdl_fullscreen),
            tooltip_text = _("Start dosbox directly in fullscreen. (Press ALT-Enter to go back)")
            )

        #self.switch_fullscreen.connect('toggled', self.cb_switch_fullscreen)

        self.label_fulldouble = Gtk.Label(
            label = _("Double buffering"),
            halign = Gtk.Align.START,
            tooltip_text = _("Use double buffering in fullscreen. It can reduce screen flickering,\nbut it can also result in a slow DOSBox.")
            )

        self.switch_fulldouble = Gtk.Switch(
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.sdl_fulldouble),
            tooltip_text = _("Use double buffering in fullscreen. It can reduce screen flickering,\nbut it can also result in a slow DOSBox.")
            )

        #self.switch_fulldouble.connect('toggled', self.cb_switch_fulldouble)

        self.label_fullresolution = Gtk.Label(
            label = _("Fullscreen resolution"),
            halign = Gtk.Align.START,
            tooltip_text = _("What resolution to use for fullscreen.")
            )

        self.combobox_fullresolution = Gtk.ComboBoxText(
            tooltip_text = _("What resolution to use for fullscreen.")
            )

        self.combobox_fullresolution.connect('changed', self.cb_combobox_fullresolution)

        self.entry_fullresolution_width = Gtk.Entry(
            placeholder_text = _("Width"),
            xalign = 0.5,
            max_length = 4,
            no_show_all = True
            )

        self.entry_fullresolution_width.connect('changed', self.cb_entry_digits_only)

        self.entry_fullresolution_height = Gtk.Entry(
            placeholder_text = _("Height"),
            xalign = 0.5,
            max_length = 4,
            no_show_all = True
            )

        self.entry_fullresolution_height.connect('changed', self.cb_entry_digits_only)

        if self.digit_in_string(self.sdl_fullresolution):
            fullresolution_str = 'fixed'
            fullresolution_width = self.sdl_fullresolution.split('x')[0]
            fullresolution_height = self.sdl_fullresolution.split('x')[1]
            self.entry_fullresolution_width.set_visible(True)
            self.entry_fullresolution_width.set_text(fullresolution_width)
            self.entry_fullresolution_height.set_visible(True)
            self.entry_fullresolution_height.set_text(fullresolution_height)
        else:
            fullresolution_str = self.sdl_fullresolution

        fullresolution_list = ['original', 'desktop', 'fixed']

        for i in range(0, len(fullresolution_list)):
            self.combobox_fullresolution.append_text(fullresolution_list[i])
            if fullresolution_list[i] == fullresolution_str:
                fullresolution_active = i

        self.combobox_fullresolution.set_active(fullresolution_active)

        self.label_windowresolution = Gtk.Label(
            label = _("Window resolution"),
            halign = Gtk.Align.START,
            tooltip_text = _("Scale the window to this size IF the output device\nsupports hardware scaling (output=surface does not!).")
            )

        self.combobox_windowresolution = Gtk.ComboBoxText(
            tooltip_text = _("Scale the window to this size IF the output device\nsupports hardware scaling (output=surface does not!).")
            )

        self.combobox_windowresolution.connect('changed', self.cb_combobox_windowresolution)

        self.entry_windowresolution_width = Gtk.Entry(
            placeholder_text = _("Width"),
            xalign = 0.5,
            max_length = 4,
            no_show_all = True
            )

        self.entry_windowresolution_width.connect('changed', self.cb_entry_digits_only)

        self.entry_windowresolution_height = Gtk.Entry(
            placeholder_text = _("Height"),
            xalign = 0.5,
            max_length = 4,
            no_show_all = True
            )

        self.entry_windowresolution_height.connect('changed', self.cb_entry_digits_only)

        if self.digit_in_string(self.sdl_windowresolution):
            windowresolution_str = 'fixed'
            windowresolution_width = self.sdl_windowresolution.split('x')[0]
            windowresolution_height = self.sdl_windowresolution.split('x')[1]
            self.entry_windowresolution_width.set_visible(True)
            self.entry_windowresolution_width.set_text(windowresolution_width)
            self.entry_windowresolution_height.set_visible(True)
            self.entry_windowresolution_height.set_text(windowresolution_height)
        else:
            windowresolution_str = self.sdl_windowresolution

        windowresolution_list = ['original', 'desktop', 'fixed']

        for i in range(0, len(windowresolution_list)):
            self.combobox_windowresolution.append_text(windowresolution_list[i])
            if windowresolution_list[i] == windowresolution_str:
                windowresolution_active = i

        self.combobox_windowresolution.set_active(windowresolution_active)

        self.label_output = Gtk.Label(
            label = _("Output"),
            halign = Gtk.Align.START,
            tooltip_text = _("What video system to use for output.")
            )

        self.combobox_output = Gtk.ComboBoxText(
            tooltip_text = _("What video system to use for output.")
            )

        #self.combobox_output.connect('changed', self.cb_combobox_output)

        # TODO Remove if scecific svn-daum version exists
        if self.dosbox_version == 'svn_daum':
            output_list = ['surface', 'overlay', 'opengl', 'openglnb', 'openglhq']
        else:
            output_list = ['surface', 'overlay', 'opengl', 'openglnb']

        output_active = 0
        for i in range(0, len(output_list)):
            self.combobox_output.append_text(output_list[i])
            if output_list[i] == self.sdl_output:
                output_active = i
        self.combobox_output.set_active(output_active)

        self.label_autolock = Gtk.Label(
            label = _("Mouse autolock"),
            halign = Gtk.Align.START,
            tooltip_text = _("Mouse will automatically lock, if you click on the screen.\n(Press CTRL-F10 to unlock)")
            )

        self.switch_autolock = Gtk.Switch(
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.sdl_autolock),
            tooltip_text = _("Mouse will automatically lock, if you click on the screen.\n(Press CTRL-F10 to unlock)")
            )

        #self.switch_autolock.connect('toggled', self.cb_switch_autolock)

        self.label_sensitivity = Gtk.Label(
            label = _("Mouse sensitivity"),
            halign = Gtk.Align.START,
            tooltip_text = _("Mouse sensitivity.")
            )

        self.adjustment_sensitivity = Gtk.Adjustment(int(self.sdl_sensitivity), 0, 1000, 1, 10)
        #self.adjustment_sensitivity.connect('value-changed', self.cb_adjustment_sensitivity)

        self.scale_sensitivity = Gtk.Scale(
            tooltip_text = _("Mouse sensitivity."),
            orientation = Gtk.Orientation.HORIZONTAL,
            draw_value = True,
            show_fill_level = True,
            adjustment = self.adjustment_sensitivity,
            digits = 0,
            round_digits = 0
            )

        self.label_waitonerror = Gtk.Label(
            label = _("Wait on error"),
            halign = Gtk.Align.START,
            tooltip_text = _("Wait before closing the console if dosbox has an error.")
            )

        self.switch_waitonerror = Gtk.Switch(
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.sdl_waitonerror),
            tooltip_text = _("Wait before closing the console if dosbox has an error.")
            )

        #self.switch_waitonerror.connect('toggled', self.cb_switch_waitonerror)

        self.label_priority = Gtk.Label(
            label = _("Priority"),
            halign = Gtk.Align.START,
            tooltip_text = _("Priority levels for dosbox.")
            )

        self.combobox_priority1 = Gtk.ComboBoxText(
            tooltip_text = _("Active.")
            )

        priority1_list = ['lowest', 'lower', 'normal', 'higher', 'highest']

        for i in range(0, len(priority1_list)):
            self.combobox_priority1.append_text(priority1_list[i])
            if priority1_list[i] == self.sdl_priority.split(',')[0]:
                priority1_active = i

        self.combobox_priority1.set_active(priority1_active)

        self.combobox_priority2 = Gtk.ComboBoxText(
            tooltip_text = _("Not focused/minimized.")
            )

        priority2_list = ['lowest', 'lower', 'normal', 'higher', 'highest', 'pause']

        for i in range(0, len(priority2_list)):
            self.combobox_priority2.append_text(priority2_list[i])
            if priority2_list[i] == self.sdl_priority.split(',')[1]:
                priority2_active = i

        self.combobox_priority2.set_active(priority2_active)

        self.label_mapperfile = Gtk.Label(
            label = _("Mapperfile"),
            halign = Gtk.Align.START,
            tooltip_text = _("File used to load/save the key/event mappings from.\nResetmapper only works with the defaul value.")
            )

        self.filechooser_mapperfile = Gtk.FileChooserButton(
            tooltip_text = _("File used to load/save the key/event mappings from.\nResetmapper only works with the defaul value."),
            title = _("Select a file"),
            action =  Gtk.FileChooserAction.OPEN,
            )

        if self.sdl_mapperfile != '':
            mapperfile = Gio.File.new_for_path(self.sdl_mapperfile)
            self.filechooser_mapperfile.set_file(mapperfile)

        self.label_scancodes = Gtk.Label(
            label = _("Use scancodes"),
            halign = Gtk.Align.START,
            tooltip_text = _("Avoid usage of symkeys.")
            )

        self.switch_scancodes = Gtk.Switch(
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.sdl_usescancodes),
            tooltip_text = _("Avoid usage of symkeys.")
            )

        self.grid_sdl.attach(self.label_fullscreen, 0, 0, 1, 1)
        self.grid_sdl.attach(self.switch_fullscreen, 1, 0, 2, 1)
        self.grid_sdl.attach(self.label_fulldouble, 0, 1, 1, 1)
        self.grid_sdl.attach(self.switch_fulldouble, 1, 1, 2, 1)
        self.grid_sdl.attach(self.label_fullresolution, 0, 2, 1, 1)
        self.grid_sdl.attach(self.combobox_fullresolution, 1, 2, 2, 1)
        self.grid_sdl.attach(self.entry_fullresolution_width, 1, 3, 1, 1)
        self.grid_sdl.attach(self.entry_fullresolution_height, 2, 3, 1, 1)
        self.grid_sdl.attach(self.label_windowresolution, 0, 4, 1, 1)
        self.grid_sdl.attach(self.combobox_windowresolution, 1, 4, 2, 1)
        self.grid_sdl.attach(self.entry_windowresolution_width, 1, 5, 1, 1)
        self.grid_sdl.attach(self.entry_windowresolution_height, 2, 5, 1, 1)
        self.grid_sdl.attach(self.label_output, 0, 6, 1, 1)
        self.grid_sdl.attach(self.combobox_output, 1, 6, 2, 1)
        self.grid_sdl.attach(self.label_autolock, 0, 7, 1, 1)
        self.grid_sdl.attach(self.switch_autolock, 1, 7, 2, 1)
        self.grid_sdl.attach(self.label_sensitivity, 0, 8, 1, 1)
        self.grid_sdl.attach(self.scale_sensitivity, 1, 8, 2, 1)
        self.grid_sdl.attach(self.label_waitonerror, 0, 9, 1, 1)
        self.grid_sdl.attach(self.switch_waitonerror, 1, 9, 2, 1)
        self.grid_sdl.attach(self.label_priority, 0, 10, 1, 1)
        self.grid_sdl.attach(self.combobox_priority1, 1, 10, 1, 1)
        self.grid_sdl.attach(self.combobox_priority2, 2, 10, 1, 1)
        self.grid_sdl.attach(self.label_mapperfile, 0, 11, 1, 1)
        self.grid_sdl.attach(self.filechooser_mapperfile, 1, 11, 2, 1)
        self.grid_sdl.attach(self.label_scancodes, 0, 12, 1, 1)
        self.grid_sdl.attach(self.switch_scancodes, 1, 12, 2, 1)

        self.scrolled_window_sdl = Gtk.ScrolledWindow()
        self.scrolled_window_sdl.add(self.grid_sdl)

        self.label_sdl = Gtk.Label(
            label = "SDL"
            )
#################################################################
        self.grid_dosbox = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_language = Gtk.Label(
            label = _("Language file"),
            halign = Gtk.Align.START,
            tooltip_text = _("Select another language file.")
            )

        self.filechooser_language = Gtk.FileChooserButton(
            tooltip_text = _("Select another language file.")
            )
        if self.dosbox_language != '':
            if not os.path.exists(self.dosbox_language):
                os.system('touch ' + self.dosbox_language)
            languagefile = Gio.File.new_for_path(self.dosbox_language)
            self.filechooser_language.set_file(languagefile)

        self.label_machine = Gtk.Label(
            label = _("Machine"),
            halign = Gtk.Align.START,
            tooltip_text = _("The type of machine DOSBox tries to emulate.")
            )

        self.combobox_machine = Gtk.ComboBoxText(
            tooltip_text = _("The type of machine DOSBox tries to emulate.")
            )

        # TODO Remove if scecific svn-daum version exists
        if self.dosbox_version == 'svn_daum':

            machine_list = [
                'hercules', 'cga', 'cga_mono', 'tandy', 'pcjr', 
                'ega', 'vgaonly', 'svga_s3', 'svga_et3000', 
                'svga_et4000', 'svga_paradise', 'vesa_nolfb', 
                'vesa_oldvbe', 'amstrad'
                ]
        else:

            machine_list = [
                'hercules', 'cga', 'tandy', 'pcjr', 'ega', 
                'vgaonly', 'svga_s3', 'svga_et3000', 'svga_et4000', 
                'svga_paradise', 'vesa_nolfb', 'vesa_oldvbe'
                ]

        for i in range(0, len(machine_list)):
            if machine_list[i] == 'svga_s3':
                machine_active = i
        for i in range(0, len(machine_list)):
            self.combobox_machine.append_text(machine_list[i])
            if machine_list[i] == str(self.dosbox_machine):
                machine_active = i
        self.combobox_machine.set_active(machine_active)

        self.label_captures = Gtk.Label(
            label = _("Captures directory"),
            halign = Gtk.Align.START,
            tooltip_text = _("Directory where things like wave, midi, screenshot get captured.")
            )

        self.filechooser_captures = Gtk.FileChooserButton(
            tooltip_text = _("Directory where things like wave, midi, screenshot get captured."),
            action =  Gtk.FileChooserAction.SELECT_FOLDER,
            )

        if not os.path.exists(self.dosbox_captures):
            os.makedirs(self.dosbox_captures)

        self.filechooser_captures.set_current_folder(self.dosbox_captures)

        self.label_memsize = Gtk.Label(
            label = _("Memory"),
            halign = Gtk.Align.START,
            tooltip_text = _("This value is best left at its default to avoid problems with some games,\nthough few games might require a higher value.\nThere is generally no speed advantage when raising this value.")
            )

        self.combobox_memsize = Gtk.ComboBoxText(
            tooltip_text = _("This value is best left at its default to avoid problems with some games,\nthough few games might require a higher value.\nThere is generally no speed advantage when raising this value.")
            )

        memsize_list = ['16', '32', '64']

        for i in range(0, len(memsize_list)):
            self.combobox_memsize.append_text(memsize_list[i])
            if memsize_list[i] == self.dosbox_memsize:
                memsize_active = i
            elif self.dosbox_memsize == '63':
                memsize_active = 2
        self.combobox_memsize.set_active(memsize_active)

        self.grid_dosbox.attach(self.label_language, 0, 0, 1, 1)
        self.grid_dosbox.attach(self.filechooser_language, 1, 0, 1, 1)
        self.grid_dosbox.attach(self.label_machine, 0, 1, 1, 1)
        self.grid_dosbox.attach(self.combobox_machine, 1, 1, 1, 1)
        self.grid_dosbox.attach(self.label_captures, 0, 2, 1, 1)
        self.grid_dosbox.attach(self.filechooser_captures, 1, 2, 1, 1)
        self.grid_dosbox.attach(self.label_memsize, 0, 3, 1, 1)
        self.grid_dosbox.attach(self.combobox_memsize, 1, 3, 1, 1)

        self.scrolled_window_dosbox = Gtk.ScrolledWindow()
        self.scrolled_window_dosbox.add(self.grid_dosbox)

        self.label_dosbox = Gtk.Label(
            label = "DosBox"
            )
#################################################################
        self.grid_render = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_frameskip = Gtk.Label(
            label = _("Frameskip"),
            halign = Gtk.Align.START,
            tooltip_text = _("How many frames DOSBox skips before drawing one.")
            )

        self.entry_frameskip = Gtk.Entry(
            tooltip_text = _("How many frames DOSBox skips before drawing one."),
            xalign = 0.5,
            max_length = 2,
            )

        self.entry_frameskip.connect('changed', self.cb_entry_digits_only)
        self.entry_frameskip.set_text(self.render_frameskip)

        self.label_aspect = Gtk.Label(
            label = _("Aspect correction"),
            halign = Gtk.Align.START,
            tooltip_text = _("Do aspect correction, if your output method doesn't support\nscaling this can slow things down!.")
            )

        self.switch_aspect = Gtk.Switch(
            halign = Gtk.Align.END,
            tooltip_text = _("Do aspect correction, if your output method doesn't support\nscaling this can slow things down!."),
            active = self.dosbox_config_to_bool(self.render_aspect)
            )

        self.label_scaler = Gtk.Label(
            label = _("Scaler"),
            halign = Gtk.Align.START,
            tooltip_text = _("Scaler used to enlarge/enhance low resolution modes.")
            )

        self.combobox_scaler = Gtk.ComboBoxText(
            tooltip_text = _("Scaler used to enlarge/enhance low resolution modes.")
            )

        # TODO Remove if scecific svn-daum version exists
        if self.dosbox_version == 'svn_daum':

            scaler_list = [
                'none', 'normal2x', 'normal3x', 'normal4x', 'normal5x', 
                'advmame2x', 'advmame3x', 'advinterp2x', 'advinterp3x', 
                'hq2x', 'hq3x', '2xsai', 'super2xsai', 'supereagle', 
                'tv2x', 'tv3x', 'rgb2x', 'rgb3x', 'scan2x', 'scan3x', 
                'hardware_none', 'hardware2x', 'hardware3x', 'hardware4x', 
                'hardware5x', 'xbrz'
                ]

        else:

            scaler_list = [
                'none', 'normal2x', 'normal3x', 'advmame2x', 
                'advmame3x', 'advinterp2x', 'advinterp3x', 'hq2x', 
                'hq3x', '2xsai', 'super2xsai', 'supereagle', 'tv2x', 
                'tv3x', 'rgb2x', 'rgb3x', 'scan2x', 'scan3x'
                ]

        scaler_active = 0
        for i in range(0, len(scaler_list)):
            self.combobox_scaler.append_text(scaler_list[i])
            if scaler_list[i] == self.render_scaler.split(' ')[0]:
                scaler_active = i
        self.combobox_scaler.set_active(scaler_active)

        self.label_forced_scaler = Gtk.Label(
            label = _("Forced scaler"),
            halign = Gtk.Align.START,
            tooltip_text = _("Scaler will be used even if the result might not be desired.")
            )

        self.switch_forced_scaler = Gtk.Switch(
            halign = Gtk.Align.END,
            tooltip_text = _("Scaler will be used even if the result might not be desired."),
            active = ('forced' in self.render_scaler)
            )

        self.grid_render.attach(self.label_frameskip, 0, 0, 1, 1)
        self.grid_render.attach(self.entry_frameskip, 1, 0, 1, 1)
        self.grid_render.attach(self.label_aspect, 0, 1, 1, 1)
        self.grid_render.attach(self.switch_aspect, 1, 1, 1, 1)
        self.grid_render.attach(self.label_scaler, 0, 2, 1, 1)
        self.grid_render.attach(self.combobox_scaler, 1, 2, 1, 1)
        self.grid_render.attach(self.label_forced_scaler, 0, 3, 1, 1)
        self.grid_render.attach(self.switch_forced_scaler, 1, 3, 1, 1)

        self.scrolled_window_render = Gtk.ScrolledWindow()
        self.scrolled_window_render.add(self.grid_render)

        self.label_render = Gtk.Label(
            label = _("Render")
            )
#################################################################
        self.grid_cpu = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_core = Gtk.Label(
            label = _("Core"),
            halign = Gtk.Align.START,
            tooltip_text = _("CPU Core used in emulation. auto will switch to\ndynamic if available and appropriate.")
            )

        self.combobox_core = Gtk.ComboBoxText(
            tooltip_text = _("CPU Core used in emulation. auto will switch to\ndynamic if available and appropriate.")
            )

        # TODO Remove if scecific svn-daum version exists
        if self.dosbox_version == 'svn_daum':
            core_list = ['auto', 'dynamic', 'normal', 'full', 'simple']
        else:
            core_list = ['auto', 'dynamic', 'normal', 'simple']

        core_active = 0
        for i in range(0, len(core_list)):
            self.combobox_core.append_text(core_list[i])
            if core_list[i] == str(self.cpu_core):
                core_active = i
        self.combobox_core.set_active(core_active)

        self.label_cputype = Gtk.Label(
            label = _("CPU type"),
            halign = Gtk.Align.START,
            tooltip_text = _("CPU Type used in emulation. auto is the fastest choice.")
            )

        self.combobox_cputype = Gtk.ComboBoxText(
            tooltip_text = _("CPU Type used in emulation. auto is the fastest choice.")
            )

        # TODO Remove if scecific svn-daum version exists
        if self.dosbox_version == 'svn_daum':
            cputype_list = [
                'auto', '386', '486', 'pentium', '386_prefetch', 
                'pentium_mmx'
                ]
        else:
            cputype_list = [
                'auto', '386', '386_slow', '486_slow', 
                'pentium_slow', '386_prefetch'
                ]

        cputype_active = 0
        for i in range(0, len(cputype_list)):
            self.combobox_cputype.append_text(cputype_list[i])
            if cputype_list[i] == str(self.cpu_cputype):
                cputype_active = i
        self.combobox_cputype.set_active(cputype_active)

        self.label_cycles = Gtk.Label(
            label = _("Cycles"),
            halign = Gtk.Align.START,
            tooltip_text = _("Amount of instructions DOSBox tries to emulate each millisecond.\nSetting this value too high results in sound dropouts and lags..")
            )

        self.combobox_cycles = Gtk.ComboBoxText(
            tooltip_text = _("Amount of instructions DOSBox tries to emulate each millisecond.\nSetting this value too high results in sound dropouts and lags..")
            )

        cycles_list = ['auto', 'max', 'fixed', _("custom")]

        for i in range(0, len(cycles_list)):
            self.combobox_cycles.append_text(cycles_list[i])
            if cycles_list[i] == self.cpu_cycles.split(' ')[0]:
                cycles_active = i
            elif len(self.cpu_cycles.split(' ')) > 2:
                cycles_active = 3
        self.combobox_cycles.set_active(cycles_active)
        self.combobox_cycles.connect('changed', self.cb_combobox_cycles)

        self.entry_fixed_cycles = Gtk.Entry(
            no_show_all = True,
            xalign = 0.5,
            placeholder_text = _("Cycles")
            )

        self.entry_custom_cycles = Gtk.Entry(
            no_show_all = True,
            xalign = 0.5,
            placeholder_text = _("Custom value")
            )

        if 'fixed' in self.cpu_cycles:
            self.entry_fixed_cycles.set_visible(True)
            self.entry_fixed_cycles.set_text(self.cpu_cycles.split(' ')[1])
        elif len(self.cpu_cycles.split(' ')) > 2:
            self.entry_custom_cycles.set_visible(True)
            self.entry_custom_cycles.set_text(self.cpu_cycles)

        self.entry_fixed_cycles.connect('changed', self.cb_entry_digits_only)

        self.label_cycleup = Gtk.Label(
            label = _("Cycle up"),
            halign = Gtk.Align.START,
            tooltip_text = _("Amount of cycles to increase with keycombo.(CTRL-F12)\nSetting it lower than 100 will be a percentage."),
            )

        self.entry_cycleup = Gtk.Entry(
            tooltip_text = _("Amount of cycles to increase with keycombo.(CTRL-F12)\nSetting it lower than 100 will be a percentage."),
            xalign = 0.5,
            text = self.cpu_cycleup
            )

        self.entry_cycleup.connect('changed', self.cb_entry_digits_only)

        self.label_cycledown = Gtk.Label(
            label = _("Cycle down"),
            halign = Gtk.Align.START,
            tooltip_text = _("Amount of cycles to decrease with keycombo.(CTRL-F11)\nSetting it lower than 100 will be a percentage.")
            )

        self.entry_cycledown = Gtk.Entry(
            tooltip_text = _("Amount of cycles to decrease with keycombo.(CTRL-F11)\nSetting it lower than 100 will be a percentage."),
            xalign = 0.5,
            text = self.cpu_cycledown
            )

        self.entry_cycledown.connect('changed', self.cb_entry_digits_only)

        self.grid_cpu.attach(self.label_core, 0, 0, 1, 1)
        self.grid_cpu.attach(self.combobox_core, 1, 0, 1, 1)
        self.grid_cpu.attach(self.label_cputype, 0, 1, 1, 1)
        self.grid_cpu.attach(self.combobox_cputype, 1, 1, 1, 1)
        self.grid_cpu.attach(self.label_cycles, 0, 2, 1, 1)
        self.grid_cpu.attach(self.combobox_cycles, 1, 2, 1, 1)
        self.grid_cpu.attach(self.entry_fixed_cycles, 1, 3, 1, 1)
        self.grid_cpu.attach(self.entry_custom_cycles, 1, 4, 1, 1)
        self.grid_cpu.attach(self.label_cycleup, 0, 5, 1, 1)
        self.grid_cpu.attach(self.entry_cycleup, 1, 5, 1, 1)
        self.grid_cpu.attach(self.label_cycledown, 0, 6, 1, 1)
        self.grid_cpu.attach(self.entry_cycledown, 1, 6, 1, 1)

        self.scrolled_window_cpu = Gtk.ScrolledWindow()
        self.scrolled_window_cpu.add(self.grid_cpu)

        self.label_cpu = Gtk.Label(
            label = _("CPU")
            )
#################################################################
        self.grid_mixer = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_nosound = Gtk.Label(
            label = _("No sound"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable silent mode, sound is still emulated though.")
            )

        self.switch_nosound = Gtk.Switch(
            halign = Gtk.Align.END,
            tooltip_text = _("Enable silent mode, sound is still emulated though."),
            active = self.dosbox_config_to_bool(self.mixer_nosound)
            )

        self.label_rate = Gtk.Label(
            label = _("Sample rate"),
            halign = Gtk.Align.START,
            tooltip_text = _("Mixer sample rate, setting any device's rate higher than\nthis will probably lower their sound quality.")
            )

        self.combobox_rate = Gtk.ComboBoxText(
            tooltip_text = _("Mixer sample rate, setting any device's rate higher than\nthis will probably lower their sound quality.")
            )

        rate_list = ['8000', '11025', '16000', '22050', '32000', '44100', '48000', '49716']

        for i in range(0, len(rate_list)):
            self.combobox_rate.append_text(rate_list[i])
            if rate_list[i] == self.mixer_rate:
                rate_active = i
        self.combobox_rate.set_active(rate_active)

        self.label_blocksize = Gtk.Label(
            label = _("Block size"),
            halign = Gtk.Align.START,
            tooltip_text = _("Mixer block size, larger blocks might help sound stuttering\nbut sound will also be more lagged.")
            )

        self.combobox_blocksize = Gtk.ComboBoxText(
            tooltip_text = _("Mixer block size, larger blocks might help sound stuttering\nbut sound will also be more lagged.")
            )

        blocksize_list = ['256', '512', '1024', '2048', '4096', '8192']

        for i in range(0, len(blocksize_list)):
            self.combobox_blocksize.append_text(blocksize_list[i])
            if blocksize_list[i] == self.mixer_blocksize:
                blocksize_active = i
        self.combobox_blocksize.set_active(blocksize_active)

        self.label_prebuffer = Gtk.Label(
            label = _("Prebuffer"),
            halign = Gtk.Align.START,
            tooltip_text = _("How many milliseconds of data to keep on top of the blocksize.")
            )

        self.entry_prebuffer = Gtk.Entry(
            tooltip_text = _("How many milliseconds of data to keep on top of the blocksize."),
            xalign = 0.5,
            max_length = 4
            )
        self.entry_prebuffer.connect('changed', self.cb_entry_digits_only)
        self.entry_prebuffer.set_text(self.mixer_prebuffer)

        self.grid_mixer.attach(self.label_nosound, 0, 0, 1, 1)
        self.grid_mixer.attach(self.switch_nosound, 1, 0, 1, 1)
        self.grid_mixer.attach(self.label_rate, 0, 1, 1, 1)
        self.grid_mixer.attach(self.combobox_rate, 1, 1, 1, 1)
        self.grid_mixer.attach(self.label_blocksize, 0, 2, 1, 1)
        self.grid_mixer.attach(self.combobox_blocksize, 1, 2, 1, 1)
        self.grid_mixer.attach(self.label_prebuffer, 0, 3, 1, 1)
        self.grid_mixer.attach(self.entry_prebuffer, 1, 3, 1, 1)

        self.scrolled_window_mixer = Gtk.ScrolledWindow()
        self.scrolled_window_mixer.add(self.grid_mixer)

        self.label_mixer = Gtk.Label(
            label = _("Mixer")
            )
#################################################################
        self.grid_midi = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_mpu401 = Gtk.Label(
            label = _("MPU-401"),
            halign = Gtk.Align.START,
            tooltip_text = _("Type of MPU-401 to emulate.")
            )

        self.combobox_mpu401 = Gtk.ComboBoxText(
            tooltip_text = _("Type of MPU-401 to emulate.")
            )

        mpu401_list = ['intelligent', 'uart', 'none']

        for i in range(0, len(mpu401_list)):
            self.combobox_mpu401.append_text(mpu401_list[i])
            if mpu401_list[i] == self.midi_mpu401:
                mpu401_active = i
        self.combobox_mpu401.set_active(mpu401_active)

        self.label_mididevice = Gtk.Label(
            label = _("MIDI device"),
            halign = Gtk.Align.START,
            tooltip_text = _("Device that will receive the MIDI data from MPU-401.")
            )

        self.combobox_mididevice = Gtk.ComboBoxText(
            tooltip_text = _("Device that will receive the MIDI data from MPU-401.")
            )

        # TODO Remove if scecific svn-daum version exists
        if self.dosbox_version == 'svn_daum':
            mididevice_list = [
                'default', 'alsa', 'oss', 'mt32', 'synth', 'timidity', 'none'
                ]
        else:
            mididevice_list = ['default', 'alsa', 'oss', 'none']

        mididevice_active = 0
        for i in range(0, len(mididevice_list)):
            self.combobox_mididevice.append_text(mididevice_list[i])
            if mididevice_list[i] == self.midi_mididevice:
                mididevice_active = i
        self.combobox_mididevice.set_active(mididevice_active)
        self.combobox_mididevice.connect('changed', self.cb_combobox_mididevice)

        self.label_midiconfig = Gtk.Label(
            label = _("MIDI configuration"),
            halign = Gtk.Align.START,
            tooltip_text = _("Special configuration options for the device driver.\nThis is usually the id of the device you want to use.\nSee the README/Manual for more details."),
            no_show_all = True,
            )

        self.entry_midiconfig = Gtk.Entry(
            tooltip_text = _("Special configuration options for the device driver.\nThis is usually the id of the device you want to use.\nSee the README/Manual for more details."),
            text = self.midi_midiconfig,
            xalign = 0.5,
            no_show_all = True,
            )

        self.label_soundfont = Gtk.Label(
            label = _("Soundfont"),
            tooltip_text = _("Soundfont file. Path shouldn't contain spaces"),
            halign = Gtk.Align.START,
            no_show_all = True
            )

        file_filter_sf2 = Gtk.FileFilter()
        file_filter_sf2.set_name("Soundfont")
        file_filter_sf2.add_pattern("*.sf2")

        self.filechooserbutton_soundfont = Gtk.FileChooserButton(
            title = _("Select a soundfont"),
            tooltip_text = _("Soundfont file. Path shouldn't contain spaces"),
            action = Gtk.FileChooserAction.OPEN,
            filter = file_filter_sf2,
            no_show_all = True
            )

        self.filechooserbutton_soundfont.set_filename(self.midi_midiconfig)

        if (self.dosbox_version == 'svn_daum') and (self.midi_mididevice == 'synth'):
            self.label_soundfont.set_visible(True)
            self.filechooserbutton_soundfont.set_visible(True)
            self.label_midiconfig.set_visible(False)
            self.entry_midiconfig.set_visible(False)
        else:
            self.label_midiconfig.set_visible(True)
            self.entry_midiconfig.set_visible(True)

        self.grid_midi.attach(self.label_mpu401, 0, 0, 1, 1)
        self.grid_midi.attach(self.combobox_mpu401, 1, 0, 1, 1)
        self.grid_midi.attach(self.label_mididevice, 0, 1, 1, 1)
        self.grid_midi.attach(self.combobox_mididevice, 1, 1, 1, 1)
        self.grid_midi.attach(self.label_midiconfig, 0, 2, 1, 1)
        self.grid_midi.attach(self.entry_midiconfig, 1, 2, 1, 1)
        self.grid_midi.attach(self.label_soundfont, 0, 3, 1, 1)
        self.grid_midi.attach(self.filechooserbutton_soundfont, 1, 3, 1, 1)

        self.scrolled_window_midi = Gtk.ScrolledWindow()
        self.scrolled_window_midi.add(self.grid_midi)

        self.label_midi = Gtk.Label(
            label = _("MIDI")
            )
#################################################################
        self.grid_sblaster = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_sbtype = Gtk.Label(
            label = _("Soundblaster type"),
            halign = Gtk.Align.START,
            tooltip_text = _("Type of Soundblaster to emulate. gb is Gameblaster.")
            )

        self.combobox_sbtype = Gtk.ComboBoxText(
            tooltip_text = _("Type of Soundblaster to emulate. gb is Gameblaster.")
            )

        # TODO Remove if scecific svn-daum version exists
        if self.dosbox_version == 'svn_daum':
            sbtype_list = [
                'sb1', 'sb2', 'sbpro1', 'sbpro2', 'sb16', 'sb16vibra', 
                'gb', 'none'
                ]
        else:
            sbtype_list = ['sb1', 'sb2', 'sbpro1', 'sbpro2', 'sb16', 'gb', 'none']

        for i in range(0, len(sbtype_list)):
            if sbtype_list[i] == 'sb16':
                sbtype_active = i
        for i in range(0, len(sbtype_list)):
            self.combobox_sbtype.append_text(sbtype_list[i])
            if sbtype_list[i] == self.sblaster_sbtype:
                sbtype_active = i
        self.combobox_sbtype.set_active(sbtype_active)

        self.label_sbbase = Gtk.Label(
            label = _("IO address"),
            halign = Gtk.Align.START,
            tooltip_text = _("The IO address of the soundblaster.")
            )

        self.combobox_sbbase = Gtk.ComboBoxText(
            tooltip_text = _("The IO address of the soundblaster.")
            )

        sbbase_list = ['220', '240', '260', '280', '2a0', '2c0', '2e0', '300']

        for i in range(0, len(sbbase_list)):
            self.combobox_sbbase.append_text(sbbase_list[i])
            if sbbase_list[i] == self.sblaster_sbbase:
                sbbase_active = i
        self.combobox_sbbase.set_active(sbbase_active)

        self.label_irq = Gtk.Label(
            label = _("IRQ number"),
            halign = Gtk.Align.START,
            tooltip_text = _("The IRQ number of the soundblaster.")
            )

        self.combobox_irq = Gtk.ComboBoxText(
            tooltip_text = _("The IRQ number of the soundblaster.")
            )

        irq_list = ['3', '5', '7', '9', '10', '11', '12']

        for i in range(0, len(irq_list)):
            self.combobox_irq.append_text(irq_list[i])
            if irq_list[i] == self.sblaster_irq:
                irq_active = i
        self.combobox_irq.set_active(irq_active)

        self.label_dma = Gtk.Label(
            label = _("DMA number"),
            halign = Gtk.Align.START,
            tooltip_text = _("The DMA number of the soundblaster.")
            )

        self.combobox_dma = Gtk.ComboBoxText(
            tooltip_text = _("The DMA number of the soundblaster.")
            )

        dma_list = ['0', '1', '3', '5', '6', '7']

        for i in range(0, len(dma_list)):
            self.combobox_dma.append_text(dma_list[i])
            if dma_list[i] == self.sblaster_dma:
                dma_active = i
        self.combobox_dma.set_active(dma_active)

        self.label_hdma = Gtk.Label(
            label = _("High DMA number"),
            halign = Gtk.Align.START,
            tooltip_text = _("The High DMA number of the soundblaster.")
            )

        self.combobox_hdma = Gtk.ComboBoxText(
            tooltip_text = _("The High DMA number of the soundblaster.")
            )

        hdma_list = ['0', '1', '3', '5', '6', '7']

        for i in range(0, len(hdma_list)):
            self.combobox_hdma.append_text(hdma_list[i])
            if hdma_list[i] == self.sblaster_hdma:
                hdma_active = i
        self.combobox_hdma.set_active(hdma_active)

        self.label_sbmixer = Gtk.Label(
            label = _("Soundblaster mixer"),
            halign = Gtk.Align.START,
            tooltip_text = _("Allow the soundblaster mixer to modify the DOSBox mixer.")
            )

        self.switch_sbmixer = Gtk.Switch(
            tooltip_text = _("Allow the soundblaster mixer to modify the DOSBox mixer."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.sblaster_sbmixer)
            )

        self.label_oplmode = Gtk.Label(
            label = _("OPL emulation"),
            halign = Gtk.Align.START,
            tooltip_text = _("Type of OPL emulation. On 'auto' the mode is determined\nby sblaster type. All OPL modes are Adlib-compatible,\nexcept for 'cms'.")
            )

        self.combobox_oplmode = Gtk.ComboBoxText(
            tooltip_text = _("Type of OPL emulation. On 'auto' the mode is determined\nby sblaster type. All OPL modes are Adlib-compatible,\nexcept for 'cms'.")
            )

        # TODO Remove if scecific svn-daum version exists
        if self.dosbox_version == 'svn_daum':
            oplmode_list = [
                'auto', 'cms', 'opl2', 'dualopl2', 'opl3', 'none', 
                'hardware', 'hardwaregb'
                ]
        elif self.dosbox_version == 'svn':
            oplmode_list = ['auto', 'cms', 'opl2', 'dualopl2', 'opl3', 'opl3gold', 'none']
        else:
            oplmode_list = ['auto', 'cms', 'opl2', 'dualopl2', 'opl3', 'none']

        oplmode_active = 0
        for i in range(0, len(oplmode_list)):
            self.combobox_oplmode.append_text(oplmode_list[i])
            if oplmode_list[i] == self.sblaster_oplmode:
                oplmode_active = i
        self.combobox_oplmode.set_active(oplmode_active)

        self.label_oplemu = Gtk.Label(
            label = _("OPL emulation provider"),
            halign = Gtk.Align.START,
            tooltip_text = _("Provider for the OPL emulation.\ncompat might provide better quality (see oplrate as well).")
            )

        self.combobox_oplemu = Gtk.ComboBoxText(
            tooltip_text = _("Provider for the OPL emulation.\ncompat might provide better quality (see oplrate as well).")
            )

        oplemu_list = ['default', 'compat', 'fast']

        for i in range(0, len(oplemu_list)):
            self.combobox_oplemu.append_text(oplemu_list[i])
            if oplemu_list[i] == self.sblaster_oplemu:
                oplemu_active = i
        self.combobox_oplemu.set_active(oplemu_active)

        self.label_oplrate = Gtk.Label(
            label = _("OPL sample rate"),
            halign = Gtk.Align.START,
            tooltip_text = _("Sample rate of OPL music emulation.\nUse 49716 for highest quality (set the mixer rate accordingly).")
            )

        self.combobox_oplrate = Gtk.ComboBoxText(
            tooltip_text = _("Sample rate of OPL music emulation.\nUse 49716 for highest quality (set the mixer rate accordingly).")
            )

        oplrate_list = ['8000', '11025', '16000', '22050', '32000', '44100', '48000', '49716']

        for i in range(0, len(oplrate_list)):
            self.combobox_oplrate.append_text(oplrate_list[i])
            if oplrate_list[i] == self.sblaster_oplrate:
                oplrate_active = i
        self.combobox_oplrate.set_active(oplrate_active)

        self.grid_sblaster.attach(self.label_sbtype, 0, 0, 1, 1)
        self.grid_sblaster.attach(self.combobox_sbtype, 1, 0, 1, 1)
        self.grid_sblaster.attach(self.label_sbbase, 0, 1, 1, 1)
        self.grid_sblaster.attach(self.combobox_sbbase, 1, 1, 1, 1)
        self.grid_sblaster.attach(self.label_irq, 0, 2, 1, 1)
        self.grid_sblaster.attach(self.combobox_irq, 1, 2, 1, 1)
        self.grid_sblaster.attach(self.label_dma, 0, 3, 1, 1)
        self.grid_sblaster.attach(self.combobox_dma, 1, 3, 1, 1)
        self.grid_sblaster.attach(self.label_hdma, 0, 4, 1, 1)
        self.grid_sblaster.attach(self.combobox_hdma, 1, 4, 1, 1)
        self.grid_sblaster.attach(self.label_sbmixer, 0, 5, 1, 1)
        self.grid_sblaster.attach(self.switch_sbmixer, 1, 5, 1, 1)
        self.grid_sblaster.attach(self.label_oplmode, 0, 6, 1, 1)
        self.grid_sblaster.attach(self.combobox_oplmode, 1, 6, 1, 1)
        self.grid_sblaster.attach(self.label_oplemu, 0, 7, 1, 1)
        self.grid_sblaster.attach(self.combobox_oplemu, 1, 7, 1, 1)
        self.grid_sblaster.attach(self.label_oplrate, 0, 8, 1, 1)
        self.grid_sblaster.attach(self.combobox_oplrate, 1, 8, 1, 1)

        self.scrolled_window_sblaster = Gtk.ScrolledWindow()
        self.scrolled_window_sblaster.add(self.grid_sblaster)

        self.label_sblaster = Gtk.Label(
            label = _("SoundBlaster")
            )
#################################################################
        self.grid_gus = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_gus = Gtk.Label(
            label = _("Gravis Ultrasound"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable the Gravis Ultrasound emulation.")
            )

        self.switch_gus = Gtk.Switch(
            tooltip_text = _("Enable the Gravis Ultrasound emulation."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.gus_gus)
            )

        self.label_gusrate = Gtk.Label(
            label = _("Sample rate"),
            halign = Gtk.Align.START,
            tooltip_text = _("Sample rate of Ultrasound emulation.")
            )

        self.combobox_gusrate = Gtk.ComboBoxText(
            tooltip_text = _("Sample rate of Ultrasound emulation.")
            )

        gusrate_list = ['8000', '11025', '16000', '22050', '32000', '44100', '48000', '49716']

        for i in range(0, len(gusrate_list)):
            self.combobox_gusrate.append_text(gusrate_list[i])
            if gusrate_list[i] == self.gus_gusrate:
                gusrate_active = i
        self.combobox_gusrate.set_active(gusrate_active)

        self.label_gusbase = Gtk.Label(
            label = _("IO address"),
            halign = Gtk.Align.START,
            tooltip_text = _("The IO base address of the Gravis Ultrasound.")
            )

        self.combobox_gusbase = Gtk.ComboBoxText(
            tooltip_text = _("The IO base address of the Gravis Ultrasound.")
            )

        gusbase_list = ['220', '240', '260', '280', '2a0', '2c0', '2e0', '300']

        for i in range(0, len(gusbase_list)):
            self.combobox_gusbase.append_text(gusbase_list[i])
            if gusbase_list[i] == self.gus_gusbase:
                gusbase_active = i
        self.combobox_gusbase.set_active(gusbase_active)

        self.label_gusirq = Gtk.Label(
            label = _("IRQ number"),
            halign = Gtk.Align.START,
            tooltip_text = _("The IRQ number of the Gravis Ultrasound.")
            )

        self.combobox_gusirq = Gtk.ComboBoxText(
            tooltip_text = _("The IRQ number of the Gravis Ultrasound.")
            )

        gusirq_list = ['3', '5', '7', '9', '10', '11', '12']

        for i in range(0, len(gusirq_list)):
            self.combobox_gusirq.append_text(gusirq_list[i])
            if gusirq_list[i] == self.gus_gusirq:
                gusirq_active = i
        self.combobox_gusirq.set_active(gusirq_active)

        self.label_gusdma = Gtk.Label(
            label = _("DMA number"),
            halign = Gtk.Align.START,
            tooltip_text = _("The DMA channel of the Gravis Ultrasound.")
            )

        self.combobox_gusdma = Gtk.ComboBoxText(
            tooltip_text = _("The DMA channel of the Gravis Ultrasound.")
            )

        gusdma_list = ['0', '1', '3', '5', '6', '7']

        for i in range(0, len(gusdma_list)):
            self.combobox_gusdma.append_text(gusdma_list[i])
            if gusdma_list[i] == self.gus_gusdma:
                gusdma_active = i
        self.combobox_gusdma.set_active(gusdma_active)

        self.label_ultradir = Gtk.Label(
            label = _("Ultrasound directory"),
            halign = Gtk.Align.START,
            tooltip_text = _("Path to Ultrasound directory. In this directory\nthere should be a MIDI directory that contains\nthe patch files for GUS playback. Patch sets used\nwith Timidity should work fine.")
            )

        self.entry_ultradir = Gtk.Entry(
            tooltip_text = _("Path to Ultrasound directory. In this directory\nthere should be a MIDI directory that contains\nthe patch files for GUS playback. Patch sets used\nwith Timidity should work fine."),
            text = self.gus_ultradir,
            xalign = 0.5
            )

        self.grid_gus.attach(self.label_gus, 0, 0, 1, 1)
        self.grid_gus.attach(self.switch_gus, 1, 0, 1, 1)
        self.grid_gus.attach(self.label_gusrate, 0, 1, 1, 1)
        self.grid_gus.attach(self.combobox_gusrate, 1, 1, 1, 1)
        self.grid_gus.attach(self.label_gusbase, 0, 2, 1, 1)
        self.grid_gus.attach(self.combobox_gusbase, 1, 2, 1, 1)
        self.grid_gus.attach(self.label_gusirq, 0, 3, 1, 1)
        self.grid_gus.attach(self.combobox_gusirq, 1, 3, 1, 1)
        self.grid_gus.attach(self.label_gusdma, 0, 4, 1, 1)
        self.grid_gus.attach(self.combobox_gusdma, 1, 4, 1, 1)
        self.grid_gus.attach(self.label_ultradir, 0, 5, 1, 1)
        self.grid_gus.attach(self.entry_ultradir, 1, 5, 1, 1)

        self.scrolled_window_gus = Gtk.ScrolledWindow()
        self.scrolled_window_gus.add(self.grid_gus)

        self.label_gus = Gtk.Label(
            label = _("Gravis Ultrasound")
            )
#################################################################
        self.grid_speaker = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_pcspeaker = Gtk.Label(
            label = _("PC-speaker"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable PC-Speaker emulation.")
            )

        self.switch_pcspeaker = Gtk.Switch(
            tooltip_text = _("Enable PC-Speaker emulation."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.speaker_pcspeaker)
            )

        self.label_pcrate = Gtk.Label(
            label = _("PC-speaker sample rate"),
            halign = Gtk.Align.START,
            tooltip_text = _("Sample rate of the PC-Speaker sound generation.")
            )

        self.combobox_pcrate = Gtk.ComboBoxText(
            tooltip_text = _("Sample rate of the PC-Speaker sound generation.")
            )

        pcrate_list = ['8000', '11025', '16000', '22050', '32000', '44100', '48000', '49716']

        for i in range(0, len(pcrate_list)):
            self.combobox_pcrate.append_text(pcrate_list[i])
            if pcrate_list[i] == self.speaker_pcrate:
                pcrate_active = i
        self.combobox_pcrate.set_active(pcrate_active)

        self.label_tandy = Gtk.Label(
            label = _("Tandy Sound System"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable Tandy Sound System emulation.\nFor 'auto', emulation is present only if\nmachine is set to 'tandy'.")
            )

        self.combobox_tandy = Gtk.ComboBoxText(
            tooltip_text = _("Enable Tandy Sound System emulation.\nFor 'auto', emulation is present only if\nmachine is set to 'tandy'.")
            )

        tandy_list = ['auto', 'on', 'off']

        for i in range(0, len(tandy_list)):
            self.combobox_tandy.append_text(tandy_list[i])
            if tandy_list[i] == self.speaker_tandy:
                tandy_active = i
        self.combobox_tandy.set_active(tandy_active)

        self.label_tandyrate = Gtk.Label(
            label = _("Tandy sample rate"),
            halign = Gtk.Align.START,
            tooltip_text = _("Sample rate of the Tandy 3-Voice generation.")
            )

        self.combobox_tandyrate = Gtk.ComboBoxText(
            tooltip_text = _("Sample rate of the Tandy 3-Voice generation.")
            )

        tandyrate_list = ['8000', '11025', '16000', '22050', '32000', '44100', '48000', '49716']

        for i in range(0, len(tandyrate_list)):
            self.combobox_tandyrate.append_text(tandyrate_list[i])
            if tandyrate_list[i] == self.speaker_tandyrate:
                tandyrate_active = i
        self.combobox_tandyrate.set_active(tandyrate_active)

        self.label_disney = Gtk.Label(
            label = _("Disney Sound Source"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable Disney Sound Source emulation.\n(Covox Voice Master and Speech Thing compatible).")
            )

        self.switch_disney = Gtk.Switch(
            tooltip_text = _("Enable Disney Sound Source emulation.\n(Covox Voice Master and Speech Thing compatible)."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.speaker_disney)
            )

        self.grid_speaker.attach(self.label_pcspeaker, 0, 0, 1, 1)
        self.grid_speaker.attach(self.switch_pcspeaker, 1, 0, 1, 1)
        self.grid_speaker.attach(self.label_pcrate, 0, 1, 1, 1)
        self.grid_speaker.attach(self.combobox_pcrate, 1, 1, 1, 1)
        self.grid_speaker.attach(self.label_tandy, 0, 2, 1, 1)
        self.grid_speaker.attach(self.combobox_tandy, 1, 2, 1, 1)
        self.grid_speaker.attach(self.label_tandyrate, 0, 3, 1, 1)
        self.grid_speaker.attach(self.combobox_tandyrate, 1, 3, 1, 1)
        self.grid_speaker.attach(self.label_disney, 0, 4, 1, 1)
        self.grid_speaker.attach(self.switch_disney, 1, 4, 1, 1)

        self.scrolled_window_speaker = Gtk.ScrolledWindow()
        self.scrolled_window_speaker.add(self.grid_speaker)

        self.label_speaker = Gtk.Label(
            label = _("Speaker")
            )
#################################################################
        self.grid_joystick = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_joysticktype = Gtk.Label(
            label = _("Joystick type"),
            halign = Gtk.Align.START,
            tooltip_text = _("Type of joystick to emulate:\n" + \
            "auto (choose emulation depending on real joystick(s)),\n" + \
            "none (disable joystick emulation),\n2axis (supports two joysticks),\n" + \
            "4axis (supports one joystick, first joystick used),\n" + \
            "4axis_2 (supports one joystick, second joystick used),\n" + \
            "fcs (Thrustmaster),\nch (CH Flightstick).\n\n" + \
            "(Remember to reset dosbox's mapperfile if you saved it earlier).")
            )

        self.combobox_joysticktype = Gtk.ComboBoxText(
            tooltip_text = _("Type of joystick to emulate:\n" + \
            "auto (choose emulation depending on real joystick(s)),\n" + \
            "none (disable joystick emulation),\n2axis (supports two joysticks),\n" + \
            "4axis (supports one joystick, first joystick used),\n" + \
            "4axis_2 (supports one joystick, second joystick used),\n" + \
            "fcs (Thrustmaster),\nch (CH Flightstick).\n\n" + \
            "(Remember to reset dosbox's mapperfile if you saved it earlier).")
            )

        joysticktype_list = ['auto', 'none', '2axis', '4axis', '4axis_2', 'fcs', 'ch']

        for i in range(0, len(joysticktype_list)):
            self.combobox_joysticktype.append_text(joysticktype_list[i])
            if joysticktype_list[i] == self.joystick_joysticktype:
                joysticktype_active = i
        self.combobox_joysticktype.set_active(joysticktype_active)

        self.label_timed = Gtk.Label(
            label = _("Timed intervals for axis"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable timed intervals for axis. Experiment with this option,\nif your joystick drifts (away).")
            )

        self.switch_timed = Gtk.Switch(
            tooltip_text = _("Enable timed intervals for axis. Experiment with this option,\nif your joystick drifts (away)."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.joystick_timed)
            )

        self.label_autofire = Gtk.Label(
            label = _("Autofire"),
            halign = Gtk.Align.START,
            tooltip_text = _("Continuously fires as long as you keep the button pressed.")
            )

        self.switch_autofire = Gtk.Switch(
            tooltip_text = _("Continuously fires as long as you keep the button pressed."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.joystick_autofire)
            )

        self.label_swap34 = Gtk.Label(
            label = _("Swap axis"),
            halign = Gtk.Align.START,
            tooltip_text = _("Swap the 3rd and the 4th axis. Can be useful for certain joysticks.")
            )

        self.switch_swap34 = Gtk.Switch(
            tooltip_text = _("Swap the 3rd and the 4th axis. Can be useful for certain joysticks."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.joystick_swap34)
            )

        self.label_buttonwrap = Gtk.Label(
            label = _("Button wrapping"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable button wrapping at the number of emulated buttons.")
            )

        self.switch_buttonwrap = Gtk.Switch(
            tooltip_text = _("Enable button wrapping at the number of emulated buttons."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.joystick_buttonwrap)
            )

        self.grid_joystick.attach(self.label_joysticktype, 0, 0, 1, 1)
        self.grid_joystick.attach(self.combobox_joysticktype, 1, 0, 1, 1)
        self.grid_joystick.attach(self.label_timed, 0, 1, 1, 1)
        self.grid_joystick.attach(self.switch_timed, 1, 1, 1, 1)
        self.grid_joystick.attach(self.label_autofire, 0, 2, 1, 1)
        self.grid_joystick.attach(self.switch_autofire, 1, 2, 1, 1)
        self.grid_joystick.attach(self.label_swap34, 0, 3, 1, 1)
        self.grid_joystick.attach(self.switch_swap34, 1, 3, 1, 1)
        self.grid_joystick.attach(self.label_buttonwrap, 0, 4, 1, 1)
        self.grid_joystick.attach(self.switch_buttonwrap, 1, 4, 1, 1)

        self.scrolled_window_joystick = Gtk.ScrolledWindow()
        self.scrolled_window_joystick.add(self.grid_joystick)

        self.label_joystick = Gtk.Label(
            label = _("Joystick")
            )
#################################################################
        self.grid_serial = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_serial1 = Gtk.Label(
            label = _("Device connected to com port 1"),
            halign = Gtk.Align.START,
            tooltip_text = _("Set type of device connected to com port.")
            )

        self.combobox_serial1 = Gtk.ComboBoxText(
            tooltip_text = _("Set type of device connected to com port.")
            )

        self.label_serial1_parameters = Gtk.Label(
            label = _("Additional parameters:"),
            halign = Gtk.Align.START,
            tooltip_text = _("Parameter for all types: irq (optional).\n" + \
            "For directserial: realport (required), rxdelay (optional).\n" + \
            "For modem: listenport (optional).\n" + \
            "For nullmodem: server, rxdelay, txdelay, telnet, usedtr,\n" + \
            "transparent, port, inhsocket (all optional).\n" + \
            "For modem: listenport (optional).\n\n" + \
            "Additional parameters must be in the form\n" + \
            "of parameter:value (Example: listenport:5000).")
            )

        self.entry_serial1_parameters = Gtk.Entry(
            tooltip_text = _("Parameter for all types: irq (optional).\n" + \
            "For directserial: realport (required), rxdelay (optional).\n" + \
            "For modem: listenport (optional).\n" + \
            "For nullmodem: server, rxdelay, txdelay, telnet, usedtr,\n" + \
            "transparent, port, inhsocket (all optional).\n" + \
            "For modem: listenport (optional).\n\n" + \
            "Additional parameters must be in the form\n" + \
            "of parameter:value (Example: listenport:5000)."),
            xalign = 0.5
            )

        if ' ' in self.serial_serial1:
            serial1_list = self.serial_serial1.split(' ')
            serial1_list.remove(serial1_list[0])
            serial1_parameters = ' '.join(serial1_list)
            self.entry_serial1_parameters.set_text(serial1_parameters)

        self.label_serial2 = Gtk.Label(
            label = _("Device connected to com port 2"),
            halign = Gtk.Align.START,
            tooltip_text = _("Set type of device connected to com port.")
            )

        self.combobox_serial2 = Gtk.ComboBoxText(
            tooltip_text = _("Set type of device connected to com port.")
            )

        self.label_serial2_parameters = Gtk.Label(
            label = _("Additional parameters:"),
            halign = Gtk.Align.START,
            tooltip_text = _("Parameter for all types: irq (optional).\n" + \
            "For directserial: realport (required), rxdelay (optional).\n" + \
            "For modem: listenport (optional).\n" + \
            "For nullmodem: server, rxdelay, txdelay, telnet, usedtr,\n" + \
            "transparent, port, inhsocket (all optional).\n" + \
            "For modem: listenport (optional).\n\n" + \
            "Additional parameters must be in the form\n" + \
            "of parameter:value (Example: listenport:5000).")
            )

        self.entry_serial2_parameters = Gtk.Entry(
            tooltip_text = _("Parameter for all types: irq (optional).\n" + \
            "For directserial: realport (required), rxdelay (optional).\n" + \
            "For modem: listenport (optional).\n" + \
            "For nullmodem: server, rxdelay, txdelay, telnet, usedtr,\n" + \
            "transparent, port, inhsocket (all optional).\n" + \
            "For modem: listenport (optional).\n\n" + \
            "Additional parameters must be in the form\n" + \
            "of parameter:value (Example: listenport:5000)."),
            xalign = 0.5
            )

        if ' ' in self.serial_serial2:
            serial2_list = self.serial_serial2.split(' ')
            serial2_list.remove(serial2_list[0])
            serial2_parameters = ' '.join(serial2_list)
            self.entry_serial2_parameters.set_text(serial2_parameters)

        self.label_serial3 = Gtk.Label(
            label = _("Device connected to com port 3"),
            halign = Gtk.Align.START,
            tooltip_text = _("Set type of device connected to com port.")
            )

        self.combobox_serial3 = Gtk.ComboBoxText(
            tooltip_text = _("Set type of device connected to com port.")
            )

        self.label_serial3_parameters = Gtk.Label(
            label = _("Additional parameters:"),
            halign = Gtk.Align.START,
            tooltip_text = _("Parameter for all types: irq (optional).\n" + \
            "For directserial: realport (required), rxdelay (optional).\n" + \
            "For modem: listenport (optional).\n" + \
            "For nullmodem: server, rxdelay, txdelay, telnet, usedtr,\n" + \
            "transparent, port, inhsocket (all optional).\n" + \
            "For modem: listenport (optional).\n\n" + \
            "Additional parameters must be in the form\n" + \
            "of parameter:value (Example: listenport:5000).")
            )

        self.entry_serial3_parameters = Gtk.Entry(
            tooltip_text = _("Parameter for all types: irq (optional).\n" + \
            "For directserial: realport (required), rxdelay (optional).\n" + \
            "For modem: listenport (optional).\n" + \
            "For nullmodem: server, rxdelay, txdelay, telnet, usedtr,\n" + \
            "transparent, port, inhsocket (all optional).\n" + \
            "For modem: listenport (optional).\n\n" + \
            "Additional parameters must be in the form\n" + \
            "of parameter:value (Example: listenport:5000)."),
            xalign = 0.5
            )

        if ' ' in self.serial_serial3:
            serial3_list = self.serial_serial3.split(' ')
            serial3_list.remove(serial3_list[0])
            serial3_parameters = ' '.join(serial3_list)
            self.entry_serial3_parameters.set_text(serial3_parameters)

        self.label_serial4 = Gtk.Label(
            label = _("Device connected to com port 4"),
            halign = Gtk.Align.START,
            tooltip_text = _("Set type of device connected to com port.")
            )

        self.combobox_serial4 = Gtk.ComboBoxText(
            tooltip_text = _("Set type of device connected to com port.")
            )

        self.label_serial4_parameters = Gtk.Label(
            label = _("Additional parameters:"),
            halign = Gtk.Align.START,
            tooltip_text = _("Parameter for all types: irq (optional).\n" + \
            "For directserial: realport (required), rxdelay (optional).\n" + \
            "For modem: listenport (optional).\n" + \
            "For nullmodem: server, rxdelay, txdelay, telnet, usedtr,\n" + \
            "transparent, port, inhsocket (all optional).\n" + \
            "For modem: listenport (optional).\n\n" + \
            "Additional parameters must be in the form\n" + \
            "of parameter:value (Example: listenport:5000).")
            )

        self.entry_serial4_parameters = Gtk.Entry(
            tooltip_text = _("Parameter for all types: irq (optional).\n" + \
            "For directserial: realport (required), rxdelay (optional).\n" + \
            "For modem: listenport (optional).\n" + \
            "For nullmodem: server, rxdelay, txdelay, telnet, usedtr,\n" + \
            "transparent, port, inhsocket (all optional).\n" + \
            "For modem: listenport (optional).\n\n" + \
            "Additional parameters must be in the form\n" + \
            "of parameter:value (Example: listenport:5000)."),
            xalign = 0.5
            )

        if ' ' in self.serial_serial4:
            serial4_list = self.serial_serial4.split(' ')
            serial4_list.remove(serial4_list[0])
            serial4_parameters = ' '.join(serial4_list)
            self.entry_serial4_parameters.set_text(serial4_parameters)

        serial_list = ['disabled', 'dummy', 'modem', 'nullmodem', 'directserial']

        for i in range(0, len(serial_list)):
            self.combobox_serial1.append_text(serial_list[i])
            self.combobox_serial2.append_text(serial_list[i])
            self.combobox_serial3.append_text(serial_list[i])
            self.combobox_serial4.append_text(serial_list[i])
            if serial_list[i] == self.serial_serial1.split(' ')[0]:
                serial1_active = i
            if serial_list[i] == self.serial_serial2.split(' ')[0]:
                serial2_active = i
            if serial_list[i] == self.serial_serial3.split(' ')[0]:
                serial3_active = i
            if serial_list[i] == self.serial_serial4.split(' ')[0]:
                serial4_active = i
        self.combobox_serial1.set_active(serial1_active)
        self.combobox_serial2.set_active(serial2_active)
        self.combobox_serial3.set_active(serial3_active)
        self.combobox_serial4.set_active(serial4_active)

        self.grid_serial.attach(self.label_serial1, 0, 0, 1, 1)
        self.grid_serial.attach(self.combobox_serial1, 1, 0, 1, 1)
        self.grid_serial.attach(self.label_serial1_parameters, 0, 1, 1, 1)
        self.grid_serial.attach(self.entry_serial1_parameters, 1, 1, 1, 1)
        self.grid_serial.attach(self.label_serial2, 0, 2, 1, 1)
        self.grid_serial.attach(self.combobox_serial2, 1, 2, 1, 1)
        self.grid_serial.attach(self.label_serial2_parameters, 0, 3, 1, 1)
        self.grid_serial.attach(self.entry_serial2_parameters, 1, 3, 1, 1)
        self.grid_serial.attach(self.label_serial3, 0, 4, 1, 1)
        self.grid_serial.attach(self.combobox_serial3, 1, 4, 1, 1)
        self.grid_serial.attach(self.label_serial3_parameters, 0, 5, 1, 1)
        self.grid_serial.attach(self.entry_serial3_parameters, 1, 5, 1, 1)
        self.grid_serial.attach(self.label_serial4, 0, 6, 1, 1)
        self.grid_serial.attach(self.combobox_serial4, 1, 6, 1, 1)
        self.grid_serial.attach(self.label_serial4_parameters, 0, 7, 1, 1)
        self.grid_serial.attach(self.entry_serial4_parameters, 1, 7, 1, 1)

        self.scrolled_window_serial = Gtk.ScrolledWindow()
        self.scrolled_window_serial.add(self.grid_serial)

        self.label_serial = Gtk.Label(
            label = _("Com port device")
            )
#################################################################
        self.grid_dos = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_xms = Gtk.Label(
            label = _("XMS"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable XMS support.")
            )

        self.switch_xms = Gtk.Switch(
            tooltip_text = _("Enable XMS support."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.dos_xms)
            )

        self.label_ems = Gtk.Label(
            label = _("EMS"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable EMS support.")
            )

        self.switch_ems = Gtk.Switch(
            tooltip_text = _("Enable EMS support."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.dos_ems)
            )

        self.label_umb = Gtk.Label(
            label = _("UMB"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable UMB support.")
            )

        self.switch_umb = Gtk.Switch(
            tooltip_text = _("Enable UMB support."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.dos_umb)
            )

        self.label_keyboardlayout = Gtk.Label(
            label = _("Keyboard lauout:"),
            halign = Gtk.Align.START,
            tooltip_text = _("Keyboard layout.")
            )

        self.combobox_keyboardlayout = Gtk.ComboBoxText(
            tooltip_text = _("Keyboard layout.")
            )

        self.entry_keyboardlayout = Gtk.Entry(
            tooltip_text = _("Language code of the keyboard layout."),
            placeholder_text = _("Keyboard layout code"),
            xalign = 0.5,
            no_show_all = True
            )

        keyboardlayout_list = ['auto', 'none', _("custom")]

        for i in range(0, len(keyboardlayout_list)):
            self.combobox_keyboardlayout.append_text(keyboardlayout_list[i])
            if keyboardlayout_list[i] == self.dos_keyboardlayout:
                keyboardlayout_active = i
            elif (self.dos_keyboardlayout != 'auto') and (self.dos_keyboardlayout != 'none'):
                keyboardlayout_active = 2
                self.entry_keyboardlayout.set_visible(True)
                self.entry_keyboardlayout.set_text(self.dos_keyboardlayout)

        self.combobox_keyboardlayout.set_active(keyboardlayout_active)

        self.combobox_keyboardlayout.connect('changed', self.cb_combobox_keyboardlayout)

        self.grid_dos.attach(self.label_xms, 0, 0, 1, 1)
        self.grid_dos.attach(self.switch_xms, 1, 0, 1, 1)
        self.grid_dos.attach(self.label_ems, 0, 1, 1, 1)
        self.grid_dos.attach(self.switch_ems, 1, 1, 1, 1)
        self.grid_dos.attach(self.label_umb, 0, 2, 1, 1)
        self.grid_dos.attach(self.switch_umb, 1, 2, 1, 1)
        self.grid_dos.attach(self.label_keyboardlayout, 0, 3, 1, 1)
        self.grid_dos.attach(self.combobox_keyboardlayout, 1, 3, 1, 1)
        self.grid_dos.attach(self.entry_keyboardlayout, 1, 4, 1, 1)

        self.scrolled_window_dos = Gtk.ScrolledWindow()
        self.scrolled_window_dos.add(self.grid_dos)

        self.label_dos = Gtk.Label(
            label = _("DOS")
            )
#################################################################
        self.grid_ipx = Gtk.Grid(
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            row_spacing = 5,
            column_spacing = 5,
            column_homogeneous = True,
            #row_homogeneous = True,
            halign = Gtk.Align.FILL,
            valign = Gtk.Align.START,
            #width_request = 600,
            )

        self.label_ipx = Gtk.Label(
            label = _("IPX"),
            halign = Gtk.Align.START,
            tooltip_text = _("Enable ipx over UDP/IP emulation.")
            )

        self.switch_ipx = Gtk.Switch(
            tooltip_text = _("Enable ipx over UDP/IP emulation."),
            halign = Gtk.Align.END,
            active = self.dosbox_config_to_bool(self.ipx_ipx)
            )

        self.grid_ipx.attach(self.label_ipx, 0, 0, 1, 1)
        self.grid_ipx.attach(self.switch_ipx, 1, 0, 1, 1)

        self.scrolled_window_ipx = Gtk.ScrolledWindow()
        self.scrolled_window_ipx.add(self.grid_ipx)

        self.label_ipx = Gtk.Label(
            label = _("IPX")
            )
#################################################################
        self.notebook = Gtk.Notebook(
            tab_pos = Gtk.PositionType.LEFT,
            scrollable = True
            )
        self.notebook.append_page(self.scrolled_window_sdl, self.label_sdl)
        self.notebook.append_page(self.scrolled_window_dosbox, self.label_dosbox)
        self.notebook.append_page(self.scrolled_window_render, self.label_render)
        self.notebook.append_page(self.scrolled_window_cpu, self.label_cpu)
        self.notebook.append_page(self.scrolled_window_mixer, self.label_mixer)
        self.notebook.append_page(self.scrolled_window_midi, self.label_midi)
        self.notebook.append_page(self.scrolled_window_sblaster, self.label_sblaster)
        self.notebook.append_page(self.scrolled_window_gus, self.label_gus)
        self.notebook.append_page(self.scrolled_window_speaker, self.label_speaker)
        self.notebook.append_page(self.scrolled_window_joystick, self.label_joystick)
        self.notebook.append_page(self.scrolled_window_serial, self.label_serial)
        self.notebook.append_page(self.scrolled_window_dos, self.label_dos)
        self.notebook.append_page(self.scrolled_window_ipx, self.label_ipx)
#################################################################

        self.button_save = Gtk.Button(
            label = _("Save and quit"),
            margin_left = 10,
            margin_right = 10,
            margin_top = 10,
            margin_bottom = 10,
            )

        self.button_save.connect('clicked', self.cb_button_save)

#################################################################

        self.box1 = Gtk.Box(
            orientation = Gtk.Orientation.VERTICAL,
            #spacing = 5
            )

        self.box1.pack_start(self.notebook, True, True, 0)
        self.box1.pack_start(self.button_save, False, True, 0)

        self.main_window.add(self.box1)

        self.main_window.show_all()

    def quit_app(self, window, event):
        Gtk.main_quit()

    def get_global_settings(self):

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

    def dosbox_config_global_load(self, config_path):

        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_path)

        if not config_parser.has_section('sdl'):
            config_parser.add_section('sdl')

        if config_parser.has_option('sdl', 'fullscreen'):
            self.sdl_fullscreen_global = config_parser.get('sdl', 'fullscreen')
        else:
            self.sdl_fullscreen_global = 'false'
            config_parser.set('sdl', 'fullscreen', self.sdl_fullscreen_global)

        if config_parser.has_option('sdl', 'fulldouble'):
            self.sdl_fulldouble_global = config_parser.get('sdl', 'fulldouble')
        else:
            self.sdl_fulldouble_global = 'false'
            config_parser.set('sdl', 'fulldouble', self.sdl_fulldouble_global)

        if config_parser.has_option('sdl', 'fullresolution'):
            self.sdl_fullresolution_global = config_parser.get('sdl', 'fullresolution')
        else:
            self.sdl_fullresolution_global = 'original'
            config_parser.set('sdl', 'fullresolution', self.sdl_fullresolution_global)

        if config_parser.has_option('sdl', 'windowresolution'):
            self.sdl_windowresolution_global = config_parser.get('sdl', 'windowresolution')
        else:
            self.sdl_windowresolution_global = 'original'
            config_parser.set('sdl', 'windowresolution', self.sdl_windowresolution_global)

        if config_parser.has_option('sdl', 'output'):
            self.sdl_output_global = config_parser.get('sdl', 'output')
        else:
            self.sdl_output_global = 'surface'
            config_parser.set('sdl', 'output', self.sdl_output_global)

        if config_parser.has_option('sdl', 'autolock'):
            self.sdl_autolock_global = config_parser.get('sdl', 'autolock')
        else:
            self.sdl_autolock_global = 'true'
            config_parser.set('sdl', 'autolock', self.sdl_autolock_global)

        if config_parser.has_option('sdl', 'sensitivity'):
            self.sdl_sensitivity_global = config_parser.get('sdl', 'sensitivity')
        else:
            self.sdl_sensitivity_global = '100'
            config_parser.set('sdl', 'sensitivity', self.sdl_sensitivity_global)

        if config_parser.has_option('sdl', 'waitonerror'):
            self.sdl_waitonerror_global = config_parser.get('sdl', 'waitonerror')
        else:
            self.sdl_waitonerror_global = 'true'
            config_parser.set('sdl', 'waitonerror', self.sdl_waitonerror_global)

        if config_parser.has_option('sdl', 'priority'):
            self.sdl_priority_global = config_parser.get('sdl', 'priority')
        else:
            self.sdl_priority_global = 'higher,normal'
            config_parser.set('sdl', 'priority', self.sdl_priority_global)

        if config_parser.has_option('sdl', 'mapperfile'):
            self.sdl_mapperfile_global = config_parser.get('sdl', 'mapperfile')
        else:
            self.sdl_mapperfile_global = ''
            config_parser.set('sdl', 'mapperfile', self.sdl_mapperfile_global)

        if config_parser.has_option('sdl', 'usescancodes'):
            self.sdl_usescancodes_global = config_parser.get('sdl', 'usescancodes')
        else:
            self.sdl_usescancodes_global = 'true'
            config_parser.set('sdl', 'usescancodes', self.sdl_usescancodes_global)
###########################################################################################
        if not config_parser.has_section('dosbox'):
            config_parser.add_section('dosbox')

        if config_parser.has_option('dosbox', 'language'):
            self.dosbox_language_global = config_parser.get('dosbox', 'language')
        else:
            self.dosbox_language_global = ''
            config_parser.set('dosbox', 'language', self.dosbox_language_global)

        if config_parser.has_option('dosbox', 'machine'):
            self.dosbox_machine_global = config_parser.get('dosbox', 'machine')
        else:
            self.dosbox_machine_global = 'svga_s3'
            config_parser.set('dosbox', 'machine', self.dosbox_machine_global)

        if config_parser.has_option('dosbox', 'captures'):
            self.dosbox_captures_global = config_parser.get('dosbox', 'captures')
        else:
            self.dosbox_captures_global = os.path.abspath(os.getenv('HOME') + '/.games_nebula/dosbox_captures')
            config_parser.set('dosbox', 'captures', self.dosbox_captures_global)

        if config_parser.has_option('dosbox', 'memsize'):
            self.dosbox_memsize_global = config_parser.get('dosbox', 'memsize')
        else:
            self.dosbox_memsize_global = '16'
            config_parser.set('dosbox', 'memsize', self.dosbox_memsize_global)
###########################################################################################
        if not config_parser.has_section('render'):
            config_parser.add_section('render')

        if config_parser.has_option('render', 'frameskip'):
            self.render_frameskip_global = config_parser.get('render', 'frameskip')
        else:
            self.render_frameskip_global = '0'
            config_parser.set('render', 'frameskip', self.render_frameskip_global)

        if config_parser.has_option('render', 'aspect'):
            self.render_aspect_global = config_parser.get('render', 'aspect')
        else:
            self.render_aspect_global = 'false'
            config_parser.set('render', 'aspect', self.render_aspect_global)

        if config_parser.has_option('render', 'scaler'):
            self.render_scaler_global = config_parser.get('render', 'scaler')
        else:
            self.render_scaler_global = 'normal2x'
            config_parser.set('render', 'scaler', self.render_scaler_global)
###########################################################################################
        if not config_parser.has_section('cpu'):
            config_parser.add_section('cpu')

        if config_parser.has_option('cpu', 'core'):
            self.cpu_core_global = config_parser.get('cpu', 'core')
        else:
            self.cpu_core_global = 'auto'
            config_parser.set('cpu', 'core', self.cpu_core_global)

        if config_parser.has_option('cpu', 'cputype'):
            self.cpu_cputype_global = config_parser.get('cpu', 'cputype')
        else:
            self.cpu_cputype_global = 'auto'
            config_parser.set('cpu', 'cputype', self.cpu_cputype_global)

        if config_parser.has_option('cpu', 'cycles'):
            self.cpu_cycles_global = config_parser.get('cpu', 'cycles')
        else:
            self.cpu_cycles_global = 'auto'
            config_parser.set('cpu', 'cycles', self.cpu_cycles_global)

        if config_parser.has_option('cpu', 'cycleup'):
            self.cpu_cycleup_global = config_parser.get('cpu', 'cycleup')
        else:
            self.cpu_cycleup_global = '10'
            config_parser.set('cpu', 'cycleup', self.cpu_cycleup_global)

        if config_parser.has_option('cpu', 'cycledown'):
            self.cpu_cycledown_global = config_parser.get('cpu', 'cycledown')
        else:
            self.cpu_cycledown_global = '20'
            config_parser.set('cpu', 'cycledown', self.cpu_cycledown_global)
###########################################################################################
        if not config_parser.has_section('mixer'):
            config_parser.add_section('mixer')

        if config_parser.has_option('mixer', 'nosound'):
            self.mixer_nosound_global = config_parser.get('mixer', 'nosound')
        else:
            self.mixer_nosound_global = 'false'
            config_parser.set('mixer', 'nosound', self.mixer_nosound_global)

        if config_parser.has_option('mixer', 'rate'):
            self.mixer_rate_global = config_parser.get('mixer', 'rate')
        else:
            self.mixer_rate_global = '44100'
            config_parser.set('mixer', 'rate', self.mixer_rate_global)

        if config_parser.has_option('mixer', 'blocksize'):
            self.mixer_blocksize_global = config_parser.get('mixer', 'blocksize')
        else:
            self.mixer_blocksize_global = '1024'
            config_parser.set('mixer', 'blocksize', self.mixer_blocksize_global)

        if config_parser.has_option('mixer', 'prebuffer'):
            self.mixer_prebuffer_global = config_parser.get('mixer', 'prebuffer')
        else:
            self.mixer_prebuffer_global = '20'
            config_parser.set('mixer', 'prebuffer', self.mixer_prebuffer_global)
###########################################################################################
        if not config_parser.has_section('midi'):
            config_parser.add_section('midi')

        if config_parser.has_option('midi', 'mpu401'):
            self.midi_mpu401_global = config_parser.get('midi', 'mpu401')
        else:
            self.midi_mpu401_global = 'intelligent'
            config_parser.set('midi', 'mpu401', self.midi_mpu401_global)

        if config_parser.has_option('midi', 'mididevice'):
            self.midi_mididevice_global = config_parser.get('midi', 'mididevice')
        else:
            self.midi_mididevice_global = 'default'
            config_parser.set('midi', 'mididevice', self.midi_mididevice_global)

        if config_parser.has_option('midi', 'midiconfig'):
            self.midi_midiconfig_global = config_parser.get('midi', 'midiconfig')
        else:
            self.midi_midiconfig_global = ''
            config_parser.set('midi', 'midiconfig', self.midi_midiconfig_global)
###########################################################################################
        if not config_parser.has_section('sblaster'):
            config_parser.add_section('sblaster')

        if config_parser.has_option('sblaster', 'sbtype'):
            self.sblaster_sbtype_global = config_parser.get('sblaster', 'sbtype')
        else:
            self.sblaster_sbtype_global = 'sb16'
            config_parser.set('sblaster', 'sbtype', self.sblaster_sbtype_global)

        if config_parser.has_option('sblaster', 'sbbase'):
            self.sblaster_sbbase_global = config_parser.get('sblaster', 'sbbase')
        else:
            self.sblaster_sbbase_global = '220'
            config_parser.set('sblaster', 'sbbase', self.sblaster_sbbase_global)

        if config_parser.has_option('sblaster', 'irq'):
            self.sblaster_irq_global = config_parser.get('sblaster', 'irq')
        else:
            self.sblaster_irq_global = '7'
            config_parser.set('sblaster', 'irq', self.sblaster_irq_global)

        if config_parser.has_option('sblaster', 'dma'):
            self.sblaster_dma_global = config_parser.get('sblaster', 'dma')
        else:
            self.sblaster_dma_global = '1'
            config_parser.set('sblaster', 'dma', self.sblaster_dma_global)

        if config_parser.has_option('sblaster', 'hdma'):
            self.sblaster_hdma_global = config_parser.get('sblaster', 'hdma')
        else:
            self.sblaster_hdma_global = '5'
            config_parser.set('sblaster', 'hdma', self.sblaster_hdma_global)

        if config_parser.has_option('sblaster', 'sbmixer'):
            self.sblaster_sbmixer_global = config_parser.get('sblaster', 'sbmixer')
        else:
            self.sblaster_sbmixer_global = 'true'
            config_parser.set('sblaster', 'sbmixer', self.sblaster_sbmixer_global)

        if config_parser.has_option('sblaster', 'oplmode'):
            self.sblaster_oplmode_global = config_parser.get('sblaster', 'oplmode')
        else:
            self.sblaster_oplmode_global = 'auto'
            config_parser.set('sblaster', 'oplmode', self.sblaster_oplmode_global)

        if config_parser.has_option('sblaster', 'oplemu'):
            self.sblaster_oplemu_global = config_parser.get('sblaster', 'oplemu')
        else:
            self.sblaster_oplemu_global = 'default'
            config_parser.set('sblaster', 'oplemu', self.sblaster_oplemu_global)

        if config_parser.has_option('sblaster', 'oplrate'):
            self.sblaster_oplrate_global = config_parser.get('sblaster', 'oplrate')
        else:
            self.sblaster_oplrate_global = '44100'
            config_parser.set('sblaster', 'oplrate', self.sblaster_oplrate_global)
###########################################################################################
        if not config_parser.has_section('gus'):
            config_parser.add_section('gus')

        if config_parser.has_option('gus', 'gus'):
            self.gus_gus_global = config_parser.get('gus', 'gus')
        else:
            self.gus_gus_global = 'false'
            config_parser.set('gus', 'gus', self.gus_gus_global)

        if config_parser.has_option('gus', 'gusrate'):
            self.gus_gusrate_global = config_parser.get('gus', 'gusrate')
        else:
            self.gus_gusrate_global = '44100'
            config_parser.set('gus', 'gusrate', self.gus_gusrate_global)

        if config_parser.has_option('gus', 'gusbase'):
            self.gus_gusbase_global = config_parser.get('gus', 'gusbase')
        else:
            self.gus_gusbase_global = '240'
            config_parser.set('gus', 'gusbase', self.gus_gusbase_global)

        if config_parser.has_option('gus', 'gusirq'):
            self.gus_gusirq_global = config_parser.get('gus', 'gusirq')
        else:
            self.gus_gusirq_global = '5'
            config_parser.set('gus', 'gusirq', self.gus_gusirq_global)

        if config_parser.has_option('gus', 'gusdma'):
            self.gus_gusdma_global = config_parser.get('gus', 'gusdma')
        else:
            self.gus_gusdma_global = '3'
            config_parser.set('gus', 'gusdma', self.gus_gusdma_global)

        if config_parser.has_option('gus', 'ultradir'):
            self.gus_ultradir_global = config_parser.get('gus', 'ultradir')
        else:
            self.gus_ultradir_global = 'C:\ULTRASND'
            config_parser.set('gus', 'ultradir', self.gus_ultradir_global)
###########################################################################################
        if not config_parser.has_section('speaker'):
            config_parser.add_section('speaker')

        if config_parser.has_option('speaker', 'pcspeaker'):
            self.speaker_pcspeaker_global = config_parser.get('speaker', 'pcspeaker')
        else:
            self.speaker_pcspeaker_global = 'true'
            config_parser.set('speaker', 'pcspeaker', self.speaker_pcspeaker_global)

        if config_parser.has_option('speaker', 'pcrate'):
            self.speaker_pcrate_global = config_parser.get('speaker', 'pcrate')
        else:
            self.speaker_pcrate_global = '44100'
            config_parser.set('speaker', 'pcrate', self.speaker_pcrate_global)

        if config_parser.has_option('speaker', 'tandy'):
            self.speaker_tandy_global = config_parser.get('speaker', 'tandy')
        else:
            self.speaker_tandy_global = 'auto'
            config_parser.set('speaker', 'tandy', self.speaker_tandy_global)

        if config_parser.has_option('speaker', 'tandyrate'):
            self.speaker_tandyrate_global = config_parser.get('speaker', 'tandyrate')
        else:
            self.speaker_tandyrate_global = '44100'
            config_parser.set('speaker', 'tandyrate', self.speaker_tandyrate_global)

        if config_parser.has_option('speaker', 'disney'):
            self.speaker_disney_global = config_parser.get('speaker', 'disney')
        else:
            self.speaker_disney_global = 'true'
            config_parser.set('speaker', 'disney', self.speaker_disney_global)
###########################################################################################
        if not config_parser.has_section('joystick'):
            config_parser.add_section('joystick')

        if config_parser.has_option('joystick', 'joysticktype'):
            self.joystick_joysticktype_global = config_parser.get('joystick', 'joysticktype')
        else:
            self.joystick_joysticktype_global = 'auto'
            config_parser.set('joystick', 'joysticktype', self.joystick_joysticktype_global)

        if config_parser.has_option('joystick', 'timed'):
            self.joystick_timed_global = config_parser.get('joystick', 'timed')
        else:
            self.joystick_timed_global = 'true'
            config_parser.set('joystick', 'timed', self.joystick_timed_global)

        if config_parser.has_option('joystick', 'autofire'):
            self.joystick_autofire_global = config_parser.get('joystick', 'autofire')
        else:
            self.joystick_autofire_global = 'false'
            config_parser.set('joystick', 'autofire', self.joystick_autofire_global)

        if config_parser.has_option('joystick', 'swap34'):
            self.joystick_swap34_global = config_parser.get('joystick', 'swap34')
        else:
            self.joystick_swap34_global = 'false'
            config_parser.set('joystick', 'swap34', self.joystick_swap34_global)

        if config_parser.has_option('joystick', 'buttonwrap'):
            self.joystick_buttonwrap_global = config_parser.get('joystick', 'buttonwrap')
        else:
            self.joystick_buttonwrap_global = 'false'
            config_parser.set('joystick', 'buttonwrap', self.joystick_buttonwrap_global)
###########################################################################################
        if not config_parser.has_section('serial'):
            config_parser.add_section('serial')

        if config_parser.has_option('serial', 'serial1'):
            self.serial_serial1_global = config_parser.get('serial', 'serial1')
        else:
            self.serial_serial1_global = 'dummy'
            config_parser.set('serial', 'serial1', self.serial_serial1_global)

        if config_parser.has_option('serial', 'serial2'):
            self.serial_serial2_global = config_parser.get('serial', 'serial2')
        else:
            self.serial_serial2_global = 'dummy'
            config_parser.set('serial', 'serial2', self.serial_serial2_global)

        if config_parser.has_option('serial', 'serial3'):
            self.serial_serial3_global = config_parser.get('serial', 'serial3')
        else:
            self.serial_serial3_global = 'disabled'
            config_parser.set('serial', 'serial3', self.serial_serial3_global)

        if config_parser.has_option('serial', 'serial4'):
            self.serial_serial4_global = config_parser.get('serial', 'serial4')
        else:
            self.serial_serial4_global = 'disabled'
            config_parser.set('serial', 'serial4', self.serial_serial4_global)
###########################################################################################
        if not config_parser.has_section('dos'):
            config_parser.add_section('dos')

        if config_parser.has_option('dos', 'xms'):
            self.dos_xms_global = config_parser.get('dos', 'xms')
        else:
            self.dos_xms_global = 'true'
            config_parser.set('dos', 'xms', self.dos_xms_global)

        if config_parser.has_option('dos', 'ems'):
            self.dos_ems_global = config_parser.get('dos', 'ems')
        else:
            self.dos_ems_global = 'true'
            config_parser.set('dos', 'ems', self.dos_ems_global)

        if config_parser.has_option('dos', 'umb'):
            self.dos_umb_global = config_parser.get('dos', 'umb')
        else:
            self.dos_umb_global = 'true'
            config_parser.set('dos', 'umb', self.dos_umb_global)

        if config_parser.has_option('dos', 'keyboardlayout'):
            self.dos_keyboardlayout_global = config_parser.get('dos', 'keyboardlayout')
        else:
            self.dos_keyboardlayout_global = 'auto'
            config_parser.set('dos', 'keyboardlayout', self.dos_keyboardlayout_global)
###########################################################################################
        if not config_parser.has_section('ipx'):
            config_parser.add_section('ipx')

        if config_parser.has_option('ipx', 'ipx'):
            self.ipx_ipx_global = config_parser.get('ipx', 'ipx')
        else:
            self.ipx_ipx_global = 'false'
            config_parser.set('ipx', 'ipx', self.ipx_ipx_global)
###########################################################################################

        config_file = open(config_path, 'w')
        config_parser.write(config_file)
        config_file.close()

    def dosbox_config_local_load(self, config_path):

        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_path)

        if config_parser.has_option('sdl', 'fullscreen'):
            self.sdl_fullscreen_local = config_parser.get('sdl', 'fullscreen')
        else:
            self.sdl_fullscreen_local = None

        if config_parser.has_option('sdl', 'fulldouble'):
            self.sdl_fulldouble_local = config_parser.get('sdl', 'fulldouble')
        else:
            self.sdl_fulldouble_local = None

        if config_parser.has_option('sdl', 'fullresolution'):
            self.sdl_fullresolution_local = config_parser.get('sdl', 'fullresolution')
        else:
            self.sdl_fullresolution_local = None

        if config_parser.has_option('sdl', 'windowresolution'):
            self.sdl_windowresolution_local = config_parser.get('sdl', 'windowresolution')
        else:
            self.sdl_windowresolution_local = None

        if config_parser.has_option('sdl', 'output'):
            self.sdl_output_local = config_parser.get('sdl', 'output')
        else:
            self.sdl_output_local = None

        if config_parser.has_option('sdl', 'autolock'):
            self.sdl_autolock_local = config_parser.get('sdl', 'autolock')
        else:
            self.sdl_autolock_local = None

        if config_parser.has_option('sdl', 'sensitivity'):
            self.sdl_sensitivity_local = config_parser.get('sdl', 'sensitivity')
        else:
            self.sdl_sensitivity_local = None

        if config_parser.has_option('sdl', 'waitonerror'):
            self.sdl_waitonerror_local = config_parser.get('sdl', 'waitonerror')
        else:
            self.sdl_waitonerror_local = None

        if config_parser.has_option('sdl', 'priority'):
            self.sdl_priority_local = config_parser.get('sdl', 'priority')
        else:
            self.sdl_priority_local = None

        if config_parser.has_option('sdl', 'mapperfile'):
            self.sdl_mapperfile_local = config_parser.get('sdl', 'mapperfile')
        else:
            self.sdl_mapperfile_local = None

        if config_parser.has_option('sdl', 'usescancodes'):
            self.sdl_usescancodes_local = config_parser.get('sdl', 'usescancodes')
        else:
            self.sdl_usescancodes_local = None

        if config_parser.has_option('dosbox', 'language'):
            self.dosbox_language_local = config_parser.get('dosbox', 'language')
        else:
            self.dosbox_language_local = None

        if config_parser.has_option('dosbox', 'machine'):
            self.dosbox_machine_local = config_parser.get('dosbox', 'machine')
        else:
            self.dosbox_machine_local = None

        if config_parser.has_option('dosbox', 'captures'):
            self.dosbox_captures_local = config_parser.get('dosbox', 'captures')
        else:
            self.dosbox_captures_local = None

        if config_parser.has_option('dosbox', 'memsize'):
            self.dosbox_memsize_local = config_parser.get('dosbox', 'memsize')
        else:
            self.dosbox_memsize_local = None

        if config_parser.has_option('render', 'frameskip'):
            self.render_frameskip_local = config_parser.get('render', 'frameskip')
        else:
            self.render_frameskip_local = None

        if config_parser.has_option('render', 'aspect'):
            self.render_aspect_local = config_parser.get('render', 'aspect')
        else:
            self.render_aspect_local = None

        if config_parser.has_option('render', 'scaler'):
            self.render_scaler_local = config_parser.get('render', 'scaler')
        else:
            self.render_scaler_local = None

        if config_parser.has_option('cpu', 'core'):
            self.cpu_core_local = config_parser.get('cpu', 'core')
        else:
            self.cpu_core_local = None

        if config_parser.has_option('cpu', 'cputype'):
            self.cpu_cputype_local = config_parser.get('cpu', 'cputype')
        else:
            self.cpu_cputype_local = None

        if config_parser.has_option('cpu', 'cycles'):
            self.cpu_cycles_local = config_parser.get('cpu', 'cycles')
        else:
            self.cpu_cycles_local = None

        if config_parser.has_option('cpu', 'cycleup'):
            self.cpu_cycleup_local = config_parser.get('cpu', 'cycleup')
        else:
            self.cpu_cycleup_local = None

        if config_parser.has_option('cpu', 'cycledown'):
            self.cpu_cycledown_local = config_parser.get('cpu', 'cycledown')
        else:
            self.cpu_cycledown_local = None

        if config_parser.has_option('mixer', 'nosound'):
            self.mixer_nosound_local = config_parser.get('mixer', 'nosound')
        else:
            self.mixer_nosound_local = None

        if config_parser.has_option('mixer', 'rate'):
            self.mixer_rate_local = config_parser.get('mixer', 'rate')
        else:
            self.mixer_rate_local = None

        if config_parser.has_option('mixer', 'blocksize'):
            self.mixer_blocksize_local = config_parser.get('mixer', 'blocksize')
        else:
            self.mixer_blocksize_local = None

        if config_parser.has_option('mixer', 'prebuffer'):
            self.mixer_prebuffer_local = config_parser.get('mixer', 'prebuffer')
        else:
            self.mixer_prebuffer_local = None

        if config_parser.has_option('midi', 'mpu401'):
            self.midi_mpu401_local = config_parser.get('midi', 'mpu401')
        else:
            self.midi_mpu401_local = None

        if config_parser.has_option('midi', 'mididevice'):
            self.midi_mididevice_local = config_parser.get('midi', 'mididevice')
        else:
            self.midi_mididevice_local = None

        if config_parser.has_option('midi', 'midiconfig'):
            self.midi_midiconfig_local = config_parser.get('midi', 'midiconfig')
        else:
            self.midi_midiconfig_local = None

        if config_parser.has_option('sblaster', 'sbtype'):
            self.sblaster_sbtype_local = config_parser.get('sblaster', 'sbtype')
        else:
            self.sblaster_sbtype_local = None

        if config_parser.has_option('sblaster', 'sbbase'):
            self.sblaster_sbbase_local = config_parser.get('sblaster', 'sbbase')
        else:
            self.sblaster_sbbase_local = None

        if config_parser.has_option('sblaster', 'irq'):
            self.sblaster_irq_local = config_parser.get('sblaster', 'irq')
        else:
            self.sblaster_irq_local = None

        if config_parser.has_option('sblaster', 'dma'):
            self.sblaster_dma_local = config_parser.get('sblaster', 'dma')
        else:
            self.sblaster_dma_local = None

        if config_parser.has_option('sblaster', 'hdma'):
            self.sblaster_hdma_local = config_parser.get('sblaster', 'hdma')
        else:
            self.sblaster_hdma_local = None

        if config_parser.has_option('sblaster', 'sbmixer'):
            self.sblaster_sbmixer_local = config_parser.get('sblaster', 'sbmixer')
        else:
            self.sblaster_sbmixer_local = None

        if config_parser.has_option('sblaster', 'oplmode'):
            self.sblaster_oplmode_local = config_parser.get('sblaster', 'oplmode')
        else:
            self.sblaster_oplmode_local = None

        if config_parser.has_option('sblaster', 'oplemu'):
            self.sblaster_oplemu_local = config_parser.get('sblaster', 'oplemu')
        else:
            self.sblaster_oplemu_local = None

        if config_parser.has_option('sblaster', 'oplrate'):
            self.sblaster_oplrate_local = config_parser.get('sblaster', 'oplrate')
        else:
            self.sblaster_oplrate_local = None

        if config_parser.has_option('gus', 'gus'):
            self.gus_gus_local = config_parser.get('gus', 'gus')
        else:
            self.gus_gus_local = None

        if config_parser.has_option('gus', 'gusrate'):
            self.gus_gusrate_local = config_parser.get('gus', 'gusrate')
        else:
            self.gus_gusrate_local = None

        if config_parser.has_option('gus', 'gusbase'):
            self.gus_gusbase_local = config_parser.get('gus', 'gusbase')
        else:
            self.gus_gusbase_local = None

        if config_parser.has_option('gus', 'gusirq'):
            self.gus_gusirq_local = config_parser.get('gus', 'gusirq')
        else:
            self.gus_gusirq_local = None

        if config_parser.has_option('gus', 'gusdma'):
            self.gus_gusdma_local = config_parser.get('gus', 'gusdma')
        else:
            self.gus_gusdma_local = None

        if config_parser.has_option('gus', 'ultradir'):
            self.gus_ultradir_local = config_parser.get('gus', 'ultradir')
        else:
            self.gus_ultradir_local = None

        if config_parser.has_option('speaker', 'pcspeaker'):
            self.speaker_pcspeaker_local = config_parser.get('speaker', 'pcspeaker')
        else:
            self.speaker_pcspeaker_local = None

        if config_parser.has_option('speaker', 'pcrate'):
            self.speaker_pcrate_local = config_parser.get('speaker', 'pcrate')
        else:
            self.speaker_pcrate_local = None

        if config_parser.has_option('speaker', 'tandy'):
            self.speaker_tandy_local = config_parser.get('speaker', 'tandy')
        else:
            self.speaker_tandy_local = None

        if config_parser.has_option('speaker', 'tandyrate'):
            self.speaker_tandyrate_local = config_parser.get('speaker', 'tandyrate')
        else:
            self.speaker_tandyrate_local = None

        if config_parser.has_option('speaker', 'disney'):
            self.speaker_disney_local = config_parser.get('speaker', 'disney')
        else:
            self.speaker_disney_local = None

        if config_parser.has_option('joystick', 'joysticktype'):
            self.joystick_joysticktype_local = config_parser.get('joystick', 'joysticktype')
        else:
            self.joystick_joysticktype_local = None

        if config_parser.has_option('joystick', 'timed'):
            self.joystick_timed_local = config_parser.get('joystick', 'timed')
        else:
            self.joystick_timed_local = None

        if config_parser.has_option('joystick', 'autofire'):
            self.joystick_autofire_local = config_parser.get('joystick', 'autofire')
        else:
            self.joystick_autofire_local = None

        if config_parser.has_option('joystick', 'swap34'):
            self.joystick_swap34_local = config_parser.get('joystick', 'swap34')
        else:
            self.joystick_swap34_local = None

        if config_parser.has_option('joystick', 'buttonwrap'):
            self.joystick_buttonwrap_local = config_parser.get('joystick', 'buttonwrap')
        else:
            self.joystick_buttonwrap_local = None

        if config_parser.has_option('serial', 'serial1'):
            self.serial_serial1_local = config_parser.get('serial', 'serial1')
        else:
            self.serial_serial1_local = None

        if config_parser.has_option('serial', 'serial2'):
            self.serial_serial2_local = config_parser.get('serial', 'serial2')
        else:
            self.serial_serial2_local = None

        if config_parser.has_option('serial', 'serial3'):
            self.serial_serial3_local = config_parser.get('serial', 'serial3')
        else:
            self.serial_serial3_local = None

        if config_parser.has_option('serial', 'serial4'):
            self.serial_serial4_local = config_parser.get('serial', 'serial4')
        else:
            self.serial_serial4_local = None

        if config_parser.has_option('dos', 'xms'):
            self.dos_xms_local = config_parser.get('dos', 'xms')
        else:
            self.dos_xms_local = None

        if config_parser.has_option('dos', 'ems'):
            self.dos_ems_local = config_parser.get('dos', 'ems')
        else:
            self.dos_ems_local = None

        if config_parser.has_option('dos', 'umb'):
            self.dos_umb_local = config_parser.get('dos', 'umb')
        else:
            self.dos_umb_local = None

        if config_parser.has_option('dos', 'keyboardlayout'):
            self.dos_keyboardlayout_local = config_parser.get('dos', 'keyboardlayout')
        else:
            self.dos_keyboardlayout_local = None

        if config_parser.has_option('ipx', 'ipx'):
            self.ipx_ipx_local = config_parser.get('ipx', 'ipx')
        else:
            self.ipx_ipx_local = None

    def dosbox_config_save(self):

        self.sdl_fullscreen_new = self.bool_to_dosbox_config(self.switch_fullscreen.get_active())
        self.sdl_fulldouble_new = self.bool_to_dosbox_config(self.switch_fulldouble.get_active())

        if self.combobox_fullresolution.get_active_text() == 'fixed':
            width = self.entry_fullresolution_width.get_text()
            height = self.entry_fullresolution_height.get_text()
            self.sdl_fullresolution_new = 'x'.join([width, height])
        else:
            self.sdl_fullresolution_new = self.combobox_fullresolution.get_active_text()

        if self.combobox_windowresolution.get_active_text() == 'fixed':
            width = self.entry_windowresolution_width.get_text()
            height = self.entry_windowresolution_height.get_text()
            self.sdl_windowresolution_new = 'x'.join([width, height])
        else:
            self.sdl_windowresolution_new = self.combobox_windowresolution.get_active_text()

        self.sdl_output_new = self.combobox_output.get_active_text()
        self.sdl_autolock_new = self.bool_to_dosbox_config(self.switch_autolock.get_active())
        self.sdl_sensitivity_new = int(self.adjustment_sensitivity.get_value())
        self.sdl_waitonerror_new = self.bool_to_dosbox_config(self.switch_waitonerror.get_active())

        priority1 = self.combobox_priority1.get_active_text()
        priority2 = self.combobox_priority2.get_active_text()

        self.sdl_priority_new = ','.join([priority1, priority2])

        if self.filechooser_mapperfile.get_filename() == None:
            self.sdl_mapperfile_new = ''
        else:
            self.sdl_mapperfile_new = self.filechooser_mapperfile.get_filename()

        self.sdl_usescancodes_new = self.bool_to_dosbox_config(self.switch_scancodes.get_active())
################################################################################
        if self.filechooser_language.get_filename() == None:
            self.dosbox_language_new = ''
        else:
            self.dosbox_language_new = self.filechooser_language.get_filename()

        self.dosbox_machine_new = self.combobox_machine.get_active_text()
        self.dosbox_captures_new = self.filechooser_captures.get_filename()

        if self.combobox_memsize.get_active_text() == '64':
            self.dosbox_memsize_new = '63'
        else:
            self.dosbox_memsize_new = self.combobox_memsize.get_active_text()

################################################################################
        self.render_frameskip_new = self.entry_frameskip.get_text()
        self.render_aspect_new = self.bool_to_dosbox_config(self.switch_aspect.get_active())

        if self.switch_forced_scaler.get_active() == False:
            self.render_scaler_new = self.combobox_scaler.get_active_text()
        else:
            self.render_scaler_new = self.combobox_scaler.get_active_text() + ' forced'
################################################################################
        self.cpu_core_new = self.combobox_core.get_active_text()
        self.cpu_cputype_new = self.combobox_cputype.get_active_text()

        if self.combobox_cycles.get_active_text() == 'fixed':
            self.cpu_cycles_new = self.combobox_cycles.get_active_text() + ' ' + \
            self.entry_fixed_cycles.get_text()
        elif self.combobox_cycles.get_active_text() == _("custom"):
            self.cpu_cycles_new = self.entry_custom_cycles.get_text()
        else:
            self.cpu_cycles_new = self.combobox_cycles.get_active_text()

        self.cpu_cycleup_new = self.entry_cycleup.get_text()
        self.cpu_cycledown_new = self.entry_cycledown.get_text()

################################################################################
        self.mixer_nosound_new = self.bool_to_dosbox_config(self.switch_nosound.get_active())
        self.mixer_rate_new = self.combobox_rate.get_active_text()
        self.mixer_blocksize_new = self.combobox_blocksize.get_active_text()
        self.mixer_prebuffer_new = self.entry_prebuffer.get_text()
################################################################################
        self.midi_mpu401_new = self.combobox_mpu401.get_active_text()
        self.midi_mididevice_new = self.combobox_mididevice.get_active_text()

        if self.midi_mididevice_new == 'synth':
            self.midi_midiconfig_new = self.filechooserbutton_soundfont.get_filename()
        else:
            self.midi_midiconfig_new = self.entry_midiconfig.get_text()

################################################################################
        self.sblaster_sbtype_new = self.combobox_sbtype.get_active_text()
        self.sblaster_sbbase_new = self.combobox_sbbase.get_active_text()
        self.sblaster_irq_new = self.combobox_irq.get_active_text()
        self.sblaster_dma_new = self.combobox_dma.get_active_text()
        self.sblaster_hdma_new = self.combobox_hdma.get_active_text()
        self.sblaster_sbmixer_new = self.bool_to_dosbox_config(self.switch_sbmixer.get_active())
        self.sblaster_oplmode_new = self.combobox_oplmode.get_active_text()
        self.sblaster_oplemu_new = self.combobox_oplemu.get_active_text()
        self.sblaster_oplrate_new = self.combobox_oplrate.get_active_text()
################################################################################
        self.gus_gus_new = self.bool_to_dosbox_config(self.switch_gus.get_active())
        self.gus_gusrate_new = self.combobox_gusrate.get_active_text()
        self.gus_gusbase_new = self.combobox_gusbase.get_active_text()
        self.gus_gusirq_new = self.combobox_gusirq.get_active_text()
        self.gus_gusdma_new = self.combobox_gusdma.get_active_text()
        self.gus_ultradir_new = self.entry_ultradir.get_text()
################################################################################
        self.speaker_pcspeaker_new = self.bool_to_dosbox_config(self.switch_pcspeaker.get_active())
        self.speaker_pcrate_new = self.combobox_pcrate.get_active_text()
        self.speaker_tandy_new = self.combobox_tandy.get_active_text()
        self.speaker_tandyrate_new = self.combobox_tandyrate.get_active_text()
        self.speaker_disney_new = self.bool_to_dosbox_config(self.switch_disney.get_active())
################################################################################
        self.joystick_joysticktype_new = self.combobox_joysticktype.get_active_text()
        self.joystick_timed_new = self.bool_to_dosbox_config(self.switch_timed.get_active())
        self.joystick_autofire_new = self.bool_to_dosbox_config(self.switch_autofire.get_active())
        self.joystick_swap34_new = self.bool_to_dosbox_config(self.switch_swap34.get_active())
        self.joystick_buttonwrap_new = self.bool_to_dosbox_config(self.switch_buttonwrap.get_active())
################################################################################
        if self.entry_serial1_parameters.get_text() != '':
            self.serial_serial1_new = self.combobox_serial1.get_active_text() + ' ' + \
            self.entry_serial1_parameters.get_text()
        else:
            self.serial_serial1_new = self.combobox_serial1.get_active_text()

        if self.entry_serial2_parameters.get_text() != '':
            self.serial_serial2_new = self.combobox_serial2.get_active_text() + ' ' + \
            self.entry_serial2_parameters.get_text()
        else:
            self.serial_serial2_new = self.combobox_serial2.get_active_text()

        if self.entry_serial3_parameters.get_text() != '':
            self.serial_serial3_new = self.combobox_serial3.get_active_text() + ' ' + \
            self.entry_serial3_parameters.get_text()
        else:
            self.serial_serial3_new = self.combobox_serial3.get_active_text()

        if self.entry_serial4_parameters.get_text() != '':
            self.serial_serial4_new = self.combobox_serial4.get_active_text() + ' ' + \
            self.entry_serial4_parameters.get_text()
        else:
            self.serial_serial4_new = self.combobox_serial4.get_active_text()
################################################################################
        self.dos_xms_new = self.bool_to_dosbox_config(self.switch_xms.get_active())
        self.dos_ems_new = self.bool_to_dosbox_config(self.switch_ems.get_active())
        self.dos_umb_new = self.bool_to_dosbox_config(self.switch_umb.get_active())

        if self.combobox_keyboardlayout.get_active_text() == _("custom"):
            self.dos_keyboardlayout_new = self.entry_keyboardlayout.get_text()
        else:
            self.dos_keyboardlayout_new = self.combobox_keyboardlayout.get_active_text()
################################################################################
        self.ipx_ipx_new = self.bool_to_dosbox_config(self.switch_ipx.get_active())

        if self.config_type == 'global':

            config_parser = ConfigParser.ConfigParser()
            config_parser.read(self.config_path)

            if not config_parser.has_section('sdl'):
                config_parser.add_section('sdl')

            config_parser.set('sdl', 'fullscreen', self.sdl_fullscreen_new)
            config_parser.set('sdl', 'fulldouble', self.sdl_fulldouble_new)
            config_parser.set('sdl', 'fullresolution', self.sdl_fullresolution_new)
            config_parser.set('sdl', 'windowresolution', self.sdl_windowresolution_new)
            config_parser.set('sdl', 'output', self.sdl_output_new)
            config_parser.set('sdl', 'autolock', self.sdl_autolock_new)
            config_parser.set('sdl', 'sensitivity', self.sdl_sensitivity_new)
            config_parser.set('sdl', 'waitonerror', self.sdl_waitonerror_new)
            config_parser.set('sdl', 'priority', self.sdl_priority_new)
            config_parser.set('sdl', 'mapperfile', self.sdl_mapperfile_new)
            config_parser.set('sdl', 'usescancodes', self.sdl_usescancodes_new)

            if not config_parser.has_section('dosbox'):
                config_parser.add_section('dosbox')

            config_parser.set('dosbox', 'language', self.dosbox_language_new)
            config_parser.set('dosbox', 'machine', self.dosbox_machine_new)
            config_parser.set('dosbox', 'captures', self.dosbox_captures_new)
            config_parser.set('dosbox', 'memsize', self.dosbox_memsize_new)

            if not config_parser.has_section('render'):
                config_parser.add_section('render')

            config_parser.set('render', 'frameskip', self.render_frameskip_new)
            config_parser.set('render', 'aspect', self.render_aspect_new)
            config_parser.set('render', 'scaler', self.render_scaler_new)

            if not config_parser.has_section('cpu'):
                config_parser.add_section('cpu')

            config_parser.set('cpu', 'core', self.cpu_core_new)
            config_parser.set('cpu', 'cputype', self.cpu_cputype_new)
            config_parser.set('cpu', 'cycles', self.cpu_cycles_new)
            config_parser.set('cpu', 'cycleup', self.cpu_cycleup_new)
            config_parser.set('cpu', 'cycledown', self.cpu_cycledown_new)

            if not config_parser.has_section('mixer'):
                config_parser.add_section('mixer')

            config_parser.set('mixer', 'nosound', self.mixer_nosound_new)
            config_parser.set('mixer', 'rate', self.mixer_rate_new)
            config_parser.set('mixer', 'blocksize', self.mixer_blocksize_new)
            config_parser.set('mixer', 'prebuffer', self.mixer_prebuffer_new)

            if not config_parser.has_section('midi'):
                config_parser.add_section('midi')

            config_parser.set('midi', 'mpu401', self.midi_mpu401_new)
            config_parser.set('midi', 'mididevice', self.midi_mididevice_new)
            config_parser.set('midi', 'midiconfig', self.midi_midiconfig_new)

            if not config_parser.has_section('sblaster'):
                config_parser.add_section('sblaster')

            config_parser.set('sblaster', 'sbtype', self.sblaster_sbtype_new)
            config_parser.set('sblaster', 'sbbase', self.sblaster_sbbase_new)
            config_parser.set('sblaster', 'irq', self.sblaster_irq_new)
            config_parser.set('sblaster', 'dma', self.sblaster_dma_new)
            config_parser.set('sblaster', 'hdma', self.sblaster_hdma_new)
            config_parser.set('sblaster', 'sbmixer', self.sblaster_sbmixer_new)
            config_parser.set('sblaster', 'oplmode', self.sblaster_oplmode_new)
            config_parser.set('sblaster', 'oplemu', self.sblaster_oplemu_new)
            config_parser.set('sblaster', 'oplrate', self.sblaster_oplrate_new)

            if not config_parser.has_section('gus'):
                config_parser.add_section('gus')

            config_parser.set('gus', 'gus', self.gus_gus_new)
            config_parser.set('gus', 'gusrate', self.gus_gusrate_new)
            config_parser.set('gus', 'gusbase', self.gus_gusbase_new)
            config_parser.set('gus', 'gusirq', self.gus_gusirq_new)
            config_parser.set('gus', 'gusdma', self.gus_gusdma_new)
            config_parser.set('gus', 'ultradir', self.gus_ultradir_new)

            if not config_parser.has_section('speaker'):
                config_parser.add_section('speaker')

            config_parser.set('speaker', 'pcspeaker', self.speaker_pcspeaker_new)
            config_parser.set('speaker', 'pcrate', self.speaker_pcrate_new)
            config_parser.set('speaker', 'tandy', self.speaker_tandy_new)
            config_parser.set('speaker', 'tandyrate', self.speaker_tandyrate_new)
            config_parser.set('speaker', 'disney', self.speaker_disney_new)

            if not config_parser.has_section('joystick'):
                config_parser.add_section('joystick')

            config_parser.set('joystick', 'joysticktype', self.joystick_joysticktype_new)
            config_parser.set('joystick', 'timed', self.joystick_timed_new)
            config_parser.set('joystick', 'autofire', self.joystick_autofire_new)
            config_parser.set('joystick', 'swap34', self.joystick_swap34_new)
            config_parser.set('joystick', 'buttonwrap', self.joystick_buttonwrap_new)

            if not config_parser.has_section('serial'):
                config_parser.add_section('serial')

            config_parser.set('serial', 'serial1', self.serial_serial1_new)
            config_parser.set('serial', 'serial2', self.serial_serial2_new)
            config_parser.set('serial', 'serial3', self.serial_serial3_new)
            config_parser.set('serial', 'serial4', self.serial_serial4_new)

            if not config_parser.has_section('dos'):
                config_parser.add_section('dos')

            config_parser.set('dos', 'xms', self.dos_xms_new)
            config_parser.set('dos', 'ems', self.dos_ems_new)
            config_parser.set('dos', 'umb', self.dos_umb_new)
            config_parser.set('dos', 'keyboardlayout', self.dos_keyboardlayout_new)

            if not config_parser.has_section('ipx'):
                config_parser.add_section('ipx')

            config_parser.set('ipx', 'ipx', self.ipx_ipx_new)

            config_file = open(self.config_path, 'w')
            config_parser.write(config_file)
            config_file.close()


        elif self.config_type == 'local':

            config_parser = ConfigParser.ConfigParser()
            config_parser.read(self.config_path)

            if not config_parser.has_section('sdl'):
                config_parser.add_section('sdl')

            if self.sdl_fullscreen_new != self.sdl_fullscreen:
                config_parser.set('sdl', 'fullscreen', self.sdl_fullscreen_new)
            elif self.sdl_fullscreen_new == self.sdl_fullscreen_global:
                config_parser.remove_option('sdl', 'fullscreen')

            if self.sdl_fulldouble_new != self.sdl_fulldouble:
                config_parser.set('sdl', 'fulldouble', self.sdl_fulldouble_new)
            elif self.sdl_fulldouble_new == self.sdl_fulldouble_global:
                config_parser.remove_option('sdl', 'fulldouble')

            if self.sdl_fullresolution_new != self.sdl_fullresolution:
                config_parser.set('sdl', 'fullresolution', self.sdl_fullresolution_new)
            elif self.sdl_fullresolution_new == self.sdl_fullresolution_global:
                config_parser.remove_option('sdl', 'fullresolution')

            if self.sdl_windowresolution_new != self.sdl_windowresolution:
                config_parser.set('sdl', 'windowresolution', self.sdl_windowresolution_new)
            elif self.sdl_windowresolution_new == self.sdl_windowresolution_global:
                config_parser.remove_option('sdl', 'windowresolution')

            if self.sdl_output_new != self.sdl_output:
                config_parser.set('sdl', 'output', self.sdl_output_new)
            elif self.sdl_output_new == self.sdl_output_global:
                config_parser.remove_option('sdl', 'output')

            if self.sdl_autolock_new != self.sdl_autolock:
                config_parser.set('sdl', 'autolock', self.sdl_autolock_new)
            elif self.sdl_autolock_new == self.sdl_autolock_global:
                config_parser.remove_option('sdl', 'autolock')

            if str(self.sdl_sensitivity_new) != self.sdl_sensitivity:
                config_parser.set('sdl', 'sensitivity', self.sdl_sensitivity_new)
            elif str(self.sdl_sensitivity_new) == self.sdl_sensitivity_global:
                config_parser.remove_option('sdl', 'sensitivity')

            if self.sdl_waitonerror_new != self.sdl_waitonerror:
                config_parser.set('sdl', 'waitonerror', self.sdl_waitonerror_new)
            elif self.sdl_waitonerror_new == self.sdl_waitonerror_global:
                config_parser.remove_option('sdl', 'waitonerror')

            if self.sdl_priority_new != self.sdl_priority:
                config_parser.set('sdl', 'priority', self.sdl_priority_new)
            elif self.sdl_priority_new == self.sdl_priority_global:
                config_parser.remove_option('sdl', 'priority')

            if self.sdl_mapperfile_new != self.sdl_mapperfile:
                config_parser.set('sdl', 'mapperfile', self.sdl_mapperfile_new)
            elif self.sdl_mapperfile_new == self.sdl_mapperfile_global:
                config_parser.remove_option('sdl', 'mapperfile')

            if self.sdl_usescancodes_new != self.sdl_usescancodes:
                config_parser.set('sdl', 'usescancodes', self.sdl_usescancodes_new)
            elif self.sdl_usescancodes_new == self.sdl_usescancodes_global:
                config_parser.remove_option('sdl', 'usescancodes')

            if len(config_parser.options('sdl')) == 0:
                config_parser.remove_section('sdl')

            if not config_parser.has_section('dosbox'):
                config_parser.add_section('dosbox')

            if self.dosbox_language_new != self.dosbox_language:
                config_parser.set('dosbox', 'language', self.dosbox_language_new)
            elif self.dosbox_language_new == self.dosbox_language_global:
                config_parser.remove_option('dosbox', 'language')

            if self.dosbox_machine_new != self.dosbox_machine:
                config_parser.set('dosbox', 'machine', self.dosbox_machine_new)
            elif self.dosbox_machine_new == self.dosbox_machine_global:
                config_parser.remove_option('dosbox', 'machine')

            if self.dosbox_captures_new != self.dosbox_captures:
                config_parser.set('dosbox', 'caprutes', self.dosbox_captures_new)
            elif self.dosbox_captures_new == self.dosbox_captures_global:
                config_parser.remove_option('dosbox', 'caprutes')

            if self.dosbox_memsize_new != self.dosbox_memsize:
                config_parser.set('dosbox', 'memsize', self.dosbox_memsize_new)
            elif self.dosbox_memsize_new == self.dosbox_memsize_global:
                config_parser.remove_option('dosbox', 'memsize')

            if len(config_parser.options('dosbox')) == 0:
                config_parser.remove_section('dosbox')

            if not config_parser.has_section('render'):
                config_parser.add_section('render')

            if self.render_frameskip_new != self.render_frameskip:
                config_parser.set('render', 'frameskip', self.render_frameskip_new)
            elif self.render_frameskip_new == self.render_frameskip_global:
                config_parser.remove_option('render', 'frameskip')

            if self.render_aspect_new != self.render_aspect:
                config_parser.set('render', 'aspect', self.render_aspect_new)
            elif self.render_aspect_new == self.render_aspect_global:
                config_parser.remove_option('render', 'aspect')

            if self.render_scaler_new != self.render_scaler:
                config_parser.set('render', 'scaler', self.render_scaler_new)
            elif self.render_scaler_new == self.render_scaler_global:
                config_parser.remove_option('render', 'scaler')

            if len(config_parser.options('render')) == 0:
                config_parser.remove_section('render')

            if not config_parser.has_section('cpu'):
                config_parser.add_section('cpu')

            if self.cpu_core_new != self.cpu_core:
                config_parser.set('cpu', 'core', self.cpu_core_new)
            elif self.cpu_core_new == self.cpu_core_global:
                config_parser.remove_option('cpu', 'core')

            if self.cpu_cputype_new != self.cpu_cputype:
                config_parser.set('cpu', 'cputype', self.cpu_cputype_new)
            elif self.cpu_cputype_new == self.cpu_cputype_global:
                config_parser.remove_option('cpu', 'cputype')

            if self.cpu_cycles_new != self.cpu_cycles:
                config_parser.set('cpu', 'cycles', self.cpu_cycles_new)
            elif self.cpu_cycles_new == self.cpu_cycles_global:
                config_parser.remove_option('cpu', 'cycles')

            if self.cpu_cycleup_new != self.cpu_cycleup:
                config_parser.set('cpu', 'cycleup', self.cpu_cycleup_new)
            elif self.cpu_cycleup_new == self.cpu_cycleup_global:
                config_parser.remove_option('cpu', 'cycleup')

            if self.cpu_cycledown_new != self.cpu_cycledown:
                config_parser.set('cpu', 'cycledown', self.cpu_cycledown_new)
            elif self.cpu_cycledown_new == self.cpu_cycledown_global:
                config_parser.remove_option('cpu', 'cycledown')

            if len(config_parser.options('cpu')) == 0:
                config_parser.remove_section('cpu')

            if not config_parser.has_section('mixer'):
                config_parser.add_section('mixer')

            if self.mixer_nosound_new != self.mixer_nosound:
                config_parser.set('mixer', 'nosound', self.mixer_nosound_new)
            elif self.mixer_nosound_new == self.mixer_nosound_global:
                config_parser.remove_option('mixer', 'nosound')

            if self.mixer_rate_new != self.mixer_rate:
                config_parser.set('mixer', 'rate', self.mixer_rate_new)
            elif self.mixer_rate_new == self.mixer_rate_global:
                config_parser.remove_option('mixer', 'rate')

            if self.mixer_blocksize_new != self.mixer_blocksize:
                config_parser.set('mixer', 'blocksize', self.mixer_blocksize_new)
            elif self.mixer_blocksize_new == self.mixer_blocksize_global:
                config_parser.remove_option('mixer', 'blocksize')

            if self.mixer_prebuffer_new != self.mixer_prebuffer:
                config_parser.set('mixer', 'prebuffer', self.mixer_prebuffer_new)
            elif self.mixer_prebuffer_new == self.mixer_prebuffer_global:
                config_parser.remove_option('mixer', 'prebuffer')

            if len(config_parser.options('mixer')) == 0:
                config_parser.remove_section('mixer')

            if not config_parser.has_section('midi'):
                config_parser.add_section('midi')

            if self.midi_mpu401_new != self.midi_mpu401:
                config_parser.set('midi', 'mpu401', self.midi_mpu401_new)
            elif self.midi_mpu401_new == self.midi_mpu401_global:
                config_parser.remove_option('midi', 'mpu401')

            if self.midi_mididevice_new != self.midi_mididevice:
                config_parser.set('midi', 'mididevice', self.midi_mididevice_new)
            elif self.midi_mididevice_new == self.midi_mididevice_global:
                config_parser.remove_option('midi', 'mididevice')

            if self.midi_midiconfig_new != self.midi_midiconfig:
                config_parser.set('midi', 'midiconfig', self.midi_midiconfig_new)
            elif self.midi_midiconfig_new == self.midi_midiconfig_global:
                config_parser.remove_option('midi', 'midiconfig')

            if len(config_parser.options('midi')) == 0:
                config_parser.remove_section('midi')

            if not config_parser.has_section('sblaster'):
                config_parser.add_section('sblaster')

            if self.sblaster_sbtype_new != self.sblaster_sbtype:
                config_parser.set('sblaster', 'sbtype', self.sblaster_sbtype_new)
            elif self.sblaster_sbtype_new == self.sblaster_sbtype_global:
                config_parser.remove_option('sblaster', 'sbtype')

            if self.sblaster_sbbase_new != self.sblaster_sbbase:
                config_parser.set('sblaster', 'sbbase', self.sblaster_sbbase_new)
            elif self.sblaster_sbbase_new == self.sblaster_sbbase_global:
                config_parser.remove_option('sblaster', 'sbbase')

            if self.sblaster_irq_new != self.sblaster_irq:
                config_parser.set('sblaster', 'irq', self.sblaster_irq_new)
            elif self.sblaster_irq_new == self.sblaster_irq_global:
                config_parser.remove_option('sblaster', 'irq')

            if self.sblaster_dma_new != self.sblaster_dma:
                config_parser.set('sblaster', 'dma', self.sblaster_dma_new)
            elif self.sblaster_dma_new == self.sblaster_dma_global:
                config_parser.remove_option('sblaster', 'dma')

            if self.sblaster_hdma_new != self.sblaster_hdma:
                config_parser.set('sblaster', 'hdma', self.sblaster_hdma_new)
            elif self.sblaster_hdma_new == self.sblaster_hdma_global:
                config_parser.remove_option('sblaster', 'hdma')

            if self.sblaster_sbmixer_new != self.sblaster_sbmixer:
                config_parser.set('sblaster', 'sbmixer', self.sblaster_sbmixer_new)
            elif self.sblaster_sbmixer_new == self.sblaster_sbmixer_global:
                config_parser.remove_option('sblaster', 'sbmixer')

            if self.sblaster_oplmode_new != self.sblaster_oplmode:
                config_parser.set('sblaster', 'oplmode', self.sblaster_oplmode_new)
            elif self.sblaster_oplmode_new == self.sblaster_oplmode_global:
                config_parser.remove_option('sblaster', 'oplmode')

            if self.sblaster_oplemu_new != self.sblaster_oplemu:
                config_parser.set('sblaster', 'oplemu', self.sblaster_oplemu_new)
            elif self.sblaster_oplemu_new == self.sblaster_oplemu_global:
                config_parser.remove_option('sblaster', 'oplemu')

            if self.sblaster_oplrate_new != self.sblaster_oplrate:
                config_parser.set('sblaster', 'oplrate', self.sblaster_oplrate_new)
            elif self.sblaster_oplrate_new == self.sblaster_oplrate_global:
                config_parser.remove_option('sblaster', 'oplrate')

            if len(config_parser.options('sblaster')) == 0:
                config_parser.remove_section('sblaster')

            if not config_parser.has_section('gus'):
                config_parser.add_section('gus')

            if self.gus_gus_new != self.gus_gus:
                config_parser.set('gus', 'gus', self.gus_gus_new)
            elif self.gus_gus_new == self.gus_gus_global:
                config_parser.remove_option('gus', 'gus')

            if self.gus_gusrate_new != self.gus_gusrate:
                config_parser.set('gus', 'gusrate', self.gus_gusrate_new)
            elif self.gus_gusrate_new == self.gus_gusrate_global:
                config_parser.remove_option('gus', 'gusrate')

            if self.gus_gusbase_new != self.gus_gusbase:
                config_parser.set('gus', 'gusbase', self.gus_gusbase_new)
            elif self.gus_gusbase_new == self.gus_gusbase_global:
                config_parser.remove_option('gus', 'gusbase')

            if self.gus_gusirq_new != self.gus_gusirq:
                config_parser.set('gus', 'gusirq', self.gus_gusirq_new)
            elif self.gus_gusirq_new == self.gus_gusirq_global:
                config_parser.remove_option('gus', 'gusirq')

            if self.gus_gusdma_new != self.gus_gusdma:
                config_parser.set('gus', 'gusdma', self.gus_gusdma_new)
            elif self.gus_gusdma_new == self.gus_gusdma_global:
                config_parser.remove_option('gus', 'gusdma')

            if self.gus_ultradir_new != self.gus_ultradir:
                config_parser.set('gus', 'ultradir', self.gus_ultradir_new)
            elif self.gus_ultradir_new == self.gus_ultradir_global:
                config_parser.remove_option('gus', 'ultradir')

            if len(config_parser.options('gus')) == 0:
                config_parser.remove_section('gus')

            if not config_parser.has_section('speaker'):
                config_parser.add_section('speaker')

            if self.speaker_pcspeaker_new != self.speaker_pcspeaker:
                config_parser.set('speaker', 'pcspeaker', self.speaker_pcspeaker_new)
            elif self.speaker_pcspeaker_new == self.speaker_pcspeaker_global:
                config_parser.remove_option('speaker', 'pcspeaker')

            if self.speaker_pcrate_new != self.speaker_pcrate:
                config_parser.set('speaker', 'pcrate', self.speaker_pcrate_new)
            elif self.speaker_pcrate_new == self.speaker_pcrate_global:
                config_parser.remove_option('speaker', 'pcrate')

            if self.speaker_tandy_new != self.speaker_tandy:
                config_parser.set('speaker', 'tandy', self.speaker_tandy_new)
            elif self.speaker_tandy_new == self.speaker_tandy_global:
                config_parser.remove_option('speaker', 'tandy')

            if self.speaker_tandyrate_new != self.speaker_tandyrate:
                config_parser.set('speaker', 'tandyrate', self.speaker_tandyrate_new)
            elif self.speaker_tandyrate_new == self.speaker_tandyrate_global:
                config_parser.remove_option('speaker', 'tandyrate')

            if self.speaker_disney_new != self.speaker_disney:
                config_parser.set('speaker', 'disney', self.speaker_disney_new)
            elif self.speaker_disney_new == self.speaker_disney_global:
                config_parser.remove_option('speaker', 'disney')

            if len(config_parser.options('speaker')) == 0:
                config_parser.remove_section('speaker')

            if not config_parser.has_section('joystick'):
                config_parser.add_section('joystick')

            if self.joystick_joysticktype_new != self.joystick_joysticktype:
                config_parser.set('joystick', 'joysticktype', self.joystick_joysticktype_new)
            elif self.joystick_joysticktype_new == self.joystick_joysticktype_global:
                config_parser.remove_option('joystick', 'joysticktype')

            if self.joystick_timed_new != self.joystick_timed:
                config_parser.set('joystick', 'timed', self.joystick_timed_new)
            elif self.joystick_timed_new == self.joystick_timed_global:
                config_parser.remove_option('joystick', 'timed')

            if self.joystick_autofire_new != self.joystick_autofire:
                config_parser.set('joystick', 'autofire', self.joystick_autofire_new)
            elif self.joystick_autofire_new == self.joystick_autofire_global:
                config_parser.remove_option('joystick', 'autofire')

            if self.joystick_swap34_new != self.joystick_swap34:
                config_parser.set('joystick', 'swap34', self.joystick_swap34_new)
            elif self.joystick_swap34_new == self.joystick_swap34_global:
                config_parser.remove_option('joystick', 'swap34')

            if self.joystick_buttonwrap_new != self.joystick_buttonwrap:
                config_parser.set('joystick', 'buttonwrap', self.joystick_buttonwrap_new)
            elif self.joystick_buttonwrap_new == self.joystick_buttonwrap_global:
                config_parser.remove_option('joystick', 'buttonwrap')

            if len(config_parser.options('joystick')) == 0:
                config_parser.remove_section('joystick')

            if not config_parser.has_section('serial'):
                config_parser.add_section('serial')

            if self.serial_serial1_new != self.serial_serial1:
                config_parser.set('serial', 'serial1', self.serial_serial1_new)
            elif self.serial_serial1_new == self.serial_serial1_global:
                config_parser.remove_option('serial', 'serial1')

            if self.serial_serial2_new != self.serial_serial2:
                config_parser.set('serial', 'serial2', self.serial_serial2_new)
            elif self.serial_serial2_new == self.serial_serial2_global:
                config_parser.remove_option('serial', 'serial2')

            if self.serial_serial3_new != self.serial_serial3:
                config_parser.set('serial', 'serial3', self.serial_serial3_new)
            elif self.serial_serial3_new == self.serial_serial3_global:
                config_parser.remove_option('serial', 'serial3')

            if self.serial_serial4_new != self.serial_serial4:
                config_parser.set('serial', 'serial4', self.serial_serial4_new)
            elif self.serial_serial4_new == self.serial_serial4_global:
                config_parser.remove_option('serial', 'serial4')

            if len(config_parser.options('serial')) == 0:
                config_parser.remove_section('serial')

            if not config_parser.has_section('dos'):
                config_parser.add_section('dos')

            if self.dos_xms_new != self.dos_xms:
                config_parser.set('dos', 'xms', self.dos_xms_new)
            elif self.dos_xms_new == self.dos_xms_global:
                config_parser.remove_option('dos', 'xms')

            if self.dos_ems_new != self.dos_ems:
                config_parser.set('dos', 'ems', self.dos_ems_new)
            elif self.dos_ems_new == self.dos_ems_global:
                config_parser.remove_option('dos', 'ems')

            if self.dos_umb_new != self.dos_umb:
                config_parser.set('dos', 'umb', self.dos_umb_new)
            elif self.dos_umb_new == self.dos_umb_global:
                config_parser.remove_option('dos', 'umb')

            if self.dos_keyboardlayout_new != self.dos_keyboardlayout:
                config_parser.set('dos', 'keyboardlayout', self.dos_keyboardlayout_new)
            elif self.dos_keyboardlayout_new == self.dos_keyboardlayout_global:
                config_parser.remove_option('dos', 'keyboardlayout')

            if len(config_parser.options('dos')) == 0:
                config_parser.remove_section('dos')

            if not config_parser.has_section('ipx'):
                config_parser.add_section('ipx')

            if self.ipx_ipx_new != self.ipx_ipx:
                config_parser.set('ipx', 'ipx', self.ipx_ipx_new)
            elif self.ipx_ipx_new == self.ipx_ipx_global:
                config_parser.remove_option('ipx', 'ipx')

            if len(config_parser.options('ipx')) == 0:
                config_parser.remove_section('ipx')

            config_file = open(self.config_path, 'w')
            config_parser.write(config_file)
            config_file.close()


    def set_dosbox_config_vars(self):

        if self.config_type == 'global':
            self.sdl_fullscreen = self.sdl_fullscreen_global
            self.sdl_fulldouble = self.sdl_fulldouble_global
            self.sdl_fullresolution = self.sdl_fullresolution_global
            self.sdl_windowresolution = self.sdl_windowresolution_global
            self.sdl_output = self.sdl_output_global
            self.sdl_autolock = self.sdl_autolock_global
            self.sdl_sensitivity = self.sdl_sensitivity_global
            self.sdl_waitonerror = self.sdl_waitonerror_global
            self.sdl_priority = self.sdl_priority_global
            self.sdl_mapperfile = self.sdl_mapperfile_global
            self.sdl_usescancodes = self.sdl_usescancodes_global
            self.dosbox_language = self.dosbox_language_global
            self.dosbox_machine = self.dosbox_machine_global
            self.dosbox_captures = self.dosbox_captures_global
            self.dosbox_memsize = self.dosbox_memsize_global
            self.render_frameskip = self.render_frameskip_global
            self.render_aspect = self.render_aspect_global
            self.render_scaler = self.render_scaler_global
            self.cpu_core = self.cpu_core_global
            self.cpu_cputype = self.cpu_cputype_global
            self.cpu_cycles = self.cpu_cycles_global
            self.cpu_cycleup = self.cpu_cycleup_global
            self.cpu_cycledown = self.cpu_cycledown_global
            self.mixer_nosound = self.mixer_nosound_global
            self.mixer_rate = self.mixer_rate_global
            self.mixer_blocksize = self.mixer_blocksize_global
            self.mixer_prebuffer = self.mixer_prebuffer_global
            self.midi_mpu401 = self.midi_mpu401_global
            self.midi_mididevice = self.midi_mididevice_global
            self.midi_midiconfig = self.midi_midiconfig_global
            self.sblaster_sbtype = self.sblaster_sbtype_global
            self.sblaster_sbbase = self.sblaster_sbbase_global
            self.sblaster_irq = self.sblaster_irq_global
            self.sblaster_dma = self.sblaster_dma_global
            self.sblaster_hdma = self.sblaster_hdma_global
            self.sblaster_sbmixer = self.sblaster_sbmixer_global
            self.sblaster_oplmode = self.sblaster_oplmode_global
            self.sblaster_oplemu = self.sblaster_oplemu_global
            self.sblaster_oplrate = self.sblaster_oplrate_global
            self.gus_gus = self.gus_gus_global
            self.gus_gusrate = self.gus_gusrate_global
            self.gus_gusbase = self.gus_gusbase_global
            self.gus_gusirq = self.gus_gusirq_global
            self.gus_gusdma = self.gus_gusdma_global
            self.gus_ultradir = self.gus_ultradir_global
            self.speaker_pcspeaker = self.speaker_pcspeaker_global
            self.speaker_pcrate = self.speaker_pcrate_global
            self.speaker_tandy = self.speaker_tandy_global
            self.speaker_tandyrate = self.speaker_tandyrate_global
            self.speaker_disney = self.speaker_disney_global
            self.joystick_joysticktype = self.joystick_joysticktype_global
            self.joystick_timed = self.joystick_timed_global
            self.joystick_autofire = self.joystick_autofire_global
            self.joystick_swap34 = self.joystick_swap34_global
            self.joystick_buttonwrap = self.joystick_buttonwrap_global
            self.serial_serial1 = self.serial_serial1_global
            self.serial_serial2 = self.serial_serial2_global
            self.serial_serial3 = self.serial_serial3_global
            self.serial_serial4 = self.serial_serial4_global
            self.dos_xms = self.dos_xms_global
            self.dos_ems = self.dos_ems_global
            self.dos_umb = self.dos_umb_global
            self.dos_keyboardlayout = self.dos_keyboardlayout_global
            self.ipx_ipx = self.ipx_ipx_global

        elif self.config_type == 'local':

            if self.sdl_fullscreen_local != None:
                self.sdl_fullscreen = self.sdl_fullscreen_local
            else:
                self.sdl_fullscreen = self.sdl_fullscreen_global

            if self.sdl_fulldouble_local != None:
                self.sdl_fulldouble = self.sdl_fulldouble_local
            else:
                self.sdl_fulldouble = self.sdl_fulldouble_global

            if self.sdl_fullresolution_local != None:
                self.sdl_fullresolution = self.sdl_fullresolution_local
            else:
                self.sdl_fullresolution = self.sdl_fullresolution_global

            if self.sdl_windowresolution_local != None:
                self.sdl_windowresolution = self.sdl_windowresolution_local
            else:
                self.sdl_windowresolution = self.sdl_windowresolution_global

            if self.sdl_output_local != None:
                self.sdl_output = self.sdl_output_local
            else:
                self.sdl_output = self.sdl_output_global

            if self.sdl_autolock_local != None:
                self.sdl_autolock = self.sdl_autolock_local
            else:
                self.sdl_autolock = self.sdl_autolock_global

            if self.sdl_sensitivity_local != None:
                self.sdl_sensitivity = self.sdl_sensitivity_local
            else:
                self.sdl_sensitivity = self.sdl_sensitivity_global

            if self.sdl_waitonerror_local != None:
                self.sdl_waitonerror = self.sdl_waitonerror_local
            else:
                self.sdl_waitonerror = self.sdl_waitonerror_global

            if self.sdl_priority_local != None:
                self.sdl_priority = self.sdl_priority_local
            else:
                self.sdl_priority = self.sdl_priority_global

            if self.sdl_mapperfile_local != None:
                self.sdl_mapperfile = self.sdl_mapperfile_local
            else:
                self.sdl_mapperfile = self.sdl_mapperfile_global

            if self.sdl_usescancodes_local != None:
                self.sdl_usescancodes = self.sdl_usescancodes_local
            else:
                self.sdl_usescancodes = self.sdl_usescancodes_global

            if self.dosbox_language_local != None:
                self.dosbox_language = self.dosbox_language_local
            else:
                self.dosbox_language = self.dosbox_language_global

            if self.dosbox_machine_local != None:
                self.dosbox_machine = self.dosbox_machine_local
            else:
                self.dosbox_machine = self.dosbox_machine_global

            if self.dosbox_captures_local != None:
                self.dosbox_captures = self.dosbox_captures_local
            else:
                self.dosbox_captures = self.dosbox_captures_global

            if self.dosbox_memsize_local != None:
                self.dosbox_memsize = self.dosbox_memsize_local
            else:
                self.dosbox_memsize = self.dosbox_memsize_global

            if self.render_frameskip_local != None:
                self.render_frameskip = self.render_frameskip_local
            else:
                self.render_frameskip = self.render_frameskip_global

            if self.render_aspect_local != None:
                self.render_aspect = self.render_aspect_local
            else:
                self.render_aspect = self.render_aspect_global

            if self.render_scaler_local != None:
                self.render_scaler = self.render_scaler_local
            else:
                self.render_scaler = self.render_scaler_global

            if self.cpu_core_local != None:
                self.cpu_core = self.cpu_core_local
            else:
                self.cpu_core = self.cpu_core_global

            if self.cpu_cputype_local != None:
                self.cpu_cputype = self.cpu_cputype_local
            else:
                self.cpu_cputype = self.cpu_cputype_global

            if self.cpu_cycles_local != None:
                self.cpu_cycles = self.cpu_cycles_local
            else:
                self.cpu_cycles = self.cpu_cycles_global

            if self.cpu_cycleup_local != None:
                self.cpu_cycleup = self.cpu_cycleup_local
            else:
                self.cpu_cycleup = self.cpu_cycleup_global

            if self.cpu_cycledown_local != None:
                self.cpu_cycledown = self.cpu_cycledown_local
            else:
                self.cpu_cycledown = self.cpu_cycledown_global

            if self.mixer_nosound_local != None:
                self.mixer_nosound = self.mixer_nosound_local
            else:
                self.mixer_nosound = self.mixer_nosound_global

            if self.mixer_rate_local != None:
                self.mixer_rate = self.mixer_rate_local
            else:
                self.mixer_rate = self.mixer_rate_global

            if self.mixer_blocksize_local != None:
                self.mixer_blocksize = self.mixer_blocksize_local
            else:
                self.mixer_blocksize = self.mixer_blocksize_global

            if self.mixer_prebuffer_local != None:
                self.mixer_prebuffer = self.mixer_prebuffer_local
            else:
                self.mixer_prebuffer = self.mixer_prebuffer_global

            if self.midi_mpu401_local != None:
                self.midi_mpu401 = self.midi_mpu401_local
            else:
                self.midi_mpu401 = self.midi_mpu401_global

            if self.midi_mididevice_local != None:
                self.midi_mididevice = self.midi_mididevice_local
            else:
                self.midi_mididevice = self.midi_mididevice_global

            if self.midi_midiconfig_local != None:
                self.midi_midiconfig = self.midi_midiconfig_local
            else:
                self.midi_midiconfig = self.midi_midiconfig_global

            if self.sblaster_sbtype_local != None:
                self.sblaster_sbtype = self.sblaster_sbtype_local
            else:
                self.sblaster_sbtype = self.sblaster_sbtype_global

            if self.sblaster_sbbase_local != None:
                self.sblaster_sbbase = self.sblaster_sbbase_local
            else:
                self.sblaster_sbbase = self.sblaster_sbbase_global

            if self.sblaster_irq_local != None:
                self.sblaster_irq = self.sblaster_irq_local
            else:
                self.sblaster_irq = self.sblaster_irq_global

            if self.sblaster_dma_local != None:
                self.sblaster_dma = self.sblaster_dma_local
            else:
                self.sblaster_dma = self.sblaster_dma_global

            if self.sblaster_hdma_local != None:
                self.sblaster_hdma = self.sblaster_hdma_local
            else:
                self.sblaster_hdma = self.sblaster_hdma_global

            if self.sblaster_sbmixer_local != None:
                self.sblaster_sbmixer = self.sblaster_sbmixer_local
            else:
                self.sblaster_sbmixer = self.sblaster_sbmixer_global

            if self.sblaster_oplmode_local != None:
                self.sblaster_oplmode = self.sblaster_oplmode_local
            else:
                self.sblaster_oplmode = self.sblaster_oplmode_global

            if self.sblaster_oplemu_local != None:
                self.sblaster_oplemu = self.sblaster_oplemu_local
            else:
                self.sblaster_oplemu = self.sblaster_oplemu_global

            if self.sblaster_oplrate_local != None:
                self.sblaster_oplrate = self.sblaster_oplrate_local
            else:
                self.sblaster_oplrate = self.sblaster_oplrate_global

            if self.gus_gus_local != None:
                self.gus_gus = self.gus_gus_local
            else:
                self.gus_gus = self.gus_gus_global

            if self.gus_gusrate_local != None:
                self.gus_gusrate = self.gus_gusrate_local
            else:
                self.gus_gusrate = self.gus_gusrate_global

            if self.gus_gusbase_local != None:
                self.gus_gusbase = self.gus_gusbase_local
            else:
                self.gus_gusbase = self.gus_gusbase_global

            if self.gus_gusirq_local != None:
                self.gus_gusirq = self.gus_gusirq_local
            else:
                self.gus_gusirq = self.gus_gusirq_global

            if self.gus_gusdma_local != None:
                self.gus_gusdma = self.gus_gusdma_local
            else:
                self.gus_gusdma = self.gus_gusdma_global

            if self.gus_ultradir_local != None:
                self.gus_ultradir = self.gus_ultradir_local
            else:
                self.gus_ultradir = self.gus_ultradir_global

            if self.speaker_pcspeaker_local != None:
                self.speaker_pcspeaker = self.speaker_pcspeaker_local
            else:
                self.speaker_pcspeaker = self.speaker_pcspeaker_global

            if self.speaker_pcrate_local != None:
                self.speaker_pcrate = self.speaker_pcrate_local
            else:
                self.speaker_pcrate = self.speaker_pcrate_global

            if self.speaker_tandy_local != None:
                self.speaker_tandy = self.speaker_tandy_local
            else:
                self.speaker_tandy = self.speaker_tandy_global

            if self.speaker_tandyrate_local != None:
                self.speaker_tandyrate = self.speaker_tandyrate_local
            else:
                self.speaker_tandyrate = self.speaker_tandyrate_global

            if self.speaker_disney_local != None:
                self.speaker_disney = self.speaker_disney_local
            else:
                self.speaker_disney = self.speaker_disney_global

            if self.joystick_joysticktype_local != None:
                self.joystick_joysticktype = self.joystick_joysticktype_local
            else:
                self.joystick_joysticktype = self.joystick_joysticktype_global

            if self.joystick_timed_local != None:
                self.joystick_timed = self.joystick_timed_local
            else:
                self.joystick_timed = self.joystick_timed_global

            if self.joystick_autofire_local != None:
                self.joystick_autofire = self.joystick_autofire_local
            else:
                self.joystick_autofire = self.joystick_autofire_global

            if self.joystick_swap34_local != None:
                self.joystick_swap34 = self.joystick_swap34_local
            else:
                self.joystick_swap34 = self.joystick_swap34_global

            if self.joystick_buttonwrap_local != None:
                self.joystick_buttonwrap = self.joystick_buttonwrap_local
            else:
                self.joystick_buttonwrap = self.joystick_buttonwrap_global

            if self.serial_serial1_local != None:
                self.serial_serial1 = self.serial_serial1_local
            else:
                self.serial_serial1 = self.serial_serial1_global

            if self.serial_serial2_local != None:
                self.serial_serial2 = self.serial_serial2_local
            else:
                self.serial_serial2 = self.serial_serial2_global

            if self.serial_serial3_local != None:
                self.serial_serial3 = self.serial_serial3_local
            else:
                self.serial_serial3 = self.serial_serial3_global

            if self.serial_serial4_local != None:
                self.serial_serial4 = self.serial_serial4_local
            else:
                self.serial_serial4 = self.serial_serial4_global

            if self.dos_xms_local != None:
                self.dos_xms = self.dos_xms_local
            else:
                self.dos_xms = self.dos_xms_global

            if self.dos_ems_local != None:
                self.dos_ems = self.dos_ems_local
            else:
                self.dos_ems = self.dos_ems_global

            if self.dos_umb_local != None:
                self.dos_umb = self.dos_umb_local
            else:
                self.dos_umb = self.dos_umb_global

            if self.dos_keyboardlayout_local != None:
                self.dos_keyboardlayout = self.dos_keyboardlayout_local
            else:
                self.dos_keyboardlayout = self.dos_keyboardlayout_global

            if self.ipx_ipx_local != None:
                self.ipx_ipx = self.ipx_ipx_local
            else:
                self.ipx_ipx = self.ipx_ipx_global


    def cb_entry_digits_only(self, entry):
        text = entry.get_text().strip()
        new_text = (''.join([i for i in text if i in '0123456789']))
        entry.set_text(new_text)

    def cb_combobox_fullresolution(self, combobox):
        if combobox.get_active_text() == 'fixed':
            self.entry_fullresolution_width.set_visible(True)
            self.entry_fullresolution_height.set_visible(True)
        else:
            self.entry_fullresolution_width.set_visible(False)
            self.entry_fullresolution_height.set_visible(False)

    def cb_combobox_windowresolution(self, combobox):
        if combobox.get_active_text() == 'fixed':
            self.entry_windowresolution_width.set_visible(True)
            self.entry_windowresolution_height.set_visible(True)
        else:
            self.entry_windowresolution_width.set_visible(False)
            self.entry_windowresolution_height.set_visible(False)

    def cb_combobox_cycles(self, combobox):
        if combobox.get_active_text() == 'fixed':
            self.entry_fixed_cycles.set_visible(True)
        else:
            self.entry_fixed_cycles.set_visible(False)

        if combobox.get_active_text() == _("custom"):
            self.entry_custom_cycles.set_visible(True)
        else:
            self.entry_custom_cycles.set_visible(False)

    def cb_combobox_keyboardlayout(self, combobox):
        if combobox.get_active_text() == _("custom"):
            self.entry_keyboardlayout.set_visible(True)
        else:
            self.entry_keyboardlayout.set_visible(False)

    def cb_button_save(self, button):
        self.dosbox_config_save()
        Gtk.main_quit()

    def dosbox_config_to_bool(self, dosbox_bool):
        if dosbox_bool == 'true':
            return True
        elif dosbox_bool == 'false':
            return False

    def bool_to_dosbox_config(self, bool):
        if bool == True:
            return 'true'
        elif bool == False:
            return 'false'

    def digit_in_string(self, string):
        for char in string:
            if char.isdigit():
                return True
        return False

    def cb_combobox_mididevice(self, combobox):
        self.entry_midiconfig.set_text('')
        if combobox.get_active_text() == 'synth':
            self.label_soundfont.set_visible(True)
            self.filechooserbutton_soundfont.set_visible(True)
            self.label_midiconfig.set_visible(False)
            self.entry_midiconfig.set_visible(False)
        else:
            self.label_soundfont.set_visible(False)
            self.filechooserbutton_soundfont.set_visible(False)
            self.label_midiconfig.set_visible(True)
            self.entry_midiconfig.set_visible(True)
def main():
    import sys
    app = GUI(sys.argv[1], sys.argv[2], sys.argv[3])
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
