import os
import tkinter as tk
from tkinter import ttk
import re

# ボタンが押されたときのイベントハンドラ
# 押すたびにテキストファイルを書き換える
def on_button_click(button):
    if button['relief'] == 'raised':
        button.configure(relief='sunken')
    else:
        button.configure(relief='raised')

    selected = [button['text'] for button in buttons if button['relief'] == 'sunken']
    print(','.join(selected))

    file_path = os.path.join(os.path.dirname(__file__), 'add_prompt.txt')
    with open(file_path, "w", encoding='utf-8') as f:
        f.write(','.join(selected))

#スライダーを動かしたときの処理
def on_slider_change(value, button):
    button['text'] = button_data[button]['before'] + str(value) + button_data[button]['after']
    button.configure(relief='raised')

# プログラムを閉じるときにテキストファイルを空にする
def click_close():
    file_path = os.path.join(os.path.dirname(__file__), 'add_prompt.txt')
    with open(file_path, "w", encoding='utf-8') as f:
        f.write('')
    root.destroy()

# メインウィンドウの作成
root = tk.Tk()

button_data = {}  # スライダー文字列を保持する辞書

# ボタンを配置するフレームを作成
frame = tk.Frame(root)
frame.pack(side='top', padx=10, pady=10)

# ボタンを作成して配置する
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'add_prompt用ワードリスト.txt')
with open(file_path, 'r', encoding = "utf-8") as f:
    words = [line.strip() for line in f]
n = len(words)
max_columns = 4
buttons = []
i = 0
# 行数と列数を計算する
row = 0
col = 0
subframe = tk.Frame(frame)
subframe.grid(row=row + 1, column=0, columnspan=max_columns)
row = 2

for i in range(n):
    # 特殊処理1
    if words[i].startswith(';'):
        # セミコロンで始まる行の場合は見出しとして表示する
        label = tk.Label(frame, text=words[i][1:], font=('Helvetica', 8))
        label.grid(row=row, column=0, columnspan=max_columns, sticky='w')

        # 新しいフレームを作成して、ボタンを配置する
        subframe = tk.Frame(frame)
        subframe.grid(row=row + 1, column=0, columnspan=max_columns)

        # 見出しを表示したら、次の行から新しいフレームにボタンを配置する
        row += 2
        col = 0
    # 特殊処理2
    elif words[i].startswith('[SL]'):
        # [SL]で開始した行はスライダー
        # 記述例
        # [SL]<loraXXX:[2]>,TRIGGERWORD
        # [SL](prompt:[2])
        # 「[]で囲まれた文字列」を区切り文字にしてsplitをかける
        splited_texts = re.split("\[.*?\]",words[i])
        # "", "<loraXXX:",  ">,TRIGGERWORD" の3要素に別れる。要素数が3でなかったら書式間違い
        if len(splited_texts) == 3:
            #フレームを切る
            subframe = tk.Frame(frame)
            subframe.grid(row=row, column=0, columnspan=max_columns)
            #元の文字列の、2つめの[]内の文字列を取得しておく
            maxweight = float(re.findall("(?<=\[).+?(?=\])", words[i])[1])
            print (maxweight)
            #ボタン
            button = tk.Button(subframe, text='0', relief='raised', font=('Helvetica', 9))
            button.pack(side='left')
            button.configure(command=lambda b=button: on_button_click(b))
            buttons.append(button)
            # ボタンに表示する文字列を記憶
            button_data[button] = {'before':splited_texts[1],'after':splited_texts[2]}

            #スライダー
            slider = tk.Scale(subframe, orient=tk.HORIZONTAL, width= 11, from_=maxweight*-1, to=maxweight, resolution=0.1, command=lambda value, button=button: on_slider_change(value, button ))
            slider.set(1)
            slider.pack(side='left')
        
        # 新しいフレームを作成して、ボタンを配置する
        subframe = tk.Frame(frame)
        subframe.grid(row=row + 1, column=0, columnspan=max_columns)

        # 次の行から新しいフレームにボタンを配置する
        row += 1
        col = 0

    # 通常の処理
    else:
        # 通常の単語の場合はボタンを作成する
        button = tk.Button(subframe, text=words[i], relief='raised', font=('Helvetica', 9))
        button.grid(row=row, column=col, padx=1, pady=0)
        button.configure(command=lambda b=button: on_button_click(b))
        buttons.append(button)

        col += 1
        if col == max_columns:
            row += 1
            col = 0

root.protocol("WM_DELETE_WINDOW", click_close)
# メインループを開始
root.mainloop()