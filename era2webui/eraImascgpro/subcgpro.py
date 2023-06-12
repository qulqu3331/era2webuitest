import pandas as pd
import os
import random
from emo import Expression
import re
from sub import get_df
from sub import get_df_2key
from sub import get_width_and_height
from sub import chikan

# order自体を変化させる前処理
# たとえば
# 条件によりコマンド差し替え（乳サイズでパイズリ→ナイズリ
# キャラ差し替え　EXフラグが立っていたらEXキャラ用の名前に変更する
# など
def preceding(order):
    Nパイズリ = "82"
    Nナイズリ = "701" #存在しないコマンド番号。
    N胸愛撫 = "6"
    N着衣胸愛撫 = "702" #存在しないコマンド番号。

    comNo = str(order["コマンド"])

    # 巨乳未満のキャラのパイズリはナイズリに変更
    # (ちんちんが隠れてしまうような描写は普乳を逸脱しているため)
    if not (("巨乳" in order["talent"]) or ("爆乳" in order["talent"])):
        if comNo == Nパイズリ:
            comNo = Nナイズリ

    # 着衣時の胸愛撫はCHAKUMOMIのLoraを適用
    if order["上半身着衣状況"] != 0:
        if comNo == N胸愛撫:
            comNo = N着衣胸愛撫


    order["コマンド"] = comNo

    return order


