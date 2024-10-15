from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QRadioButton, QButtonGroup, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QCheckBox, \
    QSizePolicy, QLayout

from model.mod import Mod, ModType


class ModWidget(QWidget):
    FF8_RELOAD_NAME = "FFVIII-Reloaded-FR-ONLY"
    RAGNAROK_NAME = "Ragnarok-EN-ONLY"
    LIST_SPECIAL_MOD = [FF8_RELOAD_NAME, RAGNAROK_NAME]
    VERSION_LIST = ["FF8 PC 2000", "FF8 Steam 2013", "FF8 Remastered"] # To remove from here
    def __init__(self, mod_manager, mod:Mod):
        QWidget.__init__(self)


        self.mod_manager = mod_manager
        self.mod = mod

        self.select = QCheckBox(parent=self, text=mod.name)
        self.select.stateChanged.connect(self._state_changed)
        self.select.setToolTip(f"Author: {mod.info["modder_name"]}\nDescription: {mod.info["mod_info"]}")
        self.select.setChecked(mod.info["default_selected"])
        #self.setSizePolicy(self.select.sizePolicy())

        self.layout_main = QVBoxLayout()
        self.setLayout(self.layout_main)
        #self.layout_main.setSpacing(10)
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        #self.layout_mod= QVBoxLayout()

        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)
        #size_policy = self.sizePolicy()
        #size_policy.setControlType(QSizePolicy.ControlType.CheckBox)
        #size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        #size_policy.setHorizontalPolicy(QSizePolicy.Policy.Minimum)

        #self.layout_mod.addWidget(self.select)
        self.layout_main.addWidget(self.select)

        # FFVIII Reloaded
        if mod.get_type() == ModType.RELOADED:
            self.layout_ff8reloaded = QVBoxLayout()
            self.ff8reloaded_classic = QRadioButton(parent=self, text="FF8 Reloaded Classic")
            self.ff8reloaded_classic.setChecked(True)
            self.ff8reloaded_classic.toggled.connect(lambda: self._ff8reloadedstate(self.ff8reloaded_classic))
            self.ff8reloaded_classic.hide()
            self.ff8reloaded_level1 = QRadioButton(parent=self, text="FF8 Reloaded Level 1")
            self.ff8reloaded_level1.toggled.connect(lambda: self._ff8reloadedstate(self.ff8reloaded_level1))
            self.ff8reloaded_level1.hide()
            self.ff8reloaded_level100 = QRadioButton(parent=self, text="FF8 Reloaded Level 100")
            self.ff8reloaded_level100.toggled.connect(lambda: self._ff8reloadedstate(self.ff8reloaded_level100))
            self.ff8reloaded_level100.hide()
            self.parent_ff8reloaded = QButtonGroup(self)
            self.parent_ff8reloaded.addButton(self.ff8reloaded_classic)
            self.parent_ff8reloaded.addButton(self.ff8reloaded_level1)
            self.parent_ff8reloaded.addButton(self.ff8reloaded_level100)
            self.select.stateChanged.connect(self._activate_ff8reload)

            self.layout_main.addWidget(self.ff8reloaded_classic)
            self.layout_main.addWidget(self.ff8reloaded_level1)
            self.layout_main.addWidget(self.ff8reloaded_level100)

        # Ragnarok
        elif mod.get_type()  == ModType.RAGNAROK:
            self.layout_ragnarok = QVBoxLayout()
            self.ragnarok_standard = QRadioButton(parent=self, text="Ragnarok standard")
            self.ragnarok_standard.setChecked(True)
            self.ragnarok_standard.toggled.connect(lambda: self._ragnarokstate(self.ragnarok_standard))
            self.ragnarok_standard.hide()
            self.ragnarok_lionheart = QRadioButton(parent=self, text="Ragnarok lionheart")
            self.ragnarok_lionheart.toggled.connect(lambda: self._ragnarokstate(self.ragnarok_lionheart))
            self.ragnarok_lionheart.hide()
            self.parent_ragnarok = QButtonGroup(self)
            self.parent_ragnarok.addButton(self.ragnarok_standard)
            self.parent_ragnarok.addButton(self.ragnarok_lionheart)

            self.layout_main.addWidget(self.ragnarok_standard)
            self.layout_main.addWidget(self.ragnarok_lionheart)
            self.select.stateChanged.connect(self._activate_ragnarok)

        #self.layout_main.addLayout(self.layout_mod)
        #self.layout_main.addStretch(1)
        # self.setSizePolicy(self.select.sizePolicy())
        self.setSizePolicy(self.select.sizePolicy())
        size_policy = self.select.sizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        #self.setSizePolicy(size_policy)
        #self.select.updateGeometry()
        #self.setFixedHeight(self.select.size().height())
        self.layout_main.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self._update_special_status()
        self.updateGeometry()

    def _state_changed(self):
        self.mod.activated = self.select.isChecked()

    def _ff8reloadedstate(self, b):
        self._update_special_status()

    def _ragnarokstate(self, b):
        self._update_special_status()

    def _activate_ff8reload(self):
        if self.mod.activated:
            self.ff8reloaded_classic.show()
            self.ff8reloaded_level1.show()
            self.ff8reloaded_level100.show()
        else:
            self.ff8reloaded_classic.hide()
            self.ff8reloaded_level1.hide()
            self.ff8reloaded_level100.hide()

    def _activate_ragnarok(self):
        if self.mod.activated:
            self.ragnarok_standard.show()
            self.ragnarok_lionheart.show()
        else:
            self.ragnarok_standard.hide()
            self.ragnarok_lionheart.hide()

    def set_selected(self, selected):
        self.select.setChecked(selected)
        self.mod.activated = selected

    def _update_special_status(self):
        if self.select.isChecked():
            if self.mod.get_type() == ModType.RELOADED:
                if self.ff8reloaded_classic.isChecked():
                    self.mod.special_status = self.ff8reloaded_classic.text()
                elif self.ff8reloaded_level1.isChecked():
                    self.mod.special_status = self.ff8reloaded_level1.text()
                elif self.ff8reloaded_level100.isChecked():
                    self.mod.special_status = self.ff8reloaded_level100.text()
            elif self.mod.get_type() == ModType.RAGNAROK:
                if self.ragnarok_standard.isChecked():
                    self.mod.special_status = self.ragnarok_standard.text()
                elif self.ragnarok_lionheart.isChecked():
                    self.mod.special_status = self.ragnarok_lionheart.text()
