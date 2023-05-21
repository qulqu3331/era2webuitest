import asyncio
import httpx
import json
from tqdm import tqdm

# プロンプトメーカーが作成したデータ受け取ってプロンプトを作成し、幅と高さを指定
async def gen_Image_api(prompt, negative, gen_width, gen_height):
    # APIのエンドポイント
    url = "http://127.0.0.1:7860"

    # 生成設定ファイルのパス
    t2iconfig_path = "t2i_config.json"

    # JSONファイルから設定を読み込み
    with open(t2iconfig_path, "r") as file:
        config = json.load(file)

    # ペイロードを作成する
    payload = config.copy()  # configの内容をコピー
    payload["prompt"] = prompt  # promptを上書き
    payload["negative_prompt"] = negative  # negative_promptを上書き

    # 渡されたgen_width幅とgen_heightが0,0の場合、JSON指定のデフォルト値
    if gen_width != 0:
        payload["width"] = gen_width  # 幅を上書き
    if gen_height != 0:
        payload["height"] = gen_height  # 高さを上書き
    
    
    async def gen_image(client):
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        return response
    
    async def update_progress_bar(client):
        #待機ゲージ初期化
        progress_bar = tqdm(total=100)
        
        #進捗の取得
        while True:
            progress = await client.get(url=f'{url}/sdapi/v1/progress?skip_current_image=false')
            progressjson = progress.json()
            progress_bar.update(int((progressjson['progress'] * 100) - progress_bar.n))
            await asyncio.sleep(0.5)
    
    
    #生成と待機ゲージの表示を並列実行
    async with httpx.AsyncClient(timeout=30) as client:
        
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

            await asyncio.sleep(0.5) #ここでちょっと待たないとimageviewer.pyエラー落ちないが表示はされる
            return results.status_code
        
        else:
            # ステータスが200以外エラー表示
            print(f"エラー：APIがステータスコード{results.status_code}で応答しました")
            return False