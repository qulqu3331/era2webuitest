import os
import tkinter as tk
from PIL import Image, ImageTk
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from tkinter import filedialog
from tkinter import simpledialog
import configparser
import sys


class FileMonitor(FileSystemEventHandler):
    #"""フォルダの監視クラス"""

    def __init__(self, folder_path, canvas,sub_win,scaling):
        super().__init__()
        self.folder_path = folder_path
        self.canvas = canvas
        self.sub_win = sub_win
        self.scaling = scaling

    def on_created(self, event):
        #"""ファイルが作成された時に呼び出される関数"""
        if not event.is_directory:
            if event.src_path.endswith('.png'):
                print("png検知")
                self.update_canvas(event.src_path)

    def update_canvas(self, image_path):
        #"""キャンバスの画像を更新する関数"""
        print("png")
        image = Image.open(image_path)
        size = (round(image.width * self.scaling), round(image.height * self.scaling))
        self.sub_win.geometry(str(round(image.width * self.scaling))+"x"+str(round(image.height * self.scaling)))
        image = image.resize(size)
        photo = ImageTk.PhotoImage(image)
        self.canvas.image = photo
        self.canvas.create_image(0, 0, anchor='nw', image=photo)
        # ウィンドウを前面に持ってくる
        self.sub_win.attributes("-topmost", True)
        self.sub_win.attributes("-topmost", False)



class App:
    #"""アプリケーションクラス"""

    def __init__(self):

        # メインウィンドウ
        self.root = tk.Tk()
        self.root.title('画像表示の設定')
        self.root.geometry('500x80')

        # iniファイル読み込み
        self.config = configparser.ConfigParser()
        self.inipath = os.path.dirname(__file__) + "\config.ini"
        self.config.read(self.inipath, 'UTF-8')
        # 監視フォルダ
        self.wdog_sdimg_Path = self.config.get("Paths", "image", fallback="")
        # 表示倍率
        self.scaling =  float(self.config.get("Viewer", "画像表示の拡大率", fallback=""))

        #上部フレーム
        frame_top = tk.Frame(self.root, pady=5, padx=5, relief=tk.RAISED, bd=2)
        tk.Label(self.root, text="画像生成フォルダ:").pack(side = tk.LEFT)
        tk.Button(self.root, text="参照", command=self.change_folder).pack(side = tk.LEFT)
        self.label_sdimg = tk.Label(self.root, text=f"{self.wdog_sdimg_Path}")
        self.label_sdimg.pack(side = tk.LEFT)
        frame_top.pack(fill=tk.X)

        tk.Button(self.root, text="表示倍率を変更", command=self.change_scaling).pack(side = tk.TOP)


        # iniで指定したフォルダが存在しないときはダイアログで選択させる
        if os.path.isdir(self.wdog_sdimg_Path) == False:
            print(tk.messagebox.showinfo(title="画像フォルダ不明", message=f"次は画像が生成されるフォルダを選択して下さい。選択フォルダの子フォルダも監視対象になります。"))
            self.select_folder_of_img()
        


        # サブウィンドウ
        self.sub_win = tk.Toplevel()
        self.sub_win.title('image')
        self.sub_win.geometry("250x100")

        # サブウィンドウを消すと親ウィンドウを道連れにする
        self.sub_win.wm_protocol('WM_DELETE_WINDOW', self.close_window)
        # サブウィンドウを常に前面に表示する
        #self.sub_win.attributes("-topmost", True)

        # キャンバス
        self.canvas = tk.Canvas(self.sub_win)
        self.canvas.pack(expand = True,fill=tk.BOTH)

        # 変数の初期化
        self.event_handler = FileMonitor(self.wdog_sdimg_Path,self.canvas,self.sub_win,self.scaling)
        self.observer_img = PollingObserver()

        self.observer_img.schedule(self.event_handler, self.wdog_sdimg_Path, recursive=True)
        self.observer_img.start()
        print("pngファイルの監視を開始しました。target_dir:" + str(self.wdog_sdimg_Path))

    def stop(self):
        #"""アプリケーションの停止関数"""
        if self.is_running:
            # 監視スレッドの停止
            self.observer_img.stop()
            self.observer_img.join()


    # フォルダ選択ダイアログの表示(画像監視フォルダ)
    def select_folder_of_img(self):
        folder_path = filedialog.askdirectory(title = "画像フォルダを選択(親フォルダでも可)",initialdir = self.wdog_sdimg_Path)
        if folder_path:
            self.wdog_sdimg_Path = folder_path
            print(f"Selected folder: {self.wdog_sdimg_Path}")
            # iniに記入
            self.config.set("Paths", "image", self.wdog_sdimg_Path)
            with open(self.inipath, "w", encoding='UTF-8') as configfile:
                self.config.write(configfile)
            # ラベル更新
            self.label_sdimg["text"] = self.wdog_sdimg_Path

    # select_folder_of_imgを呼び出した後、watchdogに変更を反映する
    def change_folder(self):
        self.select_folder_of_img()
        self.restartwatchdog()

    def change_scaling(self):
        self.scaling = float(simpledialog.askstring('倍率変更', '拡大率を数値で入力して下さい。0.5～1.0程度を推奨'))
        # iniに記入
        self.config.set("Viewer", "画像表示の拡大率", str(self.scaling))
        with open(self.inipath, "w", encoding='UTF-8') as configfile:
            self.config.write(configfile)
        self.restartwatchdog()

    def restartwatchdog(self):
        self.observer_img.stop()
        self.observer_img.join()
        print('変更を反映して監視を再開')
        # 変数の初期化
        self.event_handler = FileMonitor(self.wdog_sdimg_Path,self.canvas,self.sub_win,self.scaling)
        self.observer_img = PollingObserver()
        self.observer_img.schedule(self.event_handler, self.wdog_sdimg_Path, recursive=True)
        self.observer_img.start() 

    def close_window(self):
        sys.exit()

if __name__ == "__main__":
    
    app = App()
    app.root.mainloop()