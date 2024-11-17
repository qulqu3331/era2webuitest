# 最新バージョンについて

もともとプログラムの基幹部分を1から作り直すつもりだったんだけど面倒で手を付けていなかったところ
ちょうつよいローカルモデルが出てきてテンションが上がった
自分でもよくわからなくなってるコードに行き当たりばったりで機能追加しているバージョンだよ
プロンプト管理はDynamic promptの置換機能にズブズブに依存しているよ
cfg1はネガティブプロンプトが効かないのでnegpipの拡張が要ります

推奨モデル
イラストリアス以降のSDXLモデルで Hyper-SDXL-1step-lora と相性がよくて絵柄が好みのもの
スペックに合わせて1枚3秒未満くらいに調整してね

テスト環境、設定
旧forge　安定ver(29be1da)を使用

モデル:いろいろ
グラボ:RTX3060

- step 5
- cfg scale 1
- width 768 × height 960

で3.2秒くらい

loraを付け替えたり、強度を変更しただけでMoving modelとか言って2～4秒のラグが起こるので
Hyperのloraを付けっぱなし、ついでにelace_cumのlecoもつけっぱなし


# era2webuitest

注意：このプログラムはド素人が試作した人柱版です。まともに動作することを期待しないで下さい。
何があっても自己責任での試用をお願いします。
動作にはStable Diffusionによる画像生成環境が必要です。

### なにこれ
eraで遊ぶとプレイ内容をリアルタイムで画像生成する仕組み

### 動作の概要
・emueraのSAVETEXT関数によりプレイ状況をtxtファイルに書き出す

・プログラムがtxtを検知してプロンプト文字列を作り、Stable Diffusionに渡す

（Automatic1111の入力欄にブラウザ自動操作で文字記入する形でやっています。）
（APIでも動作するようになりましたが、こっちはいろいろ未実装です。）

### 動かしかた
1. PCにインストールされたchromeと同バージョンのchromedriverを入手し、本体と同じフォルダに入れる。
2. 同梱のERBフォルダをeraのフォルダに上書きする。
3. -remote-debugging-port=9222オプションをつけてchromeを起動し、WebUIを開いておく。（バッチファイル同梱）
4. era2webui.pyを実行する。（バッチファイル同梱）


### 動作概要図
![Flowchart Template (3)](https://github.com/user-attachments/assets/80df072f-3c10-41aa-b9dd-c29cfc7dd62f)
