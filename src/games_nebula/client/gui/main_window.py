import os
import urllib.request

from games_nebula.client.api_wrapper import Api
from games_nebula.client import config
from games_nebula.client import is_game_installed
from games_nebula.client.translator import _tr
from games_nebula.client.runnable import Runnable
from games_nebula.client.commands import Commands
from games_nebula.client.gui.gamewidget import GameWidget
from games_nebula.client.gui.sort_filter_proxy_model import SortFilterProxyModel
from games_nebula import __qt_version__
if __qt_version__ == '6':
    from PyQt6.QtCore import (
            Qt, QThreadPool, pyqtSignal, QSize
    )
    from PyQt6.QtGui import (
            QImage, QStandardItem, QStandardItemModel, QIcon, QAction, QMouseEvent
    )
    from PyQt6.QtWidgets import (
            QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QListView, QListWidget,
            QSizePolicy, QStyledItemDelegate, QSlider, QComboBox, QTabWidget, QMainWindow,
            QTableView, QHeaderView, QAbstractItemView, QToolBar
    )
elif __qt_version__ == '5':
    from PyQt5.QtCore import (
            Qt, QThreadPool, pyqtSignal, QSize
    )
    from PyQt5.QtGui import (
            QImage, QStandardItem, QStandardItemModel, QIcon, QMouseEvent
    )
    from PyQt5.QtWidgets import (
            QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QListView, QListWidget, QAction,
            QSizePolicy, QStyledItemDelegate, QSlider, QComboBox, QTabWidget, QMainWindow,
            QTableView, QHeaderView, QAbstractItemView, QToolBar
    )

class Window(QMainWindow):
    resized = pyqtSignal(QWidget)
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)

    def resizeEvent(self, event):
        self.resized.emit(self)
        return QWidget.resizeEvent(self, event)

class ComboBox(QComboBox):
    clicked = pyqtSignal(QWidget, QMouseEvent)
    def __init__(self, parent=None):
        super(ComboBox, self).__init__(parent=parent)

    def mousePressEvent(self, event):
        self.clicked.emit(self, event)
        return QComboBox.mousePressEvent(self, event)

class StyledItemDelegate(QStyledItemDelegate):

    def initStyleOption(self, option, index):
        listview = self.parent()

        window = listview.parent().parent().parent().parent()

        game_widget = listview.indexWidget(index)
        if not game_widget:
            proxy_model = listview.model()
            model = proxy_model.sourceModel()
            source_index = proxy_model.mapToSource(index)
            item = model.itemFromIndex(source_index)
            #print(item.data(Qt.ItemDataRole.DisplayRole))
            data = item.data(Qt.ItemDataRole.UserRole)
            game_widget = GameWidget(
                    data['game_slug'],
                    data['game_title'],
                    data['game_logo_path'],
                    data['game_logo_url'],
                    #data['logos_width'],
                    data['game_installed']
                    #window.logos_width
            )
            listview.setIndexWidget(index, game_widget)

            def __cb_game_widget_button():
                window = listview.parent().parent().parent().parent()
                cmd = Commands(window._api)
                if game_widget.installed:
                    # TODO In commands and cli client replace args_list to *args
                    cmd.launch([game_widget.slug])

            game_widget.button.clicked.connect(__cb_game_widget_button)
            def __set_and_scale_logo():
                game_widget.set_logo()
                game_widget.scale_logo(window.logos_width)
            if os.path.isfile(data['game_logo_path']):
                __set_and_scale_logo()
            else:
                runnable = Runnable(game_widget.download_logo)
                runnable.singnals.finished.connect(__set_and_scale_logo)
                thread_pool = QThreadPool.globalInstance()
                thread_pool.start(runnable)

