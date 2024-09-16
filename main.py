import argparse
import glob
import json
import os
import re
import shutil
from zipfile import ZipFile
import requests

GITHUB_RELEASE_TAG_PATH = "/releases/tag/"
GITHUB_RELEASE_PATH = "/releases"
GIT_MOD_FILE = os.path.join("ModSetup", "git_mod_list.txt")
GIT_TAG_FILE = os.path.join("ModSetup", "git_tag.txt")
DIRECT_LINK_FILE = os.path.join("ModSetup", "direct_link.txt")
SEP_CHAR = '>'
TYPE_DOWNLOAD = 'Steam'

FOLDER_DOWNLOAD = "ModDownloaded"
FOLDER_SETUP = "ModSetup"
FFNX_FILE_SETUP = "FFNx.toml"
MUSIC_PARAM_CHANGE = {'use_external_music': 'true', 'external_music_path': '"psf"', 'external_music_ext': '"minipsf"', 'he_bios_path': '"psf/hebios.bin"'}

mod_file_list = []


def load_mod_list():
    with open(os.path.join(FOLDER_SETUP, "mod_to_be_installed.txt"), "r") as file:
        mod_file_list.extend(file.read().split('\n'))


def download_file(link, headers={}, write_file=False, file_name=None, dest_path=FOLDER_DOWNLOAD):
    request_return = requests.get(link, headers=headers)
    if not file_name:
        if "Content-Disposition" in request_return.headers.keys():
            file_name = re.findall("filename=(.+)", request_return.headers["Content-Disposition"])[0]
        else:
            file_name = link.split("/")[-1]
    if request_return.status_code == 200:
        print("Successfully downloaded {}".format(link))
        if write_file:
            with open(os.path.join(dest_path, file_name), "wb") as file:
                file.write(request_return.content)
    else:
        print("Fail to download {}".format(link))
    return request_return


def remove_test_file():
    shutil.rmtree(args.path)
    os.makedirs(args.path)


def read_ffnx_setup_file(ff8_path):
    with open(os.path.join(ff8_path, FFNX_FILE_SETUP), "r") as file:
        ffnx_setup = file.read()
        ffnx_setup = ffnx_setup.split('\n')
    return ffnx_setup


def change_music_option(ffnx_setup_file):
    for i, line in enumerate(ffnx_setup_file):
        for param, value in MUSIC_PARAM_CHANGE.items():
            if param in line and '=' in line:
                line_split = line.split('=')
                ffnx_setup_file[i] = line_split[0] + "=" + value + "#Value changed by HobbitInstaller"


