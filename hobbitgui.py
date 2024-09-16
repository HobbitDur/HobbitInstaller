import sys

from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QCheckBox
class WindowInstaller(QWidget):
    MOD_CHECK_DEFAULT = ['FFNx', 'FFNxFF8Music']
    def __init__(self, mod_manager, keep_downloaded_mod=False):
        QWidget.__init__(self)
        self.setWindowTitle("HobbitInstaller")
        # Button
        self.install_button = QPushButton("Install")
        self.install_button.clicked.connect(self.install_click)
        self.mod_checkbox = {}
        self.mod_manager = mod_manager
        self.keep_downloaded_mod = keep_downloaded_mod
        # Checkbox
        for mod_name in self.mod_manager.mod_file_list:
            if self.mod_manager.mod_dict[mod_name]['type'] == 'github':
                self.mod_checkbox[mod_name] = QCheckBox(mod_name)
            elif self.mod_manager.mod_dict[mod_name]['type'] == 'direct_link':
                self.mod_checkbox[mod_name] = QCheckBox(mod_name)
            else:
                print("No type found for mod {} with value {}".format(mod_name, self.mod_manager.mod_dict[mod_name]))
            if mod_name in self.MOD_CHECK_DEFAULT:
                self.mod_checkbox[mod_name].setChecked(True)
        self.layout = QVBoxLayout()
        self.setup_layout()
        self.show_all()

    def show_all(self):
        for key, mod in self.mod_checkbox.items():
            mod.show()
        self.install_button.show()
        self.show()

    def setup_layout(self):
        for key, mod in self.mod_checkbox.items():
            self.layout.addWidget(mod)
        self.layout.addWidget(self.install_button)
        self.setLayout(self.layout)

    def install_click(self):
        mod_to_be_installed = []
        for mod_name in self.mod_manager.mod_file_list:
            print(mod_name)
            if self.mod_checkbox[mod_name].checkState() == Qt.Checked:
                mod_to_be_installed.append(mod_name)
        self.mod_manager.install_mods(mod_to_be_installed,self.keep_downloaded_mod)
        QCoreApplication.quit()


