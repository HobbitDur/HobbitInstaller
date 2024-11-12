import os
import struct
from tkinter import messagebox
from pathlib import Path


class ZzzEntry:
    """Represents a single entry in the zzz file."""

    def __init__(self, string_len, string_, offset, size):
        self.string_len = string_len
        self.string = string_
        self.offset = offset
        self.size = size


class ZzzWatcher:
    """Dummy class representing the zzzWatcher in the original code.
       Assumes the show_dialog and update_status methods are part of this class."""

    def __init__(self, output_directory):
        self.output_directory = output_directory

    def show_dialog(self):
        # Placeholder for dialog display functionality
        pass

    def update_status(self, local_index, local_index2, progress_current, progress_total, filename):
        # Placeholder for status update functionality
        pass


local_index = 0
local_index2 = 0


def unpack_all(out_directory):
    """Unpacks main.zzz and other.zzz files into the specified output directory."""
    global local_index, local_index2
    local_index, local_index2 = 0, 0

    if not (os.path.exists("main.zzz") and os.path.exists("other.zzz")):
        messagebox.showerror(
            "Auto unpacking error",
            "Either main.zzz or other.zzz was not found in the current directory!\n"
            "Did you put this launcher in your Final Fantasy VIII Remastered root directory?"
        )
        return

    os.makedirs(out_directory, exist_ok=True)
    watcher = ZzzWatcher(out_directory)
    watcher.show_dialog()


def unpack_file(path, out_directory, watcher):
    """Unpacks a single .zzz file given a path and output directory."""
    global local_index, local_index2
    entries = []

    with open(path, "rb") as f:
        file_count, = struct.unpack('<I', f.read(4))

        for _ in range(file_count):
            string_len, = struct.unpack('<I', f.read(4))
            string_ = f.read(string_len).decode('utf-8')
            offset, = struct.unpack('<Q', f.read(8))
            size, = struct.unpack('<I', f.read(4))
            entries.append(ZzzEntry(string_len, string_, offset, size))

        for entry in entries:
            if path == "other.zzz":
                watcher.update_status(local_index, local_index2, local_index, len(entries), entry.string)
            else:
                watcher.update_status(local_index, local_index2, len(entries), 1, entry.string)

            output_path = Path(out_directory) / entry.string
            output_path.parent.mkdir(parents=True, exist_ok=True)
            f.seek(entry.offset)
            data = f.read(entry.size)

            with open(output_path, "wb") as out_file:
                out_file.write(data)

            if path == "main.zzz":
                local_index += 1
            else:
                local_index2 += 1

if __name__ == "__main__":
    output_directory = "unpacked_files"

    # Check for the existence of "main.zzz" and "other.zzz"
    if not (os.path.exists("main.zzz") and os.path.exists("other.zzz")):
        print("Error: Either 'main.zzz' or 'other.zzz' was not found in the current directory.")
        print("Please place this script in the Final Fantasy VIII Remastered root directory.")
        exit(0)

    # Create an output directory for unpacked files
    os.makedirs(output_directory, exist_ok=True)

    # Initialize the watcher for tracking progress (dummy functionality here)
    watcher = ZzzWatcher(output_directory)

    # Unpack both files
    print("Starting to unpack 'main.zzz'...")
    unpack_file("main.zzz", output_directory, watcher)
    print("'main.zzz' unpacked successfully.")

    print("Starting to unpack 'other.zzz'...")
    unpack_file("other.zzz", output_directory, watcher)
    print("'other.zzz' unpacked successfully.")
