import inspect
# from module.emo import Expression
from module.csv_manager import CSVMFactory
# from module.sub import get_width_and_height

csvm = CSVMFactory.get_instance()
class PromptMakerRX():
    """
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
        #ここで定義してないkeyも動的に追加されるが、書いておいたほうが見た目にわかりやすい。
        self.prompt =    {"scene":"","chara":"","cloth":"","general":""}
        self.negative =  {"base":"","scene":"","chara":"","cloth":"","general":""}
        self.width = 0
        self.height = 0


    def gather_instance_data(self):
        """PromptMaker内のインスタンス変数をまとめて一つの辞書とした戻り値を返す
        ExpressionをPromptMakerを継承したサブクラスとして変数を継承すると
        PromptMakerのメソッドで設定したフラグが初期化される問題に対応

        Returns:
            dict: PromptMakerのインスタンス変数すべて
        """
        # inspect.getmembersを使用して、selfに属するすべての属性とその値を取得
        # 以下のフィルタを適用して、特殊メソッド（__init__）やメソッドは除外
        # name.startswith('__')：特殊メソッド（例：__init__）を除外
        # inspect.ismethod(value)：メソッド（関数）を除外
        pm_var = {name: value for name, value in inspect.getmembers(self)
                if not name.startswith('__') and not inspect.ismethod(value)}
        return pm_var


    def initialize_class_variables(self):
        # 判定につかうセーブデータをクラス変数内にしまう専用のメソッド
        # 判定に必要なSaveデータをinitで全部先に取得すると読みにくので分離だ
        #値が存在しない場合 NanやNoneにならないようにする あとで
        self.charno = self.sjh.get_save("キャラ固有番号")#int
        self.com    = self.sjh.get_save("シーン名")#str
        self.succ   = 1
        self.getCSV_orders  = self.sjh.get_save("getCSV")#dict型のリスト


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

        # 基礎プロンプトの読み込み
        efc = "Effect.csv"
        prompt = csvm.get_df(efc,"名称","基礎プロンプト","プロンプト")
        nega = csvm.get_df(efc,"名称","基礎プロンプト","ネガティブ")
        self.add_element("base", prompt, nega)

        # self.create_location_element() #場所

        self.create_scene_element() #シーン
        self.create_chara_element() #キャラ

        if self.getCSV_orders:
            self.execute_getCSV_orders() #getCSV:csvファイル中を検索するパラメータをera出力に直接記述するシステムの展開



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
            self.prompt[elements] = ""
            self.negative[elements] = ""

        if prompt is not None and prompt != "ERROR":
            self.prompt[elements] += prompt
        if nega is not None and nega != "ERROR":
            self.negative[elements] += nega


    def execute_getCSV_orders(self):
        """
        オーダーテキストに直接csvm.get_dfに入れる各パラメータを書けるようにした
        json中に"getCSV"という辞書のリストがあればそれを展開する
        """
        # リスト中の辞書の数だけ繰り返す
        for dictionary in self.getCSV_orders:
            csv = dictionary["csv"]
            element = dictionary["element"]
            searchcolumn = dictionary["searchcolumn"]
            searchvalue = dictionary["searchvalue"]
            pickcolumn = dictionary["pickcolumn"]

            prompt = csvm.get_df(csv,searchcolumn,searchvalue,pickcolumn)
            # 空やエラーのときは何も追加しない
            if prompt != "ERROR":
                self.add_element(element, prompt, None)


    def create_scene_element(self):
        """
        シーン名に対応したプロンプトをscene要素に書き出す。空欄のときは汎用シーンを返す。
        """
        scn = "Scene.csv"

        # プロンプト欄が未記入の場合はget_dfが"ERROR"を返すのでEvent.csvの汎用調教を呼ぶ
        prompt = csvm.get_df(scn,"シーン名",self.com,"プロンプト")
        if prompt == "ERROR":
            prompt = csvm.get_df(scn,"シーン名","汎用シーン","プロンプト")
            nega = csvm.get_df(scn,"シーン名","汎用シーン","ネガティブ")
        else:
            nega = csvm.get_df(scn,"シーン名",self.com,"ネガティブ")
        self.add_element("scene", prompt, nega)



    def create_chara_element(self):
        """
        このcreate_chara_elementメソッドは、キャラクターの描画に関するプロンプトを生成するために使うんだ。
        CSVファイルからキャラクターに関するデータを読み込み、適切なプロンプトとネガティブプロンプトを追加するぜ。

        毎回記述されるキャラクターの基本的なプロンプトはEffect.csvから読み出す。
        """
        cha = "Character.csv"
        efc = "Effect.csv"

        # キャラ描写で毎回記述するプロンプト Effect.csvから読み出す
        charabase = csvm.get_df(efc,"名称","人物プロンプト","プロンプト")
        self.add_element("base", charabase, None)

        prompt = csvm.get_df(cha,"キャラ固有番号",self.charno,"プロンプト")

        self.add_element("chara", prompt, None)



    def prompt_debug(self):
        """
        呪文作成前にどんな要素を格納されてるか調べるやつ
        """
        for key, value in self.prompt.items():
            print (f'prompt:::{key}:::{value}')

        for key, value in self.negative.items():
            print (f'nega:::{key}:::{value}')

        # 描画flag管理は必要に駆られるまでオミット
        # for key, value in self.flags.items():
        #     print (f'flags:::{key}:::{value}')
    