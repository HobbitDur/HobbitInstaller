import argparse
import os
import shutil
import sys
from PyQt5.QtWidgets import QApplication

from hobbitgui import WindowInstaller
from modmanager import ModManager




mod_file_list = []





def remove_test_file():
    shutil.rmtree(args.path)
    os.makedirs(args.path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Hobbit Installer", description="This program install mode for FF8")
    parser.add_argument("path", help="Path to FF8 folder", type=str, nargs='?', const=1, default=os.getcwd())
    parser.add_argument("-t", "--test", help="For testing purpose", action='store_true')
    parser.add_argument("-kdm", "--keep_download_mod", help="Keep downloading mod file", action='store_true')

    args = parser.parse_args()

    mod_manager = ModManager(ff8_path=args.path)

    app = QApplication.instance()
    if not app:  # sinon on crée une instance de QApplication
        app = QApplication(sys.argv)

    window_installer = WindowInstaller(mod_manager, keep_downloaded_mod=args.keep_download_mod)
    sys.exit(app.exec_())

    if args.test:
        os.makedirs("FF8FolderTest", exist_ok=True)
        if os.path.exists('tempzip'):
            shutil.rmtree('tempzip')

