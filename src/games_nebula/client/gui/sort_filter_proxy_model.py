from games_nebula import __qt_version__
if __qt_version__ == '6':
    from PyQt6.QtCore import (
            Qt, QSortFilterProxyModel
    )
elif __qt_version__ == '5':
    from PyQt5.QtCore import (
            Qt, QSortFilterProxyModel
    )
from games_nebula.client.translator import _tr

class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, hidden, parent=None):
        super(SortFilterProxyModel, self).__init__(parent)
        self.genre_filter_0 = ''
        self.genre_filter_1 = ''
        self.genre_filter_2 = ''
        self.installed_filter = ''
        self.filter_0 = ''
        self.filter_0_type = ''
        self.filter_1 = ''
        self.filter_1_type = ''
        self.hidden = hidden

    def set_filter_0(self, text):
        self.filter_0 = text

    def set_filter_0_type(self, filter_type):
        self.filter_0_type = filter_type
        self.invalidateFilter()

    def set_filter_1(self, text):
        self.filter_1 = text

    def set_filter_1_type(self, filter_type):
        self.filter_1_type = filter_type
        self.invalidateFilter()

    def set_installed_filter(self, installed):
        self.installed_filter = installed
        self.invalidateFilter()

    def set_genre_filter_0(self, genre):
        self.genre_filter_0 = genre
        self.invalidateFilter()

    def set_genre_filter_1(self, genre):
        self.genre_filter_1 = genre
        self.invalidateFilter()

    def set_genre_filter_2(self, genre):
        self.genre_filter_2 = genre
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()

        index_0 = source_model.index(source_row, 0, source_parent)
        index_1 = source_model.index(source_row, 1, source_parent)
        index_2 = source_model.index(source_row, 2, source_parent)
        index_3 = source_model.index(source_row, 3, source_parent)
        index_4 = source_model.index(source_row, 4, source_parent)
        index_5 = source_model.index(source_row, 5, source_parent)

        title_filter = self.filterRegularExpression()
        item_title = source_model.data(index_0, Qt.ItemDataRole.DisplayRole)
        item_genres = source_model.data(index_1, Qt.ItemDataRole.DisplayRole)
        item_os = source_model.data(index_2, Qt.ItemDataRole.DisplayRole)
        item_lang = source_model.data(index_3, Qt.ItemDataRole.DisplayRole)
        item_dev = source_model.data(index_4, Qt.ItemDataRole.DisplayRole)
        item_publisher = source_model.data(index_5, Qt.ItemDataRole.DisplayRole)

        item = source_model.item(source_row)
        data = item.data(Qt.ItemDataRole.UserRole)
        game_slug = data['game_slug']
        game_installed = data['game_installed']
        #######################################################################

        condition_0 = True
        if self.filter_0:
            if self.filter_0_type == _tr("OS"):
                condition_0 = self.filter_0.lower() in item_os.lower()
            elif self.filter_0_type == _tr("Language"):
                condition_0 = self.filter_0.lower() in item_lang.lower()
            elif self.filter_0_type == _tr("Developer"):
                condition_0 = self.filter_0.lower() in item_dev.lower()
            elif self.filter_0_type == _tr("Publiser"):
                condition_0 = self.filter_0.lower() in item_publisher.lower()

        condition_1 = True
        if self.filter_1:
            if self.filter_1_type == _tr("OS"):
                condition_1 = self.filter_1.lower() in item_os.lower()
            elif self.filter_1_type == _tr("Language"):
                condition_1 = self.filter_1.lower() in item_lang.lower()
            elif self.filter_1_type == _tr("Developer"):
                condition_1 = self.filter_1.lower() in item_dev.lower()
            elif self.filter_1_type == _tr("Publiser"):
                condition_1 = self.filter_1.lower() in item_publisher.lower()

        condition_3 = False
        if self.installed_filter == '':
            condition_3 = True
        elif game_installed == self.installed_filter:
            condition_3 = True

        #if (item_title.lower().startswith(title_filter.pattern().lower()) \
        #        or (game_slug.startswith(title_filter.pattern().lower()))) \
        # OR?
        if  (title_filter.match(item_title).hasMatch() \
                or title_filter.match(game_slug).hasMatch()) \
                    and self.genre_filter_0 in item_genres \
                    and self.genre_filter_1 in item_genres \
                    and self.genre_filter_2 in item_genres \
                    and game_slug not in self.hidden \
                    and condition_0 \
                    and condition_1 \
                    and condition_3:
            return True
        return False
