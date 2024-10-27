from enum import Enum


class ModType(Enum):
    RAGNAROK = 1
    RELOADED = 2
    DIRECT_IMPORT = 3
    SETUP = 4

class GroupModType(Enum):
    WRAPPER = 1
    GRAPHIC = 2
    GAMEPLAY = 3
    MUSIC = 4
    EASEOFLIFE = 5
    ALL = 6
    SETUP = 7
class ModLang(Enum):
    EN = 0
    FR = 1
    DE = 2
    ES = 3
    IT = 4

class ModVersion(Enum):
    FF8_2000 = 1
    FF8_2013 = 2
    FF8_REMASTER = 3

class ModWrapper(Enum):
    FFNX = 1
    DEMASTER = 2



class Mod:
    FF8_RELOAD_NAME = "FFVIII-Reloaded-FR-ONLY"
    RAGNAROK_NAME = "Ragnarok-EN-ONLY"
    UPDATE_DATA = "UpdateData"
    LIST_SPECIAL_MOD = [FF8_RELOAD_NAME, RAGNAROK_NAME, UPDATE_DATA]
    def __init__(self, name, mod_info):
        self.name = name
        if name in self.LIST_SPECIAL_MOD:
            if name == self.FF8_RELOAD_NAME:
                self._type = ModType.RELOADED
            elif name == self.RAGNAROK_NAME:
                self._type = ModType.RAGNAROK
            elif name == self.UPDATE_DATA:
                self._type = ModType.SETUP
        else:
            self._type = ModType.DIRECT_IMPORT

        self.info = mod_info
        self.activated = self.info["default_selected"]
        self.special_status = ""

    def __str__(self):
        return f"Mod(Name:{self.name}, Info:{self.info}"
    def __repr__(self):
        return self.__str__()

    def get_type(self):
        return self._type

    def update_from_default_selected(self):
        self.activated = self.info["default_selected"]


