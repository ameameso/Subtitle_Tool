import json
import re
import os

def process_file(input_path, mode):
    ext = os.path.splitext(input_path)[1].lower()
    
    # 模式 1：提取纯文本 (不保留时间轴)
    if mode == 'extract':
        output_path = os.path.splitext(input_path)[0] + ".txt"
        if ext == '.ass': return _handle_ass_extract(input_path, output_path)
        if ext == '.srt': return _handle_srt_extract(input_path, output_path)
        raise ValueError("该模式仅支持 .ass 和 .srt")

    # 模式 2：字幕互转 (保留时间轴)
    elif mode == 'convert':
        if ext == '.ass':
            return _ass_to_srt(input_path, os.path.splitext(input_path)[0] + ".srt")
        if ext == '.srt':
            return _srt_to_ass(input_path, os.path.splitext(input_path)[0] + ".ass")
        raise ValueError("该模式仅支持 .ass 与 .srt 互转")

    # 模式 3：剪映 JSON 专用转换
    elif mode == 'capcut':
        if ext == '.json':
            return _handle_json_to_srt(input_path, os.path.splitext(input_path)[0] + ".srt")
        raise ValueError("请拖入剪映导出的 .json 文件")
            
    raise ValueError("未知的处理模式")

def _handle_ass_extract(input_path, output_path):
    """处理 ASS 文件的私有函数"""
    with open(input_path, 'r', encoding='utf-8-sig') as f_in, \
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

def _handle_srt_extract(input_path, output_path):
    """处理 SRT 文件的私有函数"""
    with open(input_path, 'r', encoding='utf-8-sig') as f_in, \
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

# --- JSON 处理逻辑 ---
def _format_time(ms):
    """微秒转 SRT 时间格式 HH:MM:SS,mmm"""
    total_seconds = ms / 1000000
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def _handle_json_to_srt(json_file, output_srt):
    """专门处理剪映导出的 JSON 存根文件"""
    with open(json_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    fragments = data.get('extra_info', {}).get('subtitle_fragment_info_list', [])
    srt_content = []
    index = 1

    for frag in fragments:
        cache_info_str = frag.get('subtitle_cache_info', '')
        if not cache_info_str: continue
        try:
            cache_info = json.loads(cache_info_str)
            sentence_list = cache_info.get('sentence_list', [])
            for sentence in sentence_list:
                start = frag['start_time']
                end = frag['end_time']
                text = sentence.get('text', '')
                if text:
                    srt_content.append(f"{index}")
                    srt_content.append(f"{_format_time(start)} --> {_format_time(end)}")
                    srt_content.append(f"{text}\n")
                    index += 1
        except json.JSONDecodeError:
            continue

    with open(output_srt, 'w', encoding='utf-8') as f:
        f.write("\n".join(srt_content))
    return output_srt


def _ass_to_srt(input_path, output_path):
    """ASS 转 SRT (保留时间轴)"""
    with open(input_path, 'r', encoding='utf-8-sig') as f_in, open(output_path, 'w', encoding='utf-8') as f_out:
        is_events = False
        index = 1
        for line in f_in:
            if '[Events]' in line: is_events = True; continue
            if is_events and line.startswith('Dialogue:'):
                parts = line.split(',', 9)
                start, end, text = parts[1], parts[2], parts[9].strip()
                # 转换时间格式 H:MM:SS.cc -> HH:MM:SS,mmm
                start_srt = start.replace('.', ',') + '0' if len(start.split('.')[1]) == 2 else start.replace('.', ',')
                end_srt = end.replace('.', ',') + '0' if len(end.split('.')[1]) == 2 else end.replace('.', ',')
                text = re.sub(r'\{.*?\}', '', text) # 清洗样式
                f_out.write(f"{index}\n0{start_srt} --> 0{end_srt}\n{text}\n\n")
                index += 1
    return output_path

def _srt_to_ass(input_path, output_path):
    """SRT 转 ASS (保留时间轴)"""
    # 这里提供一个基础模板，ASS 需要 Header 才能运行
    header = "[Script Info]\nScriptType: v4.00+\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    with open(input_path, 'r', encoding='utf-8-sig') as f_in, open(output_path, 'w', encoding='utf-8') as f_out:
        f_out.write(header)
        content = f_in.read()
        blocks = re.findall(r'\d+\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n([\s\S]*?)(?=\n\d+\n|\Z)', content)
        for b in blocks:
            start = b[0][1:10].replace(',', '.') # HH:MM:SS,mmm -> H:MM:SS.mm
            end = b[1][1:10].replace(',', '.')
            text = b[2].strip().replace('\n', r'\N')
            f_out.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")
    return output_path
