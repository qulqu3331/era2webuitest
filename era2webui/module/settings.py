class Settings:
    # バリアントの設定（初期値はNone）
    variant = None

    @classmethod
    def select_variant(cls):
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