import configparser
import os
from tkinter import filedialog
from module.settings import Settings

# iniファイル読み込み
config_ini = configparser.ConfigParser()
# このファイルがiniと同階層にある前提
inipath = os.path.join(os.path.dirname(__file__), "config.ini")
config_ini.read(inipath, 'UTF-8')


#項目が存在しなければ追加
if not config_ini.has_section('Paths'):
    config_ini.add_section('Paths')
if not config_ini.has_section('Variant'):
    config_ini.add_section('Variant')


if not 'Variant' in config_ini['Variant']:
    config_ini.set('Variant', 'Variant', "")
if not 'erasav' in config_ini['Paths']:
    config_ini.set('Paths', 'erasav', "")

#項目が存在しなければ追加 バリアント毎の監視フォルダを記憶する項目
if not 'eratohoYMsav' in config_ini['Paths']:
    config_ini.set('Paths', 'eratohoYMsav', "")
if not 'eraTWsav' in config_ini['Paths']:
    config_ini.set('Paths', 'eraTWsav', "")
if not 'eraImascgprosav' in config_ini['Paths']:
    config_ini.set('Paths', 'eraImascgprosav', "")
if not 'eraHsav' in config_ini['Paths']:
    config_ini.set('Paths', 'eraHsav', "")
if not '東方触手宮sav' in config_ini['Paths']:
    config_ini.set('Paths', '東方触手宮sav', "")

# バリアント未選択状態にする
config_ini.set("Variant", "Variant", "")
with open(inipath, "w", encoding='UTF-8') as configfile:
    config_ini.write(configfile)



# 設定画面を呼び出し、バリアントを決定
Settings.select_variant()

Variant = Settings.variant
print(Variant)

# iniファイルにそのバリアントの監視対象フォルダは記録されているか
dir = config_ini.get("Paths", f"{Variant}sav", fallback=0)

if os.path.isdir(dir):
    print(f"前回使用した監視フォルダ：{dir}")
    print("このバリアントの監視フォルダを変更しますか? ")
    print("")
    input = input("選択(Y/[N])（変更するならYを入力 / このままENTERでN扱い） : ")
    if input in ["y","Y","ｙ","Ｙ"]:
        change_dir = True
    else:
        change_dir = False  
else:
    change_dir = True

# 監視対象フォルダの選択
if change_dir == True:
    # ダイアログを開く
    print(f"監視する {Variant} のsavフォルダを選択して下さい。 ")
    target_dir = filedialog.askdirectory(title = "監視するsavフォルダを選択",initialdir = dir)

    # ダイアログを×で閉じたときに呼ばれる
    if os.path.isdir(target_dir) == False:
        print("指定された監視フォルダ " + target_dir + " が見つかりません。終了します")
    else:
        # iniに記入
        config_ini.set("Paths", f"{Variant}sav", target_dir)
        with open(inipath, "w", encoding='UTF-8') as configfile:
            config_ini.write(configfile)
        print(f"監視フォルダを {target_dir} \n に設定し、iniファイルに書き込みました")
else:
    print("監視フォルダ設定を変更しません")

print("バリアント選択プログラムを終了します")