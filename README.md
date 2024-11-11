#最新バージョンについて

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

step 5
cfg scale 1
width 768
height 960
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

（Automatic1111の入力欄にブラウザ自動操作で文字記入する形でやっています。将来的にAPI利用も検討中）

### 動かしかた
1. PCにインストールされたchromeと同バージョンのchromedriverを入手し、本体と同じフォルダに入れる。
2. 同梱のERBフォルダをeraのフォルダに上書きする。
2. -remote-debugging-port=9222オプションをつけてchromeを起動し、WebUIを開いておく。（バッチファイル同梱）
3. era2webui.pyを実行する。（バッチファイル同梱）

### LCM使用による高速化
1. add promptを起動してlcm lora プロンプトを有効化
2. 生成パラメーターをlcm用に設定する
 - Sampling method : DPM++ 2S a Karras
 - CFG Scale : 2.5~3
 - Step 6～8
3. hiresfix使用時は hiresfix step 0

# [StreamDiffusion](https://github.com/cumulo-autumn/StreamDiffusion)対応による処理の超高速化

### 対応環境の変更

StreamDiffusionが対応しているPythonは3.10のため3.12のvenvは削除する

[StreamDiffusion](https://github.com/cumulo-autumn/StreamDiffusion)の説明に従いTorchなどをインストール

config.iniを変更

```config.ini
streamdiffusionで生成する = 1
```

プロンプトを再現する力はイマイチだが早い

東方系統に強いスケベなSDXLモデルとか作らないと駄目かなこれは


### カスタマイズについて
詳しくは別記



# era2webuiTW

`era2webui`は、`era` ゲームのデータをWebUIに変換し、画像を生成するための魔法のツールキットだ。このツールを使えば、キャラクターたちの世界が画面上で魔法のように輝き出す。

## 主要なマジックアイテム

### PromptMaker
このプロンプトの魔術師は、ゲームのシーンやキャラクターの心情を読み取り、それに合わせたプロンプトを生成する。まるでデータから未来を占う占星術師のような存在。

### CSVManager (CSVM)
CSVファイルの宝石箱を開ける鍵。キャラクターや場所、服装、行動に関するエレメントを魔法のように取り出し、プロンプト生成の材料にする。

### SaveJSONHandler (SJH)
セーブデータの守護者で、キャラクターの記憶を管理。このツールがあれば、キャラクターの情報を魔法の光で照らし出し、プロンプト生成の材料にする。


### AI魔理沙に説明書いてもらったけど要領得ない部分があるので補足
`CSVManager` クラス プロンプトが定義されたCSVファイルをクラス内部のDictに格納する｡ 起動時に1度だけその処理が行われるのでその都度.CSVを読み出していた従来の方式に比べて参照時間が短縮される
CSVに更新があった場合はFileHandlerが検知して､更新を反映させる

`SaveJSONHandler` クラス セーブデータをクラス内Dictに展開する｡そのときStr型で格納された数字はint型に変換｡全角英数字は半角に変換などの処理も行う｡ Queueを受け取るごとにインスタンスを作成してインスタントごとに`PromptMaler`クラスへ渡される｡生成完了後は破棄される｡

`PromptMaler` クラス 前記2つのクラスのDictから要素ごとにプロンプトをクラスDictに格納した後 プロンプト､ネガティブプロンプト､縦横の解像度を出力する


## CSV

プロンプトCSV 一人じゃ埋めきれない

- [era2webui eraTWプロンプトスプレッドシート](https://docs.google.com/spreadsheets/d/1hxA6WOnmCmW2DNDfd11P0WXDf8l-qfgSCcwViDkK26w/edit?usp=sharing)


## 謝辞

このプロジェクトを進める上で、多くの人々からの支援を受けた。特に以下の人々には深く感謝する。

- 魔理沙：プロジェクトの進行において、貴重な助言とサポートを提供してくれた。

他にも多くのコミュニティメンバー、貢献者たちに感謝を表したい。みんなの協力がなければ、このプロジェクトはここまで成長しなかったはずだ。