# orderをもとにプロンプトを整形する関数
def promptmaker(order):
    
    # orderを変化させる事前処理 コマンドが変われば解像度の変化もありえる
    order = preceding(order)

    kaizoudo = ""
    gen_width = 0
    gen_height = 0

    prompt = ""
    negative = ""

    flags = {"drawchara":0,"drawface":0,"drawbreasts":0,"drawvagina":0,"drawanus":0}

    flags["主人以外が相手"] = 0
    csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Event.csv')
    csv_eve = pd.read_csv(filepath_or_buffer=csvfile_path)
    if get_df(csv_eve,"名称",order["scene"],"主人以外が相手") == 1:
        flags["主人以外が相手"] = 1

    # Effect.csvとEvent.csvを読みこんでおく
    csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Effect.csv')
    csv_efc = pd.read_csv(filepath_or_buffer=csvfile_path)

    csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Event.csv')
    csv_eve = pd.read_csv(filepath_or_buffer=csvfile_path)

    prompt += get_df(csv_efc,'名称','基礎プロンプト','プロンプト') + ","
    negative += get_df(csv_efc,'名称','基礎プロンプト','ネガティブ')  + ","
 
    if "死亡" in order["talent"]:
        prompt += "tombstone,dark scene,offering of flowers,"
        negative += "girl,"
        return prompt, negative,0,0

    #シーン分岐

    #場所とキャラを描写する
    if order["scene"] == "ターゲット切替" or order["scene"] == "マスター移動":
        if order["キャラ固有番号"] == 0:
            # targetがいないとき
            prompt += "(empty scene),"
            negative += "(1girl:1.5),"
        else:
            # 立ち絵表示　背景描写を強化
            prompt += "1girl standing,detailed scenery in the background,"
            flags["drawchara"] = 1
        #ロケーション
        p,n = get_location(order)
        prompt += p
        negative += n


    #ここからTRAIN コマンド実行時の絵
    if order["scene"] == "TRAIN":
        #コマンドの処理 Train.csvを読む
        csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Train.csv')
        csv_tra = pd.read_csv(filepath_or_buffer=csvfile_path)

        # TRAINNAME関数はないと思い込んでいたので番号で処理している
        comNo = str(order["コマンド"])

        # 体位から読み取ったキャラ描画、顔描画、胸描画のフラグ（0か1が入る)
        flags["drawchara"] =  get_df(csv_tra,"コマンド番号",comNo,"キャラ描画")
        flags["drawface"] =  get_df(csv_tra,"コマンド番号",comNo,"顔描画")
        flags["drawbreasts"] =  get_df(csv_tra,"コマンド番号",comNo,"胸描画")
        flags["drawvagina"] = get_df(csv_tra,"コマンド番号",comNo,"ヴァギナ描画")
        flags["drawanus"] = get_df(csv_tra,"コマンド番号",comNo,"アナル描画")
        
        # コマンドが未記入の場合はEvent.csvの汎用調教を呼ぶ
        pro = get_df(csv_tra,"コマンド番号",comNo,"プロンプト")
        if pro == "":
            prompt += get_df(csv_eve,"名称","汎用調教","プロンプト")
            prompt += ","
            negative += get_df(csv_eve,"名称","汎用調教","ネガティブ")  
            negative += ","

            flags["drawchara"] = get_df(csv_eve,"名称","汎用調教","キャラ描画")
            flags["drawface"] = get_df(csv_eve,"名称","汎用調教","顔描画")
            flags["drawbreasts"] = get_df(csv_eve,"名称","汎用調教","胸描画")
            flags["drawvagina"] = get_df(csv_eve,"名称","汎用調教","ヴァギナ描画")
            flags["drawanus"] = get_df(csv_eve,"名称","汎用調教","アナル描画")

        else:
            # コマンド成否で分岐
            # 成否判定のないコマンドの場合、order["success"]の値は不定(前回コマンドのまま)
            deny = get_df(csv_tra,"コマンド番号",comNo,"拒否プロンプト")
            if deny == "":
                #拒否プロンプトが空なら成否判定なしと判断、通常プロンプトを出力する
                chk_success = True
            elif order["success"] == 1:
                #判定に成功した
                chk_success = True
            else:
                #判定に失敗した。拒否プロンプトを出力する
                chk_success = False

            if chk_success:
                prompt += pro
                prompt += ","
                negative += get_df(csv_tra,"コマンド番号",comNo,"ネガティブ")
                negative += ","
            else:
                prompt += deny
                prompt += ","
                negative += get_df(csv_tra,"コマンド番号",comNo,"拒否ネガティブ")
                negative += ","

        # 付着した精液
        # prompt += stain(order,flags)
        #装備 調教対象キャラが映るときのみ
        if flags["drawchara"] == 1:
            p,n = equipment(order,flags)
            prompt += p
            negative += n
        #ロケーション
        p,n = get_location(order)
        prompt += p
        negative += n

        #解像度
        kaizoudo = get_kaizoudo(order)

    #------------BEFORE、AFTERはない---------------------

    #------------ここから一般イベント---------------------
    #特殊イベントでないときは"scene"の値でcsvを検索する
    # if not order["scene"] in ["BEFORE","TRAIN","AFTER"]:
    #     Scene = order["scene"]

    #     flags["drawchara"] = get_df(csv_eve,"名称",Scene,"キャラ描画")
    #     flags["drawface"] = get_df(csv_eve,"名称",Scene,"顔描画")
    #     flags["drawbreasts"] = get_df(csv_eve,"名称",Scene,"胸描画")
    #     flags["drawvagina"] = get_df(csv_eve,"名称",Scene,"ヴァギナ描画")
    #     flags["drawanus"] = get_df(csv_eve,"名称",Scene,"アナル描画")

    #     prompt += get_df(csv_eve,"名称",Scene,"プロンプト")
    #     prompt += ","
    #     negative += get_df(csv_eve,"名称",Scene,"ネガティブ")  
    #     negative += ","

        
    #     #解像度
    #     kaizoudo = get_kaizoudo(order)

    #------------ここまで一般イベント--------------------
    #シーン分岐はここまで

    #キャラ描写
    if flags["drawchara"] == 1:

        # キャラ描写の前にBREAKしておく？これいいのか悪いのかわからぬ
        # prompt += "BREAK,"

        # キャラ描写の前に衣服
        p,n = clothing(order,flags)
        prompt += p
        negative += n

        # キャラ描写で毎回記述するプロンプト Effect.csvから読み出す
        prompt += get_df(csv_efc,"名称","人物プロンプト","プロンプト") + ","

        # Charactor.csvとAdd_charactor.csvを結合
        csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Charactor.csv')
        csv_cha = pd.read_csv(filepath_or_buffer=csvfile_path)
        csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Add_charactor.csv')
        add_cha = pd.read_csv(filepath_or_buffer=csvfile_path)

        csv_cha = pd.concat([csv_cha,add_cha])

        # 特別な名前でプロンプトを登録してある場合、キャラ描写を強制的に上書きする処理
        uwagaki = get_df(csv_cha,"キャラ名","描画キャラ上書き","プロンプト")
        if uwagaki != "": #空欄じゃなかったら上書き
            prompt += "\(" + uwagaki + "\),"
            negative += get_df(csv_cha,"キャラ名","描画キャラ上書き","ネガティブ") + ","
        else:
            #割り込みがなければ通常のキャラプロンプト読み込み処理
         
            chaName = order["target"]
            # 未確定名のときは誰だかわからなくする
            if order["名前フラグ"] != 1:
                chaNo = order["キャラ固有番号"]
                prompt += "(pixel art:2.0),faceless female,(low quality,blurry:1.5)"
                prompt += "\(" + get_df(csv_cha,"キャラ番号",chaNo,"プロンプト2") + "\),"

            else:
                prompt += "\(" + get_df(csv_cha,"キャラ名",chaName,"プロンプト") + ":" + str(get_df(csv_cha,"キャラ名",chaName,"プロンプト強調")) + "\),"
                prompt += "\(" + get_df(csv_cha,"キャラ名",chaName,"プロンプト2") + "\),"
                prompt += get_df(csv_cha,"キャラ名",chaName,"キャラLora") + ","
                prompt += get_df(csv_cha,"キャラ名",chaName,"目つきLora") + ","
                negative += get_df(csv_cha,"キャラ名",chaName,"ネガティブ") +  ","



        # エフェクト等 TFLAGは調教終了時には初期化されない。TRAINに限定しないと料理中に射精とかが起こる
        if order["scene"] == "TRAIN":
            #射精
            # prompt += cumshot(order)
        
            # ヴァギナ描画onのとき
            if flags["drawvagina"] == 1:
                # 潤滑によるpussy juice
                if order["palam"]["潤滑"] < 200:
                    negative += "pussy juice,"
                elif order["palam"]["潤滑"] in range(1000,2500):
                    prompt += "pussy juice,"
                elif order["palam"]["潤滑"] in range(2500,5000):
                    prompt += "dripping pussy juice,"
                else:
                    prompt += "(dripping pussy juice),"
                # 破瓜の血       
                # if order["処女喪失"] > 0:
                    # prompt += get_df(csv_efc,"名称","処女喪失","プロンプト") + ","
                # if order["今回の調教で処女喪失"] > 0:
                    # prompt += get_df(csv_efc,"名称","今回の調教で処女喪失","プロンプト") + ","            
                if order["放尿"] > 0:
                        prompt += get_df(csv_efc,"名称","放尿","プロンプト") + ","
            if flags["drawbreasts"]:
                if order["噴乳"] > 0:
                    prompt += get_df(csv_efc,"名称","噴乳","プロンプト") + ","
            # ここまでTRAIN限定のエフェクト
        
        if "妊娠" in order["talent"]:
            # 標準で20日で出産する。残14日から描写し、残8日でさらに進行
            if (order["出産日"] - order["日付"]) in range(8,14):
                prompt += get_df(csv_efc,"名称","妊娠中期","プロンプト") + ","
            elif (order["出産日"] - order["日付"]) <= 8:
                prompt += get_df(csv_efc,"名称","妊娠後期","プロンプト") + ","

        #乳サイズ、体型の関数を呼び出す
        p,n = body_shape(order,flags)
        prompt += p
        negative += n

        #髪色の関数 ※3000番台の名無しキャラ、および息子(2048)と娘(2049)のみ
        # if (order["キャラ固有番号"] in range(3000,4000)) or (order["キャラ固有番号"] in (2048,2049)):
        #     prompt += haircolor(order)

        #髪型の関数
        # p,n = hairstyle(order)
        # prompt += p
        # negative += n        

        #目の色をorderに追記しておく(Expression関数でclosed eyesの判定をした後に反映する)
        order["eyecolor"] = get_df(csv_cha,"キャラ名",order["target"],"目の色")

        #表情ブレンダー
        # p,n = Expression(order,flags)
        # prompt += p
        # negative += n
    #ここまでキャラ描画フラグがonのときの処理



    # 昼夜の表現
        # やたらと夜景や黄昏時を出したがるので強めにネガ
        if order["時間"] in range(0,360):
            prompt += "at night,"
            negative += "(blue sky,twilight:1.3),"
        elif order["時間"] in range(360,720):
            prompt += "in the morning,"
            negative += "(night sky,night scene,twilight:1.3),"
        elif order["時間"] in range(720,1060):
            prompt += "in the afternoon,"
            negative += "(night sky,night scene,twilight:1.3),"
        elif order["時間"] in range(1060,1150):
            prompt += "in the twilight,"
            negative += "(blue sky:1.3),"
        elif order["時間"] >= 1150:
            prompt += "at night,"
            negative += "(blue sky,twilight:1.3),"


    # 置換機能の関数を呼ぶ
    # プロンプト中に%で囲まれた文字列があれば置換する機能
    # 失敗するとErrorというプロンプトが残る
    ReplaceList= os.path.join(os.path.dirname(__file__), 'csvfiles\\ReplaceList.csv')
    prompt = chikan(prompt,ReplaceList)
    negative = chikan(negative,ReplaceList)
    
    # 解像度文字列を解釈する関数
    gen_width,gen_height = get_width_and_height(kaizoudo,ReplaceList)

    # 重複カンマを1つにまとめる
    prompt = re.sub(',+',',',prompt)
    negative = re.sub(',+',',',negative)

    return prompt,negative,gen_width,gen_height
