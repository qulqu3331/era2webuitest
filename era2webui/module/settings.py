import configparser
import os

class Settings:
    
    @classmethod
    def select_variant(cls):
        # iniファイル読み込み
        config_ini = configparser.ConfigParser()
        module_path = os.path.abspath(os.path.dirname(__file__))
        era2webui_path = os.path.abspath(os.path.dirname(module_path))
        inipath = os.path.join(era2webui_path, "config.ini")
        config_ini.read(inipath, 'UTF-8')

        Variant = config_ini.get("Variant", "Variant", fallback=0)
        if not Variant:
            # バリアント選択のロジック
            while True:
                print("バリアントを選択してください:")
                print("1: eratohoYM")
                print("2: eraTW")
                print("3: eraImascgpro")
                print("4: eraH")
                print("5: 東方触手宮")
                variant_number = input("選択: ")

                # バリアント番号に応じてバリアント名を設定
                if variant_number == '1':
                    cls.variant = 'eratohoYM'
                    break
                elif variant_number == '2':
                    cls.variant = 'eraTW'
                    break
                elif variant_number == '3':
                    cls.variant = 'eraImascgpro'
                    break
                elif variant_number == '4':
                    cls.variant = 'eraH'
                    break
                elif variant_number == '5':
                    cls.variant = '東方触手宮'
                    break

            # iniに記入
            config_ini.set("Variant", "Variant", cls.variant)
            with open(inipath, "w", encoding='UTF-8') as configfile:
                config_ini.write(configfile)

        else:
            cls.variant = Variant