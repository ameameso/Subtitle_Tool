import re
import os

def extract_text_from_ass(input_path):
    """把 ASS 变成 TXT 的核心逻辑"""
    output_path = os.path.splitext(input_path)[0] + ".txt"
    
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
                    text = parts[9].strip()
                    # 去掉花括号里的样式代码
                    clean_text = re.sub(r'\{.*?\}', '', text)
                    f_out.write(clean_text + '\n')
    
    return output_path