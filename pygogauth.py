import sys
import os
import re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2

if sys.version_info[0] == 2:
    from urlparse import urlparse
elif sys.version_info[0] == 3:
    from urllib.parse import urlparse

from gogapi.token import Token, get_auth_url

class Login:

    def __init__(self):

        self.token_path = os.getenv('HOME') + '/.config/lgogdownloader/galaxy_tokens.json'
        self.cookiejar_path = os.getenv('HOME') + '/.config/lgogdownloader/cookies.txt'
        self.create_window()

    def create_window(self):

        app_icon = GdkPixbuf.Pixbuf.new_from_file(sys.path[0] + '/images/icon.png')

        self.login_window = Gtk.Window(
            title = "Games Nebula",
            type = Gtk.WindowType.TOPLEVEL,
            window_position = Gtk.WindowPosition.CENTER_ALWAYS,
            icon = app_icon,
            width_request = 390,
            height_request = 496,
            resizable = False
        )
        self.login_window.connect('delete-event', self.quit_app)

        self.setup_cookies()

        content_manager = self.new_content_manager()
        self.webpage = WebKit2.WebView(user_content_manager=content_manager)
        self.webpage.connect('load_changed', self.webpage_loaded)

        self.webpage_color = Gdk.RGBA(
            red = 0.149019,
            green = 0.149019,
            blue = 0.149019,
            alpha = 1.0,
        )
        self.webpage.set_background_color(self.webpage_color)

        auth_url = get_auth_url()
        self.webpage.load_uri(auth_url)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.webpage)

        self.login_window.add(self.scrolled_window)
        self.login_window.show_all()

    def new_content_manager(self):

        css = """
        .icn--close {
            visibility: hidden;
        }
        button#continue_offline {
            visibility: hidden;
        }
        """
        content_injected_frames = WebKit2.UserContentInjectedFrames(0)
        user_style_level = WebKit2.UserStyleLevel(0)
        style_sheet = WebKit2.UserStyleSheet(css, content_injected_frames, user_style_level, None, None)

        content_manager = WebKit2.UserContentManager()
        content_manager.add_style_sheet(style_sheet)

        return content_manager

    def quit_app(self, window, event):
        print("Authorization failed")
        Gtk.main_quit()

    def webpage_loaded(self, webview, event):

        if event == WebKit2.LoadEvent.FINISHED:

            java_sctipt = 'document.body.style.backgroundColor = "#262626";'
            webview.run_javascript(java_sctipt, None, None, None)

        elif event == WebKit2.LoadEvent.REDIRECTED:

            url = webview.get_uri()
            url_path = urlparse(url).path
            url_query = urlparse(url).query

            if not url_path.startswith("/on_login_success"):
                return

            query_match = re.compile(r"code=([\w\-]+)").search(url_query)

            if query_match is not None:
                login_code = query_match.group(1)
                token = Token.from_code(login_code)
                token.save(self.token_path)
                print("Authorization successful!")
                Gtk.main_quit()
            else:

                message_dialog = Gtk.MessageDialog(
                    None,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    _("Error")
                )
                message_dialog.format_secondary_text(_("Could not parse code from query: %s") % url_query)

                content_area = message_dialog.get_content_area()
                content_area.set_property('margin-left', 10)
                content_area.set_property('margin-right', 10)
                content_area.set_property('margin-top', 10)
                content_area.set_property('margin-bottom', 10)

                message_dialog.run()
                message_dialog.destroy()
                print("Authorization failed")
                Gtk.main_quit()

    def setup_cookies(self):

        cookies_dir = os.path.dirname(self.cookiejar_path)
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)

        context = WebKit2.WebContext.get_default()
        cookie_manager = context.get_cookie_manager();
        cookie_manager.set_persistent_storage(self.cookiejar_path, WebKit2.CookiePersistentStorage.TEXT);

def main():
    import sys
    app = Login()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
