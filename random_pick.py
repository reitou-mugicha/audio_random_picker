"""
ランダム音声抽出ツール
------------------------------------------
指定フォルダ内(サブフォルダ含む)の音声ファイルを検索し、
ランダムに1つ選んで表示します。
表示されたファイルはラベルから直接ドラッグして、
DAWやエクスプローラーなど他のソフトへドロップできます。

必要ライブラリ:
    pip install tkinterdnd2
"""

import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox

from tkinterdnd2 import TkinterDnD, DND_FILES, COPY

# 検索対象の音声拡張子
AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".ogg", ".m4a",
    ".aac", ".wma", ".aiff", ".aif",
}


class RandomAudioPicker:
    def __init__(self, root: TkinterDnD.Tk):
        self.root = root
        self.root.title("ランダム音声抽出ツール")
        self.root.geometry("480x300")
        self.root.resizable(False, False)

        self.folder_path = tk.StringVar(value="フォルダが選択されていません")
        self.audio_files: list[str] = []
        self.current_file: str | None = None

        tk.Button(root, text="① フォルダを選択", command=self.select_folder).pack(pady=(15, 5))
        tk.Label(root, textvariable=self.folder_path, wraplength=440, fg="gray").pack()

        count_frame = tk.Frame(root)
        count_frame.pack(pady=(10, 0))
        tk.Label(count_frame, text="検出した音声ファイル数：").pack(side="left")
        self.count_label = tk.Label(count_frame, text="0", fg="blue")
        self.count_label.pack(side="left")

        tk.Button(root, text="② ランダムに1つ抽出", command=self.pick_random).pack(pady=10)

        # ドラッグ元となるラベル
        self.drag_label = tk.Label(
            root,
            text="ここに抽出結果が表示されます\n(このラベルを他のソフトへドラッグ&ドロップできます)",
            relief="ridge",
            bd=2,
            width=55,
            height=4,
            bg="#f0f0f0",
            justify="center",
        )
        self.drag_label.pack(pady=10, padx=10, fill="x")

        # ラベルをドラッグ元(ファイルドロップソース)として登録
        self.drag_label.drag_source_register(1, DND_FILES)
        self.drag_label.dnd_bind("<<DragInitCmd>>", self.on_drag_init)

        # D&Dが使えない環境向けの保険：パスをクリップボードにコピー
        tk.Button(root, text="ファイルパスをコピー", command=self.copy_path).pack(pady=(0, 10))

    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.folder_path.set(folder)
        self.audio_files = self.scan_audio_files(folder)
        self.count_label.config(text=str(len(self.audio_files)))
        self.current_file = None
        self.drag_label.config(text="ここに抽出結果が表示されます\n(このラベルを他のソフトへドラッグ&ドロップできます)")
        if not self.audio_files:
            messagebox.showwarning("警告", "音声ファイルが見つかりませんでした。")

    @staticmethod
    def scan_audio_files(folder: str) -> list[str]:
        found = []
        for dirpath, _, filenames in os.walk(folder):
            for name in filenames:
                if os.path.splitext(name)[1].lower() in AUDIO_EXTENSIONS:
                    found.append(os.path.join(dirpath, name))
        return found

    def pick_random(self):
        if not self.audio_files:
            messagebox.showwarning("警告", "先にフォルダを選択してください。")
            return
        self.current_file = random.choice(self.audio_files)
        display_name = os.path.basename(self.current_file)
        self.drag_label.config(
            text=f"抽出結果：\n{display_name}\n\n(このラベルをドラッグして他のソフトへ)"
        )

    def on_drag_init(self, event):
        """ドラッグ開始時に呼ばれ、ドラッグするファイルを返す"""
        if not self.current_file:
            return None
        return ((COPY,), (DND_FILES,), (self.current_file,))

    def copy_path(self):
        if not self.current_file:
            messagebox.showwarning("警告", "先にランダム抽出してください。")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_file)
        messagebox.showinfo("コピー完了", "ファイルパスをクリップボードにコピーしました。")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    RandomAudioPicker(root)
    root.mainloop()