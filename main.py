import os
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from processor import extract_text

def on_drop(event):
    # 清洗路径：Windows 拖拽有时会带引号或大括号
    raw_path = event.data.strip('{}').strip('"')
    
    # 检查后缀名
    if raw_path.lower().endswith(('.ass', '.srt')):
        try:
            # 调用大脑进行处理
            output_file = extract_text(raw_path)
            file_name = os.path.basename(output_file)
            
            # 更新界面状态
            status_label.config(
                text=f"✅ 转换成功！\n文件已保存至同目录下：\n{file_name}",
                fg="#2ecc71" # 成功色：绿色
            )
        except Exception as e:
            status_label.config(text=f"❌ 发生错误:\n{str(e)}", fg="#e74c3c")
    else:
        status_label.config(text="⚠️ 格式不支持！\n请拖入 .ass 或 .srt 文件", fg="#f1c40f")

# --- GUI 界面设置 ---
root = TkinterDnD.Tk()
root.title("字幕提取工具") # 你的新项目名
root.geometry("400x250")
root.config(bg="#f5f5f5")

# 使窗口始终在最前面（方便拖拽文件）
root.attributes('-topmost', True)

# 主显示区域
status_label = tk.Label(
    root, 
    text="请将 .ass 或 .srt 文件\n拖拽到此处", 
    padx=20, 
    pady=40,
    bg="#ffffff",
    fg="#34495e",
    font=("Microsoft YaHei", 12, "bold"),
    relief="groove",
    borderwidth=2
)
status_label.pack(expand=True, fill="both", padx=20, pady=20)

# 绑定拖拽事件
status_label.drop_target_register(DND_FILES)
status_label.dnd_bind('<<Drop>>', on_drop)

# 底部说明
footer = tk.Label(root, text="支持格式: ASS / SRT", bg="#f5f5f5", fg="#95a5a6", font=("Arial", 9))
footer.pack(side="bottom", pady=5)

root.mainloop()