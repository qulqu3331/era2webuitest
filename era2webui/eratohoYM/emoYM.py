from module.emo import Expression
from module.csv_manager import CSVMFactory
csvm = CSVMFactory.get_instance()
# 表情ブレンダー
# 表情のプロンプトは実行中に弄りたいのでいつかcsv化する

# 様々な表情の単語をブレンドしても良い顔ができない上に構図や絵柄に深刻な悪影響があることがわかった。
# 要素ごとにプロンプトを追加していくやり方ではすぐ限界が来る。


class ExpressionYM(Expression):
    def __init__(self, sjh):
        super().__init__(sjh)
        self.initialize_class_variables_emoYM()
        self.emolevelsYM()

    def initialize_class_variables_emoYM(self):
        """表情用判定に必要な変数の初期化
        YM用独自
        """
        self.eyecolor = self.sjh.get_save("eyecolor")#int
        self.equip = self.sjh.get_save("equip")#dict
        self.player = self.sjh.get_save("PLAYER")#int
        self.睡眠深度 = self.sjh.get_save("睡眠深度")
        self.abl = self.sjh.get_save("abl")#dict
        self.palam = self.sjh.get_save("palam")#dict
        self.palam_up = self.sjh.get_save("palam_up")#dict
        self.max_hp = self.sjh.get_save("最大体力")
        self.current_hp = self.sjh.get_save("体力")
        self.current_mp = self.sjh.get_save("気力")

        # 酔いの値を取得。存在しない場合は0とする
        self.drunk = self.sjh.get_save("酔い") if self.sjh.get_save("酔い") is not None else 0
        self.C = self.sjh.get_save("C絶頂")
        self.B = self.sjh.get_save("B絶頂")
        self.V = self.sjh.get_save("B絶頂")
        self.A = self.sjh.get_save("B絶頂")
        self.mark = self.sjh.get_save("mark")
        self.好感度 = self.sjh.get_save("好感度")

        #emoだけで使うフラグをスーパークラスのdictへ追加
        self.flags["ClosedEyes"] = False
        self.flags["強い情動"] = False
        self.flags["苦痛"] = False
        self.flags["好意"] = False
        self.flags["Love"] = False


    def emolevelsYM(self):
        """
        パラメーターに応じたレベルのチェックはここでやる
        処理の速度よりわかりやすさを優先
        レベルチェックメソッドの上書きや独自のメソッドがあるものだけ
        """
        self.check_hp_level()        #体力Lv
        if self.scene == "TRAIN":
            #調教中のみ意味を持つパラメーター
            self.check_pleasure_level()  #快感Lvと快感強度



    def generate_emotion(self):
        """
        #オーバーライド
        generate_emotionはキャラクターの感情の波を捉え、
        プロンプトとネガティブプロンプトへと変換するメソッドだ。
        このメソッドは、ただエレメントを生成するだけじゃない。
        キャラクターの心の深層に潜むフラグもしっかりと管理して、それぞれの感情表現を細かく調整するんだ。

        トレーニング中のキャラクターには特別な扱いを施し、
        その感情の高まりや痛み、恐怖までもが細かく表現される。
        さらに、目の状態や他キャラとの関係に関するフラグも考慮に入れて、
        エレメントを生成するんだ。

        このメソッドは、各種フラグに応じて、サブメソッドを呼び出し、
        キャラクターの心を豊かに表現するエレメントを組み立てる。

        Returns:
            tuple: (プロンプト文字列, ネガティブプロンプト文字列)
            この二つの文字列は、キャラクターの深層心理を探るための鍵となるエレメントで満ちているぜ。
        """
        self.emotionflags()#
        self.emolevels()   #emolevelの一括設定

        self.create_sleep_element() #睡眠中眠りぬ深さ
        self.create_hp_element() #体力
        self.create_mp_element() #気力
        self.create_drunk_element() #酔

        self.create_embarras_element()#羞恥
        self.create_resist_element() #反発
        self.create_boredom_element() #退屈
        self.create_love_emotion_element() #トキメキ
        self.create_talent_based_element() #顔つき
        #調教に対する反応 TRAIN中のみ反映
        if self.scene == "TRAIN":
            self.create_ahe_element() #絶頂
            self.create_pain_element() #痛み
            self.create_fear_element() #恐怖
            self.create_love_element() #愛情表現 ハートを飛ばす不健全っぽい方
        #目の描写がないならその要素は空文字で抹消
        if not self.flags["ClosedEyes"]:
            self.emopro["目つき"] = ""
            self.emonega["目つき"] = ""
        #主人公が相手でない時は以下2つのプロンプトを抹消
        if self.flags["主人公以外が相手"]:
            self.emopro["ハート"] = ""
            self.emonega["ハート"] = ""
            self.emopro["反発"] = ""
            self.emonega["反発"] = ""
        self.prompt_debug_emo()
        emopro_values = [value for value in self.emopro.values() if value.strip()]
        emonega_values = [value for value in self.emonega.values() if value.strip()]
        #カンマとスペースを足してヒトツナギに
        prompt = ", ".join(emopro_values)
        negative = ", ".join(emonega_values)
        return prompt,negative


    def emotionflags(self):
        #オーバーライド
        # TEQUIP:41 目拘束具関連 (YM)
        if 41 in self.tequip.get("equip", {}):
            self.flags["ClosedEyes"] = True

        if self.scene == "TRAIN":
            if self.player != 0:
                self.flags["主人公以外が相手"] = True
                print("助手とか")
        else:
            if self.flags["主人公以外が相手"]:
                print("主人以外が相手のイベント")


    def check_pleasure_level(self):
        """
        オーバーライド
        """
        pleasure = self.palam_up.get("快C")\
                    + self.palam_up.get("快B")\
                    + self.palam_up.get("快V")\
                    + self.palam_up.get("快A")

        if pleasure < 100:
            self.emolevel["快感Lv"] = 0
        elif pleasure < 1000:
            self.emolevel["快感Lv"] = 1
        elif pleasure < 3000:
            self.emolevel["快感Lv"] = 2
        elif pleasure < 7500:
            self.emolevel["快感Lv"] = 3
        elif pleasure > 7500:
            self.emolevel["快感Lv"] = 4

        #別の値をつけているが､似たようなステータスなので
        if self.sjh.get_save("絶頂の強度") is not None:
            self.emolevel["快楽強度"] = self.sjh.get_save("絶頂の強度") 


    def check_hp_level(self):
        """
        オーバーライド
        """
        # 体力が減ると汗をかく
        # 現在地が閾値より低い または MAXから〇〇以上減ってる

        damage =self. max_hp - self.current_hp
        if damage > 50:
            if self.current_hp < 700:
                self.emolevel["体力Lv"] = 1
            elif self.current_hp < 1100:
                self.emolevel["体力Lv"] = 2
            else:
                if damage in range(200,400):
                    self.emolevel["体力Lv"] = 5
                elif damage in range(400,600):
                    self.emolevel["体力Lv"] = 4
                elif damage in range(600,800):
                    self.emolevel["体力Lv"] = 3
                elif damage in range(800,1000):
                    self.emolevel["体力Lv"] = 2
                elif damage >= 1000:
                    self.emolevel["体力Lv"] = 1

        # もう止めないとまずいな感を出す
        if self.current_hp < 500:
            self.emolevel["体力Lv"] = 1


    def create_mp_element(self):
        """独自
        #気力がないとぐったりする
        """
        if self.current_mp < 100:
            self.flags["強い情動"] = True
            self.add_element("気力", "(she is utterly exhausted:1.3),sleepy", "empty eyes,looking away")


    def create_talent_based_element(self):
        """
        #オーバーライド
        #無感情 expressionlessは口を閉じる効果が高い。八の字眉傾向
        #生来のTalentによる顔つき
        このメソッドは、キャラクターの「Talent」に基づいてプロンプトを生成するんだ。
        CSVファイルに登録されている各タレントに対するプロンプトを取得して、適切なプロンプトを追加する。
        """
        tal = "Talent.csv"
        talents_dict = {
            "たれ目傾向": ["臆病", "大人しい", "悲観的"],
            "ツリ目傾向": ["反抗的", "気丈", "プライド高い", "ツンデレ", "サド"],
            "魅力": ["魅力", "魅惑", "謎の魅力"],
            "頭よさそう": ["自制心", "快感の否定", "教育者", "調合知識"],
            "ドヤ顔": ["生意気", "目立ちたがり"],
            "無感情": ["無関心", "感情乏しい", "抑圧"]
        }

        for _, value_list in talents_dict.items():
            and_list = set(self.talent) & set(value_list)
            for talent in and_list:
                prompt = csvm.get_df(tal, "名称", talent, "プロンプト")
                self.add_element("顔つき", prompt, None)


        chk_list = ["無関心","感情乏しい","抑圧"]
        and_list = set(self.talent) & set(chk_list)
        if (len(and_list)) > 0:
            if self.絶頂の強度 == 0:
                eyeprompt = "(empty eyes),"
                prompt = "expressionless,"
                negative = "((blush)),troubled eyebrows,"
                self.add_element("顔つき", prompt, negative)


        #狂気 強調しないと滅多に光らないはず。キレたときとか条件付きで光るようにした方がいいかも。した。
        chk_list = ["狂気","狂気の目"]
        and_list = set(self.talent) & set(chk_list)
        resist = self.emolevel["反発刻印"]
        if (len(and_list)) > 0:
            if resist == 3: #反発3だとずっと光る
                eyeprompt = "(glowing eyes:1.4),"
                self.add_element("目つき", eyeprompt, None)
            elif self.palam_up.get("反感") >= 500: #反感の上がるようなことをすると光る
                eyeprompt = "(glowing eyes:1.4),"
                self.add_element("目つき", eyeprompt, None)
            else:
                eyeprompt = "glowing eyes," #きまぐれに光る？
                self.add_element("目つき", eyeprompt, None)

