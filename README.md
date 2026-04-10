# ASS 字幕提取工具 (ASS Extract Tool)

这是一个基于 Python 开发的轻量级桌面工具，专门用于从 `.ass` 格式的字幕文件中快速提取纯文本对话内容，并自动保存为 `.txt` 文件。

## 🌟 项目特点

- **简单直用**：支持文件拖拽功能，无需复杂的路径选择。
- **模块化设计**：核心提取逻辑与 GUI 界面分离，易于维护和扩展。
- **干净输出**：自动识别并剔除 ASS 标签（如 `{\pos(x,y)}` 等样式代码），只保留纯文本。
- **专业构建**：提供完整的虚拟环境配置方案与自动化打包脚本。

## 📂 项目结构

```text
ASS_EXTRACT_TOOL/
├── venv/                # 虚拟环境文件夹（不上传）
├── processor.py         # 核心逻辑层：负责解析 ASS 文件并提取文本
├── main.py              # 视图层：负责 GUI 界面展示与文件拖拽交互
├── build_exe.py         # 构建层：一键打包成 .exe 的自动化脚本
├── requirements.txt     # 依赖清单：记录项目运行所需的库
└── README.md            # 项目说明书
```

## 🚀 快速开始

### 1. 环境准备
确保你的电脑已安装 Python 3.x。建议在虚拟环境中运行：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行程序
直接运行入口文件：
```bash
python main.py
```

### 3. 打包为 EXE
如果你需要分发给没有 Python 环境的用户，运行打包脚本：
```bash
python build_exe.py
```
打包完成后，可在 `dist/` 文件夹下找到生成的 `.exe` 文件。

## 🛠️ 核心逻辑说明

### 九逗号法则
在 ASS 文件结构中，对话内容通常位于 `Dialogue:` 行的第 10 个字段。本项目通过 `line.split(',', 9)` 精确切片，确保提取到完整的字幕正文。

### 正则清洗
使用正则表达式 `\{.*?\}` 自动过滤字幕中的所有样式指令，还原最纯粹的阅读体验。