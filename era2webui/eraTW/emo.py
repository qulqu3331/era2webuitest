"""
Expression クラスは、キャラクターの表情や感情状態に基づいたエレメントを生成するためのクラスだ。
このクラスは、PromptMaker クラスを継承し、特定のシチュエーションやキャラクターの状態に応じて、
細かい感情表現をプロンプトに追加するためのメソッドを提供するぜ。

主な機能:
- 様々な感情状態や状況を表すためのエレメントを管理する辞書 `emopro` と `emonega` を持つ。
- キャラクターの目の状態や、他のキャラクターとの関係を制御するためのフラグ `emoflags` を管理する。
- 感情の強度やレベルを管理する `emolevel` 辞書を持つ。

使用方法:
- SJH インスタンスを引数として、Expression インスタンスを作成する。
- 各種感情エレメント生成メソッドを呼び出して、プロンプトを構築する。

例：
expression = Expression(sjh_instance)
prompt = expression.create_emotion_elements()

Raises:
- KeyError: 必要なデータがSJHインスタンスから取得できない場合に発生する可能性がある。

Returns:
- dict: キャラクターの感情や状態を表すエレメントの辞書。
"""
import random
from eraTW.suberaTW import PromptMaker
from module.csv_manager import CSVMFactory
csvm = CSVMFactory.get_instance()


# 暫定でバリアント毎に分けたけど更新が面倒になるのでホントはまとめたい。


