import os
import sys
import win32gui
import win32con
import win32api
import configparser
import threading
import time
import pyautogui as pag
import pillow_avif
import ctypes
from ctypes import wintypes
from tkinter import messagebox
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QApplication

# version 0.2

"""
(History)
2024年 12月 15日、プログラミング練習のためコーディング。
2025年 6月 16日、プログラミング練習のため改良。
"""

print("\nSupports FHD (1920 x 1080) only\nMulti monitor not supported\n")

user32 = ctypes.windll.user32

EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

GetWindowTextLength = user32.GetWindowTextLengthW
GetWindowText = user32.GetWindowTextW
IsWindowVisible = user32.IsWindowVisible

config = configparser.ConfigParser()

if not os.path.exists("config.ini"):
    config["config"] = {
        "once_done_reset_the_counter": "true",
        "waiting_time": "3",
        "before_the_start": "10",
        "counter": "1"
    }
    config["custom resolution"] = {
        "x": "0",
        "y": "0",
        "width": "0",
        "height": "0"
    }
    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)
    config.read("config.ini", encoding="utf-8")
else:
    config.read("config.ini", encoding="utf-8")

save_dir = "Screenshots"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

class repeat_ss(QMainWindow):
    def __init__(self, hwnd_window: list, ext: str, reso: str, key: str, repeat: int, quality: int, com: str, fore: str, x: int, y: int):
        super().__init__()

        self.hwnd_window = hwnd_window
        self.ext = ext
        self.reso = reso
        self.key = key
        self.repeat = repeat
        self.quality = quality
        self.com = com
        self.fore = fore
        self.x_ = x
        self.y_ = y

        self.UI()

        self.counter = int(config["config"]["counter"])

        self.stop_event = threading.Event()
        self.stop_event.clear()

        self.repeat_thread = threading.Thread(target=self.repeat_action, name="repeat_action")
        self.repeat_thread.start()
        self.stop_thread = threading.Thread(target=self.stop, name="stop")
        self.stop_thread.start()

    def stop(self):
        while not self.stop_event.is_set():
            choice = input("\n-s to end\n")
            if choice == str("-s"):
                self.stop_button()

    def stop_button(self):
        self.stop_event.set()
        time.sleep(2)
        sys.exit()

    def UI(self):
        self.setWindowTitle("Info_screenshot")
        self.setFixedSize(150, 150)
        self.setStyleSheet("font-size: 16px;")

        label_run = QLabel("Running!!", self)
        label_run.setGeometry(0, 0, 90, 30)
        label_run.setStyleSheet("color: #fd0003")

        label_current = QLabel("Current count:", self)
        label_current.setGeometry(0, 20, 180, 30)

        self.label_count = QLabel("0", self)
        self.label_count.setGeometry(110, 20, 90, 30)
        self.label_count.setStyleSheet("color: #fd0003")

        label_waiting = QLabel("Waiting time:", self)
        label_waiting.setGeometry(0, 40, 180, 30)

        self.label_wait_time = QLabel("0", self)
        self.label_wait_time.setGeometry(110, 40, 100, 30)
        self.label_wait_time.setStyleSheet("color: #fd0003")

        label_before = QLabel("Before the start:", self)
        label_before.setGeometry(0, 60, 180, 30)

        self.label_before_s = QLabel("0", self)
        self.label_before_s.setGeometry(110, 60, 180, 30)
        self.label_before_s.setStyleSheet("color: #fd0003")

        label_counter = QLabel("Counter", self)
        label_counter.setGeometry(0, 80, 180, 30)

        self.label_counter_ = QLabel("0", self)
        self.label_counter_.setGeometry(110, 80, 180, 30)
        self.label_counter_.setStyleSheet("color: #fd0003")

        button = QPushButton("Stop", self)
        button.setGeometry(20, 110, 110, 30)

        button.clicked.connect(self.stop_button)

    def take_screenshot(self, x: int, y: int, w: int, h: int):

        screenshot = pag.screenshot(region=(x, y, w, h))
        file_name = os.path.join(save_dir, f"{self.counter}.{self.ext}")
        screenshot.save(file_name, format=self.ext, quality=self.quality, lossless=self.com)

        self.counter += int(1)

    def repeat_action(self):
        time.sleep(4)
        if self.reso == str("Entire_screen"):
            x = int(0)
            y = int(0)
            width = int(1920)
            height = int(1080)
        elif self.reso == str("Left:200 Top:5 Width:1520 Height:1070"):
            x = int(200)
            y = int(5)
            width = int(1520)
            height = int(1070)
        elif self.reso == str("Left:580 Top:5 Width:760 Height:1070"):
            x = int(580)
            y = int(5)
            width = int(760)
            height = int(1070)
        elif self.reso == str("Custom resolution"):
            x = int(config["custom resolution"]["x"])
            y = int(config["custom resolution"]["y"])
            width = int(config["custom resolution"]["width"])
            height = int(config["custom resolution"]["height"])

        before_start = int(config["config"]["before_the_start"])
        waiting_time = int(config["config"]["waiting_time"])

        self.label_wait_time.setText(str(waiting_time))
        self.label_counter_.setText(str(self.counter))

        hwnd = self.hwnd_window[0]

        if win32gui.FindWindow(None, "Info_screenshot"):
            hwnd_ss = win32gui.FindWindow(None, "Info_screenshot")
            win32gui.SetWindowPos(hwnd_ss, win32con.HWND_TOPMOST, self.x_, self.y_, 0, 0, win32con.SWP_NOSIZE)
        else:
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)

        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        try:
            while before_start > 0 and not self.stop_event.is_set():
                self.label_before_s.setText(str(before_start))
                win32api.Beep(900, 900)
                time.sleep(1)
                before_start -= 1
            self.label_before_s.setText(str(before_start))
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            while self.repeat > 0 and not self.stop_event.is_set():
                self.label_count.setText(str(self.repeat))
                self.take_screenshot(x, y, width, height)
                self.label_counter_.setText(str(self.counter))
                pag.press(keys=self.key, interval=waiting_time)
                win32api.Beep(900, 900)
                self.repeat -= 1
            if win32gui.FindWindow(None, "Info_screenshot"):
                win32gui.SetWindowPos(hwnd_ss, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)
            else:
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)

            reset_counter = str(config["config"]["once_done_reset_the_counter"])

            if not reset_counter == str("true"):
                config["config"]["counter"] = str(self.counter)
                with open("config.ini", "w", encoding="utf-8") as configfile:
                    config.write(configfile)
            else:
                config["config"]["counter"] = str("1")
            messagebox.showinfo("Done!!", "Done!!")
            sys.exit()
        except pag.FailSafeException or Exception:
            messagebox.showerror("Error", "Error")

