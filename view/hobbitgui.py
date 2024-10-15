import os
import types

from PyQt6 import sip
from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QThread, QSize
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QCheckBox, QMessageBox, QProgressBar, QLabel, QFrame, \
    QComboBox, QHBoxLayout, QSizePolicy, QLayout

from model.mod import ModVersion, ModType, Mod
from modmanager import ModManager, GroupModType, ModLang, ModWrapper
from view.listmodwidget import ListModWidget


class Installer(QObject):
    progress = pyqtSignal(int)
    completed = pyqtSignal(int)
    update_mod_list_completed = pyqtSignal()
    restore_backup_completed = pyqtSignal(bool)

    @pyqtSlot(ModManager, list, types.MethodType, bool,  bool, ModWrapper, bool)
    def install(self, mod_manager, mod_to_be_installed, update_download_func, keep_downloaded_mod, download=True,
                ff8_version=ModWrapper.FFNX, backup=True):
        for index, mod_name in enumerate(mod_to_be_installed):
            mod_manager.install_mod(mod_name, update_download_func, keep_downloaded_mod, download, ff8_version, backup)
            self.progress.emit(index + 1)
        self.completed.emit(len(mod_to_be_installed)+1)

    @pyqtSlot(ModManager)
    def update_mod_list(self, mod_manager):
        mod_manager.update_mod_list()
        self.update_mod_list_completed.emit()

    @pyqtSlot(ModManager)
    def restore_backup(self, mod_manager):
        self.restore_backup_completed.emit(mod_manager.restore_backup())


