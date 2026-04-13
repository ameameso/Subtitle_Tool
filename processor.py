import re
import os

def extract_text(input_path):
    """统一入口：根据后缀名自动选择提取逻辑"""
    ext = os.path.splitext(input_path)[1].lower()
    # 生成同名的 .txt 文件路径
    output_path = os.path.splitext(input_path)[0] + ".txt"
    
    if ext == '.ass':
        return _handle_ass(input_path, output_path)
    elif ext == '.srt':
        return _handle_srt(input_path, output_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")

def _handle_ass(input_path, output_path):
    """处理 ASS 文件的私有函数"""
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        is_events = False
        for line in f_in:
            if line.strip() == '[Events]':
                is_events = True
                continue
            if is_events and line.startswith('Dialogue:'):
                parts = line.split(',', 9)
                if len(parts) > 9:
                    # 剔除 ASS 特有的样式标签如 {\pos...}
                    text = re.sub(r'\{.*?\}', '', parts[9].strip())
                    if text:
                        f_out.write(text + '\n')
    return output_path

def _handle_srt(input_path, output_path):
    """处理 SRT 文件的私有函数"""
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            line = line.strip()
            # 过滤掉数字行、时间轴行、空行
            if not line or line.isdigit() or '-->' in line:
                continue
            # 剔除 SRT 可能含有的 HTML 标签如 <i>
            clean_text = re.sub(r'<.*?>', '', line)
            f_out.write(clean_text + '\n')
    return output_path