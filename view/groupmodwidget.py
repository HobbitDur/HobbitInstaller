from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QRadioButton, QButtonGroup, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QCheckBox, \
    QSizePolicy, QGroupBox, QLayout

from model.mod import Mod, ModVersion
from modmanager import  GroupModType, ModWrapper
from view.modwidget import ModWidget


class GroupModWidget(QWidget):
    def __init__(self, mod_manager, type: GroupModType):
        QWidget.__init__(self)

        self.mod_manager = mod_manager
        self.mod_widget_list = []

        self.group_layout = QVBoxLayout()
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
        self.group_widget.setLayout(self.group_layout)
        self.layout_main.addWidget(self.group_widget)

        self.setLayout(self.layout_main)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def add_mod(self, mod):
        self.mod_widget_list.append(ModWidget(self.mod_manager, mod))
        self.group_layout.addWidget(self.mod_widget_list[-1])
        self.updateGeometry()

    def set_visibility_specific_mod(self, lang, ff8_version):
        hide_group = True
        for mod_widget in self.mod_widget_list:
            hide_mod = True
            if (ff8_version in (ModVersion.FF8_2000, ModVersion.FF8_2013) and ModWrapper.FFNX in
                mod_widget.mod.info["compatibility"]) or (
                    ff8_version == ModVersion.FF8_REMASTER and ModWrapper.DEMASTER in mod_widget.mod.info[
                "compatibility"]):
                if lang in mod_widget.mod.info["lang"]:
                    hide_mod = False
                    hide_group = False
            if hide_mod:
                mod_widget.hide()
                mod_widget.set_selected(False)
            else:
                mod_widget.show()
                if mod_widget.mod.info["default_selected"]:
                    mod_widget.set_selected(True)
        if hide_group:
            self.hide()
        else:
            self.show()

        self.updateGeometry()

    def show_all_mod(self):
        for mod_widget in self.mod_widget_list:
            mod_widget.show()
            mod_widget.mod.update_from_default_selected()
        self.show()
        self.updateGeometry()

    def hide_all_mod(self):
        for mod_widget in self.mod_widget_list:
            mod_widget.set_selected(False)
            mod_widget.hide()
            self.hide()
        self.updateGeometry()

    def get_mod_activated(self):
        mod_activated = []
        for mod_widget in self.mod_widget_list:
            if mod_widget.mod.activated:
                mod_activated.append(mod_widget.mod)
        return mod_activated
