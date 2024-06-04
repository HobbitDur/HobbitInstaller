import os


class FFNxManager():
    FFNX_FILE_SETUP = "FFNx.toml"
    MUSIC_FFNX_PARAM_CHANGE = {'use_external_music': 'true', 'external_music_path': '"psf"', 'external_music_ext': '"minipsf"', 'he_bios_path': '"psf/hebios.bin"'}
    MUSIC_ROSE_WINE_PARAM_CHANGE = {'use_external_music': 'true', 'external_music_path': '"music"', 'external_music_ext': '"ogg"', 'he_bios_path': '"psf/hebios.bin"'}

    def __init__(self):
        self.ffnx_setup = []

    def read_ffnx_setup_file(self, ff8_path):
        with open(os.path.join(ff8_path, self.FFNX_FILE_SETUP), "r") as file:
            self.ffnx_setup = file.read()
            self.ffnx_setup = self.ffnx_setup.split('\n')

    def write_ffnx_setup_file(self, ff8_path):
        with open(os.path.join(ff8_path, self.FFNX_FILE_SETUP), "w") as file:
            for line in self.ffnx_setup:
                file.write(line + '\n')

    def change_ffnx_music_option(self):
        for i, line in enumerate(self.ffnx_setup):
            for param, value in self.MUSIC_FFNX_PARAM_CHANGE.items():
                if param in line and '=' in line:
                    line_split = line.split('=')
                    self.ffnx_setup[i] = line_split[0] + "=" + value + "#Value changed by HobbitInstaller"

    def change_rosewine_music_option(self):
        for i, line in enumerate(self.ffnx_setup):
            for param, value in self.MUSIC_ROSE_WINE_PARAM_CHANGE.items():
                if param in line and '=' in line:
                    line_split = line.split('=')
                    self.ffnx_setup[i] = line_split[0] + "=" + value + "#Value changed by HobbitInstaller"