window_titles = []

def foreach_window(hwnd, lParam):
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        window_title = buff.value
        if window_title:
            window_titles.append((hwnd, window_title))
    return True

def update(titles: list):
    if titles:
        titles.clear()
    EnumWindows(EnumWindowsProc(foreach_window), 0)

def main():
    update(window_titles)
    for i, (hwnd, title) in enumerate(window_titles, start=1):
        print(f"{i}. HWND: {hwnd}, title: {title}")
    choice = int(input("\nEnter the window name. (0 to update the window)\n"))

    while choice == int(0):
        update(window_titles)
        for i, (hwnd, title) in enumerate(window_titles, start=1):
            print(f"{i}. HWND: {hwnd}, title: {title}")
        choice = int(input("\nEnter the window name. (0 to update the window)\n"))
        if not choice == int(0):
            break

    hwnd_window = list(window_titles[choice -1])

    ext_lists = ["png", "jpg", "avif", "webp"]

    for i, s in enumerate(ext_lists, start=1):
        print(f"{i}. {s}")

    choice = int(input("\nEnter the extension.\n"))
    ext = ext_lists[choice -1]

    reso_lists = ["Entire_screen", "Left:200 Top:5 Width:1520 Height:1070", "Left:580 Top:5 Width:760 Height:1070", "Custom resolution"]

    for i, s in enumerate(reso_lists, start=1):
        print(f"{i}. {s}")

    choice = int(input("\nSelect a resolution.\n"))
    reso = reso_lists[choice -1]

    key_lists = ["up", "right", "left", "down"]
    for i, s in enumerate(key_lists, start=1):
        print(f"{i}. {s}")

    choice = int(input("\nSelect a key.\n"))
    key = key_lists[choice -1]

    repeat = int(input("\nRepeat count.\n"))

    quality = int(input("\nScreenshot quality. (1 ~ 100)\n"))

    com_lists = ["Lossless", "Lossy"]
    for i, s in enumerate(com_lists, start=1):
        print(f"{i}. {s}")

    choice = int(input("\nCompression.\n"))
    com = com_lists[choice -1]

    fore_lists = ["Disable", "Left end", "Right end"]
    for i, s in enumerate(fore_lists, start=1):
        print(f"{i}. {s}")

    choice = int(input("\nFore information window\n"))
    fore = fore_lists[choice -1]

    if hwnd_window and ext and reso and key and repeat and quality and com and fore:
        print(f"Select a window: {hwnd_window}\nSelect a extension: {ext}\nSelect a resolution: {reso}\nSelect a key: {key}\nRepeat count: {repeat}\nQuality: {quality}\nCompression: {com}\nFore information window: {fore}\n")
    else:
        print("Not enough arguments")
        sys.exit()

    kakunin = ["Start", "Try again"]
    for i, s in enumerate(kakunin, start=1):
        print(f"{i}. {s}")

    choice = int(input("\nStart?\n"))
    k = kakunin[choice -1]

    if k == str("Try again"):
        sys.exit()

    return hwnd_window, ext, reso, key, repeat, quality, com, fore

hwnd_window, ext, reso, key, repeat, quality, com, fore = main()

if not fore == str("Disable"):
    if fore == str("Left end"):
        x = int(0)
        y = int(0)
        app = QApplication(sys.argv)
        window = repeat_ss(hwnd_window, ext, reso, key, repeat, quality, com, fore, x, y)
        window.show()
        app.exec()
    elif fore == str("Right end"):
        x = int(1800)
        y = int(0)
        app = QApplication(sys.argv)
        window = repeat_ss(hwnd_window, ext, reso, key, repeat, quality, com, fore, x, y)
        window.show()
        app.exec()
else:
    x = int(0)
    y = int(0)
    app = QApplication(sys.argv)
    repeat_ss(hwnd_window, ext, reso, key, repeat, quality, com, fore, x, y)
    app.exec()
