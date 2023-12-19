import asyncio
import configparser
import os
import sys
import time
from tkinter import filedialog

import requests
#from eratohoYM.suberatohoYM import promptmaker  # YMの場合こちらをインポートする
#from eraTW.suberaTW import promptmaker #TWの場合こちらをインポートする
from eraTW.suberaTW import PromptMaker
#from eraImascgpro.subcgpro import promptmaker
from module.api import gen_image_api
from module.savedata_handler import SJHFactory
from module.csv_manager import CSVMFactory
from module.csv_manager import search_imported_variant
from module.sub import gen_Image
from selenium import webdriver
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

class FileHandler(FileSystemEventHandler):
    """受け取る引数 order_queue は list

    Args:
        FileSystemEventHandler (_type_): _description_
    """
    def __init__(self, queue):
        super().__init__()
        self.queue = queue


    # 作成と変更は同じ処理
    def on_created(self, event):
        self.handle_event(event)
    def on_modified(self, event):
        self.handle_event(event)


    def handle_event(self, event):
        if not event.is_directory:
            if event.src_path.endswith('.txt'):
                self.txt_event(event)
            elif event.src_path.endswith('.csv'):
                self.csv_event(event)

    def txt_event(self, event):
        # ファイルが作成されたらキューに追加する
        print("\ntxt検知")

        # 文字コードはeraの出力の時点でUTF-8(BOM付)にする。ERB中、SAVETEXTの第4引数を1にすればいい。
        save_path = event.src_path
        # SaveJSONHandlerにファイル読み込みを委譲
        self.save = SJHFactory.create_instance(save_path)

        if len(self.queue) >= QUEUE_MAX_SIZE:
            self.queue.pop(0)
        self.queue.append((event.src_path, self.save))

    def csv_event(self, event):
        # CSVファイルが更新されたときの処理
        print("\nCSVファイル検知: " + event.src_path)

        csvm = CSVMFactory.get_instance()
        # CSVManagerにファイルの読み込みを委譲し、データフレームを更新
        csv_name = os.path.basename(event.src_path)
        csvm.process_csv_event(csv_name)


def TaskExecutor(order_queue,driver):
    while True:
        if order_queue:
            # キューから一番古いオーダーを取り出す
            file_path, sjhandler  = order_queue.pop(0)
            # ordersはjsonをloadした結果で辞書(dict)型  [0]はpath､[1]が内容
            # ---------ここがメインのオーダー処理-----------------------
            # SaveJSONHandlerのインスタンスからJSONデータを取得
            json_data = sjhandler.data  # JSONデータを別の変数に代入
            print("txtを読み込み シーン:" + json_data["scene"]) #読み込みチェック　シーンを書き出す
            print("キャラ名:" + json_data["target"]) #キャラ名を書き出す

            # プロンプト整形 SaveJSONHandlerのメソッドを使うため  インスタンスそのもの  をわたす
            promptmaker = PromptMaker(sjhandler)
            prompt,negative,gen_width,gen_height = promptmaker.generate_prompt()

            # add_prompt.txtの内容をpromptに追記する
            if add_prompt機能:
                file_path = os.path.join(os.path.dirname(__file__), 'add_prompt.txt')
                f = open(file_path, "r", encoding='utf-8')
                prompt += f.read()

            if 解像度自動変更 == 0:
                gen_width = 0
                gen_height = 0
            else:
                # csvの解像度指定欄が空欄の場合、gen_width/gen_heightには"0"が入っている
                # このときデフォルト解像度（iniで設定）に置き換える。
                # （iniで設定された値が0なら解像度変更スキップになる）
                if gen_width == 0:
                    gen_width = デフォルト解像度x
                if gen_height == 0:
                    gen_height = デフォルト解像度y

            # ブラウザ操作
            i = 1
            while True:
                #driverを取得できない場合gen_image_apiで生成する
                if driver is None:
                    status_code = asyncio.run(gen_image_api(prompt, negative, gen_width, gen_height))
                    if status_code == 200:
                        time.sleep(0.1)
                        break #待機ゲージはapi.pyで処理する

                else:
                    if gen_Image(driver,prompt,negative,gen_width,gen_height) == True:
                        break
                    time.sleep(0.02)
                    if i % 5 == 0:
                        print("|", end="") #待機ゲージ gen_Imageがtrueを返してくれるまでやり直す
                    i += 1

            print("\n完了")
            # 残りキューの表示
            mark = " ☆" * len(order_queue)
            print("未処理キュー:" + str(len(order_queue)) + mark)
        else:
            # キューが空の場合は少し待つ
            time.sleep(0.02)