class Expression(PromptMaker):
    """"
    Args:
        PromptMaker (sjh): SaveJsonHanderインスタンス
    """
    def __init__(self, sjh):
        super().__init__(sjh)
        self.emopro =  {'眠り':"", '体力':"", '気力':"", '酔':"", '目色':"", '目つき':"", '羞恥':"",\
                        '恐怖':"", '反発':"", '苦痛':"", '絶頂':"", 'ハート':"", '退屈':"",\
                        'トキメキ':"", '顔つき':""}
        self.emonega = {'眠り':"", '体力':"", '気力':"", '酔':"", '目色':"", '目つき':"", '羞恥':"",\
                        '恐怖':"", '反発':"", '苦痛':"", '絶頂':"", 'ハート':"", '退屈':"",\
                        'トキメキ':"", '顔つき':""}
        self.emoflags = {"ClosedEyes":False,"主人公以外が相手":False,"drawbreasts":False,\
                         "drawvagina":False,"drawanus":False,"強い情動":False,"苦痛":False,\
                         "好意":False}
        self.emolevel = {"快感Lv":0,"快楽強度":0,"睡眠深度":0,"体力Lv":0,"気力Lv":0,"酩酊Lv":0,\
                         "絶頂Lv":0,"苦痛Lv":0,"恐怖Lv":0,"恥情Lv":0,"好意Lv":0,"退屈Lv":2}
                        #退屈Lvは元のコードに従い退屈Lvは2で始まるあとで変えるかも
        self.emo = self.get_csvname("emotion")

    def add_element(self, elements, prompt, nega):
        """
        add_element メソッドをオーバーライドして、Expression クラス固有の辞書に
        プロンプトを追加するようにする。

        Args:
            elements (str): プロンプト要素のキー。
            prompt (str): 追加するプロンプトのテキスト。Noneまたは'ERROR'でなければ追加。
            nega (str): 追加するネガティブプロンプトのテキスト。Noneまたは'ERROR'でなければ追加。
        """
        if elements not in self.emopro:
            raise KeyError(f" '{elements}' なんてプロンプト要素、ないぜ！")

        if prompt is not None and prompt != "ERROR":
            self.emopro[elements] += prompt
        if nega is not None and nega != "ERROR":
            self.emonega[elements] += nega

    def generate_emotion(self):
        """
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
        if self.sjh.get_save("scene") == "TRAIN":
            self.create_ahe_element() #絶頂
            self.create_pain_element() #痛み
            self.create_fear_element() #恐怖
            self.create_love_element() #愛情表現 ハートを飛ばす不健全っぽい方

        #目の描写がないならその要素は空文字で抹消
        if not self.emoflags["ClosedEyes"]:
            #self.create_eyes_element()#目色 eraTWは非対応につきコメントアウト
            self.emopro["目つき"] = ""
            self.emonega["目つき"] = ""
        #主人公が相手でない時は以下2つのプロンプトを抹消
        if not self.emoflags["主人公以外が相手"]:
            self.emopro["ハート"] = ""
            self.emonega["ハート"] = ""
            self.emopro["反発"] = ""
            self.emonega["反発"] = ""

        emopro_values = [value for value in self.emopro.values() if value.strip()]
        emonega_values = [value for value in self.emonega.values() if value.strip()]
        #カンマとスペースを足してヒトツナギに
        prompt = ", ".join(emopro_values)
        negative = ", ".join(emonega_values)
        self.prompt_debug()
        return prompt,negative

    def create_eyes_element(self):
        """
        eraTWでは非対応の要素
        霊夢の目が青かったりするのは気になるのであとで実装するかも
        """
        eyecolor = self.sjh.get_save("eyecolor")
        prompt = f"{eyecolor}eyes"
        self.add_element("目色", prompt, None)


    def emotionflags(self):
        # TEQUIP:18 アイマスク (eraTW)
        if "18" in self.sjh.get_save("equip"):
            self.emoflags["ClosedEyes"] = True

        if self.sjh.get_save("scene") == "TRAIN":
            if self.sjh.get_save("PLAYER") != 0:
                self.emoflags["主人公以外が相手"] = True
                print("助手とか")
        else:
            if self.sjh.get_save("主人以外が相手") == 1:
                self.emoflags["主人公以外が相手"] = True
                print("主人以外が相手のイベント")


    def emolevels(self):
        """
        パラメーターに応じたレベルのチェックはここでやる
        処理の速度よりわかりやすさを優先
        """
        self.check_hp_level()        #体力Lv
        self.check_boredom_level()   #退屈Lv
        self.check_love_level()      #好意Lv
        self.check_drunk_level()     #酩酊Lv
        self.check_resist_level()    #反発刻印
        if self.sjh.get_save("scene") == "TRAIN":
            #調教中のみ意味を持つパラメーター
            #現時点のeraTW対応仕様
            #移動以外のコマンドは全部 TRAIN だが今後のため
            self.check_pleasure_level()  #快感Lvと快感強度
            self.check_pain_level()      #苦痛Lv
            self.check_fear_level()      #恐怖Lv
            self.check_orgasm_level()    #絶頂Lv
            self.check_embarras_level()  #恥情Lv


    def create_sleep_element(self):
        """
        #148,睡眠薬強度
        #(0=通常睡眠　1=深い睡眠　2=非常に深い睡眠　3=昏睡)
        """
        emo = self.emo
        sleeping_pill = self.sjh.get_save("睡眠薬")
        faint = self.sjh.get_save("失神")
        if sleeping_pill is not None and faint is not None:
            if sleeping_pill > 0 or faint >= 2:
                睡眠深度 = self.sjh.get_save("睡眠深度")
                prompt = csvm.get_df(emo,"名前", 睡眠深度,"プロンプト")
                nega = csvm.get_df(emo,"名前", 睡眠深度,"ネガティブ")
                self.emoflags["ClosedEyes"] = True
                self.add_element("眠り", prompt, nega)
                # 暫定で表情変化なしにする。
                self.flags["drawface"] = 0
                # でも欲情と絶頂はちょっと効くように
                pleasure_level = self.emolevel.get("快感Lv")
                prompt = csvm.get_df_2key(emo, "状態", "快感Lv", "level", pleasure_level, "プロンプト")
                self.add_element("眠り", prompt, None)
                if self.sjh.get_save("絶頂の強度") > 0:
                    self.add_element("眠り", "(motion lines:1.2),(blush:0.9)", None)


    def create_hp_element(self):
        """
        死亡 0~5 元気いっぱいまでの5段階
        瀕死の時は目つきに特別なプロンプトを追加
        """
        emo = self.emo
        hp_level = self.emolevel["体力Lv"]
        prompt = csvm.get_df_2key(emo, "状態", "体力Lv", "level", hp_level, "プロンプト")
        self.add_element("体力", prompt, None)
        if hp_level == 1:
            # 瀕死状態のプロンプトを追加
            eyeprompt = "(half closed eyes,empty eyes:1.5)"
            self.add_element("目つき", eyeprompt, None)


    def create_mp_element(self):
        """
        未実装
        """
        emo = self.emo
        prompt = csvm.get_df_2key(emo, "状態", "気力Lv", "level", 1, "プロンプト")
        self.add_element("気力", prompt, None)
        self.emoflags["強い情動"] = True


    def create_drunk_element(self):
        """
        eraTWの挙動に即した実装になっていない
        @ALCOHOL_FACE(TARGET) で4段階の状態が取得できる
        あとで
        """
        emo = self.emo
        drunk_level = self.emolevel["酩酊Lv"]
        prompt = csvm.get_df_2key(emo, "状態", "酩酊Lv", "level", drunk_level, "プロンプト")
        self.add_element("酔", prompt, None)


    def create_pain_element(self):
        """
        ClosedEyesのフラグ操作あり
        """
        emo = self.emo
        pain_level = self.emolevel["苦痛Lv"]

        if pain_level >= 2:
            self.emoflags["強い情動"] = True
            self.emoflags["苦痛"] = True
            # 重い苦痛の追加プロンプト
            ra = random.randrange(2)
            if ra == 0: #目と口をギュッと閉じるパターン
                prompt = csvm.get_df_2key(emo, "状態", "苦痛Lv", "level", 2, "プロンプト")
                nega = csvm.get_df_2key(emo, "状態", "苦痛Lv", "level", 2, "ネガティブ")
                self.emoflags["ClosedEyes"] = True
                self.add_element("苦痛", prompt, nega)
            elif ra == 1: #目を見開くパターン
                prompt = csvm.get_df_2key(emo, "状態", "苦痛Lv", "level", 3, "プロンプト")
                nega = csvm.get_df_2key(emo, "状態", "苦痛Lv", "level", 3, "ネガティブ")
                self.add_element("苦痛", prompt, nega)
                self.add_element("目つき", "(startled eyes,.-.),", "smile")
        elif pain_level == 1:
            prompt = csvm.get_df_2key(emo, "状態", "苦痛Lv", "level", pain_level, "プロンプト")
            self.add_element("苦痛", prompt, None)


    def create_fear_element(self):
        """
        キャラクターの恐怖レベルに基づいて、恐怖のエレメントを生成するメソッドだ。
        恐怖の表現をプロンプトとして追加する。恐怖を感じているキャラクターの目は驚いた表情をするから、
        そういった細かいニュアンスも表現するんだ。
