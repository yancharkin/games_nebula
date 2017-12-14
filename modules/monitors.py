import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

def get_monitors():

    monitors_list = []

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

    return monitors_list, monitor_primary