if __name__ == '__main__':

    # 作業ディレクトリを本プログラムがあるフォルダに変更
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # iniファイル読み込み
    config_ini = configparser.ConfigParser()
    inipath = os.path.abspath(os.path.join(os.path.dirname(__file__), "config.ini"))
    config_ini.read(inipath, 'UTF-8')

    # iniに項目がなかったら追加する
    if not config_ini.has_section('Paths'):
        config_ini.add_section('Paths')
    if not config_ini.has_section('Viewer'):
        config_ini.add_section('Viewer')
    if not config_ini.has_section('Generater'):
        config_ini.add_section('Generater')
    if not 'erasav' in config_ini['Paths']:
        config_ini.set('Paths', 'erasav', '')
    if not 'image' in config_ini['Paths']:
        config_ini.set('Paths', 'image', '')
    if not '画像表示の拡大率' in config_ini['Viewer']:
        config_ini.set('Viewer', '画像表示の拡大率', "1.0")
    if not 'savフォルダの選択をスキップ' in config_ini['Generater']:
        config_ini.set('Generater', 'savフォルダの選択をスキップ', "0")
    if not '解像度自動変更' in config_ini['Generater']:
        config_ini.set('Generater', '解像度自動変更', "1")
    if not 'デフォルト解像度x' in config_ini['Generater']:
        config_ini.set('Generater', 'デフォルト解像度x', "0")
    if not 'デフォルト解像度y' in config_ini['Generater']:
        config_ini.set('Generater', 'デフォルト解像度y', "0")
    if not 'キューの最大サイズ' in config_ini['Generater']:
        config_ini.set('Generater', 'キューの最大サイズ', "2")
    if not 'add_prompt機能' in config_ini['Generater']:
        config_ini.set('Generater', 'add_prompt機能', "1")
    if not 'apiモードで起動する' in config_ini['Generater']:
        config_ini.set('Generater', 'apiモードで起動する', "0")

    # ダイアログで監視対象フォルダを選ばせる。
    # ダイアログ表示はconfigファイルでスキップ設定可能
    dir = config_ini.get("Paths", "erasav", fallback="")
    # スキップ設定を読む
    skip = int(config_ini.get("Generater", "savフォルダの選択をスキップ", fallback=0))
    if skip and os.path.isdir(dir):
        target_dir = dir
    else:
        # ダイアログを開く
        target_dir = filedialog.askdirectory(title = "監視するsavフォルダを選択",initialdir = dir)

    # iniに記入
    config_ini.set("Paths", "erasav", target_dir)
    with open(inipath, "w", encoding='UTF-8') as configfile:
        config_ini.write(configfile)

    # ダイアログを×で閉じたときに呼ばれる
    if os.path.isdir(target_dir) == False:
        print("指定された監視フォルダ " + target_dir + " が見つかりません。終了します")
        sys.exit()

    # CSVフォルダの処理
    csv_dir = config_ini.get("Paths", "eracsv", fallback="")
    skip_csv = int(config_ini.get("Generater", "csvフォルダの選択をスキップ", fallback=0))
    if skip_csv and os.path.isdir(csv_dir):
        csv_target_dir = csv_dir
    else:
        #search_imported_variantでインポートされてるCSVから監視するPathを作成
        csv_target_dir = os.path.join(os.path.dirname(__file__), search_imported_variant(), 'csvfiles')
    # iniにCSVパスを記入
    config_ini.set("Paths", "eracsv", csv_target_dir)
    with open(inipath, "w", encoding='UTF-8') as configfile:
        config_ini.write(configfile)

    # ダイアログを×で閉じたときの処理
    if os.path.isdir(csv_target_dir) == False:
        print("指定されたcsv監視フォルダ " + csv_target_dir + " が見つかりません。終了します")
        sys.exit()


    # キューの最大サイズ
    QUEUE_MAX_SIZE = int(config_ini.get("Generater", "キューの最大サイズ", fallback=2))
    # 解像度切り替え
    解像度自動変更 = int(config_ini.get("Generater", "解像度自動変更", fallback=0))
    # デフォルト解像度
    デフォルト解像度x = int(config_ini.get("Generater", "デフォルト解像度x", fallback=0))
    デフォルト解像度y = int(config_ini.get("Generater", "デフォルト解像度y", fallback=0))
    # 外付けボタンによるプロンプト追加機能
    add_prompt機能 = int(config_ini.get("Generater", "add_prompt機能", fallback=0))
    # apiモードで起動する
    apiモードで起動する = int(config_ini.get("Generater", "apiモードで起動する", fallback=0))

    # 画像ビューアの起動は手動にしました

    # キューの初期化
    order_queue = []

    # Chromeに接続
    def check_browser():
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222") #あらかじめポート9222指定のchromeでWebUIを開いておく
        try:
            print("ブラウザ取得の試行 タイムアウトまで長いので、ブラウザモードを使わない場合はconfig.iniで設定することを推奨。")
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print("ブラウザを掴むのに失敗。chromeを-remote-debugging-port=9222オプションで開いておいてね")
            print(f"APIエラー詳細: {e}")
            return None


    # APIの起動確認
    def check_api():
            try:
                response = requests.get("http://127.0.0.1:7860")
                response.raise_for_status()
                return True
            except requests.exceptions.ConnectionError as e:
                print(f"エラー: {e}")
                return e


    # APIモードで起動するかの設定をconfig.iniから取得
    api_mode = config_ini.get('Generater', 'apiモードで起動する', fallback='0') == '1'

    # iniでAPIモードの設定がある場合はブラウザのチェックを飛ばす
    if not api_mode:
        print("Chromeへの接続を試行")
        driver = check_browser()
    else:
        print("APIモードで起動")
        driver = None

    # ブラウザモードでの接続が成功したか、APIモードの処理
    if driver is not None:
        print("ブラウザモードで作動")
        print("取得したwebdriver:" + str(driver))
    else:
        print("APIの接続確認中")
        api_result = check_api()
        if api_result is True:
            print("API利用可能")
        else:
            print("APIの接続不能")
            print("ブラウザ､APIともに使用不能")
            sys.exit()



    # ファイル監視の開始
    file_handler = FileHandler(order_queue)
    observer = PollingObserver()
    #各ファイルの監視を設定
    observer.schedule(file_handler, target_dir, recursive=False)
    print("txtファイルの監視を開始しました。target_dir:" + str(target_dir))
    observer.schedule(file_handler, csv_target_dir, recursive=False)
    print("csvファイルの監視を開始しました。csv_target_dir:" + str(csv_target_dir))

    observer.start()

    # タスクの実行
    task_executor = TaskExecutor(order_queue,driver)
    task_executor.run(driver)

    # ファイル監視の停止
    observer.stop()
    observer.join()
    print("強制終了でしか終わらない現状、ここが処理されることはない")
    driver.quit()