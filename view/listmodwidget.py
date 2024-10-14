from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QRadioButton, QButtonGroup, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QCheckBox, \
    QSizePolicy, QGroupBox, QScrollArea, QScrollBar

from model.mod import Mod
from modmanager import ModType, GroupModType
from view.groupmodwidget import GroupModWidget
from view.modwidget import ModWidget


class ListModWidget(QWidget):

      # To remove from here

    def __init__(self, mod_manager, lang, ff8_version, mod_type):
        QWidget.__init__(self)

        self.window_layout = QVBoxLayout()
        self.setLayout(self.window_layout)
        self.scroll_widget = QWidget()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout_main = QVBoxLayout()
        self.scroll_widget.setLayout(self.layout_main)


        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        #self.layout_main.setContentsMargins(-1,-1,-1,0)
        self.layout_mod = QVBoxLayout()

        # self.layout_ragnarok = QVBoxLayout()
        # self.layout_ff8reloaded = QVBoxLayout()
        self.mod_manager = mod_manager

        self.label_mod = QLabel("Mod selection")
        self.label_mod.setFont(QFont('Arial', 12))
        self.label_mod.setStyleSheet("font-weight: bold")
        self.label_mod.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mod_widget_list = []

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

        self.window_layout.addWidget(self.label_mod)
        self.window_layout.addWidget(self.scroll_area)

        self.layout_main.addLayout(self.layout_mod)
        self.layout_main.addStretch(1)

        #self.show_specific_mod(lang, ff8_version, mod_type)

    def show_specific_mod(self, lang, ff8_version, mod_type):
        if mod_type == GroupModType.WRAPPER:
            self.group_widget_wrapper.hide_mod(lang, ff8_version)
        elif mod_type == GroupModType.GRAPHIC:
            self.group_widget_graphical.hide_mod(lang, ff8_version)
        elif mod_type == GroupModType.EASEOFLIFE:
            self.group_widget_easeoflife.hide_mod(lang, ff8_version)
        elif mod_type == GroupModType.MUSIC:
            self.group_widget_music.hide_mod(lang, ff8_version)
        elif mod_type == GroupModType.GAMEPLAY:
            self.group_widget_gameplay.hide_mod(lang, ff8_version)

        # for mod_widget in self.mod_widget_list:
        #     mod_found = False
        #     if mod_widget.mod.name != "UpdateData":  # It's our "local mod" to update the setup.json
        #         if mod_widget.mod.mod_info["download_type"] == 'github' or mod_widget.mod.mod_info["download_type"] == 'direct':
        #             if lang in mod_widget.mod.mod_info["lang"]:
        #                 if (ff8_version in (self.VERSION_LIST[0], self.VERSION_LIST[1]) and "ffnx" in mod_widget.mod.mod_info["compatibility"]) \
        #                         or (ff8_version == self.VERSION_LIST[2] and "demaster" in mod_widget.mod.mod_info["compatibility"]):
        #                     if mod_type in ("All", mod_widget.mod.mod_info["mod_type"]):
        #                         if mod_widget.mod.mod_info["default_selected"] == "true":
        #                             mod_widget.selected(True)
        #                         mod_found = True
        #                         mod_widget.show()
        #     if not mod_found:
        #         mod_widget.selected(False)
        #         mod_widget.hide()
        #
        #
        #
        # self.group_wrapper.hide()
        # self.group_graphical.hide()
        # self.group_music.hide()
        # self.group_gameplay.hide()
        # self.group_easeoflife.hide()
        # if mod_type == "Wrapper" or mod_type == "All":
        #     self.group_wrapper.show()
        # if mod_type == "Graphical" or mod_type == "All":
        #     self.group_graphical.show()
        # if mod_type == "Music" or mod_type == "All":
        #     self.group_music.show()
        # if mod_type == "Gameplay" or mod_type == "All":
        #     self.group_gameplay.show()
        # if mod_type == "EaseOfLife" or mod_type == "All":
        #     self.group_easeoflife.show()

        #self.updateGeometry()

    def get_mod_to_install(self):
        mod_to_be_installed = []
        special_status = {}
        for mod_widget in self.mod_widget_list:
            if mod_widget.mod.activated:
                mod_to_be_installed.append(mod_widget.mod.name)
            special_status = mod_widget.get_special_status()
        return mod_to_be_installed, special_status

    def minimumSizeHint(self):
        width = self.second_line_group.sizeHint().width()
        height = self.first_line_group.sizeHint().height() + self.second_line_group.sizeHint().height()
        return QSize(width,height)


    #def sizeHint(self):
    #    return self.second_line_group.sizeHint()
