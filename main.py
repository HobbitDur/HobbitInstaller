import argparse
import os
import sys
from PyQt6.QtWidgets import QApplication

from hobbitgui import WindowInstaller
from modmanager import ModManager

sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Hobbit Installer", description="This program install mode for FF8")
    parser.add_argument("path", help="Path to FF8 folder", type=str, nargs='?', const=1, default=os.getcwd())
    parser.add_argument("-t", "--test", help="For testing purpose", action='store_true')
    parser.add_argument("-kdm", "--keep_download_mod", help="Keep downloading mod file", action='store_true')

    args = parser.parse_args()

    sys.excepthook = exception_hook
    mod_manager = ModManager(ff8_path=args.path)

    app = QApplication.instance()
    if not app:  # sinon on crée une instance de QApplication
        app = QApplication(sys.argv)

    window_installer = WindowInstaller(mod_manager)
    sys.exit(app.exec())
