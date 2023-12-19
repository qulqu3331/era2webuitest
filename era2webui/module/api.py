"""
SDWebUIを駆使して画像をぶっ飛ばすように生成するぜ！
指定されたプロンプトや設定を使って、まるで魔法のように画像を描くんだ。

この関数は、TaskExecutorからプロンプトやネガティブプロンプト、画像のサイズを受け取って、
SDWebUIのAPIにリクエストをバシッと飛ばす。その結果、魔法のように画像が帰ってくるんだ。

Args:
    prompt (str): 画像生成のための呪文だ。これがあると、画像がどんな風になるか決まる。
    negative (str): 画像に絶対に現れてほしくないものを指定する、いわばアンチ呪文だな。
    gen_width (int): 画像の幅をピクセルで指定するぜ。0だと、config.jsonのデフォルト値を使うから安心してくれ。
    gen_height (int): 画像の高さもピクセルで指定する。こっちも0だとデフォルト値でOKだ。

Returns:
    int or bool: うまくいけばHTTPステータスコード200を叩き出す。失敗したら、残念ながらFalseが帰ってくるぜ。
    生成した画像自体はSDWebUIで設定されたt2iフォルダに保存されるぜ･
"""
import asyncio
import json
import os
import httpx
from tqdm import tqdm

# プロンプトメーカーが作成したデータ受け取ってプロンプトを作成し、幅と高さを指定


async def gen_image_api(prompt, negative, gen_width, gen_height):
    # APIのエンドポイント
    url = "http://127.0.0.1:7860"

    # 生成設定ファイルconfig.jsonのパス
    base_dir = os.path.dirname(__file__)
    # カレントディレクトリの親ディレクトリのパスを取得
    t2iconfig_path = os.path.dirname(base_dir) + "/config.json"
    # config.jsonファイルから生成設定を読み込み
    with open(t2iconfig_path, "r", encoding='utf-8') as file:
        config = json.load(file)

    # sdwebuiに生成させるためのデータ､ペイロードを作成する
    payload = config.copy()  # config.jsonの内容をコピー
    payload["prompt"] = prompt  # promptを上書き
    payload["negative_prompt"] = negative  # negative_promptを上書き

    # gen_widthとgen_heightが0,0の場合、config.json指定のデフォルト値に設定
    if gen_width != 0:
        payload["width"] = gen_width  # 幅を上書き
    if gen_height != 0:
        payload["height"] = gen_height  # 高さを上書き

    async def gen_image(client):
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        return response

    async def update_progress_bar(client):
        # 待機ゲージ初期化
        progress_bar = tqdm(total=100)

        # 進捗の取得
        while True:
            progress = await client.get(url=f'{url}/sdapi/v1/progress?skip_current_image=false')
            progressjson = progress.json()
            progress_bar.update(
                int((progressjson['progress'] * 100) - progress_bar.n))
            await asyncio.sleep(0.3)

    # 生成と待機ゲージの表示を並列実行
    async with httpx.AsyncClient(timeout=100) as client:

        gen_task = asyncio.create_task(gen_image(client))
        _ = asyncio.create_task(update_progress_bar(client))

        # gen_imageが終わるまで待つ
        results = await gen_task

        # APIからステータスコードが200が返ってきた場合、正常に処理が行われたとみなす:
        if results.status_code == 200:

            # 生成パラメーターの表示
            print("APIに渡されたパラメーター：")
            print(f"プロンプト：{payload['prompt']}")
            print(f"ネガティブプロンプト：{payload['negative_prompt']}")
            print(f"幅：{payload['width']}")
            print(f"高さ：{payload['height']}")

            # ここでちょっと待たないとimageviewer.pyがエラーを吐く落ちないが表示はされる
            await asyncio.sleep(0.1)
            return results.status_code

        else:
            # ステータスが200以外エラー表示
            print(f"エラー：APIがステータスコード{results.status_code}で応答しました")
            return False