# *********************************************************************************************************
# ----------ここまでpromptmaker----------------------------------------------------------------------------------
# *********************************************************************************************************


# 体型素質
# 一致する素質を持っていればTalent.csvに書かれたプロンプトを記入
def body_shape (order,flags):
    prompt = ""
    negative = ""
    csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Talent.csv')
    csv_tal = pd.read_csv(filepath_or_buffer=csvfile_path)


    # 乳サイズ
    # 乳強調すると脱ぎたがるのどうしよう
    if flags["drawbreasts"] == 1:
        talents = ["絶壁","貧乳","巨乳","爆乳"]
        for tal in talents:
            if tal in order["talent"]:
                prompt += get_df(csv_tal,"名称",tal,"プロンプト") + ","
                negative += get_df(csv_tal,"名称",tal,"ネガティブ") + ","

    # 体格、体型
    talents = ["小人体型","巨躯","小柄体型","ぽっちゃり","ムチムチ","スレンダー","がりがり"]
    for tal in talents:
        if tal in order["talent"]:
            prompt += get_df(csv_tal,"名称",tal,"プロンプト") + ","
            negative += get_df(csv_tal,"名称",tal,"ネガティブ") + ","

    # 胸愛撫など、普通乳なのに巨乳に描かれがちなコマンドのときプロンプトにsmall breastsを付加する
    chk_list = ["爆乳","巨乳","貧乳","絶壁"]
    and_list = set(order['talent']) & set(chk_list)
    # リストに一致しないとき即ち普通乳のとき
    if (len(and_list)) == 0:
        # 胸愛撫、ぱふぱふ、後背位胸愛撫
        if str(order["コマンド"]) in ("6","606","702"):
            prompt += "small breasts,"


    return prompt,negative

