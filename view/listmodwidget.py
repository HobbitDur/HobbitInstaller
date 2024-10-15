from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QRadioButton, QButtonGroup, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QCheckBox, \
    QSizePolicy, QGroupBox, QScrollArea, QScrollBar, QLayout

from model.mod import Mod
from modmanager import  GroupModType
from view.groupmodwidget import GroupModWidget
from view.modwidget import ModWidget


class ListModWidget(QWidget):

      # To remove from here

    def __init__(self, mod_manager):
        QWidget.__init__(self)

        #self.window_layout = QVBoxLayout()
        #self.setLayout(self.window_layout)
        #self.scroll_widget = QWidget()
        #self.scroll_area = QScrollArea()
        #self.scroll_area.setWidgetResizable(True)
        #self.scroll_area.setWidget(self.scroll_widget)
        #self.scroll_widget.setLayout(self.layout_main)
        self.layout_main = QVBoxLayout()
        self.setLayout(self.layout_main)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.layout_mod = QVBoxLayout()
        self.mod_manager = mod_manager

        self.label_mod = QLabel("Mod selection")
        self.label_mod.setFont(QFont('Arial', 12))
        self.label_mod.setStyleSheet("font-weight: bold")
        self.label_mod.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.group_widget_wrapper = GroupModWidget(mod_manager, GroupModType.WRAPPER)
        self.group_widget_graphical = GroupModWidget(mod_manager, GroupModType.GRAPHIC)
        self.group_widget_music = GroupModWidget(mod_manager, GroupModType.MUSIC)
        self.group_widget_gameplay = GroupModWidget(mod_manager, GroupModType.GAMEPLAY)
        self.group_widget_easeoflife = GroupModWidget(mod_manager, GroupModType.EASEOFLIFE)

        self.first_line_group = QHBoxLayout()
        self.first_line_group.addWidget(self.group_widget_wrapper)
        self.first_line_group.addWidget(self.group_widget_graphical)

        self.second_line_group = QHBoxLayout()
        self.second_line_group.addWidget(self.group_widget_music)
        self.second_line_group.addWidget(self.group_widget_gameplay)
        self.second_line_group.addWidget(self.group_widget_easeoflife)

        self._group_list = (self.group_widget_wrapper, self.group_widget_graphical,self.group_widget_music,self.group_widget_gameplay, self.group_widget_easeoflife)

        for mod_name, mod_info in self.mod_manager.mod_dict_json.items():
            if mod_name == "UpdateData":
                continue
            new_mod = Mod(mod_name, mod_info)
            if mod_info["mod_type"] == GroupModType.WRAPPER:
                self.group_widget_wrapper.add_mod(new_mod)
            elif mod_info["mod_type"] == GroupModType.GRAPHIC:
                self.group_widget_graphical.add_mod(new_mod)
            elif mod_info["mod_type"] == GroupModType.EASEOFLIFE:
                self.group_widget_easeoflife.add_mod(new_mod)
            elif mod_info["mod_type"] == GroupModType.MUSIC:
                self.group_widget_music.add_mod(new_mod)
            elif mod_info["mod_type"] == GroupModType.GAMEPLAY:
                self.group_widget_gameplay.add_mod(new_mod)

        self.layout_mod.addLayout(self.first_line_group)
        self.layout_mod.addLayout(self.second_line_group)

        self.layout_main.addWidget(self.label_mod)
        #self.window_layout.addWidget(self.scroll_area)
        self.layout_main.addLayout(self.layout_mod)
        self.layout_main.addStretch(1)
        self.layout_main.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.updateGeometry()


    def show_specific_mod(self, lang, ff8_version, mod_type):
        self.group_widget_wrapper.hide_all_mod()
        self.group_widget_graphical.hide_all_mod()
        self.group_widget_music.hide_all_mod()
        self.group_widget_gameplay.hide_all_mod()
        self.group_widget_easeoflife.hide_all_mod()
        if mod_type == GroupModType.WRAPPER:
            self.group_widget_wrapper.set_visibility_specific_mod(lang, ff8_version)
        elif mod_type == GroupModType.GRAPHIC:
            self.group_widget_graphical.set_visibility_specific_mod(lang, ff8_version)
        elif mod_type == GroupModType.EASEOFLIFE:
            self.group_widget_easeoflife.set_visibility_specific_mod(lang, ff8_version)
        elif mod_type == GroupModType.MUSIC:
            self.group_widget_music.set_visibility_specific_mod(lang, ff8_version)
        elif mod_type == GroupModType.GAMEPLAY:
            self.group_widget_gameplay.set_visibility_specific_mod(lang, ff8_version)
        else: # expect ALL
            self.group_widget_wrapper.set_visibility_specific_mod(lang, ff8_version)
            self.group_widget_graphical.set_visibility_specific_mod(lang, ff8_version)
            self.group_widget_easeoflife.set_visibility_specific_mod(lang, ff8_version)
            self.group_widget_music.set_visibility_specific_mod(lang, ff8_version)
            self.group_widget_gameplay.set_visibility_specific_mod(lang, ff8_version)

        self.updateGeometry()

    def get_mod_to_install(self):
        mod_to_install = []
        for mod_widget in self._group_list:
           mod_to_install.extend(mod_widget.get_mod_activated())
        return mod_to_install

    def sizeHint(self):
        height = self.first_line_group.sizeHint().height() + self.second_line_group.sizeHint().height()
        width =self.second_line_group.sizeHint().width() # One day I will find how to get this 50
        return QSize(width, height)