class WindowInstaller(QWidget):
    install_requested = pyqtSignal(ModManager, list, types.MethodType, bool,  bool, ModWrapper, bool)
    update_mod_list_requested = pyqtSignal(ModManager)
    restore_backup_requested = pyqtSignal(ModManager)

    VERSION_STR_LIST = ["FF8 PC 2000", "FF8 Steam 2013", "FF8 Remastered"]
    VERSION_LIST = [ModVersion.FF8_2000, ModVersion.FF8_2013, ModVersion.FF8_REMASTER]
    LANG_STR_LIST = ["en", "fr", "de", "es", "it"]
    LANG_LIST = [ModLang.EN, ModLang.FR, ModLang.DE, ModLang.ES, ModLang.IT]
    MOD_TYPE_STRING_LIST = ["All", "Wrapper", "Graphical", "Music", "Gameplay", "EaseOfLife"]
    MOD_TYPE_LIST = [GroupModType.ALL, GroupModType.WRAPPER, GroupModType.GRAPHIC, GroupModType.MUSIC, GroupModType.GAMEPLAY, GroupModType.EASEOFLIFE]

    def __init__(self, mod_manager, icon_path=os.path.join("HobbitInstaller-data", 'Resources')):

        QWidget.__init__(self)
        # Managing thread
        self.installer = Installer()
        self.installer_thread = QThread()
        self.installer.progress.connect(self.install_progress)
        self.installer.completed.connect(self.install_completed)
        self.installer.update_mod_list_completed.connect(self.update_mod_list_completed)
        self.installer.restore_backup_completed.connect(self.restore_backup_completed)
        self.install_requested.connect(self.installer.install)
        self.update_mod_list_requested.connect(self.installer.update_mod_list)
        self.restore_backup_requested.connect(self.installer.restore_backup)
        self.installer.moveToThread(self.installer_thread)
        self.installer_thread.start()

        # Main window
        self.setWindowTitle("HobbitInstaller")
        # self.setMinimumWidth(400)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.__icon = QIcon(os.path.join(icon_path, 'icon.png'))
        self.__icon_info = QIcon(os.path.join(icon_path, 'info.png'))
        self.setWindowIcon(self.__icon)
        self.__setup_setup()
        self.__setup_main()

        self.mod_widget = ListModWidget(mod_manager)
        self._update_mod()
        self.mod_manager = mod_manager

        self.layout_main = QVBoxLayout()
        self.layout_setup = QVBoxLayout()
        self.layout_ff8_version = QHBoxLayout()
        self.layout_language = QHBoxLayout()
        self.layout_mod_type = QHBoxLayout()
        self.setup_layout()
        self.show_all()
        self.resize(self.sizeHint())

    def __show_info(self):
        message_box = QMessageBox()
        message_box.setText(f"Tool done by <b>Hobbitdur</b>.<br/>"
                            f"You can support me on <a href='https://www.patreon.com/HobbitMods'>Patreon</a>.<br/>")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowIcon(self.__icon)
        message_box.setWindowTitle("HobbitInstaller - Info")
        message_box.exec()

    def __setup_main(self):
        # Button install
        self.install_button = QPushButton(parent=self, text="Install")
        self.install_button.clicked.connect(self.install_click)
        self.install_over = QMessageBox(parent=self)
        self.install_over.setWindowTitle("Installing over!")
        self.install_over.setText("Installing over!")
        self.install_over.hide()

        # Button Update link data
        self.update_mod_list_button = QPushButton(parent=self, text="Updating mod list")
        self.update_mod_list_button.clicked.connect(self.update_mod_list)
        self.update_mod_list_button.setToolTip("Update mod list, version available and link")

        self.restore_button = QPushButton(parent=self, text="Restore backup data")
        self.restore_button.clicked.connect(self.restore_click)
        self.restore_button.setToolTip("Restore the folder from the zip previously created")

        self.update_data_over = QMessageBox(parent=self)
        self.update_data_over.setIcon(QMessageBox.Icon.Information)
        self.update_data_over.setWindowTitle("Updating data over!")
        self.update_data_over.setText("Updating data over!")
        self.update_data_over.hide()

        self.progress = QProgressBar(parent=self)
        self.progress.setTextVisible(True)
        self.progress.setFormat("Full installation status")
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_current_download = QProgressBar(parent=self)
        self.progress_current_download.setTextVisible(True)
        self.progress_current_download.setFormat("Current download status")
        self.progress_current_download.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        self.ff8_version.addItems(self.VERSION_STR_LIST)
        self.ff8_version.activated.connect(self._update_mod)
        self.ff8_version.setToolTip(
            "Your FF8 version, either the classic one from steam released in 2013, or the remaster.")
        self.ff8_version.setCurrentIndex(1)

        self.language_label = QLabel(parent=self, text="FF8 language")
        self.language = QComboBox(parent=self)
        self.language.addItems(self.LANG_STR_LIST)
        self.language.activated.connect(self._update_mod)
        self.language.setToolTip("The language you play on")

        self.mod_type_label = QLabel(parent=self, text="Mod type")
        self.mod_type = QComboBox(parent=self)
        self.mod_type.addItems(self.MOD_TYPE_STRING_LIST)
        self.mod_type.activated.connect(self._update_mod)
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

        self.layout_ff8_version.addWidget(self.ff8_version_label)
        self.layout_ff8_version.addWidget(self.ff8_version)
        self.layout_ff8_version.addStretch(1)

        self.layout_mod_type.addWidget(self.mod_type_label)
        self.layout_mod_type.addWidget(self.mod_type)
        self.layout_mod_type.addStretch(1)

        self.layout_language.addWidget(self.language_label)
        self.layout_language.addWidget(self.language)
        self.layout_language.addStretch(1)

        self.layout_setup.addLayout(self.layout_title)
        self.layout_setup.addLayout(self.layout_language)
        self.layout_setup.addLayout(self.layout_ff8_version)
        self.layout_setup.addLayout(self.layout_mod_type)
        self.download.hide()
        self.layout_setup.addWidget(self.keep_mod_archive)
        self.layout_setup.addWidget(self.backup)
        self.layout_setup.addWidget(self.separator)
        self.layout_setup.addStretch(1)
        self.layout_setup.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

    def __setup_main_layout(self):
        self.layout_main.addLayout(self.layout_setup)
        self.layout_main.addWidget(self.mod_widget)
        self.layout_main.addWidget(self.restore_button)
        self.layout_main.addWidget(self.update_mod_list_button)
        self.layout_main.addWidget(self.install_button)
        self.layout_main.addWidget(self.progress)
        self.layout_main.addWidget(self.progress_current_download)
        self.layout_main.addStretch(1)
        self.setLayout(self.layout_main)

    def show_all(self):
        self.mod_widget.show()
        self.install_button.show()
        self.progress.hide()
        self.progress_current_download.hide()
        self.show()

    def setup_layout(self):
        self.__setup_setup_layout()
        self.__setup_main_layout()

    def install_click(self):
        self.progress.show()
        self.progress_current_download.show()
        mod_to_be_installed = self.mod_widget.get_mod_to_install()
        self.progress.setRange(0, len(mod_to_be_installed)+1)
        self.progress.setValue(0)
        self.install_requested.emit(self.mod_manager, mod_to_be_installed, self.update_download, self.keep_mod_archive.isChecked(), self.download.isChecked(), self.get_current_wrapper(), self.backup.isChecked())

    def update_download(self, advancement:int, max_size:int):
        print("update_download")
        print(advancement)
        print(max_size)
        if advancement > 0 and max_size >0:
            self.progress_current_download.setRange(0, max_size)
            self.progress_current_download.setValue(advancement)
        else:
            self.progress_current_download.setFormat("No download information")

    def update_mod_list(self):
        self.progress.show()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.update_mod_list_requested.emit(self.mod_manager)

    def restore_click(self):
        self.progress.show()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.restore_backup_requested.emit(self.mod_manager)

    def install_progress(self, nb_install_done):
        self.progress.setValue(nb_install_done)

    def install_completed(self, nb_install_done):
        self.progress.setValue(nb_install_done)
        self.progress.hide()
        self.progress_current_download.hide()
        self.progress.setValue(0)
        self.progress_current_download.setValue(0)
        self.install_over.show()
        self.progress_current_download.setFormat("Current download status")
        self.updateGeometry()
        # self.resize(self.minimumSizeHint())

    def update_mod_list_completed(self):
        self.progress.setValue(1)
        self.progress.hide()
        self.update_data_over.show()
        self._update_mod()

    def restore_backup_completed(self, worked):
        message_box = QMessageBox()
        if worked:
            message_box.setText(f"Backup retrieved !")
        else:
            message_box.setText(f"File backup_data.zip doesn't exist, couldn't retrieve")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowIcon(self.__icon)
        message_box.setWindowTitle("HobbitInstaller - Info")
        message_box.exec()
        self.progress.setValue(0)
        self.progress.hide()

    def get_current_lang(self):
        return self.LANG_LIST[self.language.currentIndex()]

    def get_current_wrapper(self):
        if self.get_current_version() in (ModVersion.FF8_2000, ModVersion.FF8_2013):
            return ModWrapper.FFNX
        elif self.get_current_version() == ModVersion.FF8_REMASTER:
            return ModWrapper.DEMASTER
        else:
            print(f"Unexpected value for current wrapper: {self.get_current_version()}")

    def get_current_version(self):
        return self.VERSION_LIST[self.ff8_version.currentIndex()]

    def get_current_mod_type(self):
        return self.MOD_TYPE_LIST[self.mod_type.currentIndex()]

    def _update_mod(self):
        self.mod_widget.show_specific_mod(self.get_current_lang(), self.get_current_version(), self.get_current_mod_type())
