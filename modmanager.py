import glob
import os
import re
import shutil
from zipfile import ZipFile
from ffnxmanager import FFNxManager
import patoolib
import requests


class ModManager():
    GIT_MOD_FILE = os.path.join("ModSetup", "git_mod_list.txt")
    GIT_TAG_FILE = os.path.join("ModSetup", "git_tag.txt")
    DIRECT_LINK_FILE = os.path.join("ModSetup", "direct_link.txt")
    SEP_CHAR = '>'
    FOLDER_DOWNLOAD = "ModDownloaded"
    FOLDER_SETUP = "ModSetup"
    TYPE_DOWNLOAD = 'Steam'
    GITHUB_RELEASE_TAG_PATH = "/releases/tag/"
    GITHUB_RELEASE_PATH = "/releases"
    MOD_AVAILABLE_FILE = 'mod_available.txt'
    MOD_FILE_NAME = 'mod_file_name.txt'
    LIST_MOD_TO_BE_SETUP = ['FFNxFF8Music', 'FFNx-RoseAndWine']

    def __init__(self, ff8_path='.'):
        self.buffer_git_list_mod = []
        self.buffer_tag_mod = []
        self.buffer_direct_link_mod = []
        self.mod_dict = {}
        self.mod_file_list = []
        self.mod_list_file_name = []
        self.github_mod_list = []
        self.direct_link_mod_list = []
        self.ffnx_manager = FFNxManager()
        os.makedirs(self.FOLDER_DOWNLOAD, exist_ok=True)
        self.ff8_path = ff8_path
        self.__read_setup_files()
        self.__load_mod_list()
        self.__load_github_info()
        self.__load_direct_link_info()
        self.__load_mod_file_name()

    def __read_setup_files(self):
        with (open(self.GIT_MOD_FILE, "r") as f):
            self.buffer_git_list_mod = f.read().split('\n')
        with (open(self.GIT_TAG_FILE, "r") as f):
            self.buffer_tag_mod = f.read().split('\n')
        with (open(self.DIRECT_LINK_FILE, "r") as f):
            self.buffer_direct_link_mod = f.read().split('\n')
        if len(self.buffer_git_list_mod) != len(self.buffer_tag_mod):
            raise ValueError("The file {} and file {} doesn't have the same number of line !".format(self.GIT_MOD_FILE, self.GIT_TAG_FILE))

    def __load_mod_file_name(self):
        with open(os.path.join(self.FOLDER_SETUP, self.MOD_FILE_NAME), "r") as file:
            self.mod_list_file_name.extend(file.read().split('\n'))

    def __load_mod_list(self):
        with open(os.path.join(self.FOLDER_SETUP, self.MOD_AVAILABLE_FILE), "r") as file:
            self.mod_file_list.extend(file.read().split('\n'))

    def __load_github_info(self):
        # Loading github info for all github mod
        self.github_mod_list = []
        for i in range(len(self.buffer_git_list_mod)):
            current_mod = self.buffer_git_list_mod[i].split(self.SEP_CHAR)[0]
            # Searching the corresponding tag
            current_mod_tag = [x.split(self.SEP_CHAR)[1] for x in self.buffer_tag_mod if x.split(self.SEP_CHAR)[0] == current_mod]
            if not current_mod_tag or len(current_mod_tag) > 1:
                print("No correspondance between the tag and the mod in github file")
            else:
                current_mod_tag = current_mod_tag[0]
            self.github_mod_list.append(current_mod)
            self.mod_dict[current_mod] = {'type': 'github', 'github': self.buffer_git_list_mod[i].split(self.SEP_CHAR)[1], 'tag': current_mod_tag}

    def __load_direct_link_info(self):
        # Loading link info for all direct link mod
        self.direct_link_mod_list = []
        for direct_mod in self.buffer_direct_link_mod:
            current_mod = direct_mod.split(self.SEP_CHAR)[0]
            self.mod_dict[current_mod] = {'type': 'direct_link', 'link': direct_mod.split(self.SEP_CHAR)[1]}
            self.direct_link_mod_list.append(current_mod)

    def download_file(self, link, headers={}, write_file=False, file_name=None, dest_path=FOLDER_DOWNLOAD):
        request_return = requests.get(link, headers=headers)
        if not file_name:
            if "Content-Disposition" in request_return.headers.keys():
                file_name = re.findall("filename\*?=['\"]?(?:UTF-\d['\"]*)?([^;\r\n\"']*)['\"]?;?", request_return.headers["Content-Disposition"])[0]
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

    def install_mod(self, mod_name: str, keep_download_mod=False, special_status={}, download=True):
        os.makedirs(self.FOLDER_DOWNLOAD, exist_ok=True)
        if mod_name in self.github_mod_list:
            if download:
                json_link = self.mod_dict[mod_name]['github'] + self.GITHUB_RELEASE_PATH
                json_link = json_link.replace('github.com', 'api.github.com/repos')
                json_file = self.download_file(json_link, headers={'content-type': 'application/json'})[0]
                json_file = json_file.json()
                assets_url = ""
                if self.mod_dict[mod_name]['tag'] == 'latest':
                    assets_url = json_file[0]['assets_url']
                else:  # Searching the tag
                    for el in json_file:
                        if el['tag_name'] == self.mod_dict[mod_name]['tag']:
                            assets_url = el['assets_url']
                            break
                json_file = self.download_file(assets_url, headers={'content-type': 'application/json'})[0].json()
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
                dd_file_name = self.mod_list_file_name[self.mod_file_list.index(mod_name)]

        elif mod_name in self.direct_link_mod_list:
            direct_file = self.mod_dict[mod_name]['link']
            if mod_name == "FFNxFF8Music":  # need remove " around
                dd_file_name = direct_file.split('/')[-1]
            else:
                dd_file_name = None
            if download:
                dd_file_name = self.download_file(direct_file, write_file=True, file_name=dd_file_name)[1]
            else:
                dd_file_name = self.mod_list_file_name[self.mod_file_list.index(mod_name)]
        else:
            raise ValueError("Unexpected ELSE")
        archive = ""
        if '.rar' in dd_file_name or '.7z' in dd_file_name:
            archive = "temparchive"
            patoolib.extract_archive(os.path.join(self.FOLDER_DOWNLOAD, dd_file_name), verbosity=-1, outdir=archive, program=os.path.join('Resources', '7z.exe'))
        # Unzip locally then copy all files, so we don't have problem erasing files while unziping
        elif '.zip' in dd_file_name:
            archive = "tempzip"
            os.makedirs(archive, exist_ok=True)
            with ZipFile(os.path.join(self.FOLDER_DOWNLOAD, dd_file_name), 'r') as zip_ref:
                zip_ref.extractall(archive)
        list_dir = os.listdir(archive)
        try:
            index_folder = os.listdir(archive).index(dd_file_name.split('.')[0])

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
        elif mod_name == "FF8Curiosite-FR-ONLY":
            archive_to_copy = archive  # Shouldn't happen
            futur_path = os.path.join(self.ff8_path, 'Data', 'lang-fr')
            os.makedirs(os.path.join(self.ff8_path, 'Data', 'Music', 'dmusic'), exist_ok=True)
            shutil.copy(os.path.join(archive, "064s-choco.sgt"), os.path.join(self.ff8_path, 'Data', 'Music', 'dmusic'))
            os.remove(os.path.join(archive, "064s-choco.sgt"))
        elif 'DefaultFiles' in mod_name:
            futur_path = os.path.join(self.ff8_path, 'Data', 'lang-{}'.format(mod_name[-2:].lower()))
            archive_to_copy = os.path.join(archive, list_dir[index_folder])
        elif index_folder >= 0:  # If the extract contain the folder name itself
            archive_to_copy = os.path.join(archive, list_dir[index_folder])
            futur_path = self.ff8_path

        else:
            archive_to_copy = archive
            futur_path = self.ff8_path
        print("Archive to copy: {}, futur path: {}".format(archive_to_copy, futur_path))
        shutil.copytree(archive_to_copy, futur_path, dirs_exist_ok=True, copy_function=shutil.copy)
        if archive != "":
            shutil.rmtree(archive)
        # remove_test_file()
        if not keep_download_mod:
            shutil.rmtree(self.FOLDER_DOWNLOAD)

        if mod_name in self.LIST_MOD_TO_BE_SETUP:
            if not os.path.join(self.ff8_path, "FFNx.toml"):
                with open(os.path.join(self.ff8_path, "FFNx.toml"), "w") as file:
                    pass
            self.ffnx_manager.read_ffnx_setup_file(ff8_path=self.ff8_path)
            if mod_name == "FFNx-FFNxFF8Music":
                self.ffnx_manager.change_ffnx_music_option()
            if mod_name == "FFNx-RoseAndWine":
                self.ffnx_manager.change_rosewine_music_option()

            self.ffnx_manager.write_ffnx_setup_file(self.ff8_path)
