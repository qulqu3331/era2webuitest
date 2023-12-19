"""eraのTEXTLOG.ERBが出力したJSONを扱いやすいように変換してクラス辞書に格納
呼び出すときは以下の例のようにファクトリークラスから呼び出す
self.save = SJHFactory.create_instance(save_path)

キューごとにインスタンスを作成するので扱うときは引数でインスタンスごと渡す
使用例: TaskExecutor の prompt,negative,gen_width,gen_height = promptmaker(sjhandler)
Returns:
    SaveJSONHandler:
"""
import sys
import json
import unicodedata

class SJHFactory:
    """
    これは、eraのセーブデータの変換場だぜ！
    eraの複雑なJSONデータを扱いやすく変換してくれるSaveJSONHandlerインスタンスを、
    あっという間に作り出すんだ。

    ここは、ファイルパスを受け取って、それをSaveJSONHandlerに渡す。
    すると、JSONデータの管理や処理ができるようになるんだ。

    Returns:
        SaveJSONHandler:eraのJSONデータを扱うためのSaveJSONHandlerクラスのインスタンス。
                        これでデータ処理がぐっと楽になるぜ！
    """
    @staticmethod
    def create_instance(file_path):
        """
        このスタティックメソッドは、eraのJSONデータを扱うための専用ツール、
        SaveJSONHandlerのインスタンスを生成する関数だぜ！

        クラスインスタンスが不要なので、直接クラスからこのメソッドを叩ける。
        つまり、SJHFactory.create_instance()という風に使うんだ。

        Args:
            file_path (str): JSONデータのファイルパス。ここにeraのセーブデータの場所を指定するんだ。
                            TaskExecutorから適時最新のpathが送られてくるから意識する必要はあまりないぜ｡

        Returns:
            SaveJSONHandler:指定されたファイルパスのJSONデータを扱うSaveJSONHandlerのインスタンスを返す。
                            これでJSONの扱いが楽チンになるぜ！
        """
        return SaveJSONHandler(file_path)

class SaveJSONHandler:
    """
    saveのjsonを扱いやすい形にするクラス
    FileHandlerから更新されたtxtのパスを受け取る
    """

    def __init__(self, savetxt_path=None):
        self.data = None
        if savetxt_path:
            self.load_save(savetxt_path)


    def load_save(self, savetxt_path):
        """渡されたpathからJSONを読んで辞書に格納
        Args:
            new_savetxt_path (str): txtのpath
        """
        if savetxt_path is None:
            print("エラー: ファイルパスが指定されていません。txtの更新を待っています。")
            return  # メソッドをここで終了させる
        try:
            with open(savetxt_path, 'r', encoding='utf-8_sig') as file:
                self.data = json.load(file)
                self.cast_data()
        except FileNotFoundError as e:
            print(f'エラー: ファイル "{savetxt_path}" が見つかりません。 - {str(e)}')
        except json.JSONDecodeError as e:
            print(
                f'エラー: ファイル "{savetxt_path}" の出力がjsonフォーマットになってない。 - {str(e)}')
            sys.exit()


    def cast_data(self):
        """
        `self.data` のデータ型を必要に応じて変換する。
        """
        # `self.data` を再帰的に辿って型を変換する
        self.data = self._cast_recursive(self.data) #数字だけのstrをint
        self.data = self._convert_to_halfwidth_recursive(self.data) #全角英字を半角英字

    def _cast_recursive(self, data):
        """
        数字が含まれる文字列を整数型に変換したデータを返す再帰的な補助関数。
        キーが文字列型の数字であれば整数型に変換する。
        """
        if isinstance(data, dict):
            new_dict = {}
            for key, value in data.items():
                # キーが文字列型の数字なら整数に変換
                new_key = int(key) if isinstance(key, str) and key.isdigit() else key
                new_dict[new_key] = self._cast_recursive(value)
            return new_dict
        elif isinstance(data, list):
            return [self._cast_recursive(item) for item in data]
        elif isinstance(data, str) and data.isdigit():
            return int(data)  # 文字列が数字のみなら整数に変換
        else:
            return data  # 他の型はそのまま返す

    def _convert_to_halfwidth_recursive(self, data):
        """
        全角英字が含まれる文字列を半角英字に変換したデータを返す再帰的な補助関数。
        文字列が全角英字を含んでいれば、それを半角英字に変換する。
        """
        if isinstance(data, dict):
            new_dict = {}
            for key, value in data.items():
                new_key = self._convert_to_halfwidth_recursive(key)
                new_dict[new_key] = self._convert_to_halfwidth_recursive(value)
            return new_dict
        elif isinstance(data, list):
            return [self._convert_to_halfwidth_recursive(item) for item in data]
        elif isinstance(data, str):
            return unicodedata.normalize('NFKC', data)  # 全角英字を半角英字に変換
        else:
            return data  # 他の型はそのまま返す

# このメソッドを使って全角英字を含むデータ構造を半角英字に変換する

    def update_data(self, key, new_value):
        """
        指定されたキーに対して新しい値を設定する。

        この関数は self.data 辞書内の特定のキーを更新する。new_value はどんなデータタイプでも良い。

        Args:
            key (str): 更新するデータのキー。
            new_value: 新しい値（どんなデータタイプでも可）。
        """
        self.data[key] = new_value


    def get_save(self, key):
        """
        お前が渡したキーにピタッと合うデータを、JSONの海から引き上げてくる機能だ。

        JSONファイルはもう読み込んである...といいんだが、もしそれがまだなら
        お前にエラーメッセージを叩きつける。そしたら、適当なファイルを読み込むんだな。
        この関数が呼ばれたら、指定したキーでデータを探してその値を返す。
        もしキーが見当たらなかったらしゃーなし、Noneを返すぞ。

        Args:
            key (str): 辞書型で読み込んだJSONデータから取得したい値のキーだ。

        Returns:
            Any: キーに対応するstr,int,list,dict、もしくはキーが存在しない場合はNone。
        """
        if not self.data:
            print('エラー: JSONファイルが読み込まれていません。')
            return None
        if key not in self.data:
            print(f'エラー: 今は "{key}"って状況にないみたいだぜ')
            return None
        return self.data.get(key)
    