import configparser
import os

# iniファイル読み込み
config_ini = configparser.ConfigParser()
module_path = os.path.abspath(os.path.dirname(__file__))
era2webui_path = os.path.abspath(os.path.dirname(module_path))
inipath = os.path.join(era2webui_path, "config.ini")
config_ini.read(inipath, 'UTF-8')

class Settings:
    # バリアントの設定（初期値はNone）
    variant = None

    @classmethod
    def select_variant(cls):
        Variant = config_ini.get("Variant", "Variant", fallback=0)
        if not Variant:
            # バリアント選択のロジック
            print("バリアントを選択してください:")
            print("1: eratohoYM")
            print("2: eraTW")
            print("3: eraImascgpro")
            variant_number = input("選択: ")

            # バリアント番号に応じてバリアント名を設定
            if variant_number == '1':
                cls.variant = 'eratohoYM'
            elif variant_number == '2':
                cls.variant = 'eraTW'
            elif variant_number == '3':
                cls.variant = 'eraImascgpro'

            # iniに記入
            config_ini.set("Variant", "Variant", cls.variant)
            with open(inipath, "w", encoding='UTF-8') as configfile:
                config_ini.write(configfile)

        else:
            cls.variant = Variant