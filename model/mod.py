from modmanager import ModType


class Mod:
    def __init__(self, name, type:ModType, mod_info, activated=True):
        self.name = name
        self._type = type
        self.mod_info = mod_info
        self.activated = activated

    def get_type(self):
        return self._type

