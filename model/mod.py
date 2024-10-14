from modmanager import ModType


class Mod:
    FF8_RELOAD_NAME = "FFVIII-Reloaded-FR-ONLY"
    RAGNAROK_NAME = "Ragnarok-EN-ONLY"
    LIST_SPECIAL_MOD = [FF8_RELOAD_NAME, RAGNAROK_NAME]
    def __init__(self, name, mod_info, activated=True):
        self.name = name
        if name in self.LIST_SPECIAL_MOD:
            if name == self.FF8_RELOAD_NAME:
                self._type = ModType.RELOADED
            elif name == self.RAGNAROK_NAME:
                self._type = ModType.RAGNAROK
        else:
            self._type = ModType.DIRECT_IMPORT
        self.mod_info = mod_info
        self.activated = activated

    def __str__(self):
        return f"Mod(Name:{self.name}, Info:{self.mod_info}"
    def __repr__(self):
        return self.__str__()

    def get_type(self):
        return self._type

