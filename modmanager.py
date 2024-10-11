import json
import os
import re
import shutil
import subprocess
import time
from enum import Enum
from zipfile import ZipFile
import psutil
from ffnxmanager import FFNxManager
import patoolib
import requests
class ModType(Enum):
    RAGNAROK = 1
    RELOADED = 2
    DIRECT_IMPORT = 3

class ModManager:
    FOLDER_SETUP = os.path.join("HobbitInstaller-data", "ModSetup")
    SEP_CHAR = '>'
    FOLDER_DOWNLOAD = "ModDownloaded"
    TYPE_DOWNLOAD = 'Steam'
    GITHUB_RELEASE_TAG_PATH = "/releases/tag/"
    GITHUB_RELEASE_PATH = "/releases"
    UPDATE_DATA_NAME = "UpdateData"
    SETUP_FILE = os.path.join(FOLDER_SETUP, "setup.json")

    def __init__(self, ff8_path='.'):
        self.ffnx_manager = FFNxManager()
        os.makedirs(self.FOLDER_DOWNLOAD, exist_ok=True)
        self.ff8_path = ff8_path
        self.mod_dict_json = {}
        self.__init_mod_data()

    def __init_mod_data(self):
        with open(self.SETUP_FILE) as f:
            self.mod_dict_json = json.load(f)['AvailableMods']
            # self.mod_dict_json = self.mod_dict_json['AvailableMods']

    def download_file(self, link, headers={}, write_file=False, file_name=None, dest_path=FOLDER_DOWNLOAD):
        print("Downloading with link: {}".format(link))
        request_return = requests.get(link, headers=headers)
        if not file_name:
            if "Content-Disposition" in request_return.headers.keys():
                file_name = re.findall("filename\*?=['\"]?(?:UTF-\d['\"]*)?([^;\r\n\"']*)['\"]?;?",
                                       request_return.headers["Content-Disposition"])[0]
            elif "download" in request_return.headers.keys():
                file_name = request_return.headers["download"]
            elif len(request_return.history) > 0 and request_return.history[0].headers[
                'Location']:  # Means there is a redirection, so taking the name from the first location
                file_name = request_return.history[0].headers['Location'].split('/')[-1]
                file_name = file_name.replace('+', ' ')
            else:
                file_name = link.split("/")[-1]
        if request_return.status_code == 200:
            print("Successfully downloaded {}".format(link))
            if write_file:
                with open(os.path.join(dest_path, file_name), "wb") as file:
                    file.write(request_return.content)
        else:
            print("Fail to download {}".format(link))
        return request_return, file_name

    def save_local_file(self, lang="en"):
        path_to_files = os.path.join(self.ff8_path, 'Data', 'lang-' + lang)

    def __get_github_link(self, mod_name: str):
        github_link = self.mod_dict_json[mod_name]['link'] + self.GITHUB_RELEASE_PATH
        github_link = github_link.replace('github.com', 'api.github.com/repos')
        return github_link

    def __get_github_url_file(self, mod_name: str, json_url="assets_url"):
        json_link = self.__get_github_link(mod_name)
        json_file = self.download_file(json_link, headers={'content-type': 'application/json'})[0]
        json_file = json_file.json()
        dd_url = ""
        if self.mod_dict_json[mod_name]['git_tag'] == 'latest':
            dd_url = json_file[0][json_url]
        else:  # Searching the tag
            for el in json_file:
                if el['tag_name'] == self.mod_dict_json[mod_name]['git_tag']:
                    dd_url = el[json_url]
        return dd_url

    def install_mod(self, mod_name: str, keep_download_mod=False, special_status={}, download=True, ff8_version="ffnx", backup=True):

        try:
            print("Backing up the data")
            with ZipFile(os.path.join(self.ff8_path, "backup_data.zip"), 'x') as zip_ref:
                zip_ref.write(os.path.join(self.ff8_path, "Data"))
        except FileExistsError:
            print(f"File backup_data.zip already exist")


        os.makedirs(self.FOLDER_DOWNLOAD, exist_ok=True)
        print("Start installing mod: {}".format(mod_name))


        if mod_name == self.UPDATE_DATA_NAME:
            dd_url = self.__get_github_url_file(self.UPDATE_DATA_NAME, "zipball_url")
            dd_file_name = self.download_file(dd_url, write_file=True)[1]
        elif self.mod_dict_json[mod_name]["download_type"] == "github":
            if download:
                dd_url = self.__get_github_url_file(mod_name, "assets_url")
                json_file = self.download_file(dd_url, headers={'content-type': 'application/json'})[0].json()
                asset_link = ""
                if mod_name == 'FFNx':
                    for el in json_file:
                        if self.TYPE_DOWNLOAD in el['browser_download_url']:
                            asset_link = el['browser_download_url']
                            break
                elif len(json_file) == 1:
                    asset_link = json_file[0]['browser_download_url']
                else:
                    print("Didn't manage several asset without a particular case")
                dd_file_name = self.download_file(asset_link, write_file=True)[1]
            else:
                dd_file_name = self.mod_dict_json["download_name"]
        elif self.mod_dict_json[mod_name]["download_type"] == "direct":
            if ff8_version == "ffnx":
                direct_file = self.mod_dict_json[mod_name]['link']
            elif ff8_version == "demaster":
                direct_file = self.mod_dict_json[mod_name]['remaster-link']
            else:
                print("Error unexpected ff8_version: {}".format(ff8_version))
                direct_file = self.mod_dict_json[mod_name]['link']
            if mod_name == "FFNxFF8Music":  # need remove " around
                dd_file_name = self.mod_dict_json[mod_name]["download_name"]
            else:
                dd_file_name = None
            if download:
                dd_file_name = self.download_file(direct_file, write_file=True, file_name=dd_file_name)[1]
            else:
                dd_file_name = self.mod_dict_json[mod_name]["download_name"]
        else:
            raise ValueError("Unexpected ELSE")

        # Trying to make auto naming instead of having to modify manually a file

        # if keep_download_mod and download:# If we keep the files downloaded, then keep a link between the downloaded name and the mod name
        #    with open(os.path.join(self.FOLDER_DOWNLOAD, self.MOD_NAME_LIST), "a+") as file:
        #        file.write(self.mod_list_file_name[self.mod_file_list.index(mod_name)] + self.SEP_CHAR + dd_file_name)

        # elif not download: # Means we get it from local folder, so we use the files link
        #    with open(os.path.join(self.FOLDER_DOWNLOAD, self.MOD_NAME_LIST), "r") as file:
        #        file_data = file.read()
        #        file_data = file_data.split("\n")
        #        dd_file_name = [x for x in file_data if self.mod_list_file_name[self.mod_file_list.index(mod_name)] in x][0].split(self.SEP_CHAR)[1]
        #        print(dd_file_name)

        archive = ""
        print("Before extraction, file to extract: {}, with command: {}".format(
            os.path.join(self.FOLDER_DOWNLOAD, dd_file_name),
            os.path.join("HobbitInstaller-data", 'Resources', '7z.exe')))
        if '.rar' in dd_file_name or '.7z' in dd_file_name:
            archive = "temparchive"
            patoolib.extract_archive(os.path.join(self.FOLDER_DOWNLOAD, dd_file_name), verbosity=-1, outdir=archive,
                                     program=os.path.join("HobbitInstaller-data", 'Resources', '7z.exe'))
        # Unzip locally then copy all files, so we don't have problem erasing files while unziping
        elif '.zip' in dd_file_name:
            archive = "tempzip"
            os.makedirs(archive, exist_ok=True)
            with ZipFile(os.path.join(self.FOLDER_DOWNLOAD, dd_file_name), 'r') as zip_ref:
                zip_ref.extractall(archive)
        list_dir = os.listdir(archive)
        try:
            index_folder = os.listdir(archive).index(dd_file_name.rsplit('.', 1)[0])

        except ValueError:
            index_folder = -1
        if mod_name == "FFVIII-Reloaded-FR-ONLY":  # Special handle
            if special_status[mod_name] == "FF8 Reloaded Classic":
                archive_to_copy = os.path.join(archive, "FFVIII Reloaded classic")
            elif special_status[mod_name] == "FF8 Reloaded Level 1":
                archive_to_copy = os.path.join(archive, "FFVIII Reloaded level 1")
            elif special_status[mod_name] == "FF8 Reloaded Level 100":
                archive_to_copy = os.path.join(archive, "FFVIII Reloaded level 100")
            else:
                archive_to_copy = archive  # Shouldn't happen
            futur_path = os.path.join(self.ff8_path, 'Data', 'lang-fr')
        elif mod_name == "Ragnarok-EN-ONLY":  # Special handle
            if special_status[mod_name] == "Ragnarok standard":
                archive_to_copy = os.path.join(archive, list_dir[index_folder], list_dir[index_folder],
                                               "Standard Mode files")
            elif special_status[mod_name] == "Ragnarok lionheart":
                archive_to_copy = os.path.join(archive, list_dir[index_folder], list_dir[index_folder],
                                               "Lionheart Mode files")
            else:
                archive_to_copy = archive  # Shouldn't happen
            futur_path = os.path.join(self.ff8_path, 'Data')
        elif mod_name == "FF8Curiosite-FR-ONLY":
            archive_to_copy = archive  # Shouldn't happen
            futur_path = os.path.join(self.ff8_path, 'Data', 'lang-fr')
            os.makedirs(os.path.join(self.ff8_path, 'Data', 'Music', 'dmusic'), exist_ok=True)
            shutil.copy(os.path.join(archive, "064s-choco.sgt"), os.path.join(self.ff8_path, 'Data', 'Music', 'dmusic'))
            os.remove(os.path.join(archive, "064s-choco.sgt"))
        elif mod_name == "Demaster":  # Big special handle
            installer_directory = os.getcwd()
            print("Installing demaster - long process !")
            if not os.path.isfile(os.path.join(self.ff8_path, "FFVIII_LAUNCHER.exe-original")):
                print(
                    "First running the original launcher to create a config file, and waiting 10 sec that it launches")
                os.chdir(os.path.join(self.ff8_path))
                subprocess.run("FFVIII_LAUNCHER.exe")
                time.sleep(10)
                print("Now killing the launcher")
                PROCNAME = "FFVIII_LAUNCHER.exe"
                for proc in psutil.process_iter():
                    # check whether the process name matches
                    if proc.name() == PROCNAME:
                        proc.kill()
                os.chdir(installer_directory)
                print("Copying demaster file to ff8")

                shutil.copy(os.path.join(self.ff8_path, "FFVIII_LAUNCHER.exe"),
                            os.path.join(self.ff8_path, "FFVIII_LAUNCHER.exe-original"))

            archive_to_copy = os.path.join(archive, "EN_FR_IT_DE_ES_LATIN")
            futur_path = os.path.join(self.ff8_path)
            shutil.copytree(archive_to_copy, futur_path, dirs_exist_ok=True,
                            copy_function=shutil.copy)
            print("Now running the extractor, please accept by saying yes. Once it's over, please exit")
            os.chdir(os.path.join(self.ff8_path))
            subprocess.run("ffviii_demaster_manager.exe")
            os.chdir(installer_directory)
            archive_to_copy = ""
            futur_path = ""

        elif 'DefaultFiles' in mod_name:
            futur_path = os.path.join(self.ff8_path, 'Data', 'lang-{}'.format(mod_name[-2:].lower()))
            archive_to_copy = os.path.join(archive, list_dir[index_folder])
        elif mod_name == self.UPDATE_DATA_NAME:
            archive_to_copy = os.path.join(archive, list_dir[index_folder])
            futur_path = os.path.join(os.getcwd(), "HobbitInstaller-data")
        elif index_folder >= 0:  # If the extract contain the folder name itself
            archive_to_copy = os.path.join(archive, list_dir[index_folder])
            futur_path = self.ff8_path
        else:
            archive_to_copy = archive
            futur_path = self.ff8_path
        if archive_to_copy and futur_path:
            print("Archive to copy: {}, futur path: {}".format(archive_to_copy, futur_path))
            shutil.copytree(archive_to_copy, futur_path, dirs_exist_ok=True,
                            copy_function=shutil.copy)  # shutil.copy to make it works on linux proton
        if archive != "":
            shutil.rmtree(archive)
        # remove_test_file()
        if not keep_download_mod:
            shutil.rmtree(self.FOLDER_DOWNLOAD)

        ffnx_param = self.mod_dict_json[mod_name]["ffnx_param"]
        if ffnx_param and ff8_version == "ffnx":
            print("Updating FFNx.toml file for mod {}".format(mod_name))
            if not os.path.join(self.ff8_path, "FFNx.toml"):
                with open(os.path.join(self.ff8_path, "FFNx.toml"), "w") as file:
                    pass
                self.ffnx_manager.change_ffnx_option(ffnx_param, self.ff8_path)

    def update_data(self):
        self.install_mod(self.UPDATE_DATA_NAME)
        self.__init_mod_data()
