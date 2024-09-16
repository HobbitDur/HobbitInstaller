import os

from PyQt6.QtCore import Qt, QCoreApplication, QThreadPool, QRunnable, QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QCheckBox, QMessageBox, QProgressDialog, QMainWindow, QProgressBar, QRadioButton, \
    QLabel, QFrame, QStyle, QSizePolicy

from modmanager import ModManager


class Installer(QObject):
    progress = pyqtSignal(int)
    completed = pyqtSignal(int)

    @pyqtSlot(ModManager, list, bool, dict, bool)
    def install(self, mod_manager, mod_to_be_installed, keep_downloaded_mod, special_status={}, download=True):
        for index, mod_name in enumerate(mod_to_be_installed):
            mod_manager.install_mod(mod_name, keep_downloaded_mod, special_status, download)
            self.progress.emit(index + 1)
        self.completed.emit(len(mod_to_be_installed))


class WindowInstaller(QWidget):
    install_requested = pyqtSignal(ModManager, list, bool, dict, bool)
    FF8_RELOAD_NAME = "FFVIII-Reloaded-FR-ONLY"
    MOD_CHECK_DEFAULT = ['FFNx', 'FFNxFF8Music']
    def __init__(self, mod_manager, icon_path='ModSetup'):

        QWidget.__init__(self)
        # Managing thread
        self.installer = Installer()
        self.installer_thread = QThread()
        self.installer.progress.connect(self.install_progress)
        self.installer.completed.connect(self.install_completed)
        self.install_requested.connect(self.installer.install)
        self.installer.moveToThread(self.installer_thread)
        self.installer_thread.start()

        # General data
        self.mod_checkbox = {}
        self.mod_manager = mod_manager

        # Main window
        self.setWindowTitle("HobbitInstaller")
        self.setMinimumWidth(300)
        self.setWindowIcon(QIcon(os.path.join(icon_path, 'icon.png')))

        # Setup
        self.label_setup = QLabel(parent=self, text="Setup parameters")
        # Checkbox
        self.download = QCheckBox(parent=self, text="Download from internet")
        self.download.setChecked(True)
        self.keep_mod_archive = QCheckBox(parent=self, text="Keep mod_archive")
        self.keep_mod_archive.setChecked(False)

        self.separator = QFrame(self)
        self.separator.setFrameStyle(0x04)  # Can't find QFrame.HLine so here we are
        self.separator.setLineWidth(2)

        # Mod
        self.label_mod = QLabel("Mod selection")
        for mod_name in self.mod_manager.mod_file_list:
            if self.mod_manager.mod_dict[mod_name]['type'] == 'github':
                self.mod_checkbox[mod_name] = QCheckBox(mod_name)
            elif self.mod_manager.mod_dict[mod_name]['type'] == 'direct_link':
                self.mod_checkbox[mod_name] = QCheckBox(mod_name)
            else:
                print("No type found for mod {} with value {}".format(mod_name, self.mod_manager.mod_dict[mod_name]))
            if mod_name in self.MOD_CHECK_DEFAULT:
                self.mod_checkbox[mod_name].setChecked(True)
            if mod_name == self.FF8_RELOAD_NAME:
                self.mod_checkbox[mod_name].toggled.connect(self.activate_ff8reload)

        # Button install
        self.install_button = QPushButton(parent=self, text="Install")
        self.install_button.clicked.connect(self.install_click)
        self.install_over = QMessageBox(parent=self)
        self.install_over.setWindowTitle("Installing over!")
        self.install_over.setText("Installing over!")
        self.install_over.hide()

        # FFVIII Reloaded
        self.ff8reloaded_classic = QRadioButton(parent=self, text="FF8 Reloaded Classic")
        self.ff8reloaded_classic.setChecked(True)
        self.ff8reloaded_classic.toggled.connect(lambda: self.ff8reloadedstate(self.ff8reloaded_classic))
        self.ff8reloaded_classic.hide()

        self.ff8reloaded_level1 = QRadioButton(parent=self,  text="FF8 Reloaded Level 1")
        self.ff8reloaded_level1.toggled.connect(lambda: self.ff8reloadedstate(self.ff8reloaded_level1))
        self.ff8reloaded_level1.hide()
        self.ff8reloaded_level100 = QRadioButton(parent=self,  text="FF8 Reloaded Level 100")
        self.ff8reloaded_level100.toggled.connect(lambda: self.ff8reloadedstate(self.ff8reloaded_level100))
        self.ff8reloaded_level100.hide()

        self.progress = QProgressBar(parent=self)

        self.layout_main = QVBoxLayout()
        self.layout_setup = QVBoxLayout()
        self.layout_mod = QVBoxLayout()
        self.setup_layout()
        self.show_all()

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

    def ff8reloadedstate(self, b):
        pass

    def show_all(self):
        for key, mod in self.mod_checkbox.items():
            mod.show()
        self.install_button.show()
        self.progress.hide()
        self.show()
        self.resize(self.minimumSizeHint())

    def setup_layout(self):
        self.layout_setup.addWidget(self.label_setup)

        self.layout_setup.addWidget(self.download)
        self.layout_setup.addWidget(self.keep_mod_archive)
        self.layout_setup.addWidget(self.separator)

        self.layout_mod.addWidget(self.label_mod)
        for key, mod in self.mod_checkbox.items():
            self.layout_mod.addWidget(mod)
        self.layout_mod.addWidget(self.ff8reloaded_classic)
        self.layout_mod.addWidget(self.ff8reloaded_level1)
        self.layout_mod.addWidget(self.ff8reloaded_level100)
        self.layout_mod.addWidget(self.install_button)
        self.layout_mod.addWidget(self.progress)

        self.layout_main.addLayout(self.layout_setup)
        self.layout_main.addLayout(self.layout_mod)
        self.setLayout(self.layout_main)
        self.resize(self.minimumSizeHint())


    def install_click(self):

        self.progress.show()
        mod_to_be_installed = []
        special_status = {}
        for mod_name in self.mod_manager.mod_file_list:
            if mod_name == self.FF8_RELOAD_NAME:
                if self.ff8reloaded_classic.isChecked():
                    special_status[self.FF8_RELOAD_NAME] = self.ff8reloaded_classic.text()
                elif self.ff8reloaded_level1.isChecked():
                    special_status[self.FF8_RELOAD_NAME] = self.ff8reloaded_level1.text()
                elif self.ff8reloaded_level100.isChecked():
                    special_status[self.FF8_RELOAD_NAME] = self.ff8reloaded_level100.text()
            if self.mod_checkbox[mod_name].checkState() == Qt.CheckState.Checked:
                mod_to_be_installed.append(mod_name)
        self.progress.setRange(0, len(mod_to_be_installed))
        self.progress.setValue(0)
        download = self.download.isChecked()

        self.install_requested.emit(self.mod_manager, mod_to_be_installed, self.keep_mod_archive.isChecked(), special_status, download)

    def install_progress(self, nb_install_done):
        self.progress.setValue(nb_install_done)

    def install_completed(self, nb_install_done):
        self.progress.setValue(nb_install_done)
        self.progress.hide()
        self.install_over.show()
        self.resize(self.minimumSizeHint())