、
        CSVManager を使用して恐怖レベルに応じた適切なプロンプトを取得する。
        最後に、このプロンプトを恐怖と目つきのエレメントとして追加するぜ。

        '恐怖' エレメントはキャラクターの表情や振る舞いに恐怖を反映させ、
        '目つき' エレメントはその恐怖が目に現れることを表現する。
        """
        emo = self.emo
        fear_level = self.emolevel.get("恐怖Lv")
        prompt = csvm.get_df_2key(emo, "状態", "恐怖Lv", "level", fear_level, "プロンプト")
        self.add_element("恐怖", prompt, None)
        self.add_element("目つき", "(startled eyes,.-.),", "smile")


    def create_ahe_element(self):
        """
        これはAI魔理沙に書いてもらおうとするとポリシー違反になる
        絶頂Lvは絶頂が重なった数
        快楽強度は eraTW{TCVAR:106}
        """
        # 淫乱持ちは少しアヘりやすい
        # 恋慕と排他じゃないバリアントでは望まなくても淫乱がついてしまうので控えめの補正にする
        emo = self.emo
        if "淫乱" in self.sjh.get_save("talent"):
            if self.emolevel["快楽強度"] > 0:
                self.emolevel["快楽強度"] += 2

        if self.emolevel["絶頂Lv"] == 4:  #四重絶頂の意
            self.emolevel["快楽強度"] += 6
        ahe_strength = self.emolevel["快楽強度"]
        # 基本の絶頂エフェクト
        if ahe_strength > 0:
            prompt = csvm.get_df_2key(emo, "状態", "快楽強度", "level", ahe_strength, "プロンプト")
            self.add_element('絶頂',prompt, None)
            self.add_element("目つき", ", (startled eyes)", None)
        if ahe_strength >= 4: #強度4　2重強絶頂以上でアヘり始める
            if ahe_strength <= 14:
                prompt = csvm.get_df_2key(emo, "状態", "快楽強度", "level", ahe_strength, "プロンプト")
                self.add_element('絶頂',prompt, None)
            #絶頂強度14～16 かなりアヘ顔
            elif ahe_strength <= 16:
            #確率でheadback 20%
            #headbackは表情描写と衝突して絵が壊れるっぽい
                ra = random.randrange(4)
                if ra == 0:
                    self.add_element('絶頂',", <lora:conceptHeadbackArched_v10:1:CT>,(HEADBACK)", None )
                    self.emoflags["ClosedEyes"] = True
                else:
                    self.add_element('絶頂',", <lora:ahegao_v1:1.5:1:lbw=F>,(ahegao),open mouth,drooling,saliva", None )
            #絶頂強度17超え 完全にアヘ顔
            else:
                prompt = csvm.get_df_2key(emo, "状態", "快楽強度", "level", ahe_strength, "プロンプト")
                self.add_element('絶頂',prompt, None)


    def create_embarras_element(self):
        """
        # embarras 1.2でもう十分なくらい恥ずかしそう blushが1.0ついている場合0.5位まで変化なし
        # 普通の調教だと恥情はあんまり上がらないが欲情で赤くなってるはず
        # embarrasよりshameの方がマイルド なはず
        """
        emo = self.emo
        embarras = self.emolevel["恥情Lv"]
        prompt = csvm.get_df_2key(emo, "状態", "快楽強度", "level", embarras, "プロンプト")
        self.add_element('羞恥',prompt, None)


        # ここからは素質・刻印等によるもの TRAIN以外でも反映＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

        # 反発 の判定-----------------------------------------------------------------
        # angerは口が歪んだりギャグみたいになる
        # Hostileはたまに幼い輪郭になる
        # furiousはへの字口が気になる
        # いずれも反発刻印3に見合うほどの憎悪は感じない


    def create_resist_element(self):
        """
        angerは口が歪んだりギャグみたいになる
        Hostileはたまに幼い輪郭になる
        furiousはへの字口が気になる
        いずれも反発刻印3に見合うほどの憎悪は感じな
        """
        emo = self.emo
        resist = self.emolevel["反発刻印"]
        # 反発刻印2
        if resist >= 2:
            prompt = csvm.get_df_2key(emo, "状態", "反発刻印", "level", resist, "プロンプト")
            self.add_element('反発',prompt, None)

        # 反発刻印1
        if resist >= 1:
            if not self.emoflags["ClosedEyes"]:
                self.emoflags["強い情動"] = True
                self.add_element("目つき", ", (glaring eyes:1.0)", None)

        # 従順1がつくまでは嫌われてると判断
        elif self.sjh.get_save("abl")["従順"] == 0:
            if "サド" in self.sjh.get_save("talent"): #frownは困り顔になって一部キャラに違和感があったので
                self.add_element('反発',", unamused", None)
            else:
                self.add_element('反発',", (frown:0.9)", None)


    def create_love_element(self):
        """
        キャラクターの好意レベルに基づいて、愛情のエレメントを生成するメソッドだ。
        このメソッドは、苦痛フラグの状態を考慮し、キャラクターが苦痛を感じていない場合、
        それかレベルの高いのマゾは愛情の表現を追加するんだ。なんというか業が深いな｡

        好意レベルは '好意Lv' として emolevel 辞書で管理され、
        CSVManager を使用してそのレベルに応じた適切なプロンプトを取得する。
        愛情のエレメントは、キャラクターの表情や振る舞いにハートマークや優しい表現を追加することで、
        その愛情を可視化するんだ。

        'ハート' エレメントは、キャラクターが持つ愛情や好意を表現し、
        シーンや状況に応じてその愛情の深さを表す。
        """
        emo = self.emo
        # 刻印レベルの苦痛フラグが立ってる場合、好意の表情をつけない。ただし高レベルマゾは例外
        if not self.emoflags["苦痛"] or self.sjh.get_save("abl")["マゾっ気"] >= 4:
            love_lv = self.emolevel["好意Lv"]
            prompt = csvm.get_df_2key(emo, "状態", "好意Lv", "level", love_lv, "プロンプト")
            self.add_element('ハート',prompt, None)


    def create_boredom_element(self):
        emo = self.emo
        boredom = self.emolevel["退屈Lv"]

        # 従順低い時のサドは挑戦的な顔
        if "サド" in self.sjh.get_save('talent'):
            self.add_element('退屈',", arrogance", None)
        else:
            # サド以外は退屈な顔
            prompt = csvm.get_df_2key(emo, "状態", "退屈Lv", "level", boredom, "プロンプト")
            self.add_element('退屈',prompt, None)


    def create_love_emotion_element(self):
        """
        恋心による表情の呪文を作るぜ！こいつは、強い情動がないときに特別な感情を表現するためのメソッドだ。
        恋する心が溢れる時、キャラクターの表情が変わるんだ。

        普段は見せない特別な笑顔や、心臓がバクバクする感じ、照れ笑いなど、恋によって引き出される感情を呪文に込めるんだ。
        性格や好意のレベルによって、たまにはこんな表情も見せてやるといい。

        このメソッドで、恋に満ちた独特の感情の呪文を生成するぜ！
        """
        # 刻印レベルの苦痛フラグが立ってる場合、好意の表情をつけない。ただし高レベルマゾは例外
        if not self.emoflags["苦痛"] and self.emoflags["好意"]:
            ra = random.randrange(20)
            if ra == 1:
                self.add_element('トキメキ',", (closed eyes smile,blushing:1.3)", None)
                self.emoflags["ClosedEyes"] = True
            if ra == 2:
                self.add_element('トキメキ',", (closed eyes smile,blushing:1.3),open mouth,", None)
                self.emoflags["ClosedEyes"]  = True
            if ra == 3:
                self.add_element('トキメキ',", (heart racing,blushing:1.3)", None)
            if ra == 4:
                self.add_element('トキメキ',", (delighted)", None)


#生来のTalentによる顔つき
    def create_talent_based_element(self):
        """
        このメソッドは、キャラクターの「Talent」に基づいてプロンプトを生成するんだ。
        CSVファイルに登録されている各タレントに対するプロンプトを取得して、適切なプロンプトを追加する。
        """
        tal = self.get_csvname("talent")
        talents_dict = {
            "たれ目傾向": ["臆病", "大人しい", "悲観的"],
            "ツリ目傾向": ["反抗的", "気丈", "プライド高い", "ツンデレ", "サド"],
            "魅力": ["魅力", "魅惑", "謎の魅力"],
            "頭よさそう": ["自制心", "快感の否定", "教育者", "調合知識"],
            "ドヤ顔": ["生意気", "目立ちたがり"],
            "無感情": ["無関心", "感情乏しい", "抑圧"]
        }

        for _, value_list in talents_dict.items():
            and_list = set(self.sjh.get_save('talent')) & set(value_list)
            for talent in and_list:
                prompt = csvm.get_df(tal, "名称", talent, "プロンプト")
                self.add_element("顔つき", prompt, None)


        # # 無感情 expressionlessは口を閉じる効果が高い。八の字眉傾向
        # # empty eyes
        # chk_list = ["無関心","感情乏しい","抑圧"]
        # and_list = set(self.sjh.get_save('talent')) & set(chk_list)
        # if (len(and_list)) > 0:
        #     if self.sjh.get_save("絶頂の強度") == 0:
        #         eyeprompt += "(empty eyes),"
        #         prompt += "expressionless,"
        #         negative += "((blush)),troubled eyebrows,"


        # #狂気 強調しないと滅多に光らないはず。キレたときとか条件付きで光るようにした。
        # chk_list = ["狂気","狂気の目"]
        # and_list = set(self.sjh.get_save('talent')) & set(chk_list)
        # if (len(and_list)) > 0:
        #     if self.sjh.get_save("mark")["反発刻印"] == 3: #反発3だとずっと光る
        #         eyeprompt += "(glowing eyes:1.4),"
        #     elif self.sjh.get_save("palam_up")["反感"] >= 500: #反感の上がるようなことをすると光る
        #         eyeprompt += "(glowing eyes:1.4),"
        #     else:
        #         eyeprompt += "glowing eyes," #きまぐれに光る？


    def check_pleasure_level(self):
        pleasure = self.sjh.get_save("palam_up")["快C"]\
                    +self.sjh.get_save("palam_up")["快B"]\
                    +self.sjh.get_save("palam_up")["快V"]\
                    +self.sjh.get_save("palam_up")["快A"]
        if pleasure >= 7500:
            self.emolevel["快感Lv"] = 4
            self.emoflags["強い情動"] = True
            self.add_element("目つき", "{rolling eyes|}", None)
        elif pleasure >= 3000:
            self.emolevel["快感Lv"] = 3
            self.emoflags["強い情動"] = True
        elif pleasure >= 1000:
            self.emolevel["快感Lv"] = 2
            self.emoflags["強い情動"] = True
        elif pleasure >= 1000:
            self.emolevel["快感Lv"] = 1
            self.emoflags["強い情動"] = True
        #別の値をつけているが､似たようなステータスなので
        ahe_strength = self.sjh.get_save("快楽強度")
        if ahe_strength == 3:
            self.emolevel["快楽強度"] = 3
        elif ahe_strength == 2:
            self.emolevel["快楽強度"] = 2
        elif ahe_strength == 1:
            self.emolevel["快楽強度"] = 1


    def check_hp_level(self):
        max_hp = self.sjh.get_save("最大体力")
        current_hp = self.sjh.get_save("体力")
        hp_ratio = current_hp / max_hp

        if current_hp <= 0:
            self.emolevel["体力Lv"] = 0  # 死亡（レベル5）
        elif hp_ratio <= 0.2:
            self.emolevel["体力Lv"] = 1  # 非常に低い体力
        elif hp_ratio <= 0.4:
            self.emolevel["体力Lv"] = 2  # 低い体力
        elif hp_ratio <= 0.6:
            self.emolevel["体力Lv"] = 3  # 中程度の体力
        elif hp_ratio <= 0.8:
            self.emolevel["体力Lv"] = 4  # 高い体力
        else:
            self.emolevel["体力Lv"] = 5  # 非常に高い体力（フル）


    def check_drunk_level(self):
        # 酔いの値を取得。存在しない場合は0とする
        drunk_value = self.sjh.get_save("酔い") \
                if self.sjh.get_save("酔い") is not None else 0

        if drunk_value < 1000:
            self.emolevel["酩酊Lv"] = 0
        elif drunk_value < 2000:
            self.emolevel["酩酊Lv"] = 1
        elif drunk_value < 3000:
            self.emolevel["酩酊Lv"] = 2
        elif drunk_value < 6000:
            self.emolevel["酩酊Lv"] = 3
        elif drunk_value < 10000:
            self.emolevel["酩酊Lv"] = 4
        else:
            self.emolevel["酩酊Lv"] = 5


    def check_pain_level(self):
        pain_value = self.sjh.get_save("palam_up")["苦痛"]

        if pain_value > 3000:
            self.emolevel["苦痛Lv"] = 2  # 重い苦痛
        elif pain_value > 500:
            self.emolevel["苦痛Lv"] = 1  # 軽い苦痛


    def check_fear_level(self):
        fear_value = self.sjh.get_save("palam_up")["恐怖"]
        if fear_value > 10000:
            self.emolevel["恐怖Lv"] = 5  # 極度の恐怖
        elif fear_value >= 6000:
            self.emolevel["恐怖Lv"] = 4  # 非常に強い恐怖
        elif fear_value >= 3000:
            self.emolevel["恐怖Lv"] = 3  # 強い恐怖
        elif fear_value >= 1000:
            self.emolevel["恐怖Lv"] = 2  # 明確な恐怖
        elif fear_value > 300:
            self.emolevel["恐怖Lv"] = 1  # 軽い恐怖


    def check_orgasm_level(self):
        C = self.sjh.get_save("Ｃ絶頂")
        B = self.sjh.get_save("Ｂ絶頂")
        V = self.sjh.get_save("Ｖ絶頂")
        A = self.sjh.get_save("Ａ絶頂")
        tajuu = sum(1 for value in [C, B, V, A] if value != 0)

        if tajuu > 4:
            self.emolevel["絶頂Lv"] = 4
        elif tajuu > 3:
            self.emolevel["絶頂Lv"] = 3
        elif tajuu > 2:
            self.emolevel["絶頂Lv"] = 2
        elif tajuu > 1:
            self.emolevel["絶頂Lv"] = 1


    def check_embarras_level(self):
        embarras = self.sjh.get_save("palam")["恥情"]
        embarras_up = self.sjh.get_save("palam_up")["恥情"]
        # '恥情'の値に基づいてLevelを設定
        if embarras >= 1000 and embarras <= 5000:
            self.emolevel["恥情Lv"] = 1
        elif embarras > 5000 and embarras <= 10000:
            self.emolevel["恥情Lv"] = 2
        elif embarras > 10000:
            self.emolevel["恥情Lv"] = 3
        # '恥情'の増加値に基づいてLevelを設定
        if embarras_up >= 500 and embarras_up < 1000:
            self.emolevel["恥情Lv"] = 4
        elif embarras_up >= 1000:
            self.emoflags["強い情動"] = True
            self.emolevel["恥情Lv"] = 5


    def check_resist_level(self):
        """
        刻印系はまとめてLevelに追加するかも
        """
        resist = self.sjh.get_save("mark")["反発刻印"]
        self.emolevel["反発刻印"] = resist


    def check_love_level(self):
        chk_list = ["恋慕","親愛","相愛"]
        and_list = set(self.sjh.get_save('talent')) & set(chk_list)
        if (len(and_list)) > 0:
            kyujun = self.sjh.get_save("palam_up")["恭順"]
            if kyujun < 5000:
                self.emolevel["好意Lv"] = 1
            elif 5000 <= kyujun < 15000:
                self.emolevel["好意Lv"] = 2
            else:
                self.emolevel["好意Lv"] = 3
            self.emoflags["好意"] = True


    def check_boredom_level(self):
        # 調教初期の表情 つまんなそうな顔
        # 何も指定しないとカワイイ笑顔になるのを防ぐためのデフォルト表情
        # scgpro 初対面シチュエーションが多いので軽めに200で解除する
        #初期化 値は 2 あとで直すかも
        if (self.sjh.get_save("abl")["従順"] > 3) or (self.sjh.get_save("好感度") > 50):
            self.emolevel["退屈Lv"] -= 1

        if (self.sjh.get_save("abl")["従順"] > 4) or (self.sjh.get_save("好感度") > 200):
            self.emolevel["退屈Lv"] -= 1
        if self.emoflags["強い情動"]: # 余裕ないときには退屈な表情はしない
            self.emolevel["退屈Lv"] = 0
    