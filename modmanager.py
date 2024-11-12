import json
import os
import re
import shutil
import subprocess
import time
import types
from enum import Enum
from zipfile import ZipFile
import psutil
from ffnxmanager import FFNxManager
import patoolib
import requests

from model.mod import GroupModType, ModLang, ModWrapper, Mod, ModType


class ModManager:
    FOLDER_SETUP = os.path.join("HobbitInstaller-data", "ModSetup")
    SEP_CHAR = '>'
    FOLDER_DOWNLOAD = "ModDownloaded"
    TYPE_DOWNLOAD = 'Steam'
    GITHUB_RELEASE_TAG_PATH = "/releases/tag/"
    GITHUB_RELEASE_PATH = "/releases"
    UPDATE_DATA_NAME = "UpdateData"
    SETUP_FILE = os.path.join(FOLDER_SETUP, "setup.json")
    VERSION_LIST = ["FF8 PC 2000", "FF8 Steam 2013", "FF8 Remastered"]
    LANG_STR_LIST = ["en", "fr", "de", "es", "it"]
    def __init__(self, ff8_path='.'):
        self.ffnx_manager = FFNxManager()
        os.makedirs(self.FOLDER_DOWNLOAD, exist_ok=True)
        self.ff8_path = ff8_path
        self.mod_dict_json = {}
        self.__init_mod_data()

    def __init_mod_data(self):
        with open(self.SETUP_FILE) as f:
            self.mod_dict_json = json.load(f)['AvailableMods']
        for mod_name in self.mod_dict_json:
            if self.mod_dict_json[mod_name]["mod_type"] == "Wrapper":
                self.mod_dict_json[mod_name]["mod_type"] = GroupModType.WRAPPER
            elif self.mod_dict_json[mod_name]["mod_type"] == "Gameplay":
                self.mod_dict_json[mod_name]["mod_type"] = GroupModType.GAMEPLAY
            elif self.mod_dict_json[mod_name]["mod_type"] == "Music":
                self.mod_dict_json[mod_name]["mod_type"] = GroupModType.MUSIC
            elif self.mod_dict_json[mod_name]["mod_type"] == "EaseOfLife":
                self.mod_dict_json[mod_name]["mod_type"] = GroupModType.EASEOFLIFE
            elif self.mod_dict_json[mod_name]["mod_type"] == "Graphical":
                self.mod_dict_json[mod_name]["mod_type"] = GroupModType.GRAPHIC
            elif self.mod_dict_json[mod_name]["mod_type"] == "Setup":
                self.mod_dict_json[mod_name]["mod_type"] = GroupModType.SETUP
            else:
                print(f"Unexpected Group mod: {self.mod_dict_json[mod_name]["mod_type"]}")
            if self.mod_dict_json[mod_name]["default_selected"] == "true":
                self.mod_dict_json[mod_name]["default_selected"] = True
            elif self.mod_dict_json[mod_name]["default_selected"] == "false":
                self.mod_dict_json[mod_name]["default_selected"] = False
            else:
                print(f"Unexpected default selection: {self.mod_dict_json[mod_name]["default_selected"]}")
                self.mod_dict_json[mod_name]["default_selected"] = False

            if self.mod_dict_json[mod_name]["lang"]:
                for index_lang, lang in enumerate(self.mod_dict_json[mod_name]["lang"]):
                    if lang == "en":
                        new_lang = ModLang.EN
                    elif lang == "fr":
                        new_lang = ModLang.FR
                    elif lang == "de":
                        new_lang = ModLang.DE
                    elif lang == "es":
                        new_lang = ModLang.ES
                    elif lang == "it":
                        new_lang = ModLang.IT
                    else:
                        print(f"Unexpected lang selection: {self.mod_dict_json[mod_name]["lang"]}")
                        new_lang = ModLang.EN
                    self.mod_dict_json[mod_name]["lang"][index_lang] = new_lang

            if self.mod_dict_json[mod_name]["compatibility"]:
                if self.mod_dict_json[mod_name]["compatibility"] == "False":  # Temp fix
                    self.mod_dict_json[mod_name]["compatibility"] = [ModWrapper.FFNX, ModWrapper.DEMASTER]
                else:
                    for index_compat, compat in enumerate(self.mod_dict_json[mod_name]["compatibility"]):
                        if compat == "ffnx":
                            new_compat = ModWrapper.FFNX
                        elif compat == "demaster":
                            new_compat = ModWrapper.DEMASTER
                        else:
                            print(f"Unexpected compatibility selection: {self.mod_dict_json[mod_name]["compatibility"]}")
                            new_compat = ModWrapper.FFNX
                        self.mod_dict_json[mod_name]["compatibility"][index_compat] = new_compat

    def __download_file(self, link, download_update_func: types.MethodType = None, headers={}, write_file=False, file_name=None, dest_path=FOLDER_DOWNLOAD) -> (
            requests.models.Response, str):
        print("Downloading with link: {}".format(link))
        if write_file:
            stream = True
        else:
            stream = False

        request_return = requests.get(link, headers=headers, stream=stream)

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

        if write_file:
            total_length = request_return.headers.get('content-length')
            if total_length is None:  # no content length header
                total_length = -1
            else:
                total_length = int(total_length)
            dl = 0
            if download_update_func:
                download_update_func(dl, total_length)
            full_data = bytearray()
            for data in request_return.iter_content(chunk_size=4096):
                dl += len(data)
                full_data.extend(data)
                if download_update_func:
                    download_update_func(dl, total_length)
            with open(os.path.join(dest_path, file_name), "wb") as file:
                file.write(full_data)

        if request_return.status_code == 200:
            print("Successfully downloaded {}".format(link))
        else:
            print("Fail to download {}".format(link))

        return request_return, file_name

    def save_local_file(self, lang="en"):
        path_to_files = os.path.join(self.ff8_path, 'Data', 'lang-' + lang)

    def __get_github_link(self, mod_name: str):
        github_link = self.mod_dict_json[mod_name]['link'] + self.GITHUB_RELEASE_PATH
        github_link = github_link.replace('github.com', 'api.github.com/repos')
        return github_link

    def __get_github_url_file(self, mod: Mod, json_url="assets_url"):
        json_link = self.__get_github_link(mod.name)
        json_file = self.__download_file(json_link, headers={'content-type': 'application/json'})[0]
        json_file = json_file.json()
        dd_url = ""
        if mod.info['git_tag'] == 'latest':
            for el in json_file:
                if el['tag_name'] != "canary" and el['tag_name'] != "prerelease" and el['tag_name'].count('.') >=1:
                    dd_url =el[json_url]
                    break
        else:  # Searching the tag
            for el in json_file:
                if el['tag_name'] == mod.info['git_tag']:
                    dd_url = el[json_url]
        return dd_url

    def restore_backup(self):
        try:
            archive = self.ff8_path
            with ZipFile(os.path.join(self.ff8_path, "backup_data.zip"), 'r') as zip_ref:
                zip_ref.extractall(archive)
            return True
        except FileNotFoundError:
            print(f"/!\\ File backup_data.zip doesn't exist, fail restoring")
            return False

    def install_mod(self, mod: Mod, download_update_func: types.MethodType = None, keep_download_mod=False, download=True, ff8_wrapper=ModWrapper.FFNX,
                    backup=True, lang_requested=ModLang.EN):
        if backup:
            print("Backing up the data")
            try:
                if not os.path.exists(os.path.join(self.ff8_path, "backup_data.zip")):
                    shutil.make_archive(base_name=os.path.join(self.ff8_path, "backup_data"), format='zip', root_dir=os.path.join(self.ff8_path, "Data"),
                                        base_dir=".")
                else:
                    print(f"File backup_data.zip already exist")
            except FileExistsError:  # Normally doesn't append with make_archive
                print(f"File already exist")
            except FileNotFoundError:
                print("No Data file found for backup, are you sure you are in the FF8 folder ?")

        os.makedirs(self.FOLDER_DOWNLOAD, exist_ok=True)
        print("Start installing mod: {}".format(mod.name))

        if mod.get_type() == ModType.SETUP:
            dd_url = self.__get_github_url_file(mod, "zipball_url")
            dd_file_name = self.__download_file(dd_url, download_update_func, write_file=True)[1]
        elif mod.info["download_type"] == "github":
            if download:
                dd_url = self.__get_github_url_file(mod, "assets_url")
                json_file = self.__download_file(dd_url, download_update_func, headers={'content-type': 'application/json'})[0].json()
                asset_link = ""
                if mod.name == 'FFNx':
                    for el in json_file:
                        if self.TYPE_DOWNLOAD in el['browser_download_url']:
                            asset_link = el['browser_download_url']
                            break
                elif len(json_file) == 1:
                    asset_link = json_file[0]['browser_download_url']
                else:
                    print("Didn't manage several asset without a particular case")
                dd_file_name = self.__download_file(asset_link, download_update_func, write_file=True)[1]
            else:
                dd_file_name = self.mod_dict_json["download_name"]
        elif mod.info["download_type"] == "direct":
            if ff8_wrapper == ModWrapper.FFNX:
                direct_file = mod.info['link']
            elif ff8_wrapper == ModWrapper.DEMASTER:
                direct_file = mod.info['remaster-link']
            else:
                print("Error unexpected ff8 wrapper: {}".format(ff8_wrapper))
                direct_file = mod.info['link']
            if mod.name == "FFNxFF8Music":  # need remove " around
                dd_file_name = mod.info["download_name"]
            else:
                dd_file_name = None
            if download:
                dd_file_name = self.__download_file(direct_file, download_update_func, write_file=True, file_name=dd_file_name)[1]
            else:
                dd_file_name = mod.info["download_name"]
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
            #subprocess.run(['HobbitInstaller-data\\Resources\\7z.exe', 'x', f'-o{archive}', '--', os.path.join(self.FOLDER_DOWNLOAD, dd_file_name)])
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
        print(mod.get_type())
        if mod.get_type() == ModType.RELOADED:  # Special handle
            archive_to_copy = os.path.join(archive, mod.special_status)
            futur_path = os.path.join(self.ff8_path, 'Data', 'lang-fr')
        elif mod.get_type() == ModType.RAGNAROK:
            print(mod.special_status)
            archive_to_copy = os.path.join(archive, list_dir[index_folder], list_dir[index_folder], mod.special_status)
            futur_path = os.path.join(self.ff8_path, 'Data')
            hext_to_copy = os.path.join(archive, list_dir[index_folder], list_dir[index_folder], "Ragnarok_mod.txt")
            futur_path_hext_to_copy = os.path.join(self.ff8_path, 'hext', 'ff8')
            shutil.copy(hext_to_copy, os.path.join(futur_path_hext_to_copy, 'en'))
            shutil.copy(hext_to_copy, os.path.join(futur_path_hext_to_copy, 'en_nv'))
            shutil.copy(hext_to_copy, os.path.join(futur_path_hext_to_copy, 'en_eidos'))
            shutil.copy(hext_to_copy, os.path.join(futur_path_hext_to_copy, 'en_eidos_nv'))
        elif mod.name == "[Tsunamods] Card-RF":
            archive_to_copy = os.path.join(archive , 'Card-RF', self.LANG_STR_LIST[lang_requested.value])
            futur_path = os.path.join(self.ff8_path)
        elif mod.name == "FF8Curiosite-FR-ONLY":
            archive_to_copy = archive
            futur_path = os.path.join(self.ff8_path, 'Data', 'lang-fr')
            os.makedirs(os.path.join(self.ff8_path, 'Data', 'Music', 'dmusic'), exist_ok=True)
            shutil.copy(os.path.join(archive, "064s-choco.sgt"), os.path.join(self.ff8_path, 'Data', 'Music', 'dmusic'))
            os.remove(os.path.join(archive, "064s-choco.sgt"))
        elif mod.name == "Demaster":  # Big special handle
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
        elif mod.get_type() == ModType.SETUP:
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
        ffnx_param = mod.info["ffnx_param"]
        if ffnx_param and ff8_wrapper == ModWrapper.FFNX:
            print("Updating FFNx.toml file for mod {}".format(mod.name))
            if not os.path.join(self.ff8_path, "FFNx.toml"): # If file doesnt exist, create it
                with open(os.path.join(self.ff8_path, "FFNx.toml"), "w") as file:
                    pass
            self.ffnx_manager.change_ffnx_option(ffnx_param, self.ff8_path)

    def update_mod_list(self):
        self.install_mod(Mod(self.UPDATE_DATA_NAME, self.mod_dict_json[self.UPDATE_DATA_NAME]), backup=False)
        self.__init_mod_data()
