from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QRadioButton, QButtonGroup, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QCheckBox, \
    QSizePolicy

from model.mod import Mod
from modmanager import ModType
from view.modwidget import ModWidget


class ListModWidget(QWidget):
    FF8_RELOAD_NAME = "FFVIII-Reloaded-FR-ONLY"
    RAGNAROK_NAME = "Ragnarok-EN-ONLY"
    LIST_SPECIAL_MOD = [FF8_RELOAD_NAME, RAGNAROK_NAME]
    VERSION_LIST = ["FF8 PC 2000", "FF8 Steam 2013", "FF8 Remastered"] # To remove from here
    def __init__(self, mod_manager, lang, ff8_version, mod_type ):
        QWidget.__init__(self)
        self.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum)

        self.layout_main = QVBoxLayout()
        self.layout_mod = QVBoxLayout()

        self.layout_ragnarok = QVBoxLayout()
        self.layout_ff8reloaded = QVBoxLayout()
        self.mod_manager = mod_manager

        self.label_mod = QLabel("Mod selection")
        self.label_mod.setFont(QFont('Arial', 12))
        self.label_mod.setStyleSheet("font-weight: bold")
        self.label_mod.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mod_list = []
        self.mod_widget_list = []

        for mod_name, mod_info in self.mod_manager.mod_dict_json.items():
            if mod_name == "UpdateData":
                continue
            if mod_name not in self.LIST_SPECIAL_MOD:
                self.mod_list.append(Mod(mod_name, ModType.DIRECT_IMPORT, mod_info))
                self.mod_widget_list.append(ModWidget(mod_manager,self.mod_list[-1] ))
            else:
                if mod_name == self.FF8_RELOAD_NAME:
                    self.mod_list.append(Mod(mod_name, ModType.RELOADED, mod_info))
                    self.mod_widget_list.append(ModWidget(mod_manager, self.mod_list[-1]))
                elif mod_name == self.RAGNAROK_NAME:
                    self.mod_list.append(Mod(mod_name, ModType.RAGNAROK, mod_info))
                    self.mod_widget_list.append(ModWidget(mod_manager, self.mod_list[-1]))

        for mod_widget in self.mod_widget_list:
            self.layout_mod.addWidget(mod_widget)

        self.layout_main.addWidget(self.label_mod)
        self.layout_main.addLayout(self.layout_mod)
        self.layout_main.addStretch(1)
        self.setLayout(self.layout_main)

        self.show_specific_mod(lang, ff8_version, mod_type)

    def show_specific_mod(self, lang, ff8_version, mod_type):
        for mod_widget in self.mod_widget_list:
            mod_found = False
            if mod_widget.mod.name != "UpdateData":  # It's our "local mod" to update the setup.json
                if mod_widget.mod.mod_info["download_type"] == 'github' or mod_widget.mod.mod_info["download_type"] == 'direct':
                    if lang in mod_widget.mod.mod_info["lang"]:
                        if (ff8_version in (self.VERSION_LIST[0], self.VERSION_LIST[1]) and "ffnx" in mod_widget.mod.mod_info["compatibility"]) \
                                or ( ff8_version == self.VERSION_LIST[2] and "demaster" in mod_widget.mod.mod_info["compatibility"]):
                            if mod_type in ("All" ,mod_widget.mod.mod_info["mod_type"]):
                                if mod_widget.mod.mod_info["default_selected"] == "true":
                                    mod_widget.selected(True)
                                mod_found = True
                                mod_widget.show()
            if not mod_found:
                mod_widget.selected(False)
                mod_widget.hide()

    def get_mod_to_install(self):
        mod_to_be_installed = []
        special_status = {}
        for mod_widget in self.mod_widget_list:
            if mod_widget.mod.activated:
                mod_to_be_installed.append(mod_widget.mod.name)
            special_status = mod_widget.get_special_status()
        return mod_to_be_installed, special_status

