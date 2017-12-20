import os, subprocess, re
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

def get_monitors():

    monitors_list = []

    try:
        x = os.environ['WAYLAND_DISPLAY']
        session_type = 'wayland'
    except KeyError:
        session_type = 'x11'

    if session_type == 'x11':

        # Use GTK
        ## Not working with Wayland (?)

        display_manager = Gdk.DisplayManager.get()
        display = Gdk.DisplayManager.get_default_display(display_manager)
        n_monitors = display.get_n_monitors()

        for monitor_index in range(n_monitors):
            monitor = display.get_monitor(monitor_index)

            model = monitor.get_model()
            geometry = monitor.get_geometry()
            monitors_list.append(model + ' ' + str(geometry.width) + 'x' + str(geometry.height))

            if monitor.is_primary():
                monitor_primary = model + ' ' + str(geometry.width) + 'x' + str(geometry.height)

    else:

        # Using xrandr

        proc = subprocess.Popen(['xrandr'],stdout=subprocess.PIPE)
        for line in proc.stdout.readlines():

            if re.compile(r'\b({0})\b'.format('connected'), flags=re.IGNORECASE).search(line):
                if 'primary' in line:
                    monitors_list.append(line.split(' ')[0] + ' ' + line.split(' ')[3].split('+')[0])
                else:
                    monitors_list.append(line.split(' ')[0] + ' ' + line.split(' ')[2].split('+')[0])
            if 'primary' in line:
                monitor_primary = line.split(' ')[0] + ' ' + line.split(' ')[3].split('+')[0]

        ## Hack for Wayland
        try:
            monitor_primary
        except NameError:
            monitor_primary = monitors_list[0]
        else:
            pass

    return monitors_list, monitor_primary
