import json
import tkinter as tk
from tkinter import filedialog
import threading
import PIL.Image
import PIL.ImageTk
import pystray
from notifypy import Notify
import time
import os
import shutil
import mimetypes

image = PIL.Image.open("ico.png")

NOTIFY_ENABLE = True

DIR_DESTINATION = ""

AUTO_SORT = False

NOTIFY = Notify()


def SendNotify(title: str, msg:str) -> None:
    NOTIFY.application_name = "Sorty!"
    NOTIFY.title = title
    NOTIFY.message = msg
    NOTIFY.icon = "ico.png"
    NOTIFY.send()

def create_settings(icon: pystray.Icon) -> None:
    root = tk.Tk()
    root.withdraw()
    ico = PIL.Image.open('ico.png')
    photo = PIL.ImageTk.PhotoImage(ico)
    root.wm_iconphoto(False, photo)

    download_folder = filedialog.askdirectory(title="Please select the downloads folder.")
    if not download_folder:
        SendNotify("😭", "I cant work correctly without folder!")
        icon.stop()




    notifications_enabled = True
    settings = {
        "notificationsenabled": notifications_enabled,
        "download_folder": download_folder
    }
    with open("settings.sorty", "w") as settings_file:
        json.dump(settings, settings_file)

def sort_files(directory: str) -> int:
    folders = {
        "Images": os.path.join(directory, "Images"),
        "Audio": os.path.join(directory, "Audio"),
        "Torrents": os.path.join(directory, "Torrents"),
        "ZIP": os.path.join(directory, "ZIP"),
        "RAR": os.path.join(directory, "RAR"),
        "Music": os.path.join(directory, "Music"),
        "Other": os.path.join(directory, "Other")
    }

    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)

    moved_files_count = 0

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isdir(file_path):
            continue

        if filename.lower().endswith('.exe'):
            target_folder = folders["Other"]
        else:
            try:
                #
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type:
                    if mime_type.startswith('image/'):
                        target_folder = folders["Images"]
                    elif mime_type.startswith('audio/'):
                        target_folder = folders["Audio"]
                    elif filename.lower().endswith('.torrent'):
                        target_folder = folders["Torrents"]
                    elif filename.lower().endswith('.zip'):
                        target_folder = folders["ZIP"]
                    elif filename.lower().endswith('.rar'):
                        target_folder = folders["RAR"]
                    elif filename.lower().endswith('.mp3') or filename.lower().endswith('.wav'):
                        target_folder = folders["Music"]
                    else:
                        target_folder = folders["Other"]
                else:
                    target_folder = folders["Other"]

                shutil.move(file_path, os.path.join(target_folder, filename))
                moved_files_count += 1
            except Exception as e:
                pass

    return moved_files_count

def sort(icon: pystray.Icon) -> None:
    if NOTIFY_ENABLE:
        SendNotify("Sorted", f"We have sorted {sort_files(DIR_DESTINATION)} files!")
    else:
        sort_files(DIR_DESTINATION)

def exit_action(icon: pystray.Icon)  -> None:
    icon.stop()
    exit(0)

def change_dir(icon: pystray.Icon)  -> None:
    global NOTIFY_ENABLE, DIR_DESTINATION
    create_settings(icon)
    with open("settings.sorty", "r") as settings_file:
        settings = json.load(settings_file)

        NOTIFY_ENABLE = settings.get("notificationsenabled", NOTIFY_ENABLE)
        DIR_DESTINATION = settings.get("download_folder", DIR_DESTINATION)

def autoswitcher()  -> int:
    global AUTO_SORT

    if AUTO_SORT:
        AUTO_SORT = False
        SendNotify("Switched", "Auto is off now!")

    else:
        AUTO_SORT = True
        SendNotify("Switched", "Auto is on now!")



def Auto() -> None:
    while True:
        if AUTO_SORT:
            prev_mtime = os.path.getmtime(DIR_DESTINATION)
            while True:
                mtime = os.path.getmtime(DIR_DESTINATION)
                if AUTO_SORT:
                    if mtime != prev_mtime:
                        sort_files(DIR_DESTINATION)
                        prev_mtime = mtime
                else:
                    break
                time.sleep(1)

def Main() -> None:

    icon = pystray.Icon("Sorty", image, menu=pystray.Menu(
        pystray.MenuItem("Sort!", sort),
        pystray.MenuItem("Сhange Directory",lambda: change_dir(icon)),
        pystray.MenuItem("Auto ON/OF", autoswitcher),
        pystray.MenuItem("Exit", lambda: exit_action(icon))
    ))
    global NOTIFY_ENABLE, DIR_DESTINATION

    if os.path.exists("settings.sorty"):
        with open("settings.sorty", "r") as settings_file:
            settings = json.load(settings_file)
            NOTIFY_ENABLE = settings.get("notificationsenabled", NOTIFY_ENABLE)
            DIR_DESTINATION = settings.get("download_folder", DIR_DESTINATION)

    else:
        create_settings(icon)



    listener_thread = threading.Thread(target=Auto)
    listener_thread.daemon = True
    listener_thread.start()



    icon.run()

if __name__ == "__main__":
    Main()
