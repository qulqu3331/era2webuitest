from module.csv_manager import CSVMFactory
from module.promptmaker import PromptMaker
from eratohoYM.emoYM import ExpressionYM

csvm = CSVMFactory.get_instance()
class PromptMakerYM(PromptMaker):
    def __init__(self,sjh):
        super().__init__(sjh)
        #YM独自の createメソッド用のキーを追加 situation keyで済むかはあとでロジック確認
        self.prompt["train_after"] = ""
        self.negative["train_after"] = ""
        self.prompt["train_beffore"] = ""
        self.negative["train_beffore"] = ""
        self.prompt["event"] = ""
        self.negative["event"] = ""
        self.prompt["equip"] = ""
        self.negative["equip"] = ""
        self.initialize_class_variablesYM()

    def initialize_class_variablesYM(self):
        #独自メソッド YM独自の変数の初期化
        #TW対応で作ったスーパークラスPromptMakerは変数名をかなり変えたの
        #ここでは元のコードの変数名に従う
        self.N挿入Gスポ責め = 614
        self.N挿入子宮口責め = 615
        self.N正常位 = 20
        self.N対面座位 = 22
        self.N対面立位 = 27
        self.N後背位 = 21
        self.N背面座位 = 23
        self.N背面立位 = 28
        self.Nパイズリ = 42
        self.Nナイズリ = 56
        self.N膣装備 = 20
        self.Nアナル装備 = 25

        self.Scene = "" #頭文字大文字と小文字は別物だけどわかりにくいあとで変えるか
        self.comNo = self.sjh.get_save("コマンド")
        self.prev = self.sjh.get_save("前回コマンド")
        #saveの値で初期化しているがcreate_location_elementで判定後代入している
        self.location = self.sjh.get_save("野外プレイの場所")
        self.expose = self.sjh.get_save("野外プレイの状況")
        self.hp = self.sjh.get_save("体力")
        self.equip = self.sjh.get_save("equip")
        self.palam_up = self.sjh.get_save("palam_up")
        self.hair_cum = self.sjh.get_save("髪の汚れ") #ビット演算
        self.b_cum = self.sjh.get_save("胸の汚れ") #ビット演算
        self.膣内に射精 = self.sjh.get_save("膣内に射精")
        self.アナルに射精 = self.sjh.get_save("アナルに射精")
        self.髪に射精 = self.sjh.get_save("髪に射精")
        self.顔に射精 = self.sjh.get_save("顔に射精")
        self.口に射精 = self.sjh.get_save("口に射精")
        self.胸に射精 = self.sjh.get_save("胸に射精")
        self.腹に射精 = self.sjh.get_save("腹に射精")
        self.腋に射精 = self.sjh.get_save("腋に射精")
        self.手に射精 = self.sjh.get_save("手に射精")
        self.秘裂に射精 = self.sjh.get_save("秘裂に射精")
        self.竿に射精 = self.sjh.get_save("竿に射精")
        self.尻に射精 = self.sjh.get_save("尻に射精")
        self.太腿に射精 = self.sjh.get_save("太腿に射精")
        self.足で射精 = self.sjh.get_save("足で射精")
        self.主人が射精 = self.sjh.get_save("主人が射精")



    def generate_prompt(self):
        #オーバーライド メソッド
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
        self.create_situation_element()#スーパークラスメソッド
        self.preceding() #独自メソッド
        self.get_kaizoudo() #オーバーライド
        self.create_location_element()#オーバーライドメソッド
        self.check_live_time() #独自メソッド

        #特殊イベントでないときは"scene"の値でcsvを検索する
        if not self.scene in ["BEFORE","TRAIN","AFTER"]:
            self.create_event_element() #独自メソッド

        if self.scene == "BEFORE":
            self.create_train_beffore_element() #独自メソッド

        if self.scene == "TRAIN":
            self.create_train_element()#オーバーライド
            self.create_equip_element()#オーバーライド
            #TRAINに限定しないと料理中に射精とかが起こる
            self.create_cum_element()#オーバーライド
            if self.flags["drawvagina"]:
                self.create_juice_element()#スーパー
                self.create_traineffect_element() #スーパー
                self.create_stain_element()#オーバーライド

        if self.scene == "AFTER":
            self.create_train_after_element()

        if self.flags["drawchara"]: # 人を描画しない場合は処理をスキップ
            self.create_chara_element() #オーバーライド
            self.create_body_element()  #オーバーライド
            self.create_effect_element()#妊娠

        if self.flags["drawface"]:  # 顔を描画しない場合は処理をスキップ
            self.create_hair_element()#髪
            self.create_hair_color_element()#独自メソッド
            pm_var = self.gather_instance_data()
            emo= ExpressionYM(pm_var) #表情
            emopro,emonega = emo.generate_emotion() #表情
            self.add_element("emotion", emopro, emonega)

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


    def preceding(self):
        # 独自メソッド. スーパークラスの方にも取り込むかも
        # order自体を変化させる前処理
        # たとえば
        # 条件によりコマンド差し替え（乳サイズでパイズリ→ナイズリ
        # キャラ差し替え　EXフラグが立っていたらEXキャラ用の名前に変更する
        # など
        # コマンドの差し替え
        # 挿入Gスポ責め/挿入子宮口責めのとき、派生元により前からアングルか後ろからアングルかで変更
        if self.comNo in (self.N挿入Gスポ責め,self.N挿入子宮口責め):
            if self.prev in (self.N正常位,self.N対面座位,self.N対面立位):
                self.comNo = self.N挿入Gスポ責め
            elif self.prev in (self.N後背位,self.N背面座位,self.N背面立位):
                self.comNo = self.N挿入子宮口責め

        # 巨乳未満のキャラのパイズリはナイズリに変更
        # (ちんちんが隠れてしまうような描写は普乳を逸脱しているため)
        if not ("巨乳" in self.talent) or ("爆乳" in self.talent):
            if self.comNo == self.Nパイズリ:
                self.comNo = self.Nナイズリ

        # メモ　EXキャラに変更するときはCFLAG:0をみてtargetを変更する。未実装


    def create_location_element(self):
        #オーバーライド メソッド
        # 調教開始前は装備なし
        #ロケーション
        #YMは調教部屋固定？他にあれば追加
        #3種以外のシーンではこのメソッドは何もしない
        if self.scene not in ["TRAIN", "AFTER", "BEFORE"]:
            return

        loc = "Location.csv"

        if self.scene in ["TRAIN","AFTER"]:
            # TEQUIP:53 お風呂場プレイ
            if 53 in self.equip:
                location = "お風呂場"
            # TEQUIP:53 野外プレイ
            elif 52 in self.equip:
                # yagai1 のような文字列で指定する locationはintなのでstrに変換
                location = "yagai"+ str(self.location)
                # ギャラリー
                if self.expose == 1:
                    prompt = "people in the background,passing by,"
                elif self.expose == 2:
                    prompt = "(people in the background,Surrounded by a crowd),"
                elif self.expose >= 3:
                    prompt = "(people in the background,Surrounded by a crowd,Attracting Attention:1.2),"
                self.add_element("location", prompt, None)
            else:
                location = "調教部屋"

        if self.scene == "BEFORE": # BEFOREなら調教部屋
            location = "調教部屋"

        prompt = csvm.get_df(loc,"名称",location,"プロンプト")
        negative = csvm.get_df(loc,"名称",location,"ネガティブ")
        self.add_element("location", prompt, negative)


    def create_train_beffore_element(self):
        #YM独自メソッド
        #------------ここまでTRAIN-ここからBEFORE---------------------
        #今のところ一般シーンとやってること同じ
        #同じならば処理を統一できないか?
        #統一できるならスーパークラスにまとめる
        eve = "Event.csv"
        self.flags["drawchara"] = bool(csvm.get_df(eve,"名称","BEFORE","キャラ描画"))
        self.flags["drawface"] = bool(csvm.get_df(eve,"名称","BEFORE","顔描画"))
        self.flags["drawbreasts"] = bool(csvm.get_df(eve,"名称","BEFORE","胸描画"))
        self.flags["drawvagina"] = bool(csvm.get_df(eve,"名称","BEFORE","ヴァギナ描画"))
        self.flags["drawanus"] = bool(csvm.get_df(eve,"名称","BEFORE","アナル描画"))
        prompt = csvm.get_df(eve,"名称","BEFORE","プロンプト")
        negative = csvm.get_df(eve,"名称","BEFORE","ネガティブ")
        self.add_element("train_beffore", prompt, negative)


    def create_train_element(self):
        """
        コマンドに対応するプロンプトを生成するんだ。
        CSVファイルから読み込んだコマンド番号に基づいて、適切なプロンプトとネガティブプロンプトを組み立てるぜ。

        行動が成功したか失敗したかによって処理が分岐するから、それもしっかりチェックしてくれよな。
        成功した場合は、CSVから読み込んだ情報に基づいてプロンプトを作成する。失敗した場合は、拒否プロンプトを使うんだ。
        # drawchara drawface drawbreasts drawvagina drawanus
        """
        tra = "Train.csv"
        eve = "Event.csv"

        # self.succ 成功で1、失敗で0だが
        # 「成否判定なしの成功」でも0をとることがある
        # 「成否判定あり」かつ フラグが失敗　のときのみ拒否プロンプトを参照する
        # YMの場合、「成否判定の有無」を取得するすべが見つかっていないので、Train.csvに手動で記述することにした
        if bool(csvm.get_df(tra,"コマンド番号",self.comNo,"成否判定の有無")) and (self.succ == 0):# このやりかたでboolに変換すると空欄=>文字列ERROR=>TRUEになるのがちょっと厄介
            deny = csvm.get_df(tra,"コマンド番号",self.comNo,"拒否プロンプト")
            if deny != "ERROR":
                # 拒否プロンプトがERRORでない場合、拒否プロンプトを出力
                nega = csvm.get_df(tra,"コマンド番号",self.comNo,"拒否ネガティブ")
                self.add_element("train", deny, nega)
                self.flags["drawchara"] = True
                self.flags["drawface"] = True
                return
        else:
            # Train.csvに定義された体位から読み取ったキャラ描画、顔描画、胸描画のフラグ（0か1が入る)
            #ブール値に変換
            self.flags["drawchara"] =  bool(csvm.get_df(tra,"コマンド番号",self.comNo,"キャラ描画"))
            self.flags["drawface"] =  bool(csvm.get_df(tra,"コマンド番号",self.comNo,"顔描画"))
            self.flags["drawbreasts"] =  bool(csvm.get_df(tra,"コマンド番号",self.comNo,"胸描画"))
            self.flags["drawvagina"] = bool(csvm.get_df(tra,"コマンド番号",self.comNo,"ヴァギナ描画"))
            self.flags["drawanus"] = bool(csvm.get_df(tra,"コマンド番号",self.comNo,"アナル描画"))

            # コマンドが未記入の場合はget_dfが"ERROR"を返すのでEvent.csvの汎用調教を呼ぶ
            prompt = csvm.get_df(tra,"コマンド番号",self.comNo,"プロンプト")
            if prompt == "ERROR":
                prompt = csvm.get_df(eve,"名称","汎用調教","プロンプト")
                nega = csvm.get_df(eve,"名称","汎用調教","ネガティブ")

                self.flags["drawchara"] = bool(csvm.get_df(eve,"名称","汎用調教","キャラ描画"))
                self.flags["drawface"] = bool(csvm.get_df(eve,"名称","汎用調教","顔描画"))
                self.flags["drawbreasts"] = bool(csvm.get_df(eve,"名称","汎用調教","胸描画"))
                self.flags["drawvagina"] = bool(csvm.get_df(eve,"名称","汎用調教","ヴァギナ描画"))
                self.flags["drawanus"] = bool(csvm.get_df(eve,"名称","汎用調教","アナル描画"))

                self.add_element("train", prompt, nega)
            nega = csvm.get_df(tra,"コマンド番号",self.comNo,"ネガティブ")
            self.add_element("train", prompt, nega)


    def create_train_after_element(self):
        for v in self.palam_up.values(): #体力不足で調教が中断されるとpalam_upが持ち越されるのでここで初期化
            v = 0
        #余裕を持って終わったとき　座る
        #気力体力を消耗しているとき　寝る
        #恋慕のときは特別な構図
        #体力を使い切ったら　事後Loraを適用

        #恋慕で余力のあるときは添い寝
        eve = "Event.csv"
        efc = "Effect.csv"
        if "恋慕" in self.talent and self.hp >= 500:
            self.scene = "AFTERピロートーク"
        else:
            # 軽い調教なら座る
            if self.hp >= 1300 or self.hp >= 500:
                self.scene = "AFTER"
            else:
                #疲れたら寝る
                self.scene = "AFTER疲労"
                #体力がなくなるまで調教した
                if self.hp < 550 and self.hp < 100:
                    prompt = csvm.get_df(efc,"名称","AFTER用事後Lora","プロンプト")
                    negative = csvm.get_df(efc,"名称","AFTER用事後Lora","ネガティブ")
                    self.add_element("train_after", prompt, negative)
                #膣内射精があると事後感を出す
                if self.cip > 0:
                    prompt = csvm.get_df(efc,"名称","AFTER用精液溢れ","プロンプト")
                    self.add_element("train_after", prompt, None)
                    # if order["今回の調教で処女喪失"] > 0:
                    #     prompt += "(milk and blood from pussy:1.4)"
                    ## いい表現が見つかったら

        prompt = csvm.get_df(eve,"名称",self.scene,"プロンプト")
        negative = csvm.get_df(eve,"名称",self.scene,"ネガティブ")
        self.add_element("train_after", prompt, negative)

        self.flags["drawchara"] = bool(csvm.get_df(eve,"名称","汎用調教","キャラ描画"))
        self.flags["drawface"] = bool(csvm.get_df(eve,"名称","汎用調教","顔描画"))
        self.flags["drawbreasts"] = bool(csvm.get_df(eve,"名称","汎用調教","胸描画"))
        self.flags["drawvagina"] = bool(csvm.get_df(eve,"名称","汎用調教","ヴァギナ描画"))
        self.flags["drawanus"] = bool(csvm.get_df(eve,"名称","汎用調教","アナル描画"))


    def create_stain_element(self):
        #オーバーライド メソッド
        #汚れ
        prompt = ""
        if (self.hair_cum & 4)  == 4:
            prompt += "(facial,bukkake:1.2),"
        if self.flags["drawbreasts"]:
            if (self.b_cum & 4)  == 4:
                prompt += "(cum on breasts),"
        if self.flags["drawvagina"]:
            if self.膣内に射精 >= 1:
                prompt += "cum drip from pussy,"
        self.add_element("stain", prompt, None)
        # cum on ～ はちんちんを誘発、semen on ～ はほとんど効果がない
        # milkはときどきグラスが出る


    def create_equip_element(self):
        # 装備
        # CSVを2列で検索する
        #オーバーライドメソッド
        equ = "Equip.csv"

        # 存在するすべてのequipについて繰り返す
        for key,value in self.equip.items():
            # 構図による装備品のスキップ
            if key == self.N膣装備:
                print("v")
                print(self.flags["drawvagina"])
                if not self.flags["drawvagina"]:
                    continue
            if key == self.Nアナル装備:
                print("a")
                print(self.flags["drawanus"])
                if not self.flags["drawanus"]:
                    continue

            prompt = csvm.get_df_2key(equ,"TEQUIP",int(key),"値",int(value),"プロンプト")
            #プロンプトが無いのにネガティブだけのCSVは無いだろうと想定
            if  prompt == "ERROR":
                continue
            negative = csvm.get_df_2key(equ,"TEQUIP",int(key),"値",int(value),"ネガティブ")
            self.add_element("equip", prompt, negative)


    def create_event_element(self):
        #独自メソッド
        #特殊イベントでないときは"scene"の値でcsvを検索する
        eve = "Event.csv"
        self.flags["drawchara"] = bool(csvm.get_df(eve,"名称",self.scene,"キャラ描画"))
        self.flags["drawface"] = bool(csvm.get_df(eve,"名称",self.scene,"顔描画"))
        self.flags["drawbreasts"] = bool(csvm.get_df(eve,"名称",self.scene,"胸描画"))
        self.flags["drawvagina"] = bool(csvm.get_df(eve,"名称",self.scene,"ヴァギナ描画"))
        self.flags["drawanus"] = bool(csvm.get_df(eve,"名称",self.scene,"アナル描画"))
        self.flags["drawlocation"] = bool(csvm.get_df(eve,"名称",self.scene,"背景描画"))

        prompt = csvm.get_df(eve,"名称",self.scene,"プロンプト")
        negative = csvm.get_df(eve,"名称",self.scene,"ネガティブ")

        self.add_element("event", prompt, negative)

        #装備、ロケーションいることある？
        #------------ここまで一般イベント--------------------
        #シーン分岐はここまで


    def create_chara_element(self):
        #キャラ描写
        #オーバーライド メソッド
        cha = "Character.csv"
        efc = "Effect.csv"
        prompt = ""
        # キャラ描写の前にBREAKしておく
        prompt += "BREAK,"

        # キャラ描写で毎回記述するプロンプト Effect.csvから読み出す
        charabase = csvm.get_df(efc,"名称","人物プロンプト","プロンプト")
        charabase = charabase + ", " #add_elementの仕様でcharaキーで辞書に格納する時カンマ スペースが入らないのでここで足す
        self.add_element("chara", charabase, None)

        # 特別な名前でプロンプトを登録してある場合、キャラ描写を強制的に上書きする処理
        uwagaki = csvm.get_df(cha,"キャラ名","描画キャラ上書き","プロンプト")
        if uwagaki != "ERROR": #EROORじゃなかったら上書き
            prompt = f"({uwagaki})"
            negative = csvm.get_df(cha,"キャラ名","描画キャラ上書き","ネガティブ")
            self.add_element("chara", prompt, negative)
        else:
            #割り込みがなければ通常のキャラプロンプト読み込み処理
            chara =csvm.get_df(cha,"キャラ名",self.name,"プロンプト")
            prompt = f"\({chara}\)"
            negative = csvm.get_df(cha,"キャラ名",self.name,"ネガティブ")
            self.add_element("chara", prompt, negative)



