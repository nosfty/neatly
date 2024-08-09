



import pystray, PIL.Image, PIL.ImageTk

import json
import tkinter as tk
from tkinter import filedialog
from notifypy import Notify




image = PIL.Image.open("ico.png")

enable_notifications = True

destination = ""

def create_settings():
    root = tk.Tk()
    root.withdraw()
    ico = PIL.Image.open('ico.png')
    photo = PIL.ImageTk.PhotoImage(ico)
    root.wm_iconphoto(False, photo)

    download_folder = filedialog.askdirectory(title="Please select the downloads folder.")
    if not download_folder:
        print("The folder is not selected. Exit the program.")
        return
    notifications_enabled = True
    settings = {
        "notificationsenabled": notifications_enabled,
        "download_folder": download_folder
    }
    with open("settings.sorty", "w") as settings_file:
        json.dump(settings, settings_file)


import os
import shutil
import mimetypes

def sort_files(directory):

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
                print(f"Перемещен: {filename} в {target_folder}")
                moved_files_count += 1
            except Exception as e:
                print(f"Не удалось переместить файл {filename}: {e}")

    return moved_files_count


def sort(icon, item):

    if enable_notifications:
        notification = Notify()
        notification.application_name = "Sorty!"
        notification.title = "Sorted!"
        notification.message = f"We have sorted {sort_files(destination)} files!"
        notification.icon = "ico.png"

        notification.send()

    else:
        sort_files(destination)

    print("sorted!")


def exit_action(icon:pystray.Icon):

    icon.stop()
    exit(0)


def change_settings():
    global enable_notifications, destination
    create_settings()
    with open("settings.sorty", "r") as settings_file:
        settings = json.load(settings_file)


        enable_notifications = settings.get("notificationsenabled", enable_notifications)
        destination = settings.get("download_folder", destination)

    print(destination)
    print(enable_notifications)

icon = pystray.Icon("Sorty", image, menu = pystray.Menu(
    pystray.MenuItem("Sort!", sort),
    pystray.MenuItem("Сhange Directory", change_settings),
    pystray.MenuItem("Exit", lambda : exit_action(icon))
))


if os.path.exists("settings.sorty"):
    with open("settings.sorty", "r") as settings_file:
        settings = json.load(settings_file)
        enable_notifications = settings.get("notificationsenabled", enable_notifications)
        destination = settings.get("download_folder", destination)

    print(destination)
    print(enable_notifications)
else:
    create_settings()

    print(destination)
    print(enable_notifications)

icon.run()

