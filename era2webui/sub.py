from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import os
import random
import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog
import configparser



# ブラウザ操作用 webdriver、ポジ、ネガを引数に取ってgenerate
def gen_Image(driver,prompt,negative,gen_width,gen_height):

    # タイトルが"Stable Diffusion"でない場合は準備ミスかビジーなのでFalseを返してやり直させる
    titlechk=driver.title

    if titlechk != "Stable Diffusion":
         return False 
    
    print("title OK")
    # WebUIはseleniumから普通に読み書きできない。JavaScriptで読み書きする。
    # 拡張機能のせいかJSPathが環境により異なるらしい。shadowRootのありなし2通りに対応している。


    # JSPathを文字列に格納 別のJSPathに手動で書き換えるならここ
    JSPath = 'document.querySelector(\"body > gradio-app\").shadowRoot.querySelector'

    try:
        #最初の試行
        driver.execute_script(f"{JSPath}(\"#txt2img_prompt > label > textarea\").focus() ;")
    except:
        # エラーだったらJSPathを変更
        JSPath = 'document.querySelector'
        try:
            #2回目の試行            
            driver.execute_script(f"{JSPath}(\"#txt2img_prompt > label > textarea\").focus() ;")
        except Exception as e:
            print(f"エラー詳細: {e}")
            print("WebUIのプロンプト欄右クリックで「検証」 からの右クリック>「Copy」>「JSPath」でコピーされる文字列を確認して下さい。")
            print("下記2パターン以外の場合、sub.pyのコード書き換えが必要です。")
            print("document.querySelector(\"body > gradio-app\").shadowRoot.querySelector(\"#txt2img_prompt > label > textarea\")")
            print("document.querySelector(\"#txt2img_prompt > label > textarea\")")


    # promptの内容をテキストボックスに書き込み
    driver.execute_script(f"{JSPath}(\"#txt2img_prompt > label > textarea\").value = \"{prompt}\" ;")
    # ここまでだとテキストの変更を認識しない。「テキスト欄になにかしら入力」を力技で行う
    actions = ActionChains(driver)
    actions.send_keys(Keys.SPACE).perform()

    driver.execute_script(f"{JSPath}(\"#txt2img_neg_prompt > label > textarea\").focus() ;")
    driver.execute_script(f"{JSPath}(\"#txt2img_neg_prompt > label > textarea\").value = \"{negative}\" ;")   
    # ここまでだとテキストの変更を認識しない2
    actions.send_keys(Keys.SPACE).perform()

    if gen_width != 0:
        driver.execute_script(f"{JSPath}(\"#txt2img_width > div.w-full.flex.flex-col > div > input\").focus() ;")
        driver.execute_script(f"{JSPath}(\"#txt2img_width > div.w-full.flex.flex-col > div > input\").value = \"{gen_width}\" ;") 
        #力技で変更を認識させる。
        actions.send_keys(Keys.UP).perform()
        actions.send_keys(Keys.DOWN).perform()
        driver.execute_script(f"{JSPath}(\"#txt2img_height > div.w-full.flex.flex-col > div > input\").focus() ;")
        driver.execute_script(f"{JSPath}(\"#txt2img_height > div.w-full.flex.flex-col > div > input\").value = \"{gen_height}\" ;")
        actions.send_keys(Keys.UP).perform()
        actions.send_keys(Keys.DOWN).perform()


    # Ctrl+EnterでGenerateする
    actions.key_down(Keys.CONTROL)
    actions.key_down(Keys.ENTER)
    actions.perform()

    # -----生成が行われたかの判定。とりあえずブラウザのtitleで判断。（生成中はタイトルが変わる。"Stable Diffusion"に戻ったら完了）タイトル変化に1秒ほどのラグがあり、1秒未満で完了すると検知できない

    print("生成中", end="")
    i = 1
    while (driver.title == titlechk):
        time.sleep(0.02)
        if i % 5 == 0:
            print("|", end="")
        i = i + 1
        if i > 500:
            print("10秒待っても生成開始を確認できませんでした。スキップします。")
            return True
    # タイトルが [〇% ETA:〇s] に変化した。元に戻るまで待つ
    i = 1
    while (driver.title != titlechk):
        time.sleep(0.02)
        if i % 5 == 0:
            print("|", end="")
        i = i + 1
        if i > 1000:
            print("生成完了を検知できず10秒以上待っています。次の処理を始めます。")
            break

    return True


