import os
import sys

from PyQt6 import sip
from PyQt6.QtCore import Qt, QCoreApplication, QThreadPool, QRunnable, QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QCheckBox, QMessageBox, QProgressDialog, \
    QMainWindow, QProgressBar, QRadioButton, \
    QLabel, QFrame, QStyle, QSizePolicy, QButtonGroup, QComboBox, QHBoxLayout

from modmanager import ModManager


class Installer(QObject):
    progress = pyqtSignal(int)
    completed = pyqtSignal(int)
    update_data_completed = pyqtSignal()

    @pyqtSlot(ModManager, list, bool, dict, bool)
    def install(self, mod_manager, mod_to_be_installed, keep_downloaded_mod, special_status={}, download=True):
        for index, mod_name in enumerate(mod_to_be_installed):
            mod_manager.install_mod(mod_name, keep_downloaded_mod, special_status, download)
            self.progress.emit(index + 1)
        self.completed.emit(len(mod_to_be_installed))

    @pyqtSlot(ModManager)
    def update_data(self, mod_manager):
        mod_manager.update_data()
        self.update_data_completed.emit()


class WindowInstaller(QWidget):
    install_requested = pyqtSignal(ModManager, list, bool, dict, bool)
    update_data_requested = pyqtSignal(ModManager)
    FF8_RELOAD_NAME = "FFVIII-Reloaded-FR-ONLY"
    RAGNAROK_NAME = "Ragnarok-EN-ONLY"
    LIST_SPECIAL_MOD = [FF8_RELOAD_NAME, RAGNAROK_NAME]
    VERSION_LIST = ["FF8 Steam 2013", "FF8 Remastered"]
    LANG_LIST = ["en", "fr", "de"]
    MOD_TYPE_LIST = ["All", "Wrapper", "Graphical", "Music", "Gameplay", "EaseOfLife"]

    def __init__(self, mod_manager, icon_path='Resources'):

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

        # General data
        self.mod_checkbox = {}
        self.mod_manager = mod_manager

        # Main window
        self.setWindowTitle("HobbitInstaller")
        self.setMinimumWidth(300)
        self.setWindowIcon(QIcon(os.path.join(icon_path, 'icon.png')))
        self.__setup_setup()
        self.__setup_mod()
        self.__setup_main()

        self.layout_main = QVBoxLayout()
        self.layout_setup = QVBoxLayout()
        self.layout_ff8_version = QHBoxLayout()
        self.layout_language = QHBoxLayout()
        self.layout_mod_type = QHBoxLayout()
        self.layout_mod = QVBoxLayout()
        self.layout_ragnarok = QVBoxLayout()
        self.layout_ff8reloaded = QVBoxLayout()
        self.setup_layout()
        self.show_all()

    def __clear_one_layout(self, layout):
        if layout:
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                widget = item.widget()
                if widget:
                    # widget.setParent(None)
                    sip.delete(widget)

    def __clear_layout(self):
        # self.__clear_one_layout(self.layout_setup)
        self.__clear_one_layout(self.layout_mod)
        # self.__clear_one_layout(self.layout_main)
        self.__clear_one_layout(self.layout_ragnarok)
        self.__clear_one_layout(self.layout_ff8reloaded)
        self.layout_mod = QVBoxLayout()
        self.layout_ragnarok = QVBoxLayout()
        self.layout_ff8reloaded = QVBoxLayout()

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

        self.update_data_over = QMessageBox(parent=self)
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
        self.keep_mod_archive.setToolTip("To keep the downloaded files from the internet, to be able to reuse them")

        self.ff8_version_label = QLabel(parent=self, text="FF8 Version")
        self.ff8_version = QComboBox(parent=self)
        self.ff8_version.addItems(self.VERSION_LIST)
        self.ff8_version.activated.connect(self.reload_gui)
        self.ff8_version.setToolTip(
            "Your FF8 version, either the classic one from steam released in 2013, or the remaster.")

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

    def __setup_mod(self):
        self.label_mod = QLabel("Mod selection")
        self.label_mod.setFont(QFont('Arial', 12))
        self.label_mod.setStyleSheet("font-weight: bold")
        self.label_mod.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # FFVIII Reloaded
        self.ff8reloaded_classic = QRadioButton(parent=self, text="FF8 Reloaded Classic")
        self.ff8reloaded_classic.setChecked(True)
        self.ff8reloaded_classic.toggled.connect(lambda: self.ff8reloadedstate(self.ff8reloaded_classic))
        self.ff8reloaded_classic.hide()
        self.ff8reloaded_level1 = QRadioButton(parent=self, text="FF8 Reloaded Level 1")
        self.ff8reloaded_level1.toggled.connect(lambda: self.ff8reloadedstate(self.ff8reloaded_level1))
        self.ff8reloaded_level1.hide()
        self.ff8reloaded_level100 = QRadioButton(parent=self, text="FF8 Reloaded Level 100")
        self.ff8reloaded_level100.toggled.connect(lambda: self.ff8reloadedstate(self.ff8reloaded_level100))
        self.ff8reloaded_level100.hide()
        self.parent_ff8reloaded = QButtonGroup(self)
        self.parent_ff8reloaded.addButton(self.ff8reloaded_classic)
        self.parent_ff8reloaded.addButton(self.ff8reloaded_level1)
        self.parent_ff8reloaded.addButton(self.ff8reloaded_level100)

        # Ragnarok
        self.ragnarok_standard = QRadioButton(parent=self, text="Ragnarok standard")
        self.ragnarok_standard.setChecked(True)
        self.ragnarok_standard.toggled.connect(lambda: self.ragnarokstate(self.ragnarok_standard))
        self.ragnarok_standard.hide()
        self.ragnarok_lionheart = QRadioButton(parent=self, text="Ragnarok lionheart")
        self.ragnarok_lionheart.toggled.connect(lambda: self.ragnarokstate(self.ragnarok_lionheart))
        self.ragnarok_lionheart.hide()
        self.parent_ragnarok = QButtonGroup(self)
        self.parent_ragnarok.addButton(self.ragnarok_standard)
        self.parent_ragnarok.addButton(self.ragnarok_lionheart)

        self.__reset_mod_loaded()

    def __reset_mod_loaded(self):
        self.mod_checkbox.clear()
        for mod_name, mod_info in self.mod_manager.mod_dict_json.items():
            if mod_name != "UpdateData":  # It's our "local mod" to update the setup.json
                if mod_info["download_type"] == 'github' or mod_info["download_type"] == 'direct':
                    if self.language.currentText() in mod_info["lang"]:
                        if (self.ff8_version.currentText() == self.VERSION_LIST[0] and "ffnx" in mod_info[
                            "compatibility"]) \
                                or (self.ff8_version.currentText() == self.VERSION_LIST[1] and "demaster" in mod_info["compatibility"]):
                            if self.mod_type.currentText() == "All" or (
                                    self.mod_type.currentText() == mod_info["mod_type"]):
                                self.mod_checkbox[mod_name] = QCheckBox(parent=self, text=mod_name)
                                self.mod_checkbox[mod_name].setToolTip(
                                    "Author: {}\nDescription: {}".format(mod_info["modder_name"], mod_info["mod_info"]))
                                if mod_info["default_selected"] == "true":
                                    self.mod_checkbox[mod_name].setChecked(True)
                                if mod_name == self.FF8_RELOAD_NAME:
                                    self.mod_checkbox[mod_name].toggled.connect(self.activate_ff8reload)
                                elif mod_name == self.RAGNAROK_NAME:
                                    self.mod_checkbox[mod_name].toggled.connect(self.activate_ragnarok)
                else:
                    print(
                        "No type found for mod {} with value {}".format(mod_name, mod_info[mod_name]))

    def __setup_setup_layout(self):
        self.layout_setup.addWidget(self.label_setup)
        self.layout_ff8_version.addWidget(self.ff8_version_label)
        self.layout_ff8_version.addWidget(self.ff8_version)
        self.layout_ff8_version.addStretch(1)
        self.layout_language.addWidget(self.language_label)
        self.layout_language.addWidget(self.language)
        self.layout_language.addStretch(1)
        self.layout_mod_type.addWidget(self.mod_type_label)
        self.layout_mod_type.addWidget(self.mod_type)
        self.layout_mod_type.addStretch(1)

        self.layout_setup.addLayout(self.layout_language)
        self.layout_setup.addLayout(self.layout_ff8_version)
        self.layout_setup.addLayout(self.layout_mod_type)
        self.layout_setup.addWidget(self.download)
        self.layout_setup.addWidget(self.keep_mod_archive)
        self.layout_setup.addWidget(self.separator)

    def __setup_mod_layout(self):
        self.layout_mod.addWidget(self.label_mod)
        for key, mod in self.mod_checkbox.items():
            if key not in self.LIST_SPECIAL_MOD:
                self.layout_mod.addWidget(mod)
            else:
                if key == self.FF8_RELOAD_NAME:
                    self.layout_ff8reloaded.addWidget(self.mod_checkbox[self.FF8_RELOAD_NAME])
                    self.layout_ff8reloaded.addWidget(self.ff8reloaded_classic)
                    self.layout_ff8reloaded.addWidget(self.ff8reloaded_level1)
                    self.layout_ff8reloaded.addWidget(self.ff8reloaded_level100)

                elif key == self.RAGNAROK_NAME:
                    self.layout_ragnarok.addWidget(self.mod_checkbox[self.RAGNAROK_NAME])
                    self.layout_ragnarok.addWidget(self.ragnarok_standard)
                    self.layout_ragnarok.addWidget(self.ragnarok_lionheart)

        if self.FF8_RELOAD_NAME in self.mod_checkbox:
            self.layout_mod.addLayout(self.layout_ff8reloaded)
        if self.RAGNAROK_NAME in self.mod_checkbox:
            self.layout_mod.addLayout(self.layout_ragnarok)

    def __setup_main_layout(self):
        self.layout_main.addLayout(self.layout_setup)
        self.layout_main.addLayout(self.layout_mod)
        self.layout_main.addWidget(self.update_data_button)
        self.layout_main.addWidget(self.install_button)
        self.layout_main.addWidget(self.progress)
        self.layout_main.addStretch(1)
        self.setLayout(self.layout_main)

    def activate_ff8reload(self):
        if self.mod_checkbox[self.FF8_RELOAD_NAME].isChecked():
            self.ff8reloaded_classic.show()
            self.ff8reloaded_level1.show()
            self.ff8reloaded_level100.show()
        else:
            self.ff8reloaded_classic.hide()
            self.ff8reloaded_level1.hide()
            self.ff8reloaded_level100.hide()
        self.resize(self.minimumSizeHint())

    def activate_ragnarok(self):
        if self.mod_checkbox[self.RAGNAROK_NAME].isChecked():
            self.ragnarok_standard.show()
            self.ragnarok_lionheart.show()
        else:
            self.ragnarok_standard.hide()
            self.ragnarok_lionheart.hide()
        self.resize(self.minimumSizeHint())

    def ff8reloadedstate(self, b):
        pass

    def ragnarokstate(self, b):
        pass

    def show_all(self):
        for key, mod in self.mod_checkbox.items():
            mod.show()
        self.install_button.show()
        self.progress.hide()
        self.resize(self.minimumSizeHint())
        self.show()

    def setup_layout(self):
        self.__setup_setup_layout()

        self.__setup_mod_layout()
        self.__setup_main_layout()
        # self.resize(self.minimumSizeHint())

    def install_click(self):

        self.progress.show()
        mod_to_be_installed = []
        special_status = {}
        for mod_name, mod_info in self.mod_manager.mod_dict_json.items():
            if mod_name not in self.mod_checkbox.keys():
                continue
            if mod_name == self.FF8_RELOAD_NAME:
                if self.ff8reloaded_classic.isChecked():
                    special_status[self.FF8_RELOAD_NAME] = self.ff8reloaded_classic.text()
                elif self.ff8reloaded_level1.isChecked():
                    special_status[self.FF8_RELOAD_NAME] = self.ff8reloaded_level1.text()
                elif self.ff8reloaded_level100.isChecked():
                    special_status[self.FF8_RELOAD_NAME] = self.ff8reloaded_level100.text()
            elif mod_name == self.RAGNAROK_NAME:
                if self.ragnarok_standard.isChecked():
                    special_status[self.RAGNAROK_NAME] = self.ragnarok_standard.text()
                elif self.ragnarok_lionheart.isChecked():
                    special_status[self.RAGNAROK_NAME] = self.ragnarok_lionheart.text()
            if self.mod_checkbox[mod_name].checkState() == Qt.CheckState.Checked:
                mod_to_be_installed.append(mod_name)
        self.progress.setRange(0, len(mod_to_be_installed) + 1)
        self.progress.setValue(1)
        download = self.download.isChecked()
        self.install_requested.emit(self.mod_manager, mod_to_be_installed, self.keep_mod_archive.isChecked(),
                                    special_status, download)

    def update_data_click(self):
        self.progress.show()
        self.progress.setRange(0, 2)
        self.progress.setValue(1)
        self.update_data_requested.emit(self.mod_manager)

    def install_progress(self, nb_install_done):
        self.progress.setValue(nb_install_done + 1)

    def install_completed(self, nb_install_done):
        self.progress.setValue(nb_install_done + 1)
        self.progress.hide()
        self.install_over.show()
        self.resize(self.minimumSizeHint())

    def update_data_completed(self):
        self.progress.setValue(1)
        self.progress.hide()
        self.update_data_over.show()
        self.reload_gui()

    def reload_gui(self):
        self.__clear_layout()
        self.__setup_mod()
        self.__reset_mod_loaded()
        self.__setup_mod_layout()
        self.layout_main.insertLayout(1, self.layout_mod)
        self.show_all()
        self.resize(self.minimumSizeHint())
