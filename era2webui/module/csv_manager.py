"""
CSVM（CSV Manager）モジュール

このモジュールは、era2webui用に特別に用意されたCSVデータを効率的に管理し、処理するための機能を提供する。
主にCSVファイルの読み込み、データの変換、そしてCSVデータの検索といったタスクを担当するぜ。

機能概要:
- CSVファイルの読み込み: era2webui用に用意されたCSVファイルをPandas DataFrameとして読み込む。
- データ変換: 文字列型の数値を整数型に変換したり、全角数字を半角に変換するなど、データを扱いやすい形式に変換する。
- CSVデータの検索と取得: 特定の条件に基づいてCSVデータから情報を検索し、取得する。

このモジュールの使用により、era2webuiの機能拡張やデータ管理がよりスムーズに、効率的に行えるぜ。
"""
import glob
import os
import re

import pandas as pd


def search_imported_variant():
    """ここがなんか汚い
    'era2webui.py' からインポートされているバリアントを検索する。
    Returns:
        str:インポートされているバリアントのモージュールが入ったフォルダ名
            見つからない場合はNoneを返す。
    """
    # カレントディレクトリのパスを取得
    base_dir = os.path.dirname(__file__)
    # カレントディレクトリの親ディレクトリのパスを取得
    parent_dir = os.path.dirname(base_dir)
    # 親ディレクトリにある 'era2webui.py' へのパスを作成
    era2webui_path = os.path.join(parent_dir, 'era2webui.py')

    try:
        with open(era2webui_path, 'r', encoding='utf-8') as file:
            content = file.read()
        match = re.search(
            r'^from (eratohoYM|eraTW|eraImascgpro)', content, re.MULTILINE)
        if match:
            return match.group(1)
        else:
            print("バリアントを選んでfromのコメントアウトを解除してください")
            return None
    except FileNotFoundError:
        print(f"'{era2webui_path}' が見つかりません。")
        return None



