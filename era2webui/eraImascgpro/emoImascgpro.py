import random
import numpy as np
import os
import random
import pandas as pd
# cgpro用の表情コード
# 暫定でバリアント毎に分けたけど更新が面倒になるのでホントはまとめたい
# YM用の記述や未対応部分はコメントアウト


# 表情ブレンダー
# 表情のプロンプトは実行中に弄りたいのでいつかcsv化する

# 様々な表情の単語をブレンドしても良い顔ができない上に構図や絵柄に深刻な悪影響があることがわかった。
# 要素ごとにプロンプトを追加していくやり方ではすぐ限界が来る。



def Expression(order,flags):
    prompt = ""
    negative = ""
    ClosedEyes = False
    eyeprompt = ""  # 目の処理はeyepromtに書き溜め、後で結合するが、最終的にclosed eyesフラグが立ってれば削除
    Pain = False
    tsuyoijoudou = False
    Love = False
    NotMaster = False

    # TEQUIP:18 アイマスク (cgpro)
    if "18" in order["equip"]:
        ClosedEyes = True

    # 主人以外が相手の時は恋慕、反発の効果を消す
    # if order["scene"] == "TRAIN":
    #     if order["PLAYER"] != 0:
    #         NotMaster = True
    #         print("助手とか")
    # else:
    #     if flags["主人以外が相手"] == 1:
    #         NotMaster = True
    #         print("主人以外が相手のイベント")

    #睡眠薬または失神中
    # 4 : 昏睡
    # 3 : 熟睡
    # 2 : 睡眠
    # 1 : まどろみ
    # 0 : 目覚め
    # 失神フラグは失神した瞬間は1、次ターンから2以上になる
    # if (order["睡眠薬"] > 0) or (order["失神"] >= 2):
    #     prompt += "(sleeping,closed eyes:1.2),"
    #     negative += "smile,"
    #     ClosedEyes = True
    #     # 暫定で表情変化なしにする。
    #     flags["drawface"] = 0
    #     # でも欲情と絶頂はちょっと効くように
    #     pleasure = order["palam_up"]["快Ｃ"]+order["palam_up"]["快Ｂ"]+order["palam_up"]["快Ｖ"]+order["palam_up"]["快Ａ"]
    #     if pleasure in range(100,1000): #最初の目標は100
    #         prompt += "(blush:0.7),"
    #     elif pleasure in range(1000,3000):
    #         prompt += "Orgasmic expression,(blush:0.9)"
    #     elif pleasure in range(3000,7500):
    #         prompt += "(Orgasmic expression),blush,"
    #     elif pleasure > 7500:
    #         prompt += "(Orgasmic expression:1.2),blush,"
    #     if order["絶頂の強度"] > 0:
    #         prompt += "(motion lines:1.2),"
    # ここまで睡眠中


    # 顔を見せない構図なら表情作りはスキップ
    if flags["drawface"] == 1 :

        # 体力が減ると汗をかく
        # 現在地が閾値より低い または MAXから〇〇以上減ってる

        damage = order["最大体力"] - order["体力"]
        if damage > 50:
            if order["体力"] < 700:
                prompt += "(sweat:1.4),(Lots and lots of drips of sweat),steam,"
            elif order["体力"] < 1100:
                prompt += "(sweat:1.4),steam,"
            else:
                if damage in range(200,400):
                    prompt += "(sweat:0.8),"
                elif damage in range(400,600):
                    prompt += "(sweat:1.0),steam,"
                elif damage in range(600,800):
                    prompt += "(sweat:1.2),Lots and lots of drips of sweat,steam,"
                elif damage in range(800,1000):
                    prompt += "(sweat:1.3),(Lots and lots of drips of sweat),steam,"
                elif damage >= 1000:
                    prompt += "(sweat:1.4),(Lots and lots of drips of sweat),steam,"

        # もう止めないとまずいな感を出す
        if order["体力"] < 500:
            prompt += "(expressionless:1.3),(shadowy face:1.4),(half opened mouth:1.4),"
            eyeprompt += "(half closed eyes ,empty eyes:1.5),"

    

        #気力がないとぐったりする
        if order["気力"] < 100:
            prompt += "(she is utterly exhausted:1.3),sleepy,"
            eyeprompt += "empty eyes,looking away,"
            tsuyoijoudou = True

        # 酔い
        # if order["酔い"] in range(1000,3000):
        #     prompt += "drunk,blush"
        # elif order["酔い"] in range(3000,6000):
        #     prompt += "(wasted,get  drunk:1.2),blush,"
        # elif order["酔い"] in range(6000,10000):
        #     prompt += "(wasted,get  drunk:1.4),(blush),"
        # elif order["酔い"] >= 10000:
        #     prompt += "(wasted,get  drunk:1.4),(expressionless:1.2),mind break,(blush),"


        # 調教に対する反応 TRAIN中のみ反映＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
        if order["scene"] == "TRAIN":
            # 苦痛 の判定-----------------------------------------------------------------
            # 苦痛は累積ではなく瞬間値が大事。palam_upで見る
            # 刻印1相当
            if order["palam_up"]["苦痛"] > 500:
                prompt += "Groaning,"
            # 刻印3相当
            if order["palam_up"]["苦痛"] > 3000:
                Pain = True
                tsuyoijoudou = True
                ra = random.randrange(2)
                #目と口をギュッと閉じるパターン
                if ra == 0:
                    prompt += "Squinting,closed eyes,clenched teeth,"
                    negative += "smile,open eyes,pupil,"
                    ClosedEyes = True
                #目を見開くパターン もう少し痛そうにしたいが
                if ra == 1:
                    prompt += "(tears),open mouth,"
                    eyeprompt += "(startled eyes,.-.),"
                    negative += "smile,"
                

            # 恐怖 の判定-----------------------------------------------------------------
            # 恐怖もupで見る
            # 軽い恐れなら timid,bearish
            # Terrifiedはちょっと漫画チックすぎる
            if order["palam_up"]["恐怖"] > 300:
                prompt += "(She's scared)," #単語でも一緒かなあ
                tsuyoijoudou = True
            if order["palam_up"]["恐怖"] > 1000:
                prompt += "(tears),"

            if order["palam_up"]["恐怖"] > 3000:
                prompt += "(tears:1.4)," 

            # 恐怖顔Loraがいい感じ
            if order["palam_up"]["恐怖"] in range(6000,10000):
                eyeprompt += "<lora:scaredExpression_v18:0.5>,scared expression,"               
            elif order["palam_up"]["恐怖"] > 10000:
                eyeprompt += "<lora:scaredExpression_v18:0.9>,scared expression,"

            # 刻印レベルの苦痛フラグが立ってる場合、好意・欲望・羞恥の表情をつけない。ただし高レベルマゾは例外
            if (Pain == False) or (order["abl"]["マゾっ気"] >= 4):  
                # 欲情の判定-----------------------------------------------------------------
                # うまくいかない
                pleasure = order["palam_up"]["快C"]+order["palam_up"]["快B"]+order["palam_up"]["快V"]+order["palam_up"]["快A"]
                # 4部位の珠入手の合計で見る

                if pleasure >= 3000:
                    tsuyoijoudou = True

                if pleasure in range(100,1000): #最初の目標は100
                    prompt += "(blush:0.7),"
                elif pleasure in range(1000,3000):
                    prompt += "Orgasmic expression,(blush:0.9)"
                elif pleasure in range(3000,7500):
                    prompt += "(Orgasmic expression),blush,"
                elif pleasure > 7500:
                    prompt += "(Orgasmic expression:1.2),blush,"
                    eyeprompt += "{rolling eyes|},"
                elif order["palam_up"]["欲情"] >= 1000:
                    prompt += "Orgasmic expression,blush,"

                # #絶頂
                # ahe_strength = order["絶頂の強度"]
                ahe_strength = order["快楽強度"]

                # 淫乱持ちは少しアヘりやすい
                # 恋慕と排他じゃないバリアントでは望まなくても淫乱がついてしまうので控えめの補正にする
                if "淫乱" in order["talent"]:
                    if ahe_strength > 0:
                        ahe_strength += 2
                # 四重絶頂で補正
                tajuu = np.count_nonzero([order["C絶頂"],order["B絶頂"],order["V絶頂"],order["A絶頂"]])
                if tajuu == 4:
                    ahe_strength += 6

                # 基本の絶頂エフェクト
                if ahe_strength > 0:
                    prompt += "(motion lines:1.2),"
                    eyeprompt += "(startled eyes),"

                if ahe_strength >= 4: #強度4　2重強絶頂以上でアヘり始める
                    #絶頂強度4～7 軽めのアヘ顔
                    if ahe_strength <= 7:
                        prompt += "(ahegao:0.7),"
                    #絶頂強度8～11 そこそこアヘ顔 最強絶頂で9 淫乱なら11に届く。単発Vセックスとかでこれ以上に届いてほしくはない
                    elif ahe_strength <= 11:
                        prompt += "ahegao,{open mouth|:o},drooling,saliva,"
                    #絶頂強度12～14 だいぶアヘ顔
                    elif ahe_strength <= 14:
                        prompt += "<lora:ahegao_v1:0.8:F>,ahegao,open mouth,drooling,saliva,"
                    #絶頂強度14～16 かなりアヘ顔 
                    elif ahe_strength <= 16:
                    #確率でheadback 20%
                    #headbackは表情描写と衝突して絵が壊れるっぽい
                        ra = random.randrange(4)
                        if ra == 0:
                            prompt += "<lora:conceptHeadbackArched_v10:1:CT>,(HEADBACK) "
                            ClosedEyes = True
                        else:
                            prompt += "<lora:ahegao_v1:1.5:F>,(ahegao),open mouth,drooling,saliva,"
                    #絶頂強度17超え 完全にアヘ顔 
                    else:
                        prompt += "<lora:ahegao_v1:1.6:F>,(ahegao:1.5),open mouth,(drooling),saliva,"

                # 羞恥の判定-----------------------------------------------------------------

                # embarrassed 1.2でもう十分なくらい恥ずかしそう blushが1.0ついている場合0.5位まで変化なし
                # 普通の調教だと恥情はあんまり上がらないが欲情で赤くなってるはず
                # embarrassedよりshameの方がマイルド なはず
                if order["palam"]["恥情"] >= 1000:      
                    if order["palam"]["恥情"] <= 5000:      
                        prompt += "(shame:0.5),"
                    elif order["palam"]["恥情"] <= 10000: 
                        prompt += "(shame:0.7),"
                    else:
                        prompt += "shame,"
                
                if order["palam_up"]["恥情"] >= 500:
                    if order["palam_up"]["恥情"] < 1000:
                        prompt += "(embarrassed:0.6),"
                    else: 
                        tsuyoijoudou = True
                        prompt += "embarrassed,"

        # ここからは素質・刻印等によるもの TRAIN以外でも反映＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

        # 反発 の判定-----------------------------------------------------------------
        # angerは口が歪んだりギャグみたいになる
        # Hostileはたまに幼い輪郭になる
        # furiousはへの字口が気になる
        # いずれも反発刻印3に見合うほどの憎悪は感じない

        # 反発刻印と恋慕の効果は主人以外には向けない
        if NotMaster == False:
            # 反発刻印3
            if order["mark"]["反発刻印"] == 3:
                prompt += "(Hostile:1.2)," # とりあえず埋めたけど弱い
            # 反発刻印2 重複させる
            if order["mark"]["反発刻印"] >= 2:
                prompt += "anger," # わかりやすくキレる 軽めにかけないとギャグ顔になる
            
            # 反発刻印1
            if order["mark"]["反発刻印"] >= 1:
                if not ClosedEyes :
                    eyeprompt += "(glaring eyes:1.0),"
                    tsuyoijoudou = True

            # 従順1がつくまでは嫌われてると判断
            elif order["abl"]["従順"] == 0:
                if "サド" in order["talent"]: #frownは困り顔になって一部キャラに違和感があったので
                    prompt += "unamused,"
                else:
                    prompt += "(frown:0.9),"


            # 好意
            # 刻印レベルの苦痛フラグが立ってる場合、好意・欲望・羞恥の表情をつけない。ただし高レベルマゾは例外
            if (Pain == False) or (order["abl"]["マゾっ気"] >= 4):  
                # 恋慕でハートを盛る
                chk_list = ["恋慕","親愛","相愛"]
                and_list = set(order['talent']) & set(chk_list)
                if (len(and_list)) > 0:
                    prompt += "(tender,Loving),(hearts around face:0.8)," # この辺の表情をもっとうまいことやりたい
                    if order["palam_up"]["恭順"] in range (5000,15000): # ハート増量
                        prompt += "hearts in speech bubble around face,happy,"
                    elif order["palam_up"]["恭順"] > 15000: # 追加
                        prompt += "(big hearts in speech bubble around face),(happy:1.2),"
                    
                    Love = True


        # 調教初期の表情 つまんなそうな顔
        # 何も指定しないとカワイイ笑顔になるのを防ぐためのデフォルト表情
        # scgpro 初対面シチュエーションが多いので軽めに200で解除する

        taikutsu = 2
        if (order["abl"]["従順"] > 3) or (order["好感度"] > 50):
            taikutsu -= 1
        if (order["abl"]["従順"] > 4) or (order["好感度"] > 200):
            taikutsu -= 1

        # 性格等で増減

        if tsuyoijoudou == True: # 余裕ないときには退屈な表情はしない
            taikutsu = 0    

        if taikutsu >= 2:
            # 従順低い時のサドは挑戦的な顔
            if "サド" in order['talent']:
                prompt += "arrogance,"
            else: 
                # サド以外は退屈な顔
                prompt += "(Blank expression,boring:1.3)," 
        elif taikutsu == 1:
            if "サド" in order['talent']:
                prompt += "arrogance,"
            else:
                prompt += "Blank expression,boring,"


        # 強い情動がないとき恋慕でたまに見せる表情
        # ここを性格で個性分けしたい
        if tsuyoijoudou == False:
            if Love == True:
                ra = random.randrange(20)
                if ra == 1:
                    prompt += "(closed eyes smile,blushing:1.3),"
                    ClosedEyes == True
                if ra == 2:
                    prompt += "(closed eyes smile,blushing:1.3),open mouth,"
                    ClosedEyes == True                
                if ra == 3:
                    prompt += "(heart racing,blushing:1.3),"
                if ra == 4:
                    prompt += "(delighted),"


        #生来のTalentによる顔つき

        #たれ目傾向 taremeは効きが悪い 恐怖の珠が上がるのでそっちでも補正できる
        chk_list = ["臆病","大人しい","悲観的"]
        and_list = set(order['talent']) & set(chk_list)
        if (len(and_list)) > 0:
            prompt += "(tareme),"
            negative += "(glaring:0.7),"

        #ツリ目傾向
        chk_list = ["反抗的","気丈","プライド高い","ツンデレ","サド"]
        and_list = set(order['talent']) & set(chk_list)
        if (len(and_list)) > 0:
            eyeprompt += "(glaring eyes:0.7)," # 0.7でもよく効いたり全然効かなかったりする。


        #無感情 expressionlessは口を閉じる効果が高い。八の字眉傾向
        # empty eyes 
        # chk_list = ["無関心","感情乏しい","抑圧"]
        # and_list = set(order['talent']) & set(chk_list)
        # if (len(and_list)) > 0:
        #     if order["絶頂の強度"] == 0:
        #         eyeprompt += "(empty eyes),"
        #         prompt += "expressionless,"
        #         negative += "((blush)),troubled eyebrows,"


        #狂気 強調しないと滅多に光らないはず。キレたときとか条件付きで光るようにした方がいいかも。した。
        chk_list = ["狂気","狂気の目"]
        and_list = set(order['talent']) & set(chk_list)
        if (len(and_list)) > 0:
            if order["mark"]["反発刻印"] == 3: #反発3だとずっと光る
                eyeprompt += "(glowing eyes:1.4),"
            elif order["palam_up"]["反感"] >= 500: #反感の上がるようなことをすると光る
                eyeprompt += "(glowing eyes:1.4),"
            else:
                eyeprompt += "glowing eyes," #きまぐれに光る？

        #笑顔up 常に効いてるのはおかしいのでいったん保留
        # chk_list = ["楽観的","解放","鼓舞"]
        # and_list = set(order['talent']) & set(chk_list)
        # if (len(and_list)) > 0:
        #     if Pain == False:
        #         prompt += "joyful,"

        #魅力 
        chk_list = ["魅力","魅惑","謎の魅力"]
        and_list = set(order['talent']) & set(chk_list)
        if (len(and_list)) > 0:
             prompt += "seductive,"
    
        #頭よさそう
        chk_list = ["自制心","快感の否定","教育者","調合知識"]
        and_list = set(order['talent']) & set(chk_list)
        if (len(and_list)) > 0:
             prompt += "smart,"

        #ドヤ顔
        chk_list = ["生意気","目立ちたがり"]
        and_list = set(order['talent']) & set(chk_list)
        if (len(and_list)) > 0:
             prompt += "(smug:0.6)," #ちょっと強いワード

        #目の処理 Closedでなければeyepromptを統合、csvの目の色を反映
        if ClosedEyes == False:
            prompt += eyeprompt
            if order["eyecolor"] != "":
                prompt += order["eyecolor"] + " eyes,"

    # 顔はここまで------------------------------------------------------------------------

    return prompt,negative