class MainWindow(Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Games Nebula")
        if os.path.exists('../data/icons/games_nebula.png'):
            self.data_path = '../data'
        else:
            self.data_path = '/usr/share/'
        self.setWindowIcon(QIcon(f'{self.data_path}/icons/games_nebula.png'))
        self._api = Api(config.CONFIG_DIR)
        self.logos_width = config.get('logos_width')
        self.listview = QListView()
        self.listview.viewport().setAutoFillBackground(False)
        #self.listview.setLayoutMode(QListView.LayoutMode.Batched)
        #self.listview.setBatchSize(20)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            _tr("Title"), _tr("Genre"), _tr("OS"), _tr("Language"),
            _tr("Developer"), _tr("Publiser")
        ])

        #######################################################################
        # TODO load hidden from file ##########################################
        #######################################################################
        hidden = set([
            'hotline_miami_2_wrong_number_digital_comics',
            'the_witcher_goodies_collection', 'gwent_the_witcher_card_game',
            'dex_demo', 'herald_an_interactive_period_drama_book_i_ii_demo',
            'infinium_strike_demo', 'kathy_rain_demo', 'mainlining_demo',
            'shadow_tactics_demo', 'silence_demo', 'star_vikings_demo',
            'stories_untold_demo', 'system_shock_demo', 'the_silver_case_demo',
            'xenonauts_2_demo', 'zombasite_demo'
        ])
        self.proxy_model = SortFilterProxyModel(hidden)

        #self.proxy_model.setFilterKeyColumn(-1) # search in all table comums
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setSourceModel(self.model)
        self.listview.setModel(self.proxy_model)

        self.listview.setSelectionMode(QListWidget.SelectionMode.NoSelection) # change for gamepads
        self.listview.setViewMode(QListView.ViewMode.IconMode)
        self.listview.setResizeMode(QListView.ResizeMode.Adjust)
        self.listview.setMovement(QListView.Movement.Static)
        self.listview.setWrapping(True)
        self.listview.setUniformItemSizes(True)

        self.tableview = QTableView()
        self.tableview.viewport().setAutoFillBackground(False)
        self.tableview.setCornerButtonEnabled(False)
        self.tableview.verticalHeader().hide()
        self.tableview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        #self.tableview.setShowGrid(False)
        self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableview.horizontalHeader().setStretchLastSection(True)
        self.tableview.setSortingEnabled(True)
        self.tableview.setModel(self.proxy_model)
        #self.tableview.horizontalHeader().sectionPressed.connect(lambda: self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive))

        #genres_all = set([_tr("All")])
        genres_all = set()
        games_dict = self._api.get_games_list()
        games_list = [g['slug'] for g in games_dict]
        for game_slug in games_list:
            game_title = self._api.get_game_title(game_slug)
            game_logo_path = self._api.get_game_logo_file_path(game_slug, size=config.get('images_size'))
            game_logo_url = self._api.get_game_logo_url(game_slug, size=config.get('images_size'))
            game_genres = self._api.get_game_genres(game_slug)
            game_os = self._api.get_game_oses(game_slug)
            game_lang = self._api.get_game_languages(game_slug)
            game_devs = self._api.get_game_developers(game_slug)
            game_publisher = self._api.get_game_publisher(game_slug)
            game_installed = is_game_installed(game_slug, quick_check=True)[0]

            genres_all.update(game_genres)

            widget_data = {
                    'game_slug': game_slug,
                    'game_title': game_title,
                    'game_logo_path': game_logo_path,
                    'game_logo_url': game_logo_url,
                    'logos_width': self.logos_width,
                    'game_installed': game_installed
            }
            # Title
            item_0 = QStandardItem()
            item_0.setData(game_title, Qt.ItemDataRole.DisplayRole)
            item_0.setData(widget_data, Qt.ItemDataRole.UserRole)
            # Genres
            item_1 = QStandardItem()
            item_1.setData(', '.join(game_genres), Qt.ItemDataRole.DisplayRole)
            # OS
            item_2 = QStandardItem()
            item_2.setData(', '.join(game_os), Qt.ItemDataRole.DisplayRole)
            # Language
            item_3 = QStandardItem()
            item_3.setData(
                    ', '.join([game_lang[l].capitalize() for l in game_lang]),
                    Qt.ItemDataRole.DisplayRole)
            # Developers
            item_4 = QStandardItem()
            item_4.setData(', '.join(game_devs), Qt.ItemDataRole.DisplayRole)
            # Publiser
            item_5 = QStandardItem()
            item_5.setData(game_publisher, Qt.ItemDataRole.DisplayRole)

            self.model.appendRow([item_0, item_1, item_2, item_3, item_4, item_5])

        delegate = StyledItemDelegate(self.listview)
        self.listview.setItemDelegate(delegate)

        search_bar = QLineEdit()
        search_bar.setClearButtonEnabled(True)
        search_bar.setTextMargins(5, 0, 5, 0)
        search_bar.setPlaceholderText(_tr("Search..."))
        search_bar.textChanged.connect(self.__cb_search_bar)
        search_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        #search_bar.textEdited.connect(self.__cb_search_bar)
        #compl = QCompleter([g['title'] for g in self._api.get_games_list()])
        #compl.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        #search_bar.setCompleter(compl)
        self.__set_icons()

        def __cb_installed_filter(installed):
            if installed == _tr("All"):
                installed = ''
            elif installed == _tr("Installed"):
                installed = True
            elif installed == _tr("Not installed"):
                installed = False
            self.proxy_model.set_installed_filter(installed)
            self.__rearrange_items()

        def __cb_genre_filter_0(genre):
            if genre == _tr("All"): genre = ''
            self.proxy_model.set_genre_filter_0(genre)
            self.__rearrange_items()

        def __cb_genre_filter_1(genre):
            if genre == _tr("All"): genre = ''
            self.proxy_model.set_genre_filter_1(genre)
            self.__rearrange_items()

        def __cb_genre_filter_2(genre):
            if genre == _tr("All"): genre = ''
            self.proxy_model.set_genre_filter_2(genre)
            self.__rearrange_items()

        combobox_installed = ComboBox()
        combobox_genre_0 = ComboBox()
        combobox_genre_1 = ComboBox()
        combobox_genre_2 = ComboBox()
        combobox_installed.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        combobox_genre_0.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        combobox_genre_1.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        combobox_genre_2.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        combobox_installed.addItems([_tr("All"), _tr("Installed"), _tr("Not installed")])
        combobox_genre_0.addItems([_tr("All")] + sorted(genres_all))
        combobox_genre_1.addItems([_tr("All")] + sorted(genres_all))
        combobox_genre_2.addItems([_tr("All")] + sorted(genres_all))
        combobox_installed.currentTextChanged.connect(__cb_installed_filter)
        combobox_genre_0.currentTextChanged.connect(__cb_genre_filter_0)
        combobox_genre_1.currentTextChanged.connect(__cb_genre_filter_1)
        combobox_genre_2.currentTextChanged.connect(__cb_genre_filter_2)
        def combobox_clicked(sender, event):
            if event.button() == Qt.MouseButton.RightButton:
                sender.setCurrentIndex(0)
                self.__rearrange_items()
        combobox_installed.clicked.connect(combobox_clicked)
        combobox_genre_0.clicked.connect(combobox_clicked)
        combobox_genre_1.clicked.connect(combobox_clicked)
        combobox_genre_2.clicked.connect(combobox_clicked)

        #combobox_genre_0.clicked.connect(lambda: combobox_genre_0.setCurrentIndex(0))
        # TODO Or load from config?
        combobox_genre_0.setCurrentIndex(0)
        combobox_genre_1.setCurrentIndex(0)
        combobox_genre_2.setCurrentIndex(0)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.slider.setFixedWidth(128)
        self.slider.setMinimum(128)
        self.slider.setMaximum(512)
        self.slider.setSingleStep(32)
        self.slider.setPageStep(128)
        self.slider.setValue(self.logos_width)
        self.slider.valueChanged.connect(self.__cb_slider)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(search_bar)
        hBoxLayout.addWidget(combobox_installed)
        hBoxLayout.addWidget(combobox_genre_0)
        hBoxLayout.addWidget(combobox_genre_1)
        hBoxLayout.addWidget(combobox_genre_2)
        #hBoxLayout.addWidget(self.slider)

        self.combobox_0 = QComboBox()
        self.combobox_0.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.combobox_0.addItems([
                _tr('OS'),
                _tr('Language'),
                _tr("Developer"),
                _tr("Publiser")
        ])
        self.combobox_1 = QComboBox()
        self.combobox_1.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.combobox_1.addItems([
                _tr('OS'),
                _tr('Language'),
                _tr("Developer"),
                _tr("Publiser")
        ])
        self.searchbar_0 = QLineEdit()
        self.searchbar_0.setClearButtonEnabled(True)
        self.searchbar_1 = QLineEdit()
        self.searchbar_1.setClearButtonEnabled(True)
        self.searchbar_0.textChanged.connect(self.__cb_searchbar_0)
        self.searchbar_1.textChanged.connect(self.__cb_searchbar_1)
        self.combobox_0.currentTextChanged.connect(lambda text: self.proxy_model.set_filter_0_type(text))
        self.combobox_1.currentTextChanged.connect(lambda text: self.proxy_model.set_filter_1_type(text))
        self.combobox_0.setVisible(False)
        self.searchbar_0.setVisible(False)
        self.combobox_1.setVisible(False)
        self.searchbar_1.setVisible(False)
        hBoxLayout2 = QHBoxLayout()
        hBoxLayout2.addWidget(self.combobox_0)
        hBoxLayout2.addWidget(self.searchbar_0)
        hBoxLayout2.addWidget(self.combobox_1)
        hBoxLayout2.addWidget(self.searchbar_1)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addLayout(hBoxLayout)
        vBoxLayout.addLayout(hBoxLayout2)
        vBoxLayout.addWidget(self.listview)

        vBoxLayout.addWidget(self.tableview)
        self.tableview.setVisible(False)

        def __cb_change_view():
            action_view_icon = QIcon(f'{self.data_path}/games_nebula/images/view_{int(not self.listview.isVisible())}.png')
            if not os.path.exists(f'{self.data_path}/games_nebula'):
                action_view_icon = QIcon(f'{self.data_path}/images/view_{int(not self.listview.isVisible())}.png')
            self.sender().setIcon(action_view_icon)
            self.listview.setVisible(not self.listview.isVisible())
            self.tableview.setVisible(not self.tableview.isVisible())
            self.slider.setVisible(not self.slider.isVisible())
            self.combobox_0.setVisible(not self.combobox_0.isVisible())
            self.searchbar_0.setVisible(not self.searchbar_0.isVisible())
            self.combobox_1.setVisible(not self.combobox_1.isVisible())
            self.searchbar_1.setVisible(not self.searchbar_1.isVisible())
            self.__rearrange_items()
            self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        page_library = QWidget()
        page_library.setLayout(vBoxLayout)

        page_downloads = QWidget()

        action_view_text = _tr("View mode (Ctl+V)")
        action_view_icon = QIcon(f'{self.data_path}/games_nebula/images/view_{int(not self.listview.isVisible())}.png')
        if not os.path.exists(f'{self.data_path}/games_nebula'):
            action_view_icon = QIcon(f'{self.data_path}/images/view_{int(not self.listview.isVisible())}.png')
        action_view = QAction(action_view_icon, action_view_text, self)
        action_view.setStatusTip(action_view_text)
        action_view.setShortcut('Ctrl+V')
        action_view.triggered.connect(__cb_change_view)

        action_settings_text = _tr("Settings (Ctl+S)")
        action_settings_icon = QIcon(f'{self.data_path}/games_nebula/images/settings.png')
        if not os.path.exists(f'{self.data_path}/games_nebula'):
            action_settings_icon = QIcon(f'{self.data_path}/images/settings.png')
        action_settings = QAction(action_settings_icon, action_settings_text, self)
        action_settings.setStatusTip(action_settings_text)
        action_settings.setShortcut('Ctrl+S')

        toolbar = QToolBar()
        #toolbar.addWidget(self.slider)
        toolbar.addAction(action_view)
        toolbar.addAction(action_settings)

        hBoxLayout3 = QHBoxLayout()
        hBoxLayout3.setContentsMargins(0, 0, 0, 0)
        container = QWidget()
        container.setLayout(hBoxLayout3)
        hBoxLayout3.addWidget(self.slider)
        hBoxLayout3.addWidget(toolbar)

        tabwidget = QTabWidget()
        tabwidget.setCornerWidget(container, Qt.Corner.TopRightCorner)
        #tabwidget.setCornerWidget(toolbar)

        #tabwidget.setTabBar(tabbar)
        #tabwidget.setTabBarAutoHide(True)
        #tabwidget.setTabsClosable(True)
        #tabwidget.tabCloseRequested.connect(self.__cb_tabclosed)
        tabwidget.addTab(page_library, _tr("LIBRARY"))
        #tabwidget.addTab(page_library_2, _tr("LIBRARY 2"))
        tabwidget.setTabEnabled(tabwidget.addTab(page_downloads, _tr("DOWNLOADS")), False)
        self.setCentralWidget(tabwidget)

        #self.setLayout(vBoxLayout)

        self.resized.connect(self.__cb_window_resized)

    def __set_icons(self):

        items = dict()

        def download_icon(game_icon_url, game_icon_path):
            if game_icon_url:
                try:
                    resp = urllib.request.urlopen(game_icon_url)
                    data = resp.read()
                    game_icon_dir = os.path.dirname(game_icon_path)
                    if not os.path.exists(game_icon_dir): os.makedirs(game_icon_dir)
                    with open(game_icon_path, 'wb') as f:
                        f.write(data)
                except:
                    pass

        def __set_icon(args):
            if args and args[0]:
                game_icon_path = args[1]
                game_slug = os.path.basename(game_icon_path).split('.')[0]
                game_icon = QIcon(game_icon_path)
                items[game_slug].setData(game_icon, Qt.ItemDataRole.DecorationRole)

        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            game_slug = data['game_slug']
            game_icon_url = self._api.get_game_icon_url(game_slug, size=config.get('icons_size'))
            game_icon_path = self._api.get_game_icon_file_path(game_slug, size=config.get('icons_size'))
            items[game_slug] = item
            if not os.path.isfile(game_icon_path):
                runnable = Runnable(download_icon, game_icon_url, game_icon_path)
                runnable.singnals.finished.connect(__set_icon)
                thread_pool = QThreadPool.globalInstance()
                thread_pool.start(runnable)
            else:
                game_icon = QIcon(game_icon_path)
                item.setData(game_icon, Qt.ItemDataRole.DecorationRole)

    #def __cb_tabclosed(self, tab_index):
    #    if tab_index != 0:
    #        self.sender().removeTab(tab_index)

    def __cb_search_bar(self, text):
        self.proxy_model.setFilterFixedString(text.strip())
        self.__rearrange_items()

    def __cb_searchbar_0(self, text):
        self.proxy_model.set_filter_0(text.strip())
        self.proxy_model.set_filter_0_type(self.combobox_0.currentText())
        self.__rearrange_items()

    def __cb_searchbar_1(self, text):
        self.proxy_model.set_filter_1(text.strip())
        self.proxy_model.set_filter_1_type(self.combobox_1.currentText())
        self.__rearrange_items()

    def __cb_slider(self, value):
        self.logos_width = value
        proxy_model = self.listview.model()
        rows = proxy_model.rowCount()
        if rows > 0:
            for i in range(rows):
                index = proxy_model.index(i, 0)
                game_widget = self.listview.indexWidget(index)
                if game_widget:
                    game_widget.scale_logo(self.logos_width)
        self.__rearrange_items()

    def __cb_window_resized(self):
        self.__rearrange_items()

    def __rearrange_items(self):
        proxy_model = self.listview.model()
        rows = proxy_model.rowCount()
        if rows > 0:
            #listview_w = self.listview.viewport().width() - self.listview.verticalScrollBar().width()
            listview_w = self.listview.contentsRect().width() - self.listview.verticalScrollBar().width()
            item_w = self.logos_width + 20 # layout ContentsMargins
            colums_n = int(listview_w / item_w)
            if colums_n <= 0: colums_n = 1
            item_w = int(listview_w / colums_n) - 1
            #############################################
            ## TODO Make this prettier :)
            #############################################
            #scale_factor = 200 / self.logos_width
            #item_h = int(120 / scale_factor) + 40 + 20
            item_h = int(self.logos_width / 1.666666667) + 40 + 20 # button height + ContentsMargins
            #############################################
            model = proxy_model.sourceModel()
            for i in range(rows):
                index = proxy_model.index(i, 0)
                source_index = proxy_model.mapToSource(index)
                item = model.itemFromIndex(source_index)
                #item_h = item.sizeHint().height()
                game_widget = self.listview.indexWidget(index)
                if game_widget:
                    game_widget.scale_logo(self.logos_width)
                    #item_h = game_widget.sizeHint().height()
                #if item_h > 0:
                item.setSizeHint(QSize(item_w, item_h))
        self.listview.setWrapping(True)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
