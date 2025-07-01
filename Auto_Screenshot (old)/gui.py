import os
import threading
import win32gui
import win32con
import win32api
import configparser
import time
import pygetwindow as gw
import pyautogui as pag
import NoAlphabet
import log
import pillow_avif
from tkinter import messagebox
from PyQt6.QtWidgets import QWidget, QLabel, QComboBox, QGroupBox, QMainWindow, QPushButton, QScrollBar, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPalette, QColor

class Resolution_Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Resolution")
        self.setFixedSize(150, 150)
        self.setStyleSheet("font-size: 16px;")

        label_x = QLabel("X:", self)
        label_x.setGeometry(0, 0, 30, 30)

        label_y = QLabel("Y:", self)
        label_y.setGeometry(70, 0, 30, 30)

        label_width = QLabel("Width", self)
        label_width.setGeometry(0, 40, 60, 30)

        label_height = QLabel("Height", self)
        label_height.setGeometry(70, 40, 60, 30)

        self.input_x = QLineEdit(self) 
        self.input_x.setGeometry(20, 0, 50, 30)

        self.input_y = QLineEdit(self) 
        self.input_y.setGeometry(90, 0, 50, 30) 

        self.input_width = QLineEdit(self) 
        self.input_width.setGeometry(0, 70, 60, 30) 

        self.input_height = QLineEdit(self) 
        self.input_height.setGeometry(70, 70, 60, 30)

        self.ok_button = QPushButton("OK", self)
        self.ok_button.setGeometry(50, 110, 60, 30)
        self.ok_button.clicked.connect(self.write_config_reso)

    def write_config_reso(self):
        config = configparser.ConfigParser()
        config.read("config.ini")

        try:
            NoAlphabet.check_string(self.input_x.text())
            NoAlphabet.check_string(self.input_y.text())
            NoAlphabet.check_string(self.input_width.text())
            NoAlphabet.check_string(self.input_height.text())
        except NoAlphabet.NoAlphabetException as e:
            messagebox.showerror("Error", f"{e}")
        else:
            config["Custom resolution"]["x"] = self.input_x.text()
            config["Custom resolution"]["y"] = self.input_y.text()
            config["Custom resolution"]["width"] = self.input_width.text()
            config["Custom resolution"]["height"] = self.input_height.text()

            with open("config.ini", "w", encoding="utf-8") as configfile:
                config.write(configfile)

            self.close()

class Signals(QObject):
    update_label_info_run_signal = pyqtSignal(str)
    update_label_info_reso_signal = pyqtSignal(str)
    update_label_info_current_signal = pyqtSignal(int)
    update_label_before_time_signal = pyqtSignal(int)
    update_label_waiting_time_signal = pyqtSignal(  int)
    update_label_counter_signal = pyqtSignal(int)