def write_ffnx_setup_file(ff8_path, ffnx_setup):
    with open(os.path.join(ff8_path, FFNX_FILE_SETUP), "w") as file:
        for line in ffnx_setup:
            file.write(line + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Hobbit Installer", description="This program install mode for FF8")
    parser.add_argument("path", help="Path to FF8 folder", type=str, nargs='?', const=1, default=os.getcwd())
    parser.add_argument("-t", "--test", help="For testing purpose", action='store_true')
    parser.add_argument("-kdm", "--keep_download_mod", help="Keep downloading mod file", action='store_true')

    args = parser.parse_args()

    load_mod_list()
    mod_list = {}

    with (open(GIT_MOD_FILE, "r") as f):
        buffer_git_list_mod = f.read().split('\n')
    with (open(GIT_TAG_FILE, "r") as f):
        buffer_tag_mod = f.read().split('\n')
    with (open(DIRECT_LINK_FILE, "r") as f):
        buffer_direct_link_mod = f.read().split('\n')

    if len(buffer_git_list_mod) != len(buffer_tag_mod):
        raise ValueError("The file {} and file {} doesn't have the same number of line !".format(GIT_MOD_FILE, GIT_TAG_FILE))
    os.makedirs(FOLDER_DOWNLOAD, exist_ok=True)
    if args.test:
        os.makedirs("FF8FolderTest", exist_ok=True)
        if os.path.exists('tempzip'):
            shutil.rmtree('tempzip')

    # Loading github info for all github mod
    github_mod_list = []
    for i in range(len(buffer_git_list_mod)):
        current_mod = buffer_git_list_mod[i].split(SEP_CHAR)[0]
        # Searching the corresponding tag
        current_mod_tag = [x.split(SEP_CHAR)[1] for x in buffer_tag_mod if x.split(SEP_CHAR)[0] == current_mod]
        if not current_mod_tag or len(current_mod_tag) > 1:
            print("No correspondance between the tag and the mod in github file")
        else:
            current_mod_tag = current_mod_tag[0]
        github_mod_list.append(current_mod)
        mod_list[current_mod] = {'github': buffer_git_list_mod[i].split(SEP_CHAR)[1], 'tag': current_mod_tag}

    # Loading link info for all direct link mod
    direct_link_mod_list = []
    for direct_mod in buffer_direct_link_mod:
        current_mod = direct_mod.split(SEP_CHAR)[0]
        mod_list[current_mod] = {'link': direct_mod.split(SEP_CHAR)[1]}
        direct_link_mod_list.append(current_mod)

    for mod_name in mod_file_list:
        print("Downloading {}".format(mod_name))
        if mod_name in github_mod_list:
            dd_file_name = "FFNx-Steam-v1.19.1.0.zip"
            json_link = mod_list[mod_name]['github'] + GITHUB_RELEASE_PATH
            json_link = json_link.replace('github.com', 'api.github.com/repos')
            json_file = download_file(json_link, headers={'content-type': 'application/json'})
            json_file = json_file.json()
            assets_url = ""
            if mod_list[mod_name]['tag'] == 'latest':
                assets_url = json_file[0]['assets_url']
            else:  # Searching the tag
                for el in json_file:
                    if el['tag_name'] == mod_list[mod_name]['tag']:
                        assets_url = el['assets_url']
                        break
            json_file = download_file(assets_url, headers={'content-type': 'application/json'})
            json_file = json_file.json()
            asset_link = ""
            for el in json_file:
                if TYPE_DOWNLOAD in el['browser_download_url']:
                    asset_link = el['browser_download_url']
                    break

            dd_file_name = asset_link.split('/')[-1]
            download_file(asset_link, write_file=True)
        elif mod_name in direct_link_mod_list:

            direct_file = mod_list[mod_name]['link']
            if mod_name == "HobbitGameplayMod":  # Special because the link as a content-type of html instead of octetstream
                dd_file_name = "HobbitGameplayMod.zip"
                download_file(direct_file, write_file=True, file_name=dd_file_name)
            elif mod_name == "FFNxFF8Music":  # need remove " around
                dd_file_name = direct_file.split('/')[-1]
                download_file(direct_file, write_file=True, file_name=dd_file_name)
                change_music_option(ffnx_setup)
            else:
                dd_file_name = direct_file.split('/')[-1]
                download_file(direct_file, write_file=True)
        else:
            raise ValueError("Unexpected ELSE")


        # Unzip locally then copy all files, so we don't have problem erasing files while unziping
        if '.zip' in dd_file_name:
            os.makedirs('tempzip', exist_ok=True)
            with ZipFile(os.path.join(FOLDER_DOWNLOAD, dd_file_name), 'r') as zip_ref:
                zip_ref.extractall('tempzip')
            list_file_zip = os.walk('tempzip')
            for (dir_path, dir_names, file_names) in list_file_zip:
                for file_name in file_names:
                    full_file_path = os.path.join(dir_path, file_name)
                    if dir_path=='tempzip': #So a direct file in folder
                        local_path = ''
                    else:
                        local_path = dir_path.replace('tempzip'+os.path.sep, '')
                    dest_folder = os.path.join(args.path, local_path)
                    dest_file = os.path.join(dest_folder, file_name)
                    if os.path.exists(dest_file):
                        os.remove(dest_file)
                    os.makedirs(dest_folder, exist_ok=True)
                    shutil.copy(full_file_path, dest_folder)
            shutil.rmtree('tempzip')


        if mod_name == "FFNx":
            ffnx_setup = read_ffnx_setup_file(ff8_path=args.path)

        # remove_test_file()
    if not args.keep_download_mod:
        shutil.rmtree(FOLDER_DOWNLOAD)
    if 'FFNx' in github_mod_list:
        write_ffnx_setup_file(args.path, ffnx_setup)
