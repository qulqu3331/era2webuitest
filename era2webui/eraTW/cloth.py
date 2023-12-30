import re
from module.csv_manager import CSVMFactory
csvm = CSVMFactory.get_instance()

# cloth.csvのDataFrameを取得
cloth_df = csvm.csvdatas['Cloth.csv']

def get_cloth_name(position_no, equip_no_position):
    """
    (装備部位,EQUIP:NO:装備部位)の装備名取得
    Args:
        position_no (int): 装備部位
        equip_no_position (int): EQUIP:NO:装備部位
                                これはeraから直に吐き出させる
    Returns:
        str: カテゴリ
    """
    # 装備部位に基づいてカテゴリを取得
    category = clothes_parts_to_category(position_no)
    # カテゴリと装備部位番号に基づいて衣装の名前を取得
    cloth_name_row = cloth_df[(cloth_df['カテゴリ'] == category) & (cloth_df['カテゴリ内番号'] == equip_no_position)]
    if not cloth_name_row.empty:
        return cloth_name_row['衣類名'].iloc[0]
    else:
        return '衣類が見つかりません'


def clothes_parts_to_category(get_equip_position_no):
    # データフレームを使用してカテゴリを検索
    category_row = cloth_df[cloth_df['装備部位'] == get_equip_position_no]
    if not category_row.empty:
        return category_row.iloc[0]['カテゴリ']
    else:
        return '不明なカテゴリー'


def get_display_part(part_no):
    """
    該当番号の表示部位の文字列を返す
    (表示部位:LOCAL)
    Args:
        part_no (int): 1~22までの任意の値

    Returns:
        str: 表示部位
    """
    display_part_row = cloth_df[cloth_df['表示部位NO'] == part_no]
    if not display_part_row.empty:
        return display_part_row.iloc[0]['表示部位']
    else:
        print(f"部位NO {part_no} に対応する表示部位が見つかりません。")
        return '不明な表示部位'


def get_equip_position(display_part):
    """
    表示部位から対応する装備部位の番号を返す
    Args:
        display_part (str): 表示部位
    Returns:
        int: 装備部位 番号
    """
    equip_position_row = cloth_df[cloth_df['表示部位'] == display_part]
    if not equip_position_row.empty:
        return equip_position_row.iloc[0]['装備部位']
    else:
        return '不明な装備部位'



class ClothFlags():
    def __init__(self, sjh):
        self.sjh = sjh

    def nobura(self):
        return (
            self.sjh.get_save('キャラ固有番号') != 0 \
            and not self.sjh.get_save("性別") ==2 \
            and self.sjh.get_save("上半身下着2") == 0 \
            and self.sjh.get_save("上半身下着1") == 0 \
            and self.sjh.get_save("ボディースーツ") == 0 \
            and self.sjh.get_save("レオタード") == 0
        )


    def nopan(self):
        return (
            self.sjh.get_save('キャラ固有番号') != 0 \
            and self.sjh.get_save("下半身下着2") == 0 \
            and self.sjh.get_save("下半身下着1") == 0 \
            and self.sjh.get_save("ボディースーツ") == 0 \
            and self.sjh.get_save("レオタード") == 0
        )

    def upperbody_layers(self):
        items = ["上半身上着1", "上半身上着2", "ボディースーツ", "ワンピース", "着物", "レオタード"]
        return sum(self.sjh.get_save(item) != 0 for item in items)

    def lowerbody_layers(self):
        items = ["下半身上着1", "下半身上着2", "スカート", "ボディースーツ", "ワンピース", "着物", "レオタード"]
        return sum(self.sjh.get_save(item) != 0 for item in items)

    def bra_exposed(self):
        if self.upperbody_layers() == 0\
            or (self.upperbody_layers() == 1\
            and self.sjh.get_save("上半身着衣状況") == 0):
            return 1
        elif self.sjh.get_save("上半身はだけ状態") == 1:
            return 1
        return 0

    def psnts_exposed(self):
        if self.lowerbody_layers() == 0\
            or (self.lowerbody_layers() == 1\
            and self.sjh.get_save("下半身着衣状況") == 0):
            return 1
        elif self.sjh.get_save("下半身ずらし状態")  == 1:
            return 1
        return 0

    def nipps_exposed(self):
        # 着てない or ブラのみの状態から脱ぐ、または元々ノーブラの状態でブラが見える条件を満たす
        if self.sjh.get_save("上半身着衣状況") == 0\
            or (self.upperbody_layers() == 0\
            and self.sjh.get_save("上半身着衣状況") == 0)\
            or (self.sjh.get_save("上半身下着2") == 0\
            and self.bra_exposed() == 1):
            return 1
        return 0

    def pussy_exposed(self):
    # なにも履いてない or パンツだけ履いてるのを脱ぐ、または元々ノーパンの状態でパンツが見える条件を満たす
        if self.sjh.get_save("下半身着衣状況") == 0\
            or (self.lowerbody_layers() == 0 and self.sjh.get_save("上半身着衣状況") == 0)\
            or (self.sjh.get_save("下半身下着2") == 0 and self.psnts_exposed() == 1):
            return 1
        return 0


def show_cloth(save):
    clothing_info = {}
    # 特定の装備部位の衣装名を取得
    for i in range(1, 23):
        display_part = get_display_part(i)
        position_no = get_equip_position(display_part)
        if position_no < 0:
            print(f"存在しない装備部位{position_no}")


        if not save.get_save("EQUIP:NO:装備部位").get(i):
            continue

        #パジャマの処理はあとで考える

        if display_part == "下半身下着2":
            #下着の名前は辞書で与えられるのでその最初の辞書のvalueを使う
            _, pantus = next(iter(save.get_save("lower_underwear").items()))
            print(f"{pantus}")

        if display_part == "上半身下着1":
            _, bura = next(iter(save.get_save("upper_underwear").items()))
            print(f"{bura}")

        # 特定の条件に基づく表示内容の決定
        equip_no_dict = save.get_save("EQUIP:NO:装備部位")
        for j, ene in equip_no_dict.items():
            if ene is None:
                continue
            hyoujinaiyou = get_cloth_name(position_no, ene)
            print(f"{display_part}[{hyoujinaiyou}]")
            break  # 名前を見つけたらループを抜ける
        #キーの重複によるデータの上書きを回避するためのキーを作る
        unique_key = f"{display_part}-{j}"
        clothing_info[unique_key] = hyoujinaiyou
    return clothing_info


def clean_cloth_data(cloth_data):
    # 新しい辞書を初期化
    cleaned_data = {}

    # 元の辞書のキーと値をループ処理
    for key, value in cloth_data.items():
        # キーから末尾の '-数字' を削除（例: '帽子-1' -> '帽子'）
        new_key = re.sub(r'-\d+$', '', key)
        cleaned_data[new_key] = value

    return cleaned_data

def get_cloth_dict(save):
    clothing_info = show_cloth(save)
    cleaned_data = clean_cloth_data(clothing_info)
    return cleaned_data