# #表情ブレンダー
# p,n = Expression(order,flags)
# prompt += p
# negative += n


    def create_body_element(self):
        #もとはキャラ描写内で呼び出し
        #オーバーライドメソッド
        #胸愛撫、ぱふぱふ、後背位胸愛撫 コマンドがスーパーと違う

        # 乳サイズ
        # 乳強調すると脱ぎたがるのどうしよう
        ## 体型素質 #もとはキャラ描写内で呼び出し
        # 一致する素質を持っていればTalent.csvに書かれたプロンプトを記入
        tal = "Talent.csv"
        if self.flags["drawbreasts"]:
            talents = ["絶壁","貧乳","巨乳","爆乳"]
            for bustsize in talents:
                if bustsize in self.talent:
                    prompt = csvm.get_df(tal,"名称",bustsize,"プロンプト")
                    negative = csvm.get_df(tal,"名称",bustsize,"ネガティブ")
                    self.add_element("body", prompt, negative)
        else:
            talents = ["絶壁","貧乳","巨乳","爆乳"]
            for bustsize in talents:
                if bustsize in self.talent:
                    prompt = csvm.get_df(tal,"名称",bustsize,"プロンプト")
                    negative = csvm.get_df(tal,"名称",bustsize,"ネガティブ")
                    if negative != "ERROR":
                        negative = "areolae, nipple" #csvのnegaが空白だった時用対策
                    else:
                        negative += ", areolae, nipple"
                    self.add_element("body", prompt, negative)

        # 体格、体型
        talents = ["小人体型","巨躯","小柄体型","ぽっちゃり","ムチムチ","スレンダー","がりがり"]
        for stature in talents:
            if stature in self.talent:
                prompt = csvm.get_df(tal,"名称",stature,"プロンプト")
                nega = csvm.get_df(tal,"名称",stature,"ネガティブ")
                self.add_element("body", prompt, nega)

        # 胸愛撫など、普通乳なのに巨乳に描かれがちなコマンドのときプロンプトにsmall breastsを付加する
        chk_list = ["爆乳","巨乳","貧乳","絶壁"]
        and_list =  set(self.talent) & set(chk_list)
        # リストに一致しないとき即ち普通乳のとき
        if (len(and_list)) == 0:
            # 胸愛撫、ぱふぱふ、後背位胸愛撫
            if self.comNo in ("3","340","616"):
                self.add_element("body", ", small breasts", None)


    def create_hair_color_element(self):
        #独自メソッド
        #子息用メソッドとスーパークラスの
        #髪色の関数 ※3000番台の名無しキャラ、および息子(2048)と娘(2049)のみ
        if (self.charno in range(3000,4000)) or (self.charno in (2048,2049)):
        # 髪色
            tal = "Talent.csv"
            talents = ["黒髪","栗毛","金髪","赤毛","銀髪","青髪","緑髪","ピンク髪","紫髪","白髪","オレンジ髪","水色髪","灰髪"]
            for hair_color in talents:
                if hair_color in self.talent:
                    # csvには色だけ書いてるのでhairをつける
                    prompt = csvm.get_df(tal,"名称",hair_color,"プロンプト") + " hair,"
                    negative = csvm.get_df(tal,"名称",hair_color,"ネガティブ") + " hair,"
                    self.add_element("hair", prompt, negative)


    def check_live_time(self):
        #独自メソッド
        #create_timezone_elementにオーバーライドしようかとも考えたが､機能が違いすぎる
        # 昼夜の表現 屋外のみ
        # epuip52が野外プレイフラグ
        if self.scene in ["ライブ0","ライブ1"] or 52 in self.equip:
            # 旧地獄市街や月の都に青空はないはず
            self.location = self.sjh.get_save("野外プレイの場所") #初期化をもし上書きされていた時用美しくない
            if 52 in self.equip and self.location in (7,11):
                self.add_element("timezone", "at night", "(blue sky,twilight:1.3)")
            elif self.time == 0:
                self.add_element("timezone", "day", "(night sky,night scene,twilight:1.3)")
            else:
                self.add_element("timezone", "in the twilight", "(blue sky:1.3)")


