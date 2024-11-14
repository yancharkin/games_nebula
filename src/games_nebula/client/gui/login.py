import urllib.request
import logging

from games_nebula import __qt_version__
if __qt_version__ == '6':
    from PyQt6.QtCore import Qt, QUrl
    from PyQt6.QtWidgets import QDialog
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
    NoContextMenu = Qt.ContextMenuPolicy.NoContextMenu

elif __qt_version__ == '5':
    from PyQt5.QtCore import Qt, QUrl
    from PyQt5.QtWidgets import QDialog
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
    NoContextMenu = Qt.NoContextMenu
from games_nebula.apis.gogapi import AUTH_URL
from games_nebula.client.translator import _tr

logger = logging.getLogger(__name__)

class LoginDialog(QDialog):
    def __init__(self, config_dir):
        super().__init__()
        self.__config_dir = config_dir
        self.login_code = None

        def cb_url_changed(url):
            url_path = url.path()
            url_query = url.query()
            if not url_path.startswith("/on_login_success"):
                return
            try:
                self.login_code = url_query.split('code=')[1]
                self.accept()
            except:
                logger.error(_tr("Could not parse code from the query:") + url_query)
                self.reject()

        def cb_load_finished():
            def get_login_form_size(size):
                width = size[0]
                height = size[1]
                self.webview.setFixedSize(width, height)
                self.setFixedSize(width, height)
            web_page = self.webview.page()
            if web_page.url().host() == 'login.gog.com':
                loginForm = web_page.runJavaScript(
                    (
                    'let loginForm = document.getElementsByClassName("form--login")[0];'
                    'if (!loginForm) loginForm = document.getElementsByClassName("form--relogin")[0];'
                    'let size = [loginForm.offsetWidth, loginForm.offsetHeight];'
                    'size;'
                    ),
                    get_login_form_size
                )
                web_page.runJavaScript(
                    (
                    'let el2Hide = document.getElementsByClassName("js-close-modal");'
                    'for (i in el2Hide) el2Hide[i].hidden = true;'
                    )
                )

        self.setFixedSize(0, 0)
        self.webview = QWebEngineView()
        self.webview.setContextMenuPolicy(NoContextMenu)
        self.webview.setPage(WebEnginePage(self))
        self.webview.setParent(self)
        self.webview.loadFinished.connect(cb_load_finished)
        self.webview.urlChanged.connect(cb_url_changed)
        self.webview.load(QUrl(AUTH_URL))

        # Cookies and storage
        profile = QWebEngineProfile.defaultProfile()
        profile.setCachePath(self.__config_dir + '/storage')
        profile.setPersistentStoragePath(self.__config_dir + '/storage')

    def run(self):
        # Check if auth.gog.com can be reached
        try:
            urllib.request.urlopen('https://auth.gog.com/auth')
        except Exception as e:
            logger.error(e.reason)
            return None

        if self.exec():
            return self.login_code
        else:
            return None

class WebEnginePage(QWebEnginePage):
    """
    Override javaScriptConsoleMessage method to prevent web page from sending
    messages to console.
    """

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        pass