class CSVMFactory:
    """
    複数箇所から呼び出されるのでファクトリークラスとかでインスタンスを実行させて
    CSVMの多重起動を防ぐ
    Returns:
        _type_: _description_
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CSVManager()
        return cls._instance

class CSVManager:
    """
    このクラスはCSVファイルとのやり取りをスムーズにしてくれるマジックアイテムだ。
    CSVファイルからのデータ読み込みや、それをキャッシュする仕組み、さらには新しいCSVへの書き込みまで、
    こいつがあれば一通りの操作をバッチリこなせるぜ。

    CSVファイルリストを生成して、特定のバリアントの全CSVファイルをキャッチ。
    読み込んだものはキャッシュに保存しておき、再利用が可能になっているんだ。
    チームでの作業や大量のデータを扱いたい時にも、この便利さは必見。

    Attributes:
        csvlist (str): CSVファイルパスのリストが記載されたCSVファイルへのパス。
        loaded_csvs (dict): 読み込み済みのCSVデータをキャッシュするための辞書。

    """
    def __init__(self):
        self.csvlist = {}
        self.csvdatas = {}
        self.generate_csvlist()
        self.csvdata_import()
        self.combine_character_csvs() #Add_Characterを結合してCharacter.csvとして扱うので必ずself.csvdata_import()の後に呼べ
        self.add_cloth_columns()
        self.load_display_part()


    def generate_csvlist(self):
        """
        現在のバリアントのCSVファイルリストを生成し、クラス変数保存するんだ。
        'era2webui.py' からインポートしてるバリアントに基づいて、
        対象ディレクトリ内のCSVファイルのパスをリストアップしてくれるぜ。

        そうして得られたCSVファイルリストは、操作がしやすいように
        'csv_list.csv' ファイルに名前とパスが記録される。
        バリアント選択が済んでない場合は教えてやるからな。
        """
        # 一致したモジュール名を取得
        imported_module = search_imported_variant()
        print(f"対応するeraバリアント: {imported_module}")

        if imported_module:
            # モジュールのあるディレクトリの親ディレクトリを取得
            base_dir = os.path.dirname(os.path.dirname(__file__))
            # モジュール名を含むディレクトリへのパスを組み立てる
            variantdir = os.path.join(base_dir, imported_module)
            csvdir = os.path.join(variantdir, 'csvfiles')

            # 指定ディレクトリ内の全てのCSVファイルのパスを取得し、辞書に格納
            self.csvlist = {os.path.basename(file): file for file in glob.glob(
                os.path.join(csvdir, '*.csv'))}

            print(f"{imported_module}のCSVファイルのリストをCSVManagerクラス変数に格納したぜ。")
        else:
            print("バリアントが見つからないか、選択されていないようだ。")


    def csvdata_import(self):
        """
        generate_csvlistで作られたself.csvlistを基づいて
        名前をキーにしてデータフレームに変換してクラス変数に保存
        """
        for csv_name, _ in self.csvlist.items():
            try:
                df = self.read_csv(csv_name)
                if df is not None:
                    # str型で数字が入っているセルをint型に変換する前処理
                    df = self.convert_str_numbers_to_int(df)
                    # 全角数字を半角数字に変換する前処理
                    df = self.convert_fullwidth_to_halfwidth(df)

                    self.csvdatas[csv_name] = df
            except FileNotFoundError:
                print(f"csvdata_import: CSVファイル {csv_name} が見つからないぜ: {csv_name}")
        print("CSVのDataをCSVManagerのクラス辞書に登録したぜ")


    def add_cloth_columns(self):
        if 'Cloth.csv' in self.csvdatas:
            df = self.csvdatas["Cloth.csv"]
            columns_to_copy  = {
                'class_name': 'カテゴリ',
                'obj_id': 'カテゴリ内番号',
                'attribute_name': '衣類名',
                'equip_position_no': '装備部位',
                'display_part_no': '表示部位NO',
                'display_part': '表示部位',
                # 他のカラム変換もここに追加
            }
            transformed_df = self.add_columns_with_copy(df, columns_to_copy)
            self.csvdatas["Cloth.csv"] = transformed_df  # 更新されたDataFrameを保存
        else:
            # 必要なファイルがない場合の処理
            print("add_cloth_columns:ファイルが見つからないから、処理飛ばすぜ。バリアンとによっては関係ない処理だ")


    def combine_character_csvs(self):
        """
        'Character.csv' と 'Add_Character.csv' を結合し、
        結合されたDataFrameを 'Character.csv' キーで保存する。
        """
        # パスの名前に基づいて両方のCSVファイルをDataFrameとして読み込む
        char_df = self.read_csv('Character.csv')
        add_char_df = self.read_csv('Add_Character.csv')

        # もしファイルが見つかれば、DataFrame同士を結合する
        if char_df is not None and add_char_df is not None:
            combined_df = pd.concat([char_df, add_char_df]).reset_index(drop=True)

            # 統合したDataFrameを 'Character.csv' キーでcsvdatasに格納
            self.csvdatas['Character.csv'] = combined_df


    def load_display_part(self):
        """
        display_part 辞書に(表示部位:n)のCSVデータを追加
        """
        # Cloth.csv と display_part.csv が存在するかチェック
        if 'Cloth.csv' in self.csvdatas and 'display_part.csv' in self.csvdatas:
            cloth_df = self.csvdatas['Cloth.csv']
            display_part_df = self.csvdatas['display_part.csv']
            # display_partのデータを使ってcloth_dfを更新
            for index, row in cloth_df.iterrows():
                # display_part_dfから対応するdisplay_part_noを検索
                display_part_row = display_part_df[display_part_df['display_part'] == row['表示部位']]
                if not display_part_row.empty:
                    # display_part_noを取得
                    new_display_part_no = display_part_row.iloc[0]['display_part_no']

                    # cloth_dfの両方のカラムに新しい値を設定
                    cloth_df.at[index, 'display_part_no'] = new_display_part_no
                    cloth_df.at[index, '表示部位NO'] = new_display_part_no

            # 更新されたDataFrameをcsvdatasに再代入
            self.csvdatas['Cloth.csv'] = cloth_df
        else:
            # 必要なファイルがない場合の処理
            print("load_display_part:ファイルが見つからないから、処理飛ばすぜ。バリアンとによっては関係ない処理だ")


    def read_csv(self, csv_name):
        """
        CSVファイル名をキーにクラス変数のPandas DataFrameを読み込んで返す。
        Args:
            csv_name (str): 読み込むCSVファイルの名前。
        Returns:
            DataFrame: CSVから読み込んだデータを含むPandasのDataFrame、
                        またはCSVファイルが見つからない場合はNone。
        """
        # find_csv_path メソッドを使ってファイルの正しいパスを取得する例
        _, file_path = self.find_csv_path(csv_name)

        try:
            df = pd.read_csv(file_path)
            return df
        except FileNotFoundError:
            print(f"read_csv:ファイル {file_path} が見つからなかったぜ。")
            return None
        except pd.errors.ParserError as e:
            print(f"read_csv:ファイル {file_path} の読み込み中にパースエラーが発生したぜ。詳細: {e}")
            return None
        except Exception as e:
            print(f"read_csv:ファイル {file_path} の読み込み中に予期せぬエラーが発生したぜ。詳細: {e}")
            return None


    def find_csv_path(self, csv_name):
        """
        CSVファイル名から正しい道すじを探し当て、その貴重なパス情報を手に入れる。

        おまえが欲しいCSVの名前を小さな声で教えてくれたら、こいつがお前の行く先を
        案内してくれるからな。csvlistを拾い読みして、指定されたファイル名と同じ名前の
        ラインを見つけ出す。そしたら、我々にとって重要なパス情報をすぐにでも
        提供してくれるんだ。

        Args:
            csv_name (str): おまえが見つけたいCSVファイルの名前だ。

        Returns:
            tuple: おまえの求めるファイルが実際にどこに落ちてるのか、その名前とパスをタプルで提供する。
                行が見つからなかった場合、悲しいけど None を返すことになるぞ。
        """
        # CSVファイルリストを読み込む
        for name, path in self.csvlist.items():
            if name.lower() == csv_name.lower():  # 大文字小文字を区別しない比較
                return name, path  # 名前とパスを返す｡ 名前はエラー表示用
        print(f"find_csv_path:'{csv_name}' という名前のCSVファイルは見つからなかったぜ。")
        return None, None


    def get_df(self, csvname, key, value, column):
        """
        気になる辞書データの要素を拾い出すにはこのメソッドを使うんだぜ｡。
        指定されたキーと値を元に辞書の中から目当ての情報を引きずり出す作業だ。

        例えば、'NOTFOUND'っていう状態の説明が見たいなら、
        状態名が'NOTFOUND'にぴったり合う行をルートアウトして、そこから説明列のデータを引っこ抜くんだ。

        探しているものが見つからなかったら空の文字列を返して、何か変なことが起こっていたら'Error'って返すから頼りにしてくれ。
        Args:
            dict_name (str): 調べる辞書の名前。
            key (str): 辿り着きたい情報のあるキー名だ。これがあるおかげで手がかりになる。
            value (str): 目指す値。この値と一致する行を特定する。
            column (str): このキーからデータをひっぱり出す。
        Returns:
            str: 発掘されたデータ。もしなにもなかったら空の文字列、何か不具合があれば'Error'とする。
        Examples:
            こんな感じで使うんだ：get_value_from_dict("status_descriptions", "状態名", "NOTFOUND", "説明")
            この例なら、'NOTFOUND'という状態に対する説明をくれてやる。
        """
        try:
            # CSVManagerの辞書からデータフレームを取得
            dataframe = self.csvdatas[csvname]
            filtered_df = dataframe[dataframe[key] == value]

            if not filtered_df.empty:
                prompt = filtered_df.loc[:, column].fillna("").values[0]
                if prompt == '':
                    # promptが空文字の場合の処理
                    print(f"get_df: {csvname}: '{key}' の項目が '{value}' の行は'{column}' 列は空文字でした。") #プロンプト埋め用
                    return "ERROR"
            else:
                print(f"get_df: {csvname}: '{key}' の項目が '{value}' のデータがありません")
                return "ERROR"

        except KeyError as e:
            print(f"get_df: {csvname}: 指定したキー '{key}' または列 '{column}' で '{value}' が無いぞ。{e}")
            return "ERROR"
        except IndexError as e:
            print(f"get_df: {csvname}: 指定したインデックスが範囲外。{e}")
            return "ERROR"
        except pd.errors.DataError as e:
            print(f"get_df: {csvname}: データ処理に関するエラー。{e}")
            return "ERROR"
        except Exception as e:
            print(f"get_df: {csvname}: 不明な他のエラー: {e}")
            return "ERROR"
        return prompt


    def get_df_2key(self, csvname, key, value, subkey, subvalue, column):
        """
        辞書から条件にピッタリ合ったデータを探り出すなら、このメソッドが役に立つぜ。
        ちゃんとした2つのキーとその対応する値を基にして、賢くデータを掘り出してくるんだ。

        キーとサブキー、それに一致する値を指定することで、要求された情報を辞書の中から見つけ出す。
        まるでダブルロックされた秘宝を解き放つような感じさ。
        Args:
            csvname (str): 調べたい辞書の名前だ。データの海の中でのガイド役になる。
            key (str): メインキーの列名。
            value (str): メインキーの列におけるターゲットとなる値。
            subkey (str): サブキーの列名だ。
            subvalue (str): サブキーの列におけるターゲットとなる値。
            column (str): 結果的に値を取得したい列の名称。
        Returns:
            str: 探し出された報酬。条件にマッチするものが無ければ空文字列、何かおかしい時は'Error'を返す。
        """
        try:
            # CSVManagerの辞書からデータフレームを取得
            dataframe = self.csvdatas[csvname]

            # DataFrameから条件に合致する行を検索し、指定されたcolumnの値を取得
            filtered_df = dataframe[(dataframe[key] == value) & (dataframe[subkey] == subvalue)]
            if not filtered_df.empty  and not pd.isna(filtered_df.iloc[0][column]):
                prompt = filtered_df.iloc[0][column]
            else:
                print(f"Error: {csvname}: 条件'{key} = {value}' かつ '{subkey} = {subvalue}' を満たす '{column}' がNaNか見つからなかったぜ")
                prompt = "ERROR"

        except KeyError as e:
            print(f"get_df_2key: {csvname}: キー'{key}'か'{subkey}'、または列'{column}' で '{value}' が無いぞ。{e}")
            return "ERROR"
        except IndexError as e:
            print(f"get_df_2key: {csvname}: 条件'{key} = {value}' かつ '{subkey} = {subvalue}' を満たすデータが見つからなかった - {e}")
            return "ERROR"
        except Exception as e:
            print(f"get_df_2key: {csvname}: 予期せぬエラー発生：{e}")
            return "ERROR"

        # 成功した場合、見つかったプロンプトを返す
        return prompt


    def chikan(self, text):
        """置換機能
        文字列中に%で囲まれた部分があればreplacelist.csvに基づいて置換する機能

        Args:
            text (str): プロンプト
        Returns:
            text (str): 置換後プロンプト
        """
        csvname, _ = self.find_csv_path('replacelist.csv')
        # 正規表現で置換対象("%"で挟まれた文字列)をリスト化
        置換対象 = re.findall('%.*?%', text)
        if len(置換対象) > 0:
            # 見つかった置換対象リストの数だけ繰り返し
            for chi in 置換対象:
                # %抜きの文字列でcsvを検索する
                csv参照用 = chi.strip("%")
                text = re.sub(chi, self.get_df(csvname, "置換前", csv参照用, "置換後"), text)
                # get_dfがエラーを出した場合、文字列"Error"に置換される
        return text

    def process_csv_event(self,csvname):
        """
        処理の遅さと引き換えに全部読み直させてバグの温床を潰す
        'Character.csv' と 'Add_Character.csv' の更新は異なる処理にする
        Args:
            csvname (str): 処理するCSVファイル名。
        """
        self.csvdata_import()
        self.combine_character_csvs() #Add_Characterを結合してCharacter.csvとして扱うので必ずself.csvdata_import()の後に呼べ
        self.add_cloth_columns()
        self.load_display_part()
        print (f"{csvname}" )



    def write_specific_df_to_csv(self, file_name, csv_name):
        """
        特定のDataFrameをCSVに書き出す。

        Args:
            file_name (str): 書き込みたいCSVファイルの名前。
            csv_name (str): self.csvdatasから取得するDataFrameのキー。

        Returns:
            None: ファイルに書き込みを完了したら、特に何も返さない。
        """
        df = self.csvdatas[csv_name]  # 特定のDataFrameを取得
        df.to_csv(file_name, index=False, encoding='utf-8-sig')


    #CSVM補助用メソッド類
    #あとで見直す 他のクラスにまとめるかも
    def convert_str_numbers_to_int(self, df):
        """数字だけのセルをintに変換

        Args:
            df (_type_): _description_
            column_name (_type_): _description_

        Returns:
            _type_: _description_
        """
        for column in df.columns:
            df[column] = df[column].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
        return df

    def convert_fullwidth_to_halfwidth(self, df):
        """全角数字を半角に変換

        Args:
            df (_type_): _description_
            column_name (_type_): _description_

        Returns:
            _type_: _description_
        """
        for column in df.columns:
            df[column] = df[column].apply(lambda x: x.translate(str.maketrans('０１２３４５６７８９', '0123456789')) if isinstance(x, str) else x)
        return df


    def add_transformed_columns(self, df, column_transformations):
        """
        DataFrameに複数の変換されたカラムを追加する。

        Args:
            df (pandas.DataFrame): 変換する対象のDataFrame
            column_transformations (dict): {新しいカラム名: (元のカラム名, 変換関数)} の辞書

        Returns:
            pandas.DataFrame: 変換後のカラムが追加されたDataFrame
        """
        for new_column, (original_column, transform_function) in column_transformations.items():
            df[new_column] = df[original_column].apply(transform_function)
        return df


    def add_columns_with_copy(self, df, columns_to_copy):
        """
        既存のカラムの値をコピーして新しいカラムに追加する。

        Args:
            df (pandas.DataFrame): 対象のDataFrame
            columns_to_copy (dict): {新しいカラム名: 既存のカラム名} の辞書

        Returns:
            pandas.DataFrame: 値がコピーされた新しいカラムが追加されたDataFrame
        """
        for new_column, original_column in columns_to_copy.items():
            df[new_column] = df[original_column]
        return df


    def retain_columns(self, old_df, new_df):
        """
        更新後のデータフレームに更新前のデータフレームにあるカラムがない場合
        更新前のデータフレームからカラムと値を移植する
        Args:
            original_df (df): 更新前のデータフレーム
            new_df (df): 更新後のデータフレーム

        Returns:
            _type_: _description_
        """
        for col in old_df.columns:
            if col not in new_df.columns:
                new_df[col] = old_df[col]
        return new_df
    