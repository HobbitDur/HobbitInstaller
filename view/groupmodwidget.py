from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QRadioButton, QButtonGroup, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QCheckBox, \
    QSizePolicy, QGroupBox

from model.mod import Mod
from modmanager import ModType, GroupModType
from view.modwidget import ModWidget


class GroupModWidget(QWidget):
    def __init__(self, mod_manager, type:GroupModType):
        QWidget.__init__(self)

        self.mod_manager = mod_manager
        self.mod_widget_list = []

        self.layout_main = QVBoxLayout()

        if type == GroupModType.GRAPHIC:
            self.name = "Graphics"
        elif type == GroupModType.WRAPPER:
            self.name = "Wrapper"
        elif type == GroupModType.MUSIC:
            self.name = "Music"
        elif type == GroupModType.EASEOFLIFE:
            self.name = "Ease of life"
        elif type == GroupModType.GAMEPLAY:
            self.name = "Gameplay"
        else:
            self.name = "Unknown"

        self.group_widget = QGroupBox(self.name)
        self.group_widget.setLayout(self.layout_main)

    def add_mod(self, mod):
        self.mod_widget_list.append(ModWidget(self.mod_manager, mod))
        self.layout_main.addWidget(self.mod_widget_list[-1])

    def hide_mod(self, lang, ff8_version):
        hide_group = True
        for mod_widget in self.mod_widget_list:
            hide_mod = True
            if (ff8_version in (self.mod_manager.VERSION_LIST[0], self.mod_manager.VERSION_LIST[1]) and "ffnx" in mod_widget.mod.mod_info[
                "compatibility"]) \
                    or (ff8_version == self.mod_manager.VERSION_LIST[2] and "demaster" in mod_widget.mod.mod_info["compatibility"]):
                if lang in mod_widget.mod.mod_info["lang"]:
                    hide_mod = False
                    hide_group = False
            if hide_mod:
                mod_widget.hide()
        if hide_group:
            self.hide()
