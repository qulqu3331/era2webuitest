import os
import tkinter as tk

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

# プログラムを閉じるときにテキストファイルを空にする
def click_close():
    file_path = os.path.join(os.path.dirname(__file__), 'add_prompt.txt')
    with open(file_path, "w", encoding='utf-8') as f:
        f.write('')
    root.destroy()

# メインウィンドウの作成
root = tk.Tk()

# ボタンを配置するフレームを作成
frame = tk.Frame(root)
frame.pack(side='top', padx=10, pady=10)

# ボタンを作成して配置する
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'add_prompt用ワードリスト.txt')
with open(file_path, 'r', encoding = "utf-8") as f:
    words = [line.strip() for line in f]
n = len(words)
max_columns = 5
buttons = []
i = 0
# 行数と列数を計算する
row = 0
col = 0
subframe = tk.Frame(frame)
subframe.grid(row=row + 1, column=0, columnspan=max_columns)
row = 2

for i in range(n):
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