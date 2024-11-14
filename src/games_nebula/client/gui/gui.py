import os
import sys
import logging
from games_nebula import __qt_version__
if __qt_version__ == '6':
    from PyQt6.QtWidgets import QApplication, QGridLayout
elif __qt_version__ == '5':
    from PyQt5.QtWidgets import QApplication, QGridLayout
from games_nebula.client.api_wrapper import Api
from games_nebula.client.gui.login import LoginDialog
from games_nebula.client.gui.setup_window import SetupWindow
from games_nebula.client.gui.systray import Systray
from games_nebula.client import config
from games_nebula.client.logger import Logger
from games_nebula.client.translator import _tr

if config.get('locale') not in ('System', 'system'):
    os.environ['LANG'] = config.get('locale')

class GuiApp:
    """GUI application."""

    def __init__(self):
        self.config_dir = config.CONFIG_DIR
        self.force_offline_mode = config.get('force_offline_mode')
        self.api = Api(self.config_dir, offline_mode=self.force_offline_mode)
        user_id = self.api.get_user_id()

        # TODO if not user_id => tmp_user (see cli client)
        Logger(log_dir=f'{self.config_dir}/users/{user_id}', log_name='gui.log').setup()
        self.logger = logging.getLogger(__name__)


    def start(self):
        app = QApplication(sys.argv)
        self.logger.info(_tr("Application started."))
        if self.api.is_gog_available() and not self.force_offline_mode:
            if not self.api.is_gog_authorized():
                login_dialog = LoginDialog(self.config_dir)
                login_code = login_dialog.run()
                self.api.login(login_code)
            if self.api.is_gog_authorized(): # Check if authorization was successful
                # Show GUI #
                setupWin = SetupWindow()
                setupWin.show()
                setupWin.setup()
                systray = Systray(app)
                systray.show()
            else:
                self.logger.info(_tr("Not authorized."))
                sys.exit()
        else:
            self.logger.warning(_tr("GOG server not available."))
            # If local db exists (not implemented yet) #
            offline_possible = False
            if offline_possible:
                self.logger.info(_tr("Starting in offline mode."))
                setupWin = SetupWindow()
                setupWin.show()
                setupWin.setup()
                systray = Systray(app)
                systray.show()
            else:
                self.logger.warning(_tr("Can't be started in offline mode."))
                sys.exit()
        self.exit(app.exec())

    def exit(self, exit_code):
        self.logger.info(_tr("Application closed."))
        sys.exit()