# 射精 元はキャラ描写内で呼び出し
    def create_cum_element(self):
        #オーバーライド メソッド
        #全部足し合わせると呪文がまとまらん
        #あとで優先順位ロジック考える
        prompt = ""
        if self.膣内に射精 > 0:
            prompt += "(cum in pussy,internal ejaculation),"
        if self.アナルに射精 > 0:
            prompt += "(cum in ass),"
        if self.髪に射精 > 0:
            prompt += "(cum on hair,projectile cum),"
        if self.顔に射精 > 0:
            prompt += "(cum on face,facial,projectile cum),"
        if self.口に射精 > 0:
            prompt += "(cum in mouth),"
        if self.胸に射精 > 0:
            prompt += "(cum on breasts,projectile cum),"
        if self.腹に射精 > 0:
            prompt += "(cum on stomach,projectile cum),"
        if self.腋に射精 > 0:
            prompt += "(cum on armpit,projectile cum),"
        if self.手に射精 > 0:
            prompt += "(cum on hand,projectile cum),"
        if self.秘裂に射精 > 0:
            prompt += "(cum on lower body,projectile cum),"
        if self.竿に射精 > 0:
            prompt += "(cum on penis,projectile cum),"
        if self.尻に射精 > 0:
            prompt += "(cum on ass,projectile cum),"
        if self.太腿に射精 > 0:
            prompt += "(cum on thigh,projectile cum),"
        if self.足で射精 > 0: # ここだけ「足 "で"」
            prompt += "(cum on feet,projectile cum),"
        #射精エフェクト
        efc = "Effect.csv"
        if self.主人が射精 > 0:
            if self.主人が射精 == 1:
                prompt += csvm.get_df(efc,"名称","主人が射精","プロンプト")
            else:
                prompt += csvm.get_df(efc,"名称","主人が大量射精","プロンプト")
        self.add_element("stain", prompt, None)


    # # 置換機能の関数を呼ぶ
    # # プロンプト中に%で囲まれた文字列があれば置換する機能
    # # 失敗するとErrorというプロンプトが残る
    # #\ReplaceList.csv は chikan メソッドで読み込まれるので不要
    # prompt = csvm.chikan(prompt)
    # negative = csvm.chikan(negative)

    # # 解像度文字列を解釈する関数
    # gen_width,gen_height = get_width_and_height()

    # 解像度をcsvから読む
    def get_kaizoudo(self):
        """
        あとでアスペクト比を基に可変できるようにする
        このget_kaizoudoメソッドは、シーンに応じて解像度をCSVファイルから読み込むために使うんだ。
        TRAINシーンとその他のEVENTシーンで読み取るCSVが異なるから、条件分岐を使って適切なCSVを選択するぜ。

        TRAINシーンの場合はTrain.csvから、その他の場合はEvent.csvから解像度を取得するんだ。
        解像度は、画像生成における品質を決定する重要な要素だから、正確に取得することが大事だぜ！
        """
        from module.sub import get_width_and_height
        # TRAINとその他のEVENTで読み取るcsvが異なる
        if self.scene == "TRAIN":
            tra = "Train.csv"
            kaizoudo = csvm.get_df(tra,"コマンド番号",self.comNo,"解像度")
        #これ用のプロンプトや解像度はあとでCSVにかく
        elif self.scene == "マスター移動" or self.scene == "ターゲット切替":
            return

        else:
            eve = "Event.csv"
            kaizoudo = csvm.get_df(eve,"名称",self.scene,"解像度")
            self.width, self.height = get_width_and_height(kaizoudo)