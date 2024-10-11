import os

from PyQt6 import sip
from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QThread, QSize
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QCheckBox, QMessageBox, QProgressBar, QLabel, QFrame, \
    QComboBox, QHBoxLayout, QSizePolicy

from modmanager import ModManager
from view.listmodwidget import ListModWidget


class Installer(QObject):
    progress = pyqtSignal(int)
    completed = pyqtSignal(int)
    update_data_completed = pyqtSignal()

    @pyqtSlot(ModManager, list, bool, dict, bool, str, bool)
    def install(self, mod_manager, mod_to_be_installed, keep_downloaded_mod, special_status={}, download=True,
                ff8_version="ffnx", backup=True):
        for index, mod_name in enumerate(mod_to_be_installed):
            mod_manager.install_mod(mod_name, keep_downloaded_mod, special_status, download, ff8_version, backup)
            self.progress.emit(index + 1)
        self.completed.emit(len(mod_to_be_installed))

    @pyqtSlot(ModManager)
    def update_data(self, mod_manager):
        mod_manager.update_data()
        self.update_data_completed.emit()


class WindowInstaller(QWidget):
    install_requested = pyqtSignal(ModManager, list, bool, dict, bool, str, bool)
    update_data_requested = pyqtSignal(ModManager)

    VERSION_LIST = ["FF8 PC 2000", "FF8 Steam 2013", "FF8 Remastered"]
    LANG_LIST = ["en", "fr", "de"]
    MOD_TYPE_LIST = ["All", "Wrapper", "Graphical", "Music", "Gameplay", "EaseOfLife"]

    def __init__(self, mod_manager, icon_path=os.path.join("HobbitInstaller-data", 'Resources')):

        QWidget.__init__(self)
        # Managing thread
        self.installer = Installer()
        self.installer_thread = QThread()
        self.installer.progress.connect(self.install_progress)
        self.installer.completed.connect(self.install_completed)
        self.installer.update_data_completed.connect(self.update_data_completed)
        self.install_requested.connect(self.installer.install)
        self.update_data_requested.connect(self.installer.update_data)
        self.installer.moveToThread(self.installer_thread)
        self.installer_thread.start()

        # Main window
        self.setWindowTitle("HobbitInstaller")
        #self.setMinimumWidth(300)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.__icon = QIcon(os.path.join(icon_path, 'icon.png'))
        self.__icon_info = QIcon(os.path.join(icon_path, 'info.png'))
        self.setWindowIcon(self.__icon)
        self.__setup_setup()
        self.__setup_main()

        self.mod_widget = ListModWidget(mod_manager, self.language.currentText(), self.ff8_version.currentText(),
                                        self.mod_type.currentText())
        self.mod_manager = mod_manager

        self.layout_main = QVBoxLayout()
        self.layout_setup = QVBoxLayout()
        self.layout_ff8_version = QHBoxLayout()
        self.layout_language = QHBoxLayout()
        self.layout_mod_type = QHBoxLayout()
        self.setup_layout()
        self.show_all()

    def __show_info(self):
        message_box = QMessageBox()
        message_box.setText(f"Tool done by <b>Hobbitdur</b>.<br/>"
                            f"You can support me on <a href='https://www.patreon.com/HobbitMods'>Patreon</a>.<br/>")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowIcon(self.__icon)
        message_box.setWindowTitle("HobbitInstaller - Info")
        message_box.exec()

    def __clear_one_layout(self, layout):
        if layout:
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                widget = item.widget()
                if widget:
                    # widget.setParent(None)
                    sip.delete(widget)

    def __clear_layout(self):
        pass
        # self.__clear_one_layout(self.layout_setup)
        # self.__clear_one_layout(self.layout_mod)
        # self.__clear_one_layout(self.layout_main)
        # self.__clear_one_layout(self.layout_ragnarok)
        # self.__clear_one_layout(self.layout_ff8reloaded)
        # self.layout_mod = QVBoxLayout()
        # self.layout_ragnarok = QVBoxLayout()
        # self.layout_ff8reloaded = QVBoxLayout()

    def __setup_main(self):
        # Button install
        self.install_button = QPushButton(parent=self, text="Install")
        self.install_button.clicked.connect(self.install_click)
        self.install_over = QMessageBox(parent=self)
        self.install_over.setWindowTitle("Installing over!")
        self.install_over.setText("Installing over!")
        self.install_over.hide()

        # Button Update link data
        self.update_data_button = QPushButton(parent=self, text="Updating mod list")
        self.update_data_button.clicked.connect(self.update_data_click)
        self.update_data_button.setToolTip("Update mod list, version available and link")

        self.restore_button = QPushButton(parent=self, text="Restore backup data")
        self.restore_button.clicked.connect(self.restore_click)
        self.restore_button.setToolTip("Restore the folder from the zip previously created")

        self.update_data_over = QMessageBox(parent=self)
        self.update_data_over.setIcon(QMessageBox.Icon.Information)
        self.update_data_over.setWindowTitle("Updating data over!")
        self.update_data_over.setText("Updating data over!")
        self.update_data_over.hide()

        self.progress = QProgressBar(parent=self)

    def __setup_setup(self):
        # Setup
        self.label_setup = QLabel(parent=self, text="Setup parameters")
        self.label_setup.setFont(QFont('Arial', 12))
        self.label_setup.setStyleSheet("font-weight: bold")
        self.label_setup.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.download = QCheckBox(parent=self, text="Download from internet")
        self.download.setChecked(True)
        self.download.setToolTip(
            "Check to download from internet, uncheck to use previously downloaded files and kept with the keep mod_archive")
        self.keep_mod_archive = QCheckBox(parent=self, text="Keep mod_archive")
        self.keep_mod_archive.setChecked(False)
        self.keep_mod_archive.setToolTip(
            "To keep the downloaded files from the internet, to be able to reuse them manually")

        self.backup = QCheckBox(parent=self, text="Backup data")
        self.backup.setChecked(True)
        self.backup.setToolTip("Backup in a zip the content of the Data folder.<br>"
                               "If you have already backup the data, no new backup will be done")

        self.ff8_version_label = QLabel(parent=self, text="FF8 Version")
        self.ff8_version = QComboBox(parent=self)
        self.ff8_version.addItems(self.VERSION_LIST)
        self.ff8_version.activated.connect(self.reload_gui)
        self.ff8_version.setToolTip(
            "Your FF8 version, either the classic one from steam released in 2013, or the remaster.")
        self.ff8_version.setCurrentIndex(1)

        self.language_label = QLabel(parent=self, text="FF8 language")
        self.language = QComboBox(parent=self)
        self.language.addItems(self.LANG_LIST)
        self.language.activated.connect(self.reload_gui)
        self.language.setToolTip("The language you play on")

        self.mod_type_label = QLabel(parent=self, text="Mod type")
        self.mod_type = QComboBox(parent=self)
        self.mod_type.addItems(self.MOD_TYPE_LIST)
        self.mod_type.activated.connect(self.reload_gui)
        self.mod_type.setToolTip("To sort all mods by type")

        self.separator = QFrame(self)
        self.separator.setFrameStyle(0x04)  # Can't find QFrame.HLine so here we are
        self.separator.setLineWidth(2)

        self.info_button = QPushButton()
        self.info_button.setIcon(self.__icon_info)
        self.info_button.setIconSize(QSize(30, 30))
        self.info_button.setFixedSize(40, 40)
        self.info_button.setToolTip("Show toolmaker info")
        self.info_button.clicked.connect(self.__show_info)

    def __setup_setup_layout(self):
        self.layout_title = QHBoxLayout()
        self.layout_title.addWidget(self.info_button)
        self.layout_title.addWidget(self.label_setup)
        self.layout_setup.addLayout(self.layout_title)

        self.layout_ff8_version.addWidget(self.ff8_version_label)
        self.layout_ff8_version.addWidget(self.ff8_version)
        self.layout_ff8_version.addStretch(1)

        self.layout_language.addWidget(self.language_label)
        self.layout_language.addWidget(self.language)
        self.layout_language.addStretch(1)

        self.layout_setup.addLayout(self.layout_language)
        self.layout_setup.addLayout(self.layout_ff8_version)
        self.layout_setup.addLayout(self.layout_mod_type)
        # self.layout_setup.addWidget(self.download)
        self.download.hide()
        self.layout_setup.addWidget(self.keep_mod_archive)
        self.layout_setup.addWidget(self.backup)
        self.layout_setup.addWidget(self.separator)

    def __setup_main_layout(self):
        self.layout_main.addLayout(self.layout_setup)
        self.layout_main.addWidget(self.mod_widget)
        self.layout_main.addWidget(self.update_data_button)
        self.layout_main.addWidget(self.install_button)
        self.layout_main.addWidget(self.progress)
        self.setLayout(self.layout_main)

    def show_all(self):
        self.mod_widget.show()
        self.install_button.show()
        self.progress.hide()
        #self.resize(self.minimumSizeHint())
        self.show()

    def setup_layout(self):
        self.__setup_setup_layout()
        self.__setup_main_layout()
        # self.resize(self.minimumSizeHint())

    def install_click(self):
        self.progress.show()
        (mod_to_be_installed, special_status) = self.mod_widget.get_mod_to_install()

        self.progress.setRange(0, len(mod_to_be_installed) + 1)
        self.progress.setValue(1)
        download = self.download.isChecked()
        if self.ff8_version.currentText() in (self.VERSION_LIST[0], self.VERSION_LIST[1]):
            ff8_version = "ffnx"
        elif self.ff8_version.currentText() == self.VERSION_LIST[1]:
            ff8_version = "demaster"
        else:
            ff8_version = ""
        self.install_requested.emit(self.mod_manager, mod_to_be_installed, self.keep_mod_archive.isChecked(),
                                    special_status, download, ff8_version, self.backup.isChecked())

    def update_data_click(self):
        self.progress.show()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.update_data_requested.emit(self.mod_manager)

    def restore_click(self):
        self.progress.show()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.update_data_requested.emit(self.mod_manager)

    def install_progress(self, nb_install_done):
        self.progress.setValue(nb_install_done + 1)

    def install_completed(self, nb_install_done):
        self.progress.setValue(nb_install_done + 1)
        self.progress.hide()
        self.install_over.show()
        #self.resize(self.minimumSizeHint())

    def update_data_completed(self):
        self.progress.setValue(1)
        self.progress.hide()
        self.update_data_over.show()
        self.reload_gui()

    def reload_gui(self):
        lang = self.language.currentText()
        ff8_version = self.ff8_version.currentText()
        mod_type = self.mod_type.currentText()
        # self.__clear_layout()
        self.mod_widget.show_specific_mod(lang, ff8_version, mod_type)

        # self.layout_main.insertLayout(1, self.layout_mod)
        self.show_all()
        #self.resize(self.minimumSizeHint())
