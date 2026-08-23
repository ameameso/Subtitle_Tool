import os
import platform
import subprocess
import ctypes
import customtkinter as ctk  # pip install customtkinter
from tkinterdnd2 import DND_FILES, TkinterDnD
from processor import process_file

APP_VERSION = "1.5.1"

# ==================== 1. Windows DPI 高清修复 ====================
try:
    if platform.system() == "Windows":
        ctypes.windll.shcore.SetProcessDpiAwareness(2) 
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ==================== 2. 全局主题与智能配色 ====================
ctk.set_appearance_mode("System")  # 自动跟随系统（Dark / Light 模式）
ctk.set_default_color_theme("blue") # 现代科技蓝主题

# 自定义一些特殊状态颜色（适配轻量/暗黑双色）
STATUS_COLORS = {
    "success": ("#34C759", "#30D158"), # 浅色绿 / 暗色绿
    "error": ("#FF3B30", "#FF453A"),   # 浅色红 / 暗色红
    "mute": ("#86868B", "#AEAED2")     # 浅色灰 / 暗色灰
}

# ==================== 核心修正：双重继承混合类 ====================
class SubtitleToolApp(ctk.CTk, TkinterDnD.DnDWrapper):
    """通过混合继承，完美融合 CustomTkinter 视效与 tkinterdnd2 拖拽功能"""
    def __init__(self):
        # 1. 优先初始化 CustomTkinter 窗体底座
        ctk.CTk.__init__(self)
        
        # 2. 核心修正：通过内部私有方法 _require 将 Tcl 拖拽内核精准注入当前 ctk 窗体
        try:
            self.TkdndVersion = TkinterDnD._require(self)
        except Exception as e:
            print(f"❌ 拖拽内核注入失败，请检查 tkinterdnd2 是否安装正确。错误: {e}")
        
        # 窗体基础配置
        self.title(f"Subtitle Tool v{APP_VERSION}")
        self.geometry("700x420")
        self.minsize(620, 380)
        self.attributes('-topmost', True) # 窗口常驻置顶
        
        # 核心模式变量 (必须采用 ctk 的 StringVar)
        self.mode_var = ctk.StringVar(value="extract")
        self.menu_buttons = {}
        
        # 主网格弹性布局 (左侧固定，右侧随窗口自适应拉伸)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 构建界面组件
        self.create_sidebar()
        self.create_workspace()
        
        # 绑定模式切换监听
        self.mode_var.trace_add("write", self.on_mode_change)
        self.on_mode_change() # 触发首次渲染视图

    # ==================== 3. 左侧现代化侧边栏 ====================
    def create_sidebar(self):
        # 侧边栏主体 Frame
        self.sidebar = ctk.CTkFrame(self, corner_radius=0, width=240)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # 侧边栏极简大标题
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar, text="SUBTITLE TOOL", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        self.sidebar_title.pack(fill="x", padx=25, pady=(30, 20), anchor="w")
        
        # 菜单模式项配置
        modes_config = [
            ("文本提取 (-> TXT)", "extract"),
            ("格式互转 (ASS ↔ SRT)", "convert"),
            ("剪映 JSON 转 SRT", "capcut")
        ]
        
        # 动态创建现代化侧边栏按钮组件
        for text, code in modes_config:
            btn = ctk.CTkButton(
                self.sidebar, 
                text=text, 
                font=ctk.CTkFont(family="Microsoft YaHei", size=12),
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color="transparent",  # 未选中时背景完全透明
                text_color=("#1D1D1F", "#E5E5EA"), # 浅色模式偏黑，暗黑模式偏白
                hover_color=("#E5E5EA", "#2C2C2E"), # 丝滑 Hover 反馈
                command=lambda c=code: self.mode_var.set(c)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.menu_buttons[code] = btn

        # 底部融入式功能按钮
        self.open_btn = ctk.CTkButton(
            self.sidebar,
            text="📂 定位剪映草稿目录",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            fg_color=("#E5E5EA", "#2C2C2E"),
            text_color=("#1D1D1F", "#E5E5EA"),
            hover_color=("#D1D1D6", "#3A3A3C"),
            command=self.open_capcut_draft_dir
        )
        self.open_btn.pack(side="bottom", fill="x", padx=15, pady=20)

    # ==================== 4. 右侧自适应投放区 ====================
    def create_workspace(self):
        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.workspace.grid_rowconfigure(0, weight=1)
        self.workspace.grid_columnconfigure(0, weight=1)
        
        # 悬空圆角卡片投放容器
        self.drop_card = ctk.CTkFrame(self.workspace, corner_radius=12)
        self.drop_card.grid(row=0, column=0, sticky="nsew")
        
        # 状态及说明的核心提示 Label
        self.status_label = ctk.CTkLabel(
            self.drop_card,
            text="",
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            justify="center"
        )
        self.status_label.pack(expand=True, fill="both", padx=20)
        
        # 智能尺寸监听：随着窗口拉伸，动态计算文字的最佳换行宽度
        self.drop_card.bind(
            "<Configure>", 
            lambda e: self.status_label.configure(wraplength=max(200, e.width - 40))
        )
        
        # 核心：由于类已经继承了 DnDWrapper，这里可以直接调用拖拽注册接口
        self.status_label.drop_target_register(DND_FILES)
        self.status_label.dnd_bind('<<Drop>>', self.on_drop)
        
        # 右下角极简版本号
        self.footer_lbl = ctk.CTkLabel(
            self.workspace, text=f"v{APP_VERSION} CustomTkinter UI",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=STATUS_COLORS["mute"]
        )
        self.footer_lbl.grid(row=1, column=0, sticky="e", pady=(8, 0))

    # ==================== 5. 核心控制与事件交互 ====================
    def on_mode_change(self, *args):
        """模式改变时，动态刷新按钮激活态及右侧卡片提示文案"""
        mode = self.mode_var.get()
        
        # 获取当前 ctk 主题的官方经典蓝色作为激活色
        theme_primary_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        
        for m, btn in self.menu_buttons.items():
            if m == mode:
                btn.configure(fg_color=theme_primary_color, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=("#1D1D1F", "#E5E5EA"))

        # 右侧状态文案字典
        hints = {
            "extract": "💧 纯文本提取模式\n\n请将 .ass 或 .srt 文件拖入此区域\n自动剔除时间轴，输出纯内容文本",
            "convert": "⚡ 字幕格式互转模式\n\n请将 .ass 或 .srt 文件拖入此区域\n智能双向互转，完美保留时间轴",
            "capcut": "🎬 剪映脚本转换模式\n\n请将 draft_content.json 拖入此区域\n(可点击左下角一键定位草稿目录)"
        }
        self.status_label.configure(text=hints[mode], text_color=STATUS_COLORS["mute"])

    def open_capcut_draft_dir(self):
        """一键定位剪映草稿功能"""
        try:
            local_appdata = os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser("~"), "AppData", "Local")
            capcut_path = os.path.join(local_appdata, "CapCut", "User Data", "Projects", "com.lveditor.draft")
            
            if os.path.exists(capcut_path):
                if platform.system() == "Windows":
                    os.startfile(capcut_path)
                else:
                    subprocess.run(["open", capcut_path])
                    
                self.mode_var.set("capcut")
                theme_primary_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
                self.status_label.configure(
                    text="📂 已打开草稿目录！\n\n请进入对应的工程文件夹\n将 draft_content.json 拖到右侧",
                    text_color=theme_primary_color
                )
            else:
                self.status_label.configure(text="❌ 未找到剪映草稿路径\n请确认是否安装了桌面版剪映", text_color=STATUS_COLORS["error"])
        except Exception as e:
            self.status_label.configure(text=f"❌ 打开失败: {str(e)}", text_color=STATUS_COLORS["error"])

    def on_drop(self, event):
        """文件解析拖拽响应事件"""
        raw_path = event.data.strip('{}').strip('"')
        mode = self.mode_var.get()
        
        theme_primary_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.status_label.configure(text="⚙️ 正在解析处理中...", text_color=theme_primary_color)
        self.update()

        try:
            output_file = process_file(raw_path, mode)
            self.status_label.configure(
                text=f"✨ 转换完成！文件已保存在同目录下\n\n📄 {os.path.basename(output_file)}",
                text_color=STATUS_COLORS["success"]
            )
        except Exception as e:
            self.status_label.configure(text=f"💥 转换失败\n\n{str(e)}", text_color=STATUS_COLORS["error"])

if __name__ == "__main__":
    app = SubtitleToolApp()
    app.mainloop()