# csv読み出し用
# key = value になる行を探して　列名 column の要素を取得する
# 例 : get_df(csv_tra,"コマンド名","何もしない","プロンプト") で何もしない時のプロンプトを返す
# csvの該当箇所が空欄の時は""を返す
# 検索条件がおかしい場合は"Error"を返す
def get_df(dataframe,key, value, column):
    try:
        result = dataframe.loc[dataframe[key] == value, column].fillna("").values[0]
    except Exception as e:
        print("Error: {}".format(e))
        print("取り出そうとした要素: {}={}なる行の{}".format(key,value,column))
        return "Error"
    return result

# csv読み出し用 検索条件が2列で構成される場合
def get_df_2key(dataframe,key,value,subkey,subvalue,column):
    try:
        result = dataframe.loc[(dataframe[key] == value) & (dataframe[subkey] == subvalue), column].fillna("").values[0]
    except Exception as e:
        print("Error: {}".format(e))
        print("取り出そうとした要素: {}={}かつ{}={}なる行の{}".format(key,value,subkey,subvalue,column))
        return "Error"
    return result

# 置換機能
# 文字列中に%で囲まれた部分があればReplaceList.csvに基づいて置換する機能
def chikan(text):
    csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\ReplaceList.csv')
    csv_chi = pd.read_csv(filepath_or_buffer=csvfile_path)
    # 正規表現で置換対象("%"で挟まれた文字列)をリスト化
    置換対象 =re.findall('%.*?%',text)
    if len(置換対象) > 0:
        # 見つかった置換対象リストの数だけ繰り返し
        for chi in 置換対象:
            # %抜きの文字列でcsvを検索する
            csv参照用 = chi.strip("%")
            text = re.sub(chi,get_df(csv_chi,"置換前",csv参照用,"置換後"),text)
            # get_dfがエラーを出した場合、文字列"Error"に置換される
    return text


# GUI
class readconfig:
    def __init__(self):
        # iniファイル読み込み
        self.config = configparser.ConfigParser()
        self.config.read("./config.ini")

    # フォルダ選択ダイアログ表示(テキスト監視フォルダ)
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selectedDir = folder_path
            print(f"Selected folder: {self.selectedDir}")
            # iniに記入
            self.config.set("Paths", "Path1", self.selectedDir)
            with open("config.ini", "w") as configfile:
                self.config.write(configfile)
            return self.selectedDir


# 解像度をcsvから読む
# シーン分岐ごとに読む
def get_kaizoudo(order):
    # TRAINとその他のEVENTで読み取るcsvが異なる
    if order["scene"] == "TRAIN":
        csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Train.csv')
        csvfile = pd.read_csv(filepath_or_buffer=csvfile_path)
        kaizoudo = str(get_df(csvfile,"コマンド番号",str(order["コマンド"]),"解像度"))
    else:
        csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Event.csv')
        csvfile = pd.read_csv(filepath_or_buffer=csvfile_path)
        kaizoudo = str(get_df(csvfile,"名称",str(order["scene"]),"解像度"))
    
    return kaizoudo


# 解像度文字列を解釈する関数
def get_width_and_height(kaizoudo):

    # 解像度欄でも置換機能を使えるようにする。%で囲まれた文字列があると置換を試みる。
    kaizoudo = chikan(kaizoudo)

    # 読み出した結果が空欄やエラーの場合は0,0を返す。解像度の変更はスキップされる。
    if kaizoudo in ("","Error"):
        print("解像度指定なし")
        return 0,0
    print("解像度変更あり")

    # ","で分割されている場合、ランダムで選ぶ
    # 例 3択ランダムなら"512x768,768x512,1024x512"みたいに書く。置換機能を使ってもよい。
    if "," in kaizoudo:
        splitkai = re.split(",",kaizoudo)
        ra = random.randrange(len(splitkai))
        kaizoudo = splitkai[ra]

    # xで分割 (区切り文字としてXと*と×も認める)
    kai = re.split("[xX*×]",kaizoudo)
    # エラー処理2 splitで2要素に分割されなかった場合
    if len(kai) != 2:
        print("解像度取得に失敗。splitで2要素に分割されなかった。解像度変更を中止")
        return 0,0

    try:
        width = int(kai[0])
        height = int(kai[1])
    except Exception as e:
        # エラー処理3 splitできたが数値として認識できない場合
        print(f"解像度取得に失敗。splitできたが数値として認識できなかった。詳細:{e}")
        print("解像度変更を中止")
        return 0,0
    
    return width,height