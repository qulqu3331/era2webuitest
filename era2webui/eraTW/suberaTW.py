"""_summary_

Raises:
    KeyError: _description_

Returns:
    _type_: _description_
    
"""
from eraTW.cloth import ClothFlags, get_cloth_dict
from module.csv_manager import CSVMFactory
from module.sub import get_width_and_height
from module.promptmaker import PromptMaker
from eraTW.emoTW import ExpressionTW
csvm = CSVMFactory.get_instance()
class PromptMakerTW(PromptMaker):
    """
    # module.promptmaker をスーパークラスとしてるが全部オーバーライド
    # あとで
    
    このPromptMakerクラスは、eraTWゲームの状況に合わせたプロンプトを作るための強力なツールだぜ。
    シナリオやキャラクターの状態に応じた、細かくカスタマイズされたテキストを生成するんだ。使い方を間違えないようにな！

    Attributes:
        sjh (SaveJSONHandler): ゲームのセーブデータを管理するインスタンス。これがないと始まらないぜ。
        erascene (str): 現在のシーンを格納している。シーンによって生成するプロンプトが変わるから重要だ。
        prompt (dict): シナリオに関連するプロンプトを格納する辞書。ここにデータを詰め込むんだ。
        negative (dict): ネガティブなプロンプトを格納する辞書。時にはダークな面も見せる必要があるからな。
        flags (dict): 描画に関する各種フラグを保持する辞書。どんなシーンを描くかはこれで決まるぜ。
        csv_files (dict): CSVファイルの名前とそれに関連するキーを格納する辞書。データはここから引っ張るんだ。

    Methods:
        generate_prompt: 様々な条件に基づいてプロンプトを生成する。ここがこのクラスの肝だぜ。
        他にもいろいろなメソッドがあるけど、詳細はコードを見てくれ。長くなるからここでは割愛するぜ。

    このクラスを使って、どんなシナリオでも対応できるプロンプトを作り出せるぜ。使いこなせるかな？
    """
    def __init__(self, sjh):
        self.sjh = sjh
        self.initialize_class_variables()#判定に必要なセーブデータを一括取得 #0 or 1はBoolにするかも
        self.prompt =    {"situation":"", "location":"", "weather":"", "timezone":"", "scene":"",\
                          "chara":"","cloth":"","train": "","emotion": "","stain": "",\
                          "潤滑": "","effect": "", "body": "","hair": "","event":""}
        self.negative =  {"situation":"", "location":"", "weather":"", "timezone":"", "scene":"",\
                          "chara":"","cloth":"", "train": "","emotion": "","stain": "",\
                          "潤滑": "","effect": "","eyes": "", "body": "","hair": "","event":""}
        self.flags = {"drawchara":True,"drawface":True,"drawbreasts":False,\
            "drawvagina":False,"drawanus":False,"drawlocation":False,"主人公以外が相手":False,"indoor":False}
        self.width = 0
        self.height = 0
        self.initialize_class_variablesTW()#判定に必要なセーブデータを一括取得

    def initialize_class_variablesTW(self):
        self.loca   = self.sjh.get_save("現在位置Str")#str
        self.panty = self.sjh.get_save("lower_underwear") #str
        self.uniquepanty = self.sjh.get_save("固有下着") #int (boole
        self.dish = self.sjh.get_save("作った料理") #str

    def generate_prompt(self):
        """
        このgenerate_promptは、elementsをギュッと集めて呪文を生成するんだ。
        シチュエーション、ロケーション、天気、装備、キャラクターなど、色々な要素から呪文を組み立てていく。

        屋内か屋外かで天気の扱いが変わるし、TRAINシーンかどうかで処理も変わるんだ
        全部を合わせて、強力な呪文を作り上げるぜ。

        Returns:
            tuple: (prompt, negative, width, height)を返す。
                - prompt (str): シナリオに基づいた呪文のテキスト。
                - negative (str): 呪文のネガティブな面を表すテキスト。
                - width (int), height (int): 生成する画像のサイズ。

        このメソッドを使って、どんなシナリオにもバッチリ対応できる呪文を作れるぜ！
        """
        #呪文に含めるかの条件分岐はあとで考える
        self.update()
        self.create_situation_element() #シチュエーション｢マスター移動｣｢ターゲット切替｣
        self.create_location_element() #場所
        self.create_season_element()#季節 屋内外問わず
        self.get_kaizoudo() #解像度
        #屋内なら天気は無し
        if not self.flags.get("indoor"):
            self.create_weather_element() #天候
        self.create_timezone_element() #時間帯

        # 一般EVENT
        if not self.scene in ["TRAIN","ターゲット切替","マスター移動"]:#例外シーンを作るたびにここに列挙しないといけない
            self.create_event_element() #継承
            self.create_equip_element()#一時装備
            if self.flags["drawvagina"]:
                self.create_juice_element()#汁
                self.create_stain_element()#如何わしい汚れ

        if self.scene == "TRAIN":
            self.create_train_element()#行動
            self.create_equip_element()#一時装備
            #TRAINに限定しないと料理中に射精とかが起こる
            #eraTWでは性行為以外でもコマンドがある=TRAINとして吐き出させてるのでであとで直す必要あるかも
            self.create_cum_element()
            if self.flags["drawvagina"]:
                self.create_juice_element()#汁
                self.create_traineffect_element() #噴乳はここでない気がする
                self.create_stain_element()#如何わしい汚れ
            if self.com == "スカートをめくる":
                self.create_panty_element()
            if self.com == "料理を作る":
                self.create_dish_element()

        if self.scene == "パンツをくすねる":
            self.create_panty_element()


        #主人公しか居ない時はフラグをOFF 連れ出すときもOFFになる
        if self.charno == 0:
            self.flags["drawchara"] = False
            self.flags["drawface"]  = False

        if self.flags["drawchara"]: # 人を描画しない場合は処理をスキップ
            self.create_chara_element() #キャラ
            self.create_body_element()  #体
            self.create_effect_element()#妊娠
            #self.create_clothing_element() #未完成につきコメントアウト

        if self.flags["drawface"]:  # 顔を描画しない場合は処理をスキップ
            self.create_hair_element()#髪
            pm_var = self.gather_instance_data()
            emo = ExpressionTW(pm_var)
            emopro,emonega = emo.generate_emotion() #表情
            self.add_element("emotion", emopro, emonega)

        if self.flags["drawlocation"] == False: # 背景オフ指定の場合は場所・天気・時間の影響を削除
            self.prompt["location"] = ""
            self.negative["location"] = ""
            self.prompt["weather"] = ""
            self.negative["weather"] = ""
            self.prompt["timezone"] = ""
            self.negative["timezone"] = ""


        #辞書のvalueが空の要素を消す
        prompt_values = [value for value in self.prompt.values() if value.strip()]
        negative_values = [value for value in self.negative.values() if value.strip()]
        #カンマとスペースを足してヒトツナギに
        prompt = ", ".join(prompt_values)
        negative = ", ".join(negative_values)
        width = self.width
        height = self.height
        prompt = csvm.chikan(prompt)
        negative = csvm.chikan(negative)
        self.prompt_debug()
        return prompt,negative,width,height


    def add_element(self, elements, prompt, nega):
        """
        指定された要素に対してプロンプトやネガティブプロンプトを追加するんだ。
        渡したエレメントが辞書に存在しない場合は、このメソッドが手痛いお仕置きをするから気をつけてくれよな！

        Args:
            elements (str): プロンプト要素のキーだ。辞書にあるキーを正しく渡すんだぜ。
            prompt (str): 追加したいプロンプトのテキスト。Noneか'ERROR'じゃなければ追加するぜ。
            nega (str): 追加したいネガティブプロンプトのテキスト。こっちもNoneか'ERROR'じゃなければ追加する。

        Raises:
            KeyError: '{elements}'がプロンプト辞書にないときに投げられる例外だ。ちゃんと辞書を確認してから使ってくれよな！
            KeyError: ネガティブプロンプト辞書に'{elements}'がないときにも同じ例外が飛ぶぜ。こっちも確認しておくんだな！

        このメソッドを使えば、お前の辞書に新しいプロンプトやネガティブプロンプトをサクッと追加できるぜ。
        """
        if elements not in self.prompt:
            raise KeyError(f" '{elements}' なんてプロンプト要素、ないぜ！")

        if prompt is not None and prompt != "ERROR":
            self.prompt[elements] += prompt
        if nega is not None and nega != "ERROR":
            self.negative[elements] += nega


    def update(self):
        """
        このupdateメソッドは、現在のゲーム状況に合わせてコマンド名を更新するために使うんだ。
        特に、キャラクターの特徴や状況に応じてコマンドを差し替える処理を行う。

        例えば、巨乳未満のキャラで'パイズリ'コマンドが使われた場合、それを'ナイズリ'に変更する。
        また、着衣時の胸愛撫は別のコマンドに変える処理もあるぜ。

        このメソッドは、SaveJSONHandlerのデータを適切に更新することで、シナリオのリアリティを高める役割を果たす。
        """
        # SaveJSONHandler の class dict の更新などの処理
        # 条件によりコマンド差し替え（乳サイズでパイズリ→ナイズリ
        # キャラ差し替え　EXフラグが立っていたらEXキャラ用の名前に変更する
        # など
        #SJH使う場合要らないかも あとで考える


        # 巨乳未満のキャラのパイズリはナイズリに変更
        # (ちんちんが隠れてしまうような描写は普乳を逸脱しているため)
        if not ("巨乳" in self.talent) or ("爆乳" in self.talent):
            if self.com == "パイズリ":
                self.com = "ナイズリ"

        # 着衣時の胸愛撫はCHAKUMOMIのLoraを適用
        if self.upwear != 0:
            if self.com == "胸愛撫":
                self.com = "着衣胸愛撫"            
            if self.com == "胸揉み":
                self.com = "着衣胸揉み"


    def create_situation_element(self):
        """
        このcreate_situation_elementメソッドは、現在のシナリオに合わせて状況のプロンプトを生成するんだ。
        特に、ターゲットの切り替えやマスターの移動などのシーンに応じて、適切なプロンプトを組み立てるぜ。

        基礎プロンプトのネガティブプロンプトは常に追加される。
        シナリオがターゲット切替やマスター移動の場合は特定の条件に基づいて異なるプロンプトを追加する。
        # drawchara､drawface フラグの変更
        """
        efc = "Effect.csv"
        prompt = csvm.get_df(efc,"名称","基礎プロンプト","プロンプト")
        nega = csvm.get_df(efc,"名称","基礎プロンプト","ネガティブ")
        self.add_element("situation", None, nega)
        if self.scene == "ターゲット切替" or self.scene == "マスター移動" or self.scene == "真名看破":
            self.flags["drawlocation"] = True
            if self.charno == 0:
                # targetがいないとき #この条件はTWではうまく動かない
                self.add_element("situation", "(empty scene)", "(1girl:1.7)")

            else:
                self.add_element("situation", "1girl standing, detailed scenery in the background", None)
                #ターゲットが居るならキャラ｡顔表示ONにしないと誰かが居ても空っぽの場所になるよ
                self.flags["drawchara"] = True
                self.flags["drawface"] = True


    def create_location_element(self):
        """
        現在のシナリオに合わせて、ロケーションに関するプロンプトを生成するメソッドだぜ。
        CSVファイルからロケーションに関するデータを読み込み、適切なプロンプトとネガティブプロンプトを追加する。

        # ロケーションが屋内か屋外かもチェックして、フラグを設定するんだ。この情報は天気のプロンプトを生成するときにも使われるぜ。
        """
        # 700箇所
        #IDとの整合はあとで確かめる
        loc = "Location.csv"
        prompt = csvm.get_df(loc,"Str", self.loca,"プロンプト")
        nega = csvm.get_df(loc,"Str", self.loca,"ネガティブ")
        self.add_element("location", prompt, nega)
        #室内外かはCSVに書いて
        doors = csvm.get_df(loc,"Str", self.loca,"室内外")
        if doors == "indoor":
            self.flags["indoor"] = True


    def create_season_element(self):
        """
        現在の季のプロンプトを生成するメソッドだぜ。
        CSVファイルから天気のCSVについでに書いてあるデータを読み込んで、適切なプロンプトとネガティブプロンプトを組み立てる。
        """
        wea = "Weather.csv"
        prompt = csvm.get_df(wea,"天気", self.season,"プロンプト")
        nega = csvm.get_df(wea,"天気", self.season,"ネガティブ")
        self.add_element("weather", prompt, nega)


    def create_weather_element(self):
        """
        現在の天気に応じて、天気のプロンプトを生成するメソッドだぜ。
        CSVファイルから天気データを読み込んで、適切なプロンプトとネガティブプロンプトを組み立てる。
        """
        wea = "Weather.csv"
        prompt = csvm.get_df(wea,"天気", self.weath,"プロンプト")
        nega = csvm.get_df(wea,"天気", self.weath,"ネガティブ")
        if self.time in range(0, 360) or self.time >= 1150:#夜間にsunshineとか出ないようにする
            if (self.weath == "晴れ") or (self.weath == "快晴"):
                prompt,nega = "",""
        self.add_element("weather", prompt, nega)


    def create_timezone_element(self):
        """
        ゲーム内の時間に応じて、昼夜のエレメントを生成する魔法をかけるぜ。
        「時間」を基にして、昼間か夜間か、それとも薄暮（トワイライト）かを判断し、
        対応するプロンプトとネガティブプロンプトを生成するんだ。

        昼間は 'day,' と表現し、夜間は 'at night,' で示す。
        薄暮の時間帯は 'in the twilight,' となるぜ。
        """
        if self.time in range(0, 360) or self.time >= 1150:
            self.add_element("timezone", "at night", "(blue sky,twilight:1.3)")
        elif self.time in range(360, 1060):
            self.add_element("timezone", "day", "(night sky,night scene,twilight:1.3)")
        elif self.time in range(1060, 1150):
            self.add_element("timezone", "in the twilight", "(blue sky:1.3)")


    def create_train_element(self):
        """
        コマンドに対応するプロンプトを生成するんだ。
        CSVファイルから読み込んだコマンド名に基づいて、適切なプロンプトとネガティブプロンプトを組み立てるぜ。

        行動が成功したか失敗したかによって処理が分岐するから、それもしっかりチェックしてくれよな。
        成功した場合は、CSVから読み込んだ情報に基づいてプロンプトを作成する。失敗した場合は、拒否プロンプトを使うんだ。
        # drawchara drawface drawbreasts drawvagina drawanus
        """
        tra = "Train.csv"
        eve = "Event.csv"

        #0 以上だと成功
        #あとで検証
        if self.succ < 0:
            deny = csvm.get_df(tra,"コマンド名",self.com,"拒否プロンプト")
            if deny != "ERROR":
                # 拒否プロンプトがERRORでない場合、拒否プロンプトを出力
                nega = csvm.get_df(tra,"コマンド名",self.com,"拒否ネガティブ")
                self.add_element("train", deny, nega)
                self.flags["drawchara"] = True
                self.flags["drawface"] = True
                self.flags["drawlocation"] = bool(csvm.get_df(tra,"コマンド名",self.com,"背景描画"))
                return
        else:
            # Train.csvに定義された体位から読み取ったキャラ描画、顔描画、胸描画のフラグ（0か1が入る)
            #ブール値に変換
            self.flags["drawchara"] =  bool(csvm.get_df(tra,"コマンド名",self.com,"キャラ描画"))
            self.flags["drawface"] =  bool(csvm.get_df(tra,"コマンド名",self.com,"顔描画"))
            self.flags["drawbreasts"] =  bool(csvm.get_df(tra,"コマンド名",self.com,"胸描画"))
            self.flags["drawvagina"] = bool(csvm.get_df(tra,"コマンド名",self.com,"ヴァギナ描画"))
            self.flags["drawanus"] = bool(csvm.get_df(tra,"コマンド名",self.com,"アナル描画"))
            self.flags["drawlocation"] = bool(csvm.get_df(tra,"コマンド名",self.com,"背景描画"))

            # コマンドが未記入の場合はget_dfが"ERROR"を返すのでEvent.csvの汎用調教を呼ぶ
            prompt = csvm.get_df(tra,"コマンド名",self.com,"プロンプト")
            if prompt == "ERROR":
                prompt = csvm.get_df(eve,"名称","汎用調教","プロンプト")
                nega = csvm.get_df(eve,"名称","汎用調教","ネガティブ")

                self.flags["drawchara"] = bool(csvm.get_df(eve,"名称","汎用調教","キャラ描画"))
                self.flags["drawface"] = bool(csvm.get_df(eve,"名称","汎用調教","顔描画"))
                self.flags["drawbreasts"] = bool(csvm.get_df(eve,"名称","汎用調教","胸描画"))
                self.flags["drawvagina"] = bool(csvm.get_df(eve,"名称","汎用調教","ヴァギナ描画"))
                self.flags["drawanus"] = bool(csvm.get_df(eve,"名称","汎用調教","アナル描画"))
                self.flags["drawlocation"] = bool(csvm.get_df(eve,"名称","汎用調教","背景描画"))

                self.add_element("train", prompt, nega)
            nega = csvm.get_df(tra,"コマンド名",self.com,"ネガティブ")
            self.add_element("train", prompt, nega)


    def create_equip_element(self):
        """
        このcreate_equip_elementメソッドは、現在のゲーム状況に合わせて装備品のプロンプトを生成するんだ。
        CSVファイルから装備品に関するデータを読み込み、適切なプロンプトとネガティブプロンプトを追加するぜ。

        装備品は、シーンの構図によって表示されるかどうかが変わる。
        だから、描画フラグに基づいて装備品をスキップする処理も行うんだ。
        こうすることで、シナリオのリアリティを高めることができるぜ！
        """
        equ = "Equip.csv"

        N膣装備 = ["11","12","13","22"]
        Nアナル装備 = ["14","15","23"]
        #装備の値はあとで確認
        # 存在するすべてのequipについて繰り返す
        for key,value in self.tequip.items():
            # 構図による装備品のスキップ
            if key in N膣装備:
                print("v")
                print(self.flags["drawvagina"])
                if not self.flags["drawvagina"]:
                    continue
            if key in Nアナル装備:
                print("a")
                print(self.flags["drawanus"])
                if not self.flags["drawanus"]:
                    continue

            if key > 11: #eraTWでtequipで意味ある数字は11以上
                prompt = csvm.get_df_2key(equ,"TEQUIP",int(key),"値",int(value),"プロンプト")
                if  prompt == "ERROR":
                    continue
                nega = csvm.get_df_2key(equ,"TEQUIP",int(key),"値",int(value),"ネガティブ")
                self.add_element("equip", prompt, nega)


    def create_stain_element(self):
        """
        このcreate_stain_elementメソッドは、特定の条件下での精液の付着を描写するプロンプトを生成するために使うんだ。
        キャラクターの描画フラグに基づいて、適切なプロンプトを組み立てるぜ。

        たとえば、キャラクターが描画される場合には、装備品のプロンプトも考慮に入れるんだ。
        さらに、胸やヴァギナに精液が付着しているかどうかをチェックして、それに応じたプロンプトを追加する。
        """
        # 付着した精液
        if self.flags["drawchara"]:
            self.create_equip_element()
        if self.flags["drawbreasts"]:
            if self.bstain is not None and self.bstain == 4:
                self.add_element("stain", "(cum on breasts)", None)
        if self.flags["drawvagina"]:
            if self.cip is not None and self.cip >= 1:
                self.add_element("stain", "cum drip from pussy", None)

        # cum on ～ はちんちんを誘発、semen on ～ はほとんど効果がない
        # milkはときどきグラスが出る


    def create_chara_element(self):
        """
        このcreate_chara_elementメソッドは、キャラクターの描画に関するプロンプトを生成するために使うんだ。
        CSVファイルからキャラクターに関するデータを読み込み、適切なプロンプトとネガティブプロンプトを追加するぜ。

        毎回記述されるキャラクターの基本的なプロンプトはEffect.csvから読み出す。
        さらに、特別な名前でプロンプトを登録してある場合は、キャラクター描写を強制的に上書きする処理も行うんだ。

        """
        cha = "Character.csv"
        efc = "Effect.csv"

        # キャラ描写で毎回記述するプロンプト Effect.csvから読み出す
        charabase = csvm.get_df(efc,"名称","人物プロンプト","プロンプト")
        charabase = charabase + ", " #charaキーで辞書に格納する時カンマ スペースが入らないのでここで足す
        self.add_element("chara", charabase, None)

        # 特別な名前でプロンプトを登録してある場合、キャラ描写を強制的に上書きする処理
        uwagaki = csvm.get_df(cha,"キャラ名","描画キャラ上書き","プロンプト")
        if uwagaki != "ERROR": #EROORじゃなかったら上書き
            prompt = f"({uwagaki})"
            nega = csvm.get_df(cha,"キャラ名","描画キャラ上書き","ネガティブ")
            self.add_element("chara", prompt, nega)

        else:
            #割り込みがなければ通常のキャラプロンプト読み込み処理
            prompt = csvm.get_df(cha,"キャラ名",self.name,"プロンプト")
            prompt_wait = csvm.get_df(cha,"キャラ名",self.name,"プロンプト強調")
            # prompt_waitが"ERROR"でない場合にのみ結合する
            if prompt_wait != "ERROR":
                prompt = f"({prompt}:{prompt_wait})"
            self.add_element("chara", prompt, None)

            prompt2 = csvm.get_df(cha,"キャラ名",self.name,"プロンプト2")
            self.add_element("chara", prompt2, None)

            chara_lora = csvm.get_df(cha,"キャラ名",self.name,"キャラLora")
            nega = csvm.get_df(cha,"キャラ名",self.name,"ネガティブ")
            self.add_element("chara", chara_lora, nega)


    def create_cum_element(self):
        """
        このcreate_cum_elementメソッドは、射精箇所に基づいてプロンプトを生成するために使うんだ。
        ビット演算を使って、どの射精箇所が選ばれているかを判定するぜ。

        ビット演算ってのは、数字をビット単位で見て、特定のビットが立っているかどうかをチェックする方法だ。
        たとえば、'射精箇所'がビットで示されていて、各ビットが特定の射精箇所を表しているんだ。
        """
        efc = "Effect.csv"
        #;TFLAG:1 射精箇所 (ビット0=コンドーム 1=膣内 2=アナル 3=手淫 4=口淫 5=パイズリ 6=素股 7=足コキ 8=体表 9=アナル奉仕
        #なにこれ? → 20=手淫フェラ 21=パイズリフェラ22=シックスナイン 24=子宮口 25=疑似 26=授乳プレイ

        # チェックするビット位置のリスト
        ejaculation_places = {
                2: "(cum in pussy,internal ejaculation)",
                4: "(cum in ass)",
                8: "(cum on hand, ejaculation, projectile cum)",
                16: "(cum in mouth)",
                32: "(cum on breasts, ejaculation, projectile cum)",
                64: "(cum on lower body, ejaculation, projectile cum)",
                128: "(cum on feet, ejaculation, projectile cum)",
                256: "(cum on stomach, ejaculation, projectile cum)",
                512: "(ejaculation, projectile cum)"
            }
        for bit, description in ejaculation_places.items():
            if self.cump & bit != 0:
                cumin = description
                if self.mcum <= 1:
                    prompt = csvm.get_df(efc,"名称","主人が射精","プロンプト")
                else:
                    prompt = csvm.get_df(efc,"名称","主人が大量射精","プロンプト")

                prompt += cumin
                self.add_element("stain", prompt, None)


    def create_juice_element(self):
        """
        このcreate_juice_elementメソッドは、キャラクターの潤滑状態に基づいてプロンプトを生成するんだ。
        TRAINシーン限定で、ヴァギナ描画がonのときに使われるぜ。

        潤滑度の値に基づいて、適切なプロンプトを追加するんだ。
        たとえば、潤滑度が低い場合は特定のネガティブプロンプトを、潤滑度が高い場合はより具体的なプロンプトを追加する。
        """
        #TRAIN限定のエフェクト
        # 潤滑度に基づいてプロンプトを追加
        if self.juice < 200:
            self.add_element("潤滑", None, "pussy juice")
        elif 1000 <= self.juice < 2500:
            self.add_element("潤滑", "pussy juice", None)
        elif 2500 <= self.juice < 5000:
            self.add_element("潤滑", "dripping pussy juice", None)
        else:
            self.add_element("潤滑", "(dripping pussy juice)", None)


    def create_traineffect_element(self):
        """
        このcreate_traineffect_elementメソッドは、TRAINシーン限定の特定エフェクトに基づいてプロンプトを生成するために使うんだ。
        CSVファイルからエフェクトに関するデータを読み込み、適切なプロンプトを追加するぜ。

        破瓜の血や放尿など、特定の状況で発生するエフェクトを考慮に入れて、シナリオのリアリティを高めるプロンプトを作成するんだ。
        """
        #TRAIN限定のエフェクト
        # エフェクト等
        efc = "Effect.csv"
        # 破瓜の血
        if self.lostv > 0:
            prompt = csvm.get_df(efc,"名称","処女喪失","プロンプト")
            self.add_element("effect", prompt, None)
        if self.b is not None and self.b > 0:
            prompt = csvm.get_df(efc,"名称","今回の調教で処女喪失","プロンプト")
            self.add_element("effect", prompt, None)
        if self.nyo > 0:
            prompt = csvm.get_df(efc,"名称","放尿","プロンプト")
            self.add_element("effect", prompt, None)
        if self.flags["drawbreasts"]:
            if self.nyu > 0:
                prompt = csvm.get_df(efc,"名称","噴乳","プロンプト")
                self.add_element("effect", prompt, None)


    def create_effect_element(self):
        """
        このcreate_effect_elementメソッドは、キャラクターの特定の状態や状況に基づいてプロンプトを生成するんだ。
        CSVファイルからエフェクトに関するデータを読み込み、適切なプロンプトを追加するぜ。

        たとえば、キャラクターが妊娠している場合、妊娠の進行度に応じて異なるプロンプトを追加するんだ。
        これによって、シナリオのリアリティがさらに高まるぜ！
        """
        efc = "Effect.csv"
        if "妊娠" in self.talent:
            # 標準で20日で出産する。残14日から描写し、残8日でさらに進行
            if (self.birth - self.days) in range(8,14):
                prompt = csvm.get_df(efc,"名称","妊娠中期","プロンプト")
            elif (self.birth - self.days) <= 8:
                prompt = csvm.get_df(efc,"名称","妊娠後期","プロンプト")
            self.add_element("effect", prompt, None)
        
        if self.sjh.get_save("時間停止") != 0:
            prompt = csvm.get_df(efc,"名称","時間停止","プロンプト")
            nega = csvm.get_df(efc,"名称","時間停止","ネガティブ")
            self.add_element("effect", prompt, nega)

        if self.sjh.get_save("睡眠") != 0:
            prompt = csvm.get_df(efc,"名称","睡眠中","プロンプト")
            nega = csvm.get_df(efc,"名称","睡眠中","ネガティブ")
            self.add_element("effect", prompt, nega)


    def create_body_element(self):
        """
        このcreate_body_elementメソッドは、キャラクターの体の特徴に基づいてプロンプトを生成するために使うんだ。
        CSVファイルから体の特徴に関するデータを読み込み、適切なプロンプトを追加するぜ。

        乳サイズや体格、体型など、キャラクターの特徴をしっかりと表現するプロンプトを組み立てるんだ。
        特に、普通の乳サイズなのに誤って巨乳と描写されることを避けるための工夫もしているぜ！

        このメソッドを使えば、キャラクターの体の特徴を効果的に表現できるぜ！
        """
        tal = "Talent.csv"

        # 乳サイズ
        if self.flags["drawbreasts"]:
            talents = ["絶壁","貧乳","巨乳","爆乳"]
            for tal in talents:
                if tal in self.talent:
                    prompt = csvm.get_df(tal,"名称",tal,"プロンプト")
                    nega = csvm.get_df(tal,"名称",tal,"ネガティブ")
                    self.add_element("body", prompt, nega)
        else:
            talents = ["絶壁","貧乳","巨乳","爆乳"]
            for tal in talents:
                if tal in self.talent:
                    prompt = csvm.get_df(tal,"名称",tal,"プロンプト")
                    nega = csvm.get_df(tal,"名称",tal,"ネガティブ")
                    nega += "areolae, nipple" #negaが空白だった時用対策 #あとで nega空白ならERROR
                    self.add_element("body", prompt, nega)

        # 体格、体型
        talents = ["小人体型","巨躯","小柄体型","ぽっちゃり","ムチムチ","スレンダー","がりがり"]
        for tal in talents:
            if tal in self.talent:
                prompt = csvm.get_df(tal,"名称",tal,"プロンプト")
                nega = csvm.get_df(tal,"名称",tal,"ネガティブ")
                self.add_element("body", prompt, nega)

        # 胸愛撫など、普通乳なのに巨乳に描かれがちなコマンドのときプロンプトにsmall breastsを付加する
        chk_list = ["爆乳","巨乳","貧乳","絶壁"]
        and_list = set(self.talent) & set(chk_list)
        # リストに一致しないとき即ち普通乳のとき
        if (len(and_list)) == 0:
            if self.com in ("胸愛撫","胸揉み","パイズリ","着衣胸愛撫","着衣胸揉み"):
                self.add_element("body", "small breasts", None)


    def create_hair_element(self):
        """
        このcreate_hair_elementメソッドは、キャラクターの髪型に基づいてプロンプトを生成するために使うんだ。
        CSVファイルから髪型に関するデータを読み込み、適切なプロンプトを追加するぜ。

        長髪、セミロング、ショートカット、ツインテールなど、さまざまな髪型を考慮に入れる。
        髪型はキャラクターの個性を表現するのに重要な要素だから、しっかりと反映させるんだ。
        """
        tal = "Talent.csv"
        talents = ["長髪","セミロング","ショートカット","ポニーテール","ツインテール",\
                   "サイドテール","縦ロール","ツインリング","三つ編み","短髪","おさげ髪",\
                   "ポンパドール","ポニーアップ","サイドダウン","お団子髪","ツーサイドアップ",\
                   "ダブルポニー","横ロール","まとめ髪","ボブカット","シニヨン","ロングヘア"]
        for tal in talents:
            if tal in self.talent:
                prompt = csvm.get_df(tal,"名称",tal,"プロンプト")
                nega = csvm.get_df(tal,"名称",tal,"ネガティブ")
                self.add_element("hair", prompt, nega)


    # 解像度をcsvから読む
    def get_kaizoudo(self):
        """
        あとでアスペクト比を基に可変できるようにする
        このget_kaizoudoメソッドは、シーンに応じて解像度をCSVファイルから読み込むために使うんだ。
        TRAINシーンとその他のEVENTシーンで読み取るCSVが異なるから、条件分岐を使って適切なCSVを選択するぜ。

        TRAINシーンの場合はTrain.csvから、その他の場合はEvent.csvから解像度を取得するんだ。
        解像度は、画像生成における品質を決定する重要な要素だから、正確に取得することが大事だぜ！
        """
        # TRAINとその他のEVENTで読み取るcsvが異なる
        if self.scene == "TRAIN":
            tra = "Train.csv"
            kaizoudo = csvm.get_df(tra,"コマンド名",self.com,"解像度")
        #これ用のプロンプトや解像度はあとでCSVにかく
        elif self.scene == "マスター移動" or self.scene == "ターゲット切替":
            return

        else:
            eve = "Event.csv"
            kaizoudo = csvm.get_df(eve,"名称",self.scene,"解像度")
        self.width, self.height = get_width_and_height(kaizoudo)


    # 服装
    def create_clothing_element(self):
        """
        このclothingメソッドは、キャラクターの装備や服装に基づいてプロンプトを生成するために使うんだ。
        CSVファイルから服装に関するデータを読み込み、適切なプロンプトを追加するぜ。

        ノーパンやノーブラの判定、露出状態の判定も行う。服装はシナリオの雰囲気やキャラクターの個性を伝える重要な要素だから、しっかりと反映させるんだ。

        注意：このメソッドはまだ未完成だ。いつか完成させるぜ！
        """
        clo = "Cloth.csv"

        #グラグの処理はクラスにまとめる
        cf = ClothFlags(self.sjh)
        #TARGETの現在の装備一覧 dict
        cloth_dict = get_cloth_dict(self.sjh)

        #ノーパンノーブラ判定 bool
        nop = cf.nopan()
        nob = cf.nobura()
        #eはexposed は露出の e
        nippse = cf.nipps_exposed()
        pussye = cf.pussy_exposed()
        burae = cf.bra_exposed()
        pantse = cf.psnts_exposed()

        # 上着描写
        # 上半身上着
        if (self.sjh.get_save("下半身下着表示フラグ") == 0 and nippse == 0)\
            or self.sjh.get_save("上半身はだけ状態") == 1:
            clothings = ["上半身上着1","上半身上着2","ボディースーツ","ワンピース","着物","レオタード"]
            for key, value in cloth_dict.items():
                if key in clothings:
                    prompt = csvm.get_df(clo,"衣類名", value, "プロンプト")
                    if prompt != "ERROR":
                        prompt = f"(wearing {prompt}:1.3)"
                        nega = csvm.get_df(clo,"衣類名", value, "ネガティブ")
                        self.add_element("cloth", prompt, nega)

        # 下半身上着
        if (pantse == 0 and pussye == 0)\
            or self.sjh.get_save("下半身ずらし状態") == 1:
            clothings = ["下半身上着1","下半身上着2","スカート", "ズボン",]
            for key, value in cloth_dict.items():
                if key in clothings:
                    prompt = csvm.get_df(clo,"衣類名", value, "プロンプト")
                    if prompt != "ERROR":
                        prompt = f"(wearing {prompt}:1.3)"
                        nega = csvm.get_df(clo,"衣類名", value, "ネガティブ")
                        self.add_element("cloth", prompt, nega)

        for key, value in cloth_dict.items():
            clothings = ["帽子", "アクセサリ", "腕部装束", "外衣", "上半身下着2",\
                         "下半身下着1", "その他1", "その他2", "その他3", "靴下", "靴"]
            if key in clothings:
                prompt = csvm.get_df(clo,"衣類名", value, "プロンプト")
                nega = csvm.get_df(clo,"衣類名", value, "ネガティブ")
                self.add_element("cloth", prompt, nega)

        if nob: #ノーブラ
            prompt = csvm.get_df(clo,"衣類名","ノーブラ","プロンプト")
            nega = csvm.get_df(clo,"衣類名","ノーブラ","ネガティブ")
            self.add_element("cloth", prompt, nega)

        elif burae == 1: #ブラ見える
            if self.sjh.get_save("上半身下着2") != 0:
                prompt = csvm.get_df(clo,"衣類名",self.sjh.get_save("upper_underwear"),"プロンプト")
                if prompt != "ERROR":
                    prompt = f"(wearing {prompt}:1.3)"
                    nega = csvm.get_df(clo,"衣類名", value, "ネガティブ")
                    self.add_element("cloth", prompt, nega)

        if nop: #ノーパン
            prompt = csvm.get_df(clo,"衣類名","ノーパン","プロンプト")
            nega = csvm.get_df(clo,"衣類名","ノーブラ","ネガティブ")
            self.add_element("cloth", prompt, nega)
        elif burae == 1: #パンツ見える
            if self.sjh.get_save("上半身下着2") != 0:
                prompt = csvm.get_df(clo,"衣類名",self.sjh.get_save("upper_underwear"),"プロンプト")
                if prompt != "ERROR":
                    prompt = f"(wearing {prompt}:1.3)"
                    nega = csvm.get_df(clo,"衣類名", value, "ネガティブ")
                    self.add_element("cloth", prompt, nega)

        # panty aside
        # 挿入とクンニ
        if (self.sjh.get_save("マスターがＶ挿入") != 0 )\
            or(self.sjh.get_save("マスターがＡ挿入") != 0)\
            or (self.sjh.get_save("コマンド") == "1"):
            if self.sjh.get_save("下半身下着2") != 0:
                self.add_element("cloth", "(pantie aside)", None)

    # パンツの柄描画
    def create_panty_element(self):
        if not self.uniquepanty:
            #ふつうのパンツ（固有パンツ以外）
            prompt = csvm.get_df("Cloth.csv","衣類名", self.panty,"プロンプト")
            nega = csvm.get_df("Cloth.csv","衣類名", self.panty,"ネガティブ")
            self.add_element("cloth", prompt, nega)
        else:
            #固有パンツの場合
            prompt = csvm.get_df("Uniquecloth.csv","キャラ名", self.name,"下半身下着プロンプト")
            nega = csvm.get_df("Uniquecloth.csv","キャラ名", self.name,"下半身下着ネガティブ")
            self.add_element("cloth", prompt, nega)

    def create_dish_element(self):
        prompt = csvm.get_df("Dish.csv","名称", self.dish,"プロンプト")
        nega = csvm.get_df("Dish.csv","名称", self.dish,"ネガティブ")
        #暫定でtrain
        self.add_element("train", prompt, nega)


    def prompt_debug(self):
        """
        呪文作成前にどんな要素を格納されてるか調べるやつ
        """
        for key, value in self.prompt.items():
            print (f'prompt:::{key}:::{value}')

        for key, value in self.negative.items():
            print (f'nega:::{key}:::{value}')

        for key, value in self.flags.items():
            print (f'flags:::{key}:::{value}')
    