# 髪色
def haircolor(order):
    csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Talent.csv')
    csv_tal = pd.read_csv(filepath_or_buffer=csvfile_path)
    prompt = ""
    negative = ""
    talents = ["黒髪","栗毛","金髪","赤毛","銀髪","青髪","緑髪","ピンク髪","紫髪","白髪","オレンジ髪","水色髪","灰髪"]
    for tal in talents:
        if tal in order["talent"]:
            # csvには色だけ書いてるのでhairをつける
            prompt += get_df(csv_tal,"名称",tal,"プロンプト") + " hair,"
            negative += get_df(csv_tal,"名称",tal,"ネガティブ") + " hair,"
    return prompt


# 髪型 
def hairstyle(order):
    csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Talent.csv')
    csv_tal = pd.read_csv(filepath_or_buffer=csvfile_path)
    prompt = ""
    negative = ""
    talents = ["長髪","セミロング","ショートカット","ポニーテール","ツインテール","サイドテール","縦ロール","ツインリング","三つ編み","短髪","おさげ髪","ポンパドール","ポニーアップ","サイドダウン","お団子髪","ツーサイドアップ","ダブルポニー","横ロール","まとめ髪","ボブカット","シニヨン","ロングヘア"]
    for tal in talents:
        if tal in order["talent"]:
            prompt += get_df(csv_tal,"名称",tal,"プロンプト") + ","
            negative += get_df(csv_tal,"名称",tal,"ネガティブ") + ","
    return prompt,negative

