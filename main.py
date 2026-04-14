import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from processor import process_file

def on_drop(event):
    raw_path = event.data.strip('{}').strip('"')
    mode = mode_var.get()
    
    try:
        output_file = process_file(raw_path, mode)
        status_label.config(text=f"✅ 处理成功！\n{os.path.basename(output_file)}", fg="#2ecc71")
    except Exception as e:
        status_label.config(text=f"❌ 错误: {str(e)}", fg="#e74c3c")

root = TkinterDnD.Tk()
root.title("Subtitle Tool Pro v1.3")
root.geometry("450x380")
root.config(bg="#f8f9fa")

# --- 模式选择区 (Header) ---
header = tk.Label(root, text="选择工作模式", bg="#f8f9fa", font=("微软雅黑", 10, "bold"))
header.pack(pady=(15, 5))

mode_frame = tk.Frame(root, bg="#f8f9fa")
mode_frame.pack(pady=10)

mode_var = tk.StringVar(value="extract")

# 使用更清晰的标签名
modes = [
    ("提取纯文本", "extract"),
    ("ASS ↔ SRT", "convert"),
    ("剪映 JSON 转字幕", "capcut")
]

for text, value in modes:
    tk.Radiobutton(
        mode_frame, text=text, variable=mode_var, value=value, 
        bg="#f8f9fa", activebackground="#f8f9fa", font=("微软雅黑", 9)
    ).pack(side="left", padx=10)

# --- 拖拽投放区 ---
status_label = tk.Label(
    root, text="请将文件拖拽至此\n(支持 .ass / .srt / .json)", 
    bg="#ffffff", relief="flat", borderwidth=0, 
    font=("微软雅黑", 11), height=10
)
status_label.pack(expand=True, fill="both", padx=30, pady=20)

# 给投放区加个简单的边框样式（视觉增强）
status_label.config(highlightbackground="#dee2e6", highlightthickness=2)

status_label.drop_target_register(DND_FILES)
status_label.dnd_bind('<<Drop>>', on_drop)

root.mainloop()