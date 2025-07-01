import sys
import os
import pyautogui as pag
import keyboard as kb
from tkinter import messagebox
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QLineEdit

class ScreenshotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(700, 400, 300, 280)

        #キーのコンボボックスを追加
        self.combo3 = QComboBox(self)
        for s in ["Press the Insert key to take a screenshot.", "Press the Left key to take a screenshot.", "Press the Right key to take a screenshot."]:
            self.combo3.addItem(s)

        #キーのコンボボックスの位置
        self.combo3.move(0, 240)
        self.combo3.resize(300, 30)

        self.label_combo3 = QLabel(self)

        #初期設定
        self.key_config = "insert"
        kb.add_hotkey(self.key_config, lambda: self.take_screenshot())
        print("Press the Insert key to take a screenshot.")

        # スクリーンショットの解像度を変更、コンボボックス作成
        self.combo2 = QComboBox(self)
        for s in ["Entire screen", "Left:200 Top:5 Width:1520 Height:1070", "Left:580 Top:5 Width:760 Height:1070", "Enter the resolution"]:
            self.combo2.addItem(s)

        # 解像度のコンボボックス、位置
        self.combo2.move(0, 150) # X , Y
        self.combo2.resize(300, 30) # W , H

        # 拡張子コンボボックスを作成
        self.combo1 = QComboBox(self)
        for s in ["png", "jpg", "webp", "tiff"]:
            self.combo1.addItem(s)
        
        # 拡張子コンボボックス
        self.combo1.move(0, 60)
        self.combo1.resize(300, 30)

        # 拡張子のラベル
        self.label_ext = QLabel(self)
        self.label_ext.setStyleSheet('font-family: Kaiti SC; font-size: 21px; color: #f0f0f0')
        self.label_ext.move(130, 20)
        self.label_ext.resize(200, 30)

        # 解像度のラベル
        self.label_reso = QLabel(self)
        self.label_reso.setStyleSheet('font-family: Kaiti SC; font-size: 16px; color: #f0f0f0')
        self.label_reso.move(10, 120)
        self.label_reso.resize(280, 20)

        # ラベルと入力フィールドの作成
        self.label_x = QLabel('X:', self)
        self.input_x = QLineEdit(self)

        self.label_y = QLabel('Y:', self)
        self.input_y = QLineEdit(self)

        self.label_width = QLabel('Width:', self)
        self.input_width = QLineEdit(self)

        self.label_height = QLabel('Height:', self)
        self.input_height = QLineEdit(self)

        # ラベルの位置
        self.label_x.move(0, 190)
        self.label_x.resize(50, 20)

        self.label_y.move(0, 220)
        self.label_y.resize(50, 20)

        self.label_width.move(140, 190)
        self.label_width.resize(50, 20)

        self.label_height.move(140, 220)
        self.label_height.resize(50, 20)

        # 入力フィールドの位置
        self.input_x.move(20, 190)
        self.input_x.resize(110, 20)

        self.input_y.move(20, 220)
        self.input_y.resize(110, 20)

        self.input_width.move(180, 190)
        self.input_width.resize(110, 20)

        self.input_height.move(180, 220)
        self.input_height.resize(110, 20)

        #初期状態で入力フィールドを非表示にする
        self.toggle_input_fields(False)

        #プリント
        self.combo1.currentTextChanged.connect(self.print_select_ext)
        self.combo2.currentTextChanged.connect(self.print_select_reso)
        self.combo3.currentTextChanged.connect(self.print_select_SS)
        self.combo3.currentTextChanged.connect(self.update_key_config)

        #スクリーンショットのディレクトリを作成
        self.save_dir = "Screenshots"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        #カウンター.txt
        self.counter_file = os.path.join(self.save_dir, 'counter.txt')

        if os.path.exists(self.counter_file):
            with open(self.counter_file, 'r') as file:
                self.counter = int(file.read())
        else:
            self.counter = 1

    def print_select_ext(self, text):
        self.label_ext.setText(text)
        print(f"Select a {text}")

    def print_select_reso(self, text):
        self.label_reso.setText(text)
        print(f"Select a {text}")
        #"Enter the resolution" が選択されているか確認し、入力フィールドの表示/非表示を切り替える
        self.toggle_input_fields(text == "Enter the resolution")

    def print_select_SS(self, text):
        self.label_combo3.setText(text)
        print(f"Select a {text}")

    #コンボボックス3から文字列を取得
    def update_key_config(self):
        get_key = self.combo3.currentText()
        kb.remove_hotkey(self.key_config)  #以前のホットキーを削除

        if get_key == "Press the Insert key to take a screenshot.":
            self.key_config = "insert"
        elif get_key == "Press the Left key to take a screenshot.":
            self.key_config = "left"
        elif get_key == "Press the Right key to take a screenshot.":
            self.key_config = "right"

        kb.add_hotkey(self.key_config, lambda: self.take_screenshot())  #新しいホットキーを追加

    def toggle_input_fields(self, show):
        self.label_x.setVisible(show)
        self.input_x.setVisible(show)
        self.label_y.setVisible(show)
        self.input_y.setVisible(show)
        self.label_width.setVisible(show)
        self.input_width.setVisible(show)
        self.label_height.setVisible(show)
        self.input_height.setVisible(show)

    def take_screenshot(self):
        try:
            # 解像度コンボボックスと拡張子コンボボックスの選択値を取得
            resolution = self.combo2.currentText()
            extension = self.combo1.currentText()

            if resolution == str("Entire screen"):
                #画面全体のスクリーンショットを撮る
                screenshot = pag.screenshot()
                file_name = os.path.join(self.save_dir, f"{self.counter}.{extension}")
                screenshot.save(file_name)
                self.counter += 1
                with open(self.counter_file, "w") as file:
                    file.write(str(self.counter))
                print(f"Screenshot saved as {file_name}")

            elif resolution == str("Left:200 Top:5 Width:1520 Height:1070"):
                x = int(200)
                y = int(5)
                width = (1520)
                height = (1070)

                #指定された領域のスクリーンショットを撮る
                screenshot = pag.screenshot(region=(x, y, width, height))
                file_name = os.path.join(self.save_dir, f"{self.counter}.{extension}")
                screenshot.save(file_name)
                self.counter += 1
                with open(self.counter_file, "w") as file:
                    file.write(str(self.counter))
                    print(f"Screenshot saved as {file_name}")

            elif resolution == str("Left:580 Top:5 Width:760 Height:1070"):
                x = int(580)
                y = int(5)
                width = int(760)
                height = int(1070)

                #指定された領域のスクリーンショットを撮る
                screenshot = pag.screenshot(region=(x, y, width, height))
                file_name = os.path.join(self.save_dir, f"{self.counter}.{extension}")
                screenshot.save(file_name)
                self.counter += 1
                with open(self.counter_file, "w") as file:
                    file.write(str(self.counter))
                    print(f"Screenshot saved as {file_name}")
                    
            else:
                # 入力フィールドから値を取得
                x = int(self.input_x.text())
                y = int(self.input_y.text())
                width = int(self.input_width.text())
                height = int(self.input_height.text())

                #指定された領域のスクリーンショットを撮る
                screenshot = pag.screenshot(region=(x, y, width, height))
                file_name = os.path.join(self.save_dir, f"{self.counter}.{extension}")
                screenshot.save(file_name)
                self.counter += 1
                with open(self.counter_file, "w") as file:
                    file.write(str(self.counter))
                    print(f"Screenshot saved as {file_name}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers for the coordinates and dimensions.")
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotGUI()
    window.show()

    sys.exit(app.exec())