class Maingui(QMainWindow):
    def __init__(self):
        super().__init__()

        #スクリーンショットのディレクトリを作成
        self.save_dir = "Screenshots"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        self.reso_w = Resolution_Window()
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        self.signals = Signals()
        self.signals.update_label_info_run_signal.connect(self.update_label_info_run)
        self.signals.update_label_info_current_signal.connect(self.update_label_info_current)
        self.signals.update_label_before_time_signal.connect(self.update_label_before_time)
        self.signals.update_label_waiting_time_signal.connect(self.update_label_waiting_time)
        self.signals.update_label_counter_signal.connect(self.update_label_counter)
        self.signals.update_label_info_reso_signal.connect(self.update_label_info_reso)

        #ウィンドウ
        self.setFixedSize(250, 650)
        self.setStyleSheet('font-size: 14px; color: #f0f0f0')
        self.setWindowTitle("Screenshot")

        #メインウィンドウのウィジェットを設定
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        #ComboBox(Window)のラベル
        label_window_ComboBox = QLabel("Select a window name", self)
        label_window_ComboBox.setGeometry(0, 0, 220, 30)

        #ウィンドウのコンボボックス
        self.window_ComboBox = QComboBox(central_widget)
        self.window_ComboBox.addItems(self.get_windows())
        self.window_ComboBox.setGeometry(0, 30, 250, 30)

        #拡張子のラベル
        label_ext_1 = QLabel("Select extension", self)
        label_ext_1.setGeometry(0, 50, 100, 30)

        #拡張子コンボボックスを作成
        self.ext_ComboBox = QComboBox(central_widget)
        for s in ["png", "jpg", "avif", "webp"]:
            self.ext_ComboBox.addItem(s)
        
        self.ext_ComboBox.setGeometry(0, 80, 250, 30)

        #解像度のラベル
        label_reso_1 = QLabel("Select resolution", self)
        label_reso_1.setGeometry(0, 105, 150, 30)

        #解像度のコンボボックス
        self.reso_ComboBox = QComboBox(central_widget)
        for s in ["Entire screen", "Left:200 Top:5 Width:1520 Height:1070", "Left:580 Top:5 Width:760 Height:1070", "Enter the resolution"]:
            self.reso_ComboBox.addItem(s)

        self.reso_ComboBox.setGeometry(0, 135, 250, 30)
        self.reso_ComboBox.setStyleSheet("font-size: 13px;")

        #キーコンボボックスのラベル
        label_key_ComboBox = QLabel("Select key", self)
        label_key_ComboBox.setGeometry(0, 160, 100, 30)

        #キーのコンボボックス
        self.key_ComboBox = QComboBox(central_widget)
        for s in ["up", "right", "left", "down"]:
            self.key_ComboBox.addItem(s)

        self.key_ComboBox.setGeometry(0, 190, 250, 30)

        #リピートのラベル
        label_repeat = QLabel('Repeat count', self)
        label_repeat.setGeometry(0, 220, 190, 20)

        #リピート
        self.repeat_QScrollBar = QScrollBar(central_widget)
        self.repeat_QScrollBar.setStyleSheet('background-color: #1e1e1e')
        self.repeat_QScrollBar.setOrientation(Qt.Orientation.Horizontal) #横にする
        self.repeat_QScrollBar.setRange(1, 999)
        self.repeat_QScrollBar.setValue(1)
        self.repeat_QScrollBar.setGeometry(0, 245, 250, 20)

        #画質のラベル
        label_quality = QLabel("Quality", self)
        label_quality.setGeometry(0, 265, 190, 20)

        #画質のクオリティースクロールバー
        self.quality_QscrollBar = QScrollBar(central_widget)
        self.quality_QscrollBar.setStyleSheet('background-color: #1e1e1e')
        self.quality_QscrollBar.setOrientation(Qt.Orientation.Horizontal) #横にする
        self.quality_QscrollBar.setRange(1, 100)
        self.quality_QscrollBar.setValue(50)
        self.quality_QscrollBar.setGeometry(0, 290, 250, 20)

        #圧縮のコンボボックスのラベル
        label_comp = QLabel("Compression", self)
        label_comp.setGeometry(0, 310, 190, 20)

        #圧縮のコンボボックス
        self.ComboBox_comp = QComboBox(central_widget)
        for s in ["Lossless", "Lossy"]:
            self.ComboBox_comp.addItem(s)

        self.ComboBox_comp.setGeometry(0, 330, 250, 30)

        #スタートボタン
        start_button = QPushButton("Start", self)
        start_button.setGeometry(80, 365, 80, 30)
        start_button.clicked.connect(self.start_button)

        #リセットボタン
        stop_button = QPushButton("Stop", self)
        stop_button.setGeometry(0, 365, 80, 30)
        stop_button.clicked.connect(self.stop_button)

        #ウィンドウを更新ボタン
        update_button = QPushButton("Update", self)
        update_button.setGeometry(160, 365, 80, 30)
        update_button.clicked.connect(self.update)

        #Screenshotウィンドウを前面にだすコンボボックス
        self.fore_ss_window_combo = QComboBox(self)
        for s in ["Fore ss window", "None"]:
            self.fore_ss_window_combo.addItem(s)

        self.fore_ss_window_combo.setGeometry(150, 480, 100, 30)
        self.fore_ss_window_combo.setStyleSheet("font-size: 11px;")

        #カウンターのボタン
        counter_button = QPushButton("Counter init", self)
        counter_button.setStyleSheet("font-size: 11px;")
        counter_button.setGeometry(150, 450, 100, 30)
        counter_button.clicked.connect(self.counter_init)

        #グループボックス（Info）
        group_box_info = QGroupBox("Information", central_widget)
        group_box_info.setGeometry(0, 390, 250, 130)

        #infoのウィンドウの名前
        label_info_window = QLabel("Window name:", self)
        label_info_window.setGeometry(3, 405, 100, 20)

        self.label_info_window_r = QLabel(self)
        self.label_info_window_r.setStyleSheet("color: #fd0003")
        self.label_info_window_r.setGeometry(100, 405, 200, 20)

        #infoの拡張子
        label_info_ext = QLabel("Select extension:", self)
        label_info_ext.setGeometry(3, 420, 110, 20)

        self.label_ext_r = QLabel("png", self)
        self.label_ext_r.setStyleSheet("color: #fd0003")
        self.label_ext_r.setGeometry(110, 420, 100, 20)

        #解像度の表示
        label_info_reso = QLabel("Select resolution:", self)
        label_info_reso.setGeometry(3, 435, 110, 20)

        self.label_info_reso_r = QLabel("Entire screen", self)
        self.label_info_reso_r.setStyleSheet("color: #fd0003")
        self.label_info_reso_r.setGeometry(110, 435, 200, 20)

        #キーを選択
        label_info_key = QLabel("Select key:", self)
        label_info_key.setGeometry(3, 450, 110, 20)

        self.label_info_key_r = QLabel("up", self)
        self.label_info_key_r.setStyleSheet("color: #fd0003")
        self.label_info_key_r.setGeometry(70, 450, 110, 20)

        #リピートカウント
        label_info_count = QLabel("Repeat count:", self)
        label_info_count.setGeometry(3, 465, 110, 20)

        self.label_info_count_r = QLabel("1", self)
        self.label_info_count_r.setStyleSheet("color: #fd0003")
        self.label_info_count_r.setGeometry(90, 465, 110, 20)

        #クオリティーのinfoラベル
        label_info_quality = QLabel("Quality:", self)
        label_info_quality.setGeometry(3, 480, 110, 20)

        #クオリティーのラベル
        self.label_info_quality_r = QLabel("50", self)
        self.label_info_quality_r.setStyleSheet("color: #fd0003")
        self.label_info_quality_r.setGeometry(55, 480, 110, 20)

        #圧縮のinfoラベル
        label_info_comp = QLabel("Compression:", self)
        label_info_comp.setGeometry(3, 495, 110, 20)

        #圧縮方式のラベル
        self.label_info_comp_r = QLabel("Lossless", self)
        self.label_info_comp_r.setStyleSheet("color: #fd0003")
        self.label_info_comp_r.setGeometry(90, 495, 110, 20)

        #グループボックスWorking info
        group_box_working_info = QGroupBox("Working info", central_widget)
        group_box_working_info.setGeometry(0, 520, 250, 130)

        #動いてるか
        self.label_work_info_run = QLabel("Not a running", self)
        self.label_work_info_run.setStyleSheet("color: #fd0003")
        self.label_work_info_run.setGeometry(3, 530, 110, 30)

        #Current count
        label_work_info_current = QLabel("Current count:", self)
        label_work_info_current.setGeometry(3, 545, 100, 30)

        self.label_work_info_current_r = QLabel("0", self)
        self.label_work_info_current_r.setStyleSheet("color: #fd0003")
        self.label_work_info_current_r.setGeometry(95, 545, 100, 30)

        #witing timeのラベル    
        label_work_waitng_time = QLabel("Waiting time:", self)
        label_work_waitng_time.setGeometry(3, 565, 100, 30)

        #開始までの時間
        label_work_before_time = QLabel("Before the start:", self)
        label_work_before_time.setGeometry(3, 585, 100, 30)

        #カウンターのラベル
        label_counter = QLabel("Counter:", self)
        label_counter.setGeometry(3, 605, 100, 30)

        #ラベルを表示
        if os.path.exists("config.ini"):
            config = configparser.ConfigParser()
            config.read("config.ini", encoding='utf-8')
            s1 = config["Config"]["waiting_time"]
            s2 = config["Config"]["before_the_start"]
            s3 = config["Config"]["counter"]

            self.label_work_waitng_time_r = QLabel(str(s1), self)
            self.label_work_waitng_time_r.setStyleSheet("color: #fd0003")
            self.label_work_waitng_time_r.setGeometry(90, 565, 100, 30)

            self.label_work_before_time_r = QLabel(str(s2), self)
            self.label_work_before_time_r.setStyleSheet("color: #fd0003")
            self.label_work_before_time_r.setGeometry(105, 585, 100, 30)

            self.label_counter_r = QLabel(str(s3), self)
            self.label_counter_r.setStyleSheet("color: #fd0003")
            self.label_counter_r.setGeometry(60, 605, 100, 30)
        else:
            self.destroy()

        #コンフィグの作成
        if not os.path.exists("config.ini"):
            config = configparser.ConfigParser()
            config["Config"] = {
            "waiting_time": "3",
            "before_the_start": "10",
            "counter": "1"
            }
            config["Custom resolution"] = {
                "x": "0",
                "y": "0",
                "width": "0",
                "height": "0"
            }
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)

            config.read("config.ini", encoding='utf-8')
            s1 = config["Config"]["waiting_time"]
            s2 = config["Config"]["before_the_start"]
            s3 = config["Config"]["counter"]

            self.label_work_waitng_time_r = QLabel(str(s1), self)
            self.label_work_waitng_time_r.setStyleSheet("color: #fd0003")
            self.label_work_waitng_time_r.setGeometry(90, 565, 100, 30)

            self.label_work_before_time_r = QLabel(str(s2), self)
            self.label_work_before_time_r.setStyleSheet("color: #fd0003")
            self.label_work_before_time_r.setGeometry(105, 585, 100, 30)

            self.label_counter_r = QLabel(str(s3), self)
            self.label_counter_r.setStyleSheet("color: #fd0003")
            self.label_counter_r.setGeometry(60, 605, 100, 30)

        #guiに表示
        self.window_ComboBox.currentTextChanged.connect(self.get_combobox_window)
        self.ext_ComboBox.currentTextChanged.connect(self.get_combobox_ext)
        self.reso_ComboBox.currentTextChanged.connect(self.get_combobox_reso)
        self.key_ComboBox.currentTextChanged.connect(self.get_combobox_key)
        self.repeat_QScrollBar.valueChanged.connect(self.get_scroll_count)
        self.quality_QscrollBar.valueChanged.connect(self.get_scroll_quality)
        self.ComboBox_comp.currentTextChanged.connect(self.get_combobox_comp)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Base, QColor(47, 47, 47))

        self.setPalette(palette)
        self.ComboBox_comp.setPalette(palette)
        self.window_ComboBox.setPalette(palette)
        self.ext_ComboBox.setPalette(palette)
        self.reso_ComboBox.setPalette(palette)
        self.key_ComboBox.setPalette(palette)
        self.quality_QscrollBar.setPalette(palette)

    #カウンターを初期化
    def counter_init(self):
        if os.path.exists("config.ini"):
            config = configparser.ConfigParser()
            config.read("Config.ini")
            config["Config"]["counter"] = str(1)

            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)

            self.update()

    #update
    def update(self):
        self.window_ComboBox.clear()
        self.window_ComboBox.addItems(self.get_windows())

        if os.path.exists("config.ini"):
            config = configparser.ConfigParser()
            config.read("config.ini", encoding='utf-8')
            s1 = config["Config"]["waiting_time"]
            s2 = config["Config"]["before_the_start"]
            s3 = config["Config"]["counter"]

            i2 = int(s2)
            i1 = int(s1)
            i3 = int(s3)

            self.signals.update_label_info_run_signal.emit("Not a running")
            self.signals.update_label_before_time_signal.emit(i2)
            self.signals.update_label_waiting_time_signal.emit(i1)
            self.signals.update_label_counter_signal.emit(i3)
            self.signals.update_label_info_current_signal.emit(0)
        else:
            self.destroy()

    def start_button(self):
        self.stop_event.clear()
        self.repeat_thread = threading.Thread(target=self.repeat_action)
        self.repeat_thread.start()

    def stop_button(self):
        if self.repeat_thread.is_alive():
            self.stop_event.set()

    #コンボボックスのウィンドウを取得
    def get_combobox_window(self, text):
        self.label_info_window_r.setText(text)

    #コンボボックスの拡張子を取得
    def get_combobox_ext(self, text):
        self.label_ext_r.setText(text)

    #解像度のコンボボックスを取得
    def get_combobox_reso(self, text):
        self.label_info_reso_r.setText(text)
        if text == "Enter the resolution":
            self.resolution_window = Resolution_Window()
            self.resolution_window.show()

    #キーのコンボボックスを取得
    def get_combobox_key(self, text):
        self.label_info_key_r.setText(text)

    #スクロールバーを取得
    def get_scroll_count(self, count):
        self.label_info_count_r.setText(str(count))

    #クオリティーのスクロールバーを取得
    def get_scroll_quality(self, count):
        self.label_info_quality_r.setText(str(count))

    #圧縮のコンボボックスを取得
    def get_combobox_comp(self, text):
        self.label_info_comp_r.setText(text)

    #Window名を取得
    def get_windows(self):
        windows = gw.getAllTitles()
        return [window for window in windows if window]
    
    #Foreコンボボックスを取得
    def fore_window(self):
        window_name = self.fore_ss_window_combo.currentText()

        if window_name == str("Fore ss window"):
            self.hwnd_ss = win32gui.FindWindow(None,"Screenshot")
            win32gui.SetWindowPos(self.hwnd_ss, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)

    #解像度の値のラベル
    def update_label_info_reso(self, text):
        painter = QPainter(self.label_info_reso_r)
        self.label_info_reso_r.setText(str(text))
        self.label_info_reso_r.repaint()
        painter.end()

    #カウンターのアップデート
    def update_label_counter(self, value):
        painter = QPainter(self.label_counter_r)
        self.label_counter_r.setText(str(value))
        self.label_counter_r.repaint()
        painter.end()

    #ウェイトタイムのアップデート
    def update_label_waiting_time(self, value):
        painter = QPainter(self.label_work_waitng_time_r)
        self.label_work_waitng_time_r.setText(str(value))
        self.label_work_waitng_time_r.repaint()
        painter.end()

    #開始までのカウントをアップデート
    def update_label_before_time(self, value):
        painter = QPainter(self.label_work_before_time_r)
        self.label_work_before_time_r.setText(str(value))
        self.label_work_before_time_r.repaint()
        painter.end()

    #現在の回数のラベルをアップデート
    def update_label_info_current(self, value):
        painter = QPainter(self.label_work_info_current_r)
        self.label_work_info_current_r.setText(str(value))
        self.label_work_info_current_r.repaint()
        painter.end()

    #Runningのラベルをアップデート
    def update_label_info_run(self, text):
        painter = QPainter(self.label_work_info_run)
        self.label_work_info_run.setText(str(text))
        self.label_work_info_run.repaint()
        painter.end()

    def take_screenshot(self):      
        try:
            resolution = self.reso_ComboBox.currentText()
            extension = self.ext_ComboBox.currentText()
            qua = self.quality_QscrollBar.value()

            #圧縮と拡張子
            extension = self.ext_ComboBox.currentText()
            comp_s = self.ComboBox_comp.currentText()

            if comp_s == str("Lossless"):
                comp = bool(True)
            else:
                comp_s == str("Lossy")
                comp = bool(False)

            if extension == str("png"):
                ext_format = str("PNG")
            elif extension == str("jpg"):
                ext_format = str("JPG")
            elif extension == str("avif"):
                ext_format = str("AVIF")
            else:
                ext_format = str("WEBP")

            config = configparser.ConfigParser()

            if resolution == str("Entire screen"):

                config.read("config.ini")
                counter_s = config["Config"]["counter"]

                log.logger.info(f"Screenshot{counter_s}")

                counter = int(counter_s)

                screenshot = pag.screenshot()
                file_name = os.path.join(self.save_dir, f"{counter}.{extension}")
                screenshot.save(file_name, format=ext_format, quality=qua, lossless=comp)

                counter += int(1)
                counter_s = str(counter)
                config["Config"]["counter"] = counter_s

                with open("config.ini", "w") as configfile:
                    config.write(configfile)
            elif resolution == str("Left:200 Top:5 Width:1520 Height:1070"):
                x = int(200)
                y = int(5)
                width = int(1520)
                height = int(1070)

                config.read("config.ini")
                counter_s = config["Config"]["counter"]
                counter = int(counter_s)

                log.logger.info(f"Screenshot_{counter_s}")

                screenshot = pag.screenshot(region=(x, y, width, height))
                file_name = os.path.join(self.save_dir, f"{counter}.{extension}")
                screenshot.save(file_name, format=ext_format, quality=qua, lossless=comp)

                counter += int(1)
                counter_s = str(counter)
                config["Config"]["counter"] = counter_s
                with open("config.ini", "w") as configfile:
                    config.write(configfile)
            elif resolution == str("Left:580 Top:5 Width:760 Height:1070"):
                x = int(580)
                y = int(5)
                width = int(760)
                height = int(1070)

                config.read("config.ini")
                counter_s = config["Config"]["counter"]
                counter = int(counter_s)

                log.logger.info(f"Screenshot_{counter_s}")

                screenshot = pag.screenshot(region=(x, y, width, height))
                file_name = os.path.join(self.save_dir, f"{counter}.{extension}")
                screenshot.save(file_name, format=ext_format, quality=qua, lossless=comp)

                counter += int(1)
                counter_s = str(counter)
                config["Config"]["counter"] = counter_s
                with open("config.ini", "w") as configfile:
                    config.write(configfile)
            else:
                x = int(self.reso_w.input_x.text())
                y = int(self.reso_w.input_y.text())
                width = int(self.reso_w.input_width.text())
                height = int(self.reso_w.input_height.text())

                config.read("config.ini")
                counter_s = config["Config"]["counter"]
                counter = int(counter_s)

                log.logger.info(f"Screenshot_{counter_s}")

                screenshot = pag.screenshot(region=(x, y, width, height))
                file_name = os.path.join(self.save_dir, f"{counter}.{extension}")
                screenshot.save(file_name, format=ext_format, quality=qua, lossless=comp)

                counter += int(1)
                counter_s = str(counter)
                config["Config"]["counter"] = counter_s
                with open("config.ini", "w") as configfile:
                    config.write(configfile)
        except ValueError as e:
            log.logger.error(f"{e}")
            messagebox.showerror("Error", f"{e}")
            self.stop_button()

    def repeat_action(self):
        try:
            with self.lock:
                repeat_count = self.repeat_QScrollBar.value()
                window_name = self.window_ComboBox.currentText()
                key = self.key_ComboBox.currentText()

                log.logger.info(f"Screenshot ready. Window name: {window_name}")

                config = configparser.ConfigParser()
                config.read("config.ini", encoding='utf-8')

                before_start_s = config["Config"]["Before_the_start"]
                waiting_time_s = config["Config"]["Waiting_time"]

                waiting_time = int(waiting_time_s)
                before_start = int(before_start_s)

                hwnd = win32gui.FindWindow(None, window_name)

                while before_start > 0 and not self.stop_event.is_set():
                    self.signals.update_label_info_run_signal.emit("Running!!")
                    self.signals.update_label_before_time_signal.emit(before_start)
                    win32api.Beep(900, 900)
                    time.sleep(1)
                    before_start -= 1
                self.signals.update_label_before_time_signal.emit(before_start)
                self.fore_window()
                win32gui.SetForegroundWindow(hwnd) #ウィンドウを前面に出す
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW) #ウィンドウをアクティブ化
                win32api.Beep(900, 900)
                log.logger.info(f"Screenshot start. Window name: {window_name}")
                time.sleep(1)
                while repeat_count > 0 and not self.stop_event.is_set():
                    self.signals.update_label_info_run_signal.emit("Running!!")
                    self.signals.update_label_info_current_signal.emit(repeat_count)
                    self.take_screenshot()
                    time.sleep(waiting_time)
                    pag.press(key)
                    win32api.Beep(900, 900)
                    repeat_count -= 1
                self.signals.update_label_info_run_signal.emit("Not a running")
                config.read("config.ini", encoding='utf-8')
                s1 = config["Config"]["waiting_time"]
                s2 = config["Config"]["before_the_start"]
                s3 = config["Config"]["counter"]

                i2 = int(s2)
                i1 = int(s1)
                i3 = int(s3)

                self.signals.update_label_info_run_signal.emit("Not a running")
                self.signals.update_label_before_time_signal.emit(i2)
                self.signals.update_label_waiting_time_signal.emit(i1)
                self.signals.update_label_counter_signal.emit(i3)
                self.signals.update_label_info_current_signal.emit(repeat_count)
                win32gui.SetWindowPos(self.hwnd_ss, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)
                log.logger.info("Screenshot done")
                messagebox.showinfo("Info", "Done")
        except pag.FailSafeException or SystemError:
            log.logger.error("Screenshot stoped")
            messagebox.showerror("Error", "Error")
            self.stop_button()