# 装備
# CSVを2列で検索する
def equipment(order,flags):
    prompt = ""
    negative = ""
    csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Equip.csv')
    csv_equ = pd.read_csv(filepath_or_buffer=csvfile_path)

    N膣装備 = "20"
    Nアナル装備 = "25"    
    # 存在するすべてのequipについて繰り返す
    for key,value in order["equip"].items():
        # 構図による装備品のスキップ
        if key == N膣装備:
            print("v")
            print(flags["drawvagina"])
            if flags["drawvagina"] == 0:
                continue
        if key == Nアナル装備:
            print("a")
            print(flags["drawanus"])
            if flags["drawanus"] == 0:
                continue
        
        equ = get_df_2key(csv_equ,"TEQUIP",int(key),"値",int(value),"プロンプト")
        if  equ != "ERROR":
            prompt += equ + ","
        equ = get_df_2key(csv_equ,"TEQUIP",int(key),"値",int(value),"ネガティブ")
        if  equ != "ERROR":
            negative += equ + ","
        
    return prompt,negative

#ロケーション
def get_location(order):
    prompt = ""
    negative = ""

    # 72番から寮の部屋 最大数200もあれば十分のはず
    if order["現在位置"] in range(72,300):
        # 私室描写（てきとう
        prompt += "in girl's private room,bed,desk,furniture,"
    else:
        csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Location.csv')
        csv_loc = pd.read_csv(filepath_or_buffer=csvfile_path)
    
        prompt += get_df(csv_loc,"番号",order["現在位置"],"プロンプト")
        prompt += ","
        negative += get_df(csv_loc,"番号",order["現在位置"],"ネガティブ")
        negative += ","

    return prompt, negative

# 射精 コメントアウト中
def cumshot(order):
    prompt = ""
    if order["膣内に射精"] > 0:
        prompt += "(cum in pussy,internal ejaculation),"    
    if order["アナルに射精"] > 0:
        prompt += "(cum in ass),"
    if order["髪に射精"] > 0:
        prompt += "(cum on hair,projectile cum),"
    if order["顔に射精"] > 0:
        prompt += "(cum on face,facial,projectile cum),"
    if order["口に射精"] > 0:
        prompt += "(cum in mouth),"
    if order["胸に射精"] > 0:
        prompt += "(cum on breasts,projectile cum),"
    if order["腹に射精"] > 0:
        prompt += "(cum on stomach,projectile cum),"
    if order["腋に射精"] > 0:
        prompt += "(cum on armpit,projectile cum),"
    if order["手に射精"] > 0:
        prompt += "(cum on hand,projectile cum),"
    if order["秘裂に射精"] > 0:
        prompt += "(cum on lower body,projectile cum),"
    if order["竿に射精"] > 0:
        prompt += "(cum on penis,projectile cum),"
    if order["尻に射精"] > 0:
        prompt += "(cum on ass,projectile cum),"
    if order["太腿に射精"] > 0:
        prompt += "(cum on thigh,projectile cum),"
    if order["足で射精"] > 0: # ここだけ「足 "で"」
        prompt += "(cum on feet,projectile cum),"
    #射精エフェクト
    if order["主人が射精"] > 0:
        csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Effect.csv')
        csv_efc = pd.read_csv(filepath_or_buffer=csvfile_path)
        if order["主人が射精"] == 1:
            prompt += get_df(csv_efc,"名称","主人が射精","プロンプト") + ","
        else:
            prompt += get_df(csv_efc,"名称","主人が大量射精","プロンプト") + ","
    return prompt

#汚れ
def stain(order,flags):
    prompt = ""
    # if ((order["髪の汚れ"] & 4)  == 4):
    #     prompt += "(facial,bukkake:1.2),"
    if flags["drawbreasts"] == 1:
        if (order["胸の汚れ"] & 4)  == 4:
            prompt += "(cum on breasts),"
    if flags["drawvagina"] == 1:
        if (order["膣内射精フラグ"]) >= 1:
            prompt += "cum drip from pussy,"
    return prompt
# cum on ～ はちんちんを誘発、semen on ～ はほとんど効果がない
# milkはときどきグラスが出る


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

# 服装
def clothing(order,flags):
    prompt = ""
    negative = ""
    csvfile_path= os.path.join(os.path.dirname(__file__), 'csvfiles\\Cloth.csv')
    csv_clo = pd.read_csv(filepath_or_buffer=csvfile_path)
    # 脱衣コマンドのコマンド番号
    N上半身脱衣_上着 = "200"
    N下半身脱衣_上着 = "201"
    N上半身脱衣_下着 = "202"
    N下半身脱衣_下着 = "203"
    # 体から離れた衣服の生成打率はいまだ著しく低いので、脱いでいる服の描写は未実装。脱衣コマンドを実行すると脱衣後の姿を表示する。
    # 決して諦めてはならない。

    ブラ露出フラグ = 0
    パンツ露出フラグ = 0
    乳露出フラグ = 0
    秘部露出フラグ = 0
    上半身はだけフラグ = 0 #未実装
    下半身はだけフラグ = 0 #未実装

    # 下着１（貞操帯、絆創膏、ニプレス）は未実装

    print(f"上半身上着重ね着数{上半身上着重ね着数(order)}")
    print(f"下半身上着重ね着数{下半身上着重ね着数(order)}")

    # 上着を着てないとき or 1枚だけ着てるのを脱いでるとき に露出フラグが立つ。ノーブラでもフラグを立てておき、あとで折る
    if 上半身上着重ね着数(order) == 0 or (上半身上着重ね着数(order) == 1 and order["コマンド"] == N上半身脱衣_上着):
        ブラ露出フラグ = 1
    elif 上半身はだけフラグ == 1:
        ブラ露出フラグ = 1
    
    if 下半身上着重ね着数(order) == 0 or (下半身上着重ね着数(order) == 1 and order["コマンド"] == N下半身脱衣_上着):
        パンツ露出フラグ = 1 
    elif 下半身はだけフラグ == 1:
        パンツ露出フラグ = 1
    
    # 着てない or ブラのみの状態から脱ぐ、または元々ノーブラの状態でブラが見える条件を満たす
    if order["上半身着衣状況"] == 0 or (上半身上着重ね着数(order) == 0 and order["コマンド"] == N上半身脱衣_下着) or (order["上半身下着２"] == 0 and ブラ露出フラグ == 1):
        ブラ露出フラグ = 0
        乳露出フラグ = 1

    # なにも履いてない or パンツだけ履いてるのを脱ぐ、または元々ノーパンの状態でパンツが見える条件を満たす
    if order["下半身着衣状況"] == 0 or (下半身上着重ね着数(order) == 0 and order["コマンド"] == N下半身脱衣_下着) or (order["下半身下着２"] == 0 and パンツ露出フラグ == 1):
        パンツ露出フラグ = 0 
        秘部露出フラグ = 1
    
    # 裸体描写
    # 上半身だけ着てる
    if 秘部露出フラグ == 1 and 乳露出フラグ == 0:
        prompt += "nsfw, her lower body is naked,(bottomless, naked clotch, pussy),"
    # 下半身だけ着てる
    if 秘部露出フラグ == 0 and 乳露出フラグ == 1:
        prompt += "nsfw, her upper body is naked,(topless, naked breasts, nipples),"
    # 全裸
    if 秘部露出フラグ == 1 and 乳露出フラグ == 1:
        prompt += "nsfw, full nude,completely naked, navel, (naked breasts,nipples),"

    # 上着描写
    # 上半身上着
    if (ブラ露出フラグ == 0 and 乳露出フラグ == 0) or 上半身はだけフラグ == 1:
        clothings = ["上半身上着１","上半身上着２","ボディースーツ","ワンピース","着物","レオタード"]
        for clo in clothings:
            print(clo)
            print(order[clo])
            clothNo = str(order[clo])
            if order[clo] != 0:
                prompt += "(wearing "  + 今日の服(order,clothNo) + " " + get_df(csv_clo,"番号",clothNo,"プロンプト") + ":1.3),"
                negative += get_df(csv_clo,"番号",clothNo,"ネガティブ") + ","

    # 下半身上着
    if (パンツ露出フラグ == 0 and 秘部露出フラグ == 0) or 下半身はだけフラグ == 1:
        clothings = ["下半身上着１","下半身上着２","スカート"]
        for clo in clothings:
            print(clo)
            print(order[clo])
            clothNo = str(order[clo])
            if order[clo] != 0:
                prompt += "(wearing "  + 今日の服(order,clothNo) + " " + get_df(csv_clo,"番号",clothNo,"プロンプト") + ":1.3),"
                negative += get_df(csv_clo,"番号",clothNo,"ネガティブ") + ","


    if ブラ露出フラグ == 1:
        if order["上半身下着２"] != 0:
            prompt += "(wearing "  + 今日の服(order,"8888") + " " + get_df(csv_clo,"番号",str(order["上半身下着２"]),"プロンプト") + ":1.3),"

    if パンツ露出フラグ == 1:
        if order["下半身下着２"] != 0:
            # パンツの種類は未対応
            prompt += "(wearing "  + 今日の服(order,"8888") + " panties:1.3),"

    # panty aside
    if order["マスターがＶ挿入"] != 0 or order["マスターがＡ挿入"] != 0 :
        if order["下半身下着２"] != 0:
            prompt += "pantie aside,"

    return prompt,negative

# 日付とキャラ番号を使った疑似乱数でその日の服の色形を固定する
def 今日の服(order,clothNo):
    clothcolor = ""
    # 色決まってるようなやつは除外　ブルマ、白衣、ワイシャツ、体操服、スク水
    if not clothNo in ["802","1210","1304","1322","1701"]:
        clothcolor = ""
        random.seed(int(order["キャラ固有番号"])+int(order["日付"])+int(clothNo))

        # 確率で水玉、ストライプ、チェック柄を入れてみるテスト
        ra = random.randrange(10)
        if ra == 0:
            clothcolor += "polka-dots "
        elif ra == 1:
            clothcolor += "stripes pattern "
        elif ra == 2:
            clothcolor += "plaid "
            
        colors = ["light blue","yellow","white","black","light green","pink","purple"]
        clothcolor += random.choice(colors)
    
    # ちひろさんは緑の服を着るべき
    if order["target"] == "千川ちひろ":
        if clothNo == "1204":
            clothcolor = "green"
        elif clothNo == "901":
            clothcolor = "black"
        # ワイシャツに白を指定するとwhite dress shirt になり、たぶんwhite dressが強すぎて破綻する。なのであえて色指定なし
        elif clothNo == "1304":
            clothcolor = ""

    # しまむーのブレザーは他の色を指定しても高確率で茶色になるので茶色しか着せない
    if order["target"] == "島村卯月":
        if clothNo == "1208":
            clothcolor = "brown"
        # 制服スカートも固定しようとしたが、このままだとブレザーを脱いだ瞬間にスカートの色が変化してしまう
        # 脱いだ服を保存してあるはずなのでそっちを見るように修正が必要
        # if clothNo == "902":
        #     if order["上半身上着１"] == 1208:
        #         clothcolor = "plaid red"
                


    return clothcolor

def 上半身上着重ね着数(order):
    return ((order["上半身上着１"] != 0) + (order["上半身上着２"] != 0) + (order["ボディースーツ"] != 0) + (order["ワンピース"] != 0) + (order["着物"] != 0) + (order["レオタード"] != 0))

def 下半身上着重ね着数(order):
    return ((order["下半身上着１"] != 0) + (order["下半身上着２"] != 0) + (order["スカート"] != 0) + (order["ボディースーツ"] != 0) + (order["ワンピース"] + order["着物"] != 0) + (order["レオタード"] != 0))