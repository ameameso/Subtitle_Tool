import PyInstaller.__main__
import os
import sys

# 1. 动态获取当前脚本所在目录，确保路径绝对正确
base_dir = os.path.dirname(os.path.abspath(__file__))
entry_point = os.path.join(base_dir, 'main.py')

# 2. 检查入口文件是否存在
if not os.path.exists(entry_point):
    print(f"❌ 错误：找不到入口文件 {entry_point}，请确保脚本在项目根目录运行。")
    sys.exit(1)

# 3. 执行打包
PyInstaller.__main__.run([
    entry_point,
    '--name=Subtitle_Tool_v1.3.1',  # 建议使用下划线，避免中文和括号在部分系统报错
    '--onefile',                      # 单文件模式
    '--noconsole',                    # 隐藏黑窗口
    '--collect-all=tkinterdnd2',      # 收集拖拽库依赖
    '--clean',                        # 清理缓存
    '--workpath=build',               # 临时文件目录
    '--distpath=dist',                # 成品目录
    # 如果你想给程序加个图标，可以解开下面这行的注释（需要准备一个 .ico 文件）
    # '--icon=logo.ico', 
])

print("\n✅ 打包完成！")
print(f"📁 请查看目录: {os.path.join(base_dir, 'dist')}")