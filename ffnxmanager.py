import os


class FFNxManager():
    FFNX_FILE_SETUP = "FFNx.toml"

    def __init__(self):
        self.ffnx_setup = []

    def __read_ffnx_setup_file(self, ff8_path):
        with open(os.path.join(ff8_path, self.FFNX_FILE_SETUP), "r") as file:
            self.ffnx_setup = file.read()
            self.ffnx_setup = self.ffnx_setup.split('\n')

    def __write_ffnx_setup_file(self, ff8_path):
        with open(os.path.join(ff8_path, self.FFNX_FILE_SETUP), "w") as file:
            for line in self.ffnx_setup:
                file.write(line + '\n')

    def change_ffnx_option(self, ffnx_param, ff8_path):
        self.__read_ffnx_setup_file(ff8_path)
        for i, line in enumerate(self.ffnx_setup):
            for param, value in ffnx_param.items():
                if param in line and '=' in line:
                    line_split = line.split('=')
                    self.ffnx_setup[i] = line_split[0] + "=" + value + "#Value changed by HobbitInstaller"
        self.__write_ffnx_setup_file(ff8_path)
