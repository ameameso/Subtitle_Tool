import PyInstaller.__main__
import os

# 确保在打包前能找到你的入口文件
entry_point = 'main.py'

PyInstaller.__main__.run([
    entry_point,
    '--name=字幕提取工具',  # 给你的 exe 起个好听的名字
    '--onefile',                 # 封装成单个文件
    '--noconsole',               # 运行程序时不弹出黑色命令行窗口
    '--collect-all=tkinterdnd2', # 关键！强制收集拖拽库的所有依赖
    '--clean',                   # 清理之前的临时缓存
    '--workpath=build',          # 指定临时文件存放路径
    '--distpath=dist',           # 指定生成的 exe 存放路径
])

print("\n✅ 打包完成！请在 dist 文件夹中查看你的 .exe 文件。")