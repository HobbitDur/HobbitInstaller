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
    def __init__(self, ff8_path='.'):
        self.read_setup_files()
        self.buffer_git_list_mod = []
        self.buffer_tag_mod = []
        self.buffer_direct_link_mod = []
        self.mod_dict = {}
        self.mod_file_list = []
        self.github_mod_list = []
        self.direct_link_mod_list = []
        self.ffnx_manager = FFNxManager()
        os.makedirs(self.FOLDER_DOWNLOAD, exist_ok=True)
        self.ff8_path = ff8_path
        self.read_setup_files()
        self.load_mod_list()
        self.load_github_info()
        self.load_direct_link_info()



    def read_setup_files(self):
        with (open(self.GIT_MOD_FILE, "r") as f):
            self.buffer_git_list_mod = f.read().split('\n')
        with (open(self.GIT_TAG_FILE, "r") as f):
            self.buffer_tag_mod = f.read().split('\n')
        with (open(self.DIRECT_LINK_FILE, "r") as f):
            self.buffer_direct_link_mod = f.read().split('\n')

        if len(self.buffer_git_list_mod) != len(self.buffer_tag_mod):
            raise ValueError("The file {} and file {} doesn't have the same number of line !".format(GIT_MOD_FILE, GIT_TAG_FILE))

    def load_mod_list(self):
        with open(os.path.join(self.FOLDER_SETUP, self.MOD_AVAILABLE_FILE), "r") as file:
            self.mod_file_list.extend(file.read().split('\n'))
        print(self.mod_file_list)
    def load_github_info(self):
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

    def load_direct_link_info(self):
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

    def install_mods(self, mod_to_be_installed, keep_download_mod=False):
        for mod_name in mod_to_be_installed:
            if mod_name in self.github_mod_list:
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
            elif mod_name in self.direct_link_mod_list:
                direct_file = self.mod_dict[mod_name]['link']
                if mod_name == "HobbitGameplayMod":  # Special because the link as a content-type of html instead of octetstream
                    dd_file_name = "HobbitGameplayMod.zip"
                elif mod_name == "FFNxBattlefield":
                    dd_file_name = "FFNxBattlefields.rar"
                elif mod_name == "FFNxLunarCry":
                    dd_file_name = "FFNxLunarCry.rar"
                elif mod_name == "FFNxSeedReborn":
                    dd_file_name = "FFNxSeedReborn.rar"
                elif mod_name == "FFNxTripod":
                    dd_file_name = "FFNxTripod.rar"
                elif mod_name == "FFNxFF8Music":  # need remove " around
                    dd_file_name = direct_file.split('/')[-1]
                    self.ffnx_manager.change_music_option()
                else:
                    dd_file_name = None
                dd_file_name = self.download_file(direct_file, write_file=True, file_name=dd_file_name)[1]
            else:
                raise ValueError("Unexpected ELSE")
            archive = ""
            if '.rar' in dd_file_name:
                patoolib.extract_archive(os.path.join(self.FOLDER_DOWNLOAD, dd_file_name), verbosity=-1, outdir='temprar', program='Resources/7z.exe')
                archive = "temprar"
            # Unzip locally then copy all files, so we don't have problem erasing files while unziping
            elif '.zip' in dd_file_name:
                archive = "tempzip"
                os.makedirs(archive, exist_ok=True)
                with ZipFile(os.path.join(self.FOLDER_DOWNLOAD, dd_file_name), 'r') as zip_ref:
                    zip_ref.extractall(archive)
            list_file_archive = os.walk(archive)
            for (dir_path, dir_names, file_names) in list_file_archive:
                for file_name in file_names:
                    full_file_path = os.path.join(dir_path, file_name)
                    if dir_path == archive:  # So a direct file in folder
                        local_path = ''
                    else:
                        local_path = dir_path.replace(archive + os.path.sep, '')
                        if local_path in ['FFNxBattlefields', 'FFNxLunarCry', 'FFNxSeedReborn', 'FFNxTripod']:
                            local_path = local_path.replace(mod_name, '')
                    if mod_name in ['FFNxBattlefields', 'FFNxLunarCry', 'FFNxSeedReborn', 'FFNxTripod']:
                        local_path = local_path.replace(mod_name + os.path.sep, '')
                    dest_folder = os.path.join(self.ff8_path, local_path)
                    dest_file = os.path.join(dest_folder, file_name)
                    if os.path.exists(dest_file):
                        os.remove(dest_file)
                    os.makedirs(dest_folder, exist_ok=True)
                    shutil.copy(full_file_path, dest_folder)

            if archive != "":
                shutil.rmtree(archive)

            if mod_name == "FFNx":
                ffnx_setup = self.ffnx_manager.read_ffnx_setup_file(ff8_path=self.ff8_path)

        # remove_test_file()
        if not keep_download_mod:
            shutil.rmtree(self.FOLDER_DOWNLOAD)
        if 'FFNx' in self.mod_file_list:
            self.ffnx_manager.write_ffnx_setup_file(self.ff8_path)