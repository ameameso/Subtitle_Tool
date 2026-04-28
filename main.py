import tkinter as tk
from tkinter import font as tkfont
from tkinterdnd2 import DND_FILES, TkinterDnD
from processor import process_file
import os

# --- 现代颜色方案 ---
COLORS = {
    "bg": "#F0F2F5",       # 浅灰背景
    "card": "#FFFFFF",     # 白色卡片
    "primary": "#4A90E2",  # 科技蓝
    "text": "#333333",     # 深灰文字
    "success": "#27AE60",  # 成功绿
    "error": "#E74C3C",    # 错误红
    "border": "#DCDFE6"    # 边框色
}

def on_drop(event):
    raw_path = event.data.strip('{}').strip('"')
    mode = mode_var.get()
    
    # UI 反馈：开始处理
    status_label.config(text="正在处理...", fg=COLORS["primary"])
    root.update()

    try:
        output_file = process_file(raw_path, mode)
        status_label.config(
            text=f"✅ 处理成功！\n\n{os.path.basename(output_file)}", 
            fg=COLORS["success"]
        )
    except Exception as e:
        status_label.config(text=f"❌ 错误:\n{str(e)}", fg=COLORS["error"])

# --- 界面初始化 ---
root = TkinterDnD.Tk()
root.title("Subtitle Tool v1.3.1")
root.geometry("500x450")
root.config(bg=COLORS["bg"])

# 设置默认字体
default_font = tkfont.Font(family="Microsoft YaHei", size=10)
title_font = tkfont.Font(family="Microsoft YaHei", size=12, weight="bold")

# --- 顶层装饰条 ---
top_bar = tk.Frame(root, bg=COLORS["primary"], height=4)
top_bar.pack(fill="x")

# --- 标题区 ---
header_label = tk.Label(
    root, text="字幕处理工具箱", 
    bg=COLORS["bg"], fg=COLORS["text"], font=title_font
)
header_label.pack(pady=(20, 10))

# --- 模式选择区 (卡片样式) ---
mode_frame = tk.LabelFrame(
    root, text=" 请选择工作模式 ", bg=COLORS["bg"], 
    fg="#606266", font=default_font, labelanchor="n", padx=20, pady=10
)
mode_frame.pack(padx=30, fill="x")

mode_var = tk.StringVar(value="extract")
modes = [
    ("提取纯文本 (ASS/SRT -> TXT)", "extract"),
    ("字幕格式互转 (ASS ↔ SRT)", "convert"),
    ("剪映 JSON 转 SRT", "capcut")
]

for text, value in modes:
    rb = tk.Radiobutton(
        mode_frame, text=text, variable=mode_var, value=value,
        bg=COLORS["bg"], activebackground=COLORS["bg"],
        font=default_font, fg=COLORS["text"], cursor="hand2"
    )
    rb.pack(anchor="w", pady=2)

# --- 拖拽投放区 (核心视觉) ---
drop_frame = tk.Frame(root, bg=COLORS["card"], highlightbackground=COLORS["border"], highlightthickness=1)
drop_frame.pack(expand=True, fill="both", padx=30, pady=25)

status_label = tk.Label(
    drop_frame, 
    text="将文件拖拽至此\n\n(支持 .ass / .srt / .json)", 
    bg=COLORS["card"], 
    fg="#909399", 
    font=("Microsoft YaHei", 11),
    justify="center"
)
status_label.pack(expand=True, fill="both")

# 绑定拖拽
status_label.drop_target_register(DND_FILES)
status_label.dnd_bind('<<Drop>>', on_drop)

# --- 底部版权信息 ---
footer = tk.Label(
    root, text="Subtitle Tool v1.3.1 | 始终置顶已开启", 
    bg=COLORS["bg"], fg="#C0C4CC", font=("Arial", 8)
)
footer.pack(side="bottom", pady=10)

root.attributes('-topmost', True) # 保持置顶
root.mainloop()