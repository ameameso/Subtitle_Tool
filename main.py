import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from processor import extract_text_from_ass  # 导入我们写的那个工具

def on_drop(event):
    file_path = event.data.strip('{}').strip('"')
    if file_path.lower().endswith('.ass'):
        # 调用核心逻辑
        out = extract_text_from_ass(file_path)
        label.config(text=f"成功！保存至：\n{out}")
    else:
        label.config(text="请拖入 .ass 文件")

root = TkinterDnD.Tk()
root.title("字幕提取器")
root.geometry("300x200")

label = tk.Label(root, text="把文件拖到这里", bg="white", width=30, height=10)
label.pack(pady=20)

# 绑定拖拽
label.drop_target_register(DND_FILES)
label.dnd_bind('<<Drop>>', on_drop)

root.mainloop()