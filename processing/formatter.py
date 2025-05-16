# processing/formatter.py
from typing import List, Dict, Any
import re
import json

def generate_enhanced_output(styled_words: List[Dict[str, Any]], output_format='html', group_words=False, style_params=None) -> str:
    """
    Generate the output file with styled words and icons
    
    Args:
        styled_words: List of word dictionaries with style information
        output_format: Output format ('html', 'enhanced_srt', 'standard_srt', 'vtt', 'ass', or 'json')
        group_words: Whether to group words by time in output
        style_params: Additional styling parameters (e.g. custom colors)
        
    Returns:
        Formatted output string
    """
    if not styled_words:
        return ""
    
    try:    
        if output_format == 'html':
            # Tạo CSS tùy chỉnh từ style_params
            custom_css = ""
            if style_params:
                if 'primary_color' in style_params:
                    custom_css += f".important {{ color: {style_params['primary_color']} !important; }}\n"
                if 'secondary_color' in style_params:
                    custom_css += f".category {{ color: {style_params['secondary_color']} !important; }}\n"
            
            html_output = f'''
            <html>
            <head>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        line-height: 1.6; 
                        background-color: #f9f9f9;
                        padding: 20px;
                    }}
                    .subtitle-container {{
                        background-color: white;
                        border-radius: 5px;
                        padding: 15px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .word {{ 
                        margin-right: 5px; 
                        display: inline-block;
                        padding: 2px 4px;
                        border-radius: 3px;
                        transition: all 0.2s;
                        position: relative;
                    }}
                    .word:hover {{
                        transform: scale(1.1);
                        background-color: rgba(0,0,0,0.05);
                    }}
                    .word-icon {{
                        display: inline-flex;
                        align-items: center;
                        cursor: help;
                        padding: 2px;
                        border-radius: 3px;
                        transition: all 0.2s;
                    }}
                    .word-icon:hover {{
                        background-color: rgba(0,0,0,0.1);
                    }}
                    .secondary-icons {{
                        font-size: 0.8em;
                        color: #666;
                        margin-left: 2px;
                        background-color: rgba(0,0,0,0.05);
                        padding: 0 3px;
                        border-radius: 3px;
                    }}
                    .timestamp {{ 
                        font-size: 10px; 
                        color: #666; 
                        margin-right: 10px;
                        background-color: #f0f0f0;
                        padding: 2px 5px;
                        border-radius: 3px;
                    }}
                    .time-block {{
                        margin-bottom: 10px;
                    }}
                    {custom_css}
                </style>
            </head>
            <body>
            <div class="subtitle-container">
            '''
            
            current_time = ""
            for word in styled_words:
                if current_time != word.get('start_time', ''):
                    if current_time:
                        html_output += '</div>'
                    current_time = word.get('start_time', '')
                    html_output += f'<div class="time-block"><span class="timestamp">[{current_time}]</span>'
                
                style = word.get('style', {})
                color = style.get('color', '#000000')
                font_weight = style.get('font_weight', 'normal')
                
                # Xử lý icons thông minh hơn
                primary_icon = word.get('primary_icon', '')
                secondary_icons = word.get('secondary_icons', [])
                context_info = word.get('context_info', {})
                
                # Tạo tooltip với thông tin chi tiết
                tooltip_parts = []
                if context_info.get('syntax', {}).get('pos'):
                    pos_name = {
                        'NOUN': 'Danh từ', 'VERB': 'Động từ', 'ADJ': 'Tính từ',
                        'ADV': 'Trạng từ', 'PROPN': 'Tên riêng'
                    }.get(context_info['syntax']['pos'], context_info['syntax']['pos'])
                    tooltip_parts.append(f"Loại từ: {pos_name}")
                
                if context_info.get('categories'):
                    tooltip_parts.append(f"Thể loại: {', '.join(context_info['categories'])}")
                
                if secondary_icons:
                    icon_contexts = context_info.get('icon_contexts', {})
                    context_descriptions = []
                    for icon in secondary_icons:
                        context = icon_contexts.get(icon, '')
                        if context == 'direct_match':
                            desc = 'trực tiếp'
                        elif context == 'category_default':
                            desc = 'mặc định'
                        elif context.startswith('related_'):
                            rel = context.split('_')[1]
                            desc = f'liên quan ({rel})'
                        else:
                            desc = context
                        context_descriptions.append(f"{icon}: {desc}")
                    tooltip_parts.append("Icons bổ sung:\\n" + "\\n".join(context_descriptions))
                
                tooltip = " | ".join(tooltip_parts)
                
                # Tạo HTML cho icon với tooltip
                icon_html = f'<span class="word-icon" title="{tooltip}">{primary_icon}'
                if secondary_icons:
                    icon_html += f' <span class="secondary-icons">[+{len(secondary_icons)}]</span>'
                icon_html += '</span>'
                
                # Add appropriate classes based on word properties
                classes = ['word']
                if word.get('important', False):
                    classes.append('important')
                if word.get('categories', []):
                    classes.append('category')
                
                class_str = ' '.join(classes)
                html_output += f'<span class="{class_str}" style="color:{color};font-weight:{font_weight};">{icon_html}</span>'
            
            if current_time:
                html_output += '</div>'
            
            html_output += '''
            </div>
            </body>
            </html>
            '''
            return html_output
        
        elif output_format == 'enhanced_srt':
            # SRT với màu sắc, phong cách và biểu tượng
            return generate_srt_output(styled_words, group_words, include_styling=True)
        
        elif output_format == 'standard_srt':
            # SRT tiêu chuẩn, không có định dạng đặc biệt
            return generate_srt_output(styled_words, group_words, include_styling=False)
        
        elif output_format == 'vtt':
            # Định dạng WebVTT
            return generate_vtt_output(styled_words, group_words)
            
        elif output_format == 'ass':
            # Định dạng Advanced SubStation Alpha
            return generate_ass_output(styled_words, group_words)
        
        elif output_format == 'json':
            # Fix JSON output generation
            simplified_words = []
            for word in styled_words:
                simplified_word = {
                    'index': word.get('index', 0),
                    'start_time': word.get('start_time', '00:00:00,000'),
                    'end_time': word.get('end_time', '00:00:00,000'),
                    'word': word.get('word', ''),
                    'important': word.get('important', False),
                    'categories': word.get('categories', []),
                    'style': {
                        'color': word.get('style', {}).get('color', '#000000'),
                        'font_weight': word.get('style', {}).get('font_weight', 'normal'),
                        'icon': word.get('style', {}).get('icon', '')
                    }
                }
                simplified_words.append(simplified_word)
            return json.dumps(simplified_words, ensure_ascii=False, indent=2)
    
    except Exception as e:
        print(f"Error generating output: {e}")
        # Trả về thông báo lỗi thay vì để trống
        if output_format == 'html':
            return f"<html><body><h1>Error generating HTML</h1><p>{str(e)}</p></body></html>"
        elif output_format in ['enhanced_srt', 'standard_srt']:
            return f"1\n00:00:00,000 --> 00:00:05,000\nError generating SRT: {str(e)}\n\n"
        elif output_format == 'vtt':
            return f"WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nError generating VTT: {str(e)}\n\n"
        elif output_format == 'ass':
            return f"[Script Info]\nTitle: Error\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\nDialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Error generating ASS: {str(e)}\n"
        else:
            return "{\"error\": \"Error generating JSON output\"}"
    
    return ""

def generate_srt_output(styled_words: List[Dict[str, Any]], group_words=False, include_styling=True) -> str:
    """
    Generate SRT format output
    
    Args:
        styled_words: List of word dictionaries with style information
        group_words: Whether to group words by time
        include_styling: Whether to include color, font weight, and icons
        
    Returns:
        SRT formatted string
    """
    if not styled_words:
        return "1\n00:00:00,000 --> 00:00:05,000\nKhông có dữ liệu phụ đề.\n\n"
    
    srt_output = ""
    
    try:
        if group_words:
            # Nhóm các từ theo thời gian bắt đầu
            time_groups = {}
            for word in styled_words:
                start_time = word.get('start_time', '00:00:00,000')
                if start_time not in time_groups:
                    time_groups[start_time] = []
                time_groups[start_time].append(word)
            
            # Sắp xếp các nhóm thời gian
            sorted_times = sorted(time_groups.keys())
            
            # Tạo các entry SRT
            entry_index = 1
            for i, start_time in enumerate(sorted_times):
                words = time_groups[start_time]
                
                # Xác định thời gian kết thúc của nhóm từ
                if i < len(sorted_times) - 1:
                    end_time = sorted_times[i+1]
                else:
                    # Sử dụng thời gian kết thúc của từ cuối cùng trong nhóm
                    end_time = words[-1].get('end_time', start_time)
                
                # Tạo nội dung có định dạng
                content = ""
                for word in words:
                    if include_styling:
                        style = word.get('style', {})
                        color = style.get('color', '#000000').replace('#', '')
                        font_weight = style.get('font_weight', 'normal')
                        
                        # Xử lý icons thông minh hơn
                        primary_icon = word.get('primary_icon', '')
                        secondary_icons = word.get('secondary_icons', [])
                        context_info = word.get('context_info', {})
                        
                        # Tạo chuỗi icon với thông tin bổ sung
                        icon_str = primary_icon
                        if secondary_icons:
                            categories = context_info.get('categories', [])
                            if categories:
                                icon_str += f" [{', '.join(categories[:1])}+{len(secondary_icons)}]"
                            else:
                                icon_str += f" [+{len(secondary_icons)}]"
                        
                        # Tạo định dạng font với màu sắc và độ đậm
                        if font_weight == 'bold':
                            styled_text = f"{icon_str} <font color=\"{color}\"><b>{word.get('word', '')}</b></font>"
                        else:
                            styled_text = f"{icon_str} <font color=\"{color}\">{word.get('word', '')}</font>"
                        
                        content += styled_text + " "
                    else:
                        content += word.get('word', '') + " "
                
                # Loại bỏ khoảng trắng cuối cùng
                content = content.rstrip()
                
                # Thêm entry vào output SRT
                srt_output += f"{entry_index}\n"
                srt_output += f"{start_time} --> {end_time}\n"
                srt_output += f"{content}\n\n"
                
                entry_index += 1
        else:
            # Giữ định dạng 1 từ/dòng
            for i, word in enumerate(styled_words):
                # Đảm bảo tất cả các trường cần thiết đều có sẵn
                index = word.get('index', i+1)
                start_time = word.get('start_time', '00:00:00,000')
                end_time = word.get('end_time', '00:00:00,000')
                word_text = word.get('word', '')
                
                if include_styling:
                    # Lấy thông tin style an toàn
                    style = word.get('style', {})
                    color_code = style.get('color', '#000000').replace('#', '')
                    font_weight = style.get('font_weight', 'normal')
                    
                    # Xử lý icons thông minh hơn
                    primary_icon = word.get('primary_icon', '')
                    secondary_icons = word.get('secondary_icons', [])
                    context_info = word.get('context_info', {})
                    
                    # Tạo chuỗi icon với thông tin bổ sung
                    icon_str = primary_icon
                    if secondary_icons:
                        categories = context_info.get('categories', [])
                        if categories:
                            icon_str += f" [{', '.join(categories[:1])}+{len(secondary_icons)}]"
                        else:
                            icon_str += f" [+{len(secondary_icons)}]"
                    
                    # Tạo từ có style
                    if font_weight == 'bold':
                        styled_word = f"{icon_str} <font color=\"{color_code}\"><b>{word_text}</b></font>"
                    else:
                        styled_word = f"{icon_str} <font color=\"{color_code}\">{word_text}</font>"
                    
                    # Thêm entry vào output SRT
                    srt_output += f"{index}\n"
                    srt_output += f"{start_time} --> {end_time}\n"
                    srt_output += f"{styled_word}\n\n"
                else:
                    # Không thêm định dạng
                    srt_output += f"{index}\n"
                    srt_output += f"{start_time} --> {end_time}\n"
                    srt_output += f"{word_text}\n\n"
    except Exception as e:
        print(f"Error generating SRT: {e}")
        return "1\n00:00:00,000 --> 00:00:05,000\nLỗi khi tạo file SRT: " + str(e) + "\n\n"
    
    if not srt_output:
        return "1\n00:00:00,000 --> 00:00:05,000\nKhông thể tạo nội dung SRT.\n\n"
    
    return srt_output

def generate_vtt_output(styled_words: List[Dict[str, Any]], group_words=False) -> str:
    """
    Generate WebVTT format output
    
    Args:
        styled_words: List of word dictionaries with style information
        group_words: Whether to group words by time
        
    Returns:
        WebVTT formatted string
    """
    vtt_output = "WEBVTT\n\n"
    
    # Chuyển đổi thời gian từ SRT sang VTT (thay dấu phẩy bằng dấu chấm)
    def convert_to_vtt_time(srt_time):
        return srt_time.replace(',', '.')
    
    if group_words:
        # Nhóm các từ theo thời gian bắt đầu
        time_groups = {}
        for word in styled_words:
            start_time = word.get('start_time', '00:00:00,000')
            if start_time not in time_groups:
                time_groups[start_time] = []
            time_groups[start_time].append(word)
        
        # Sắp xếp các nhóm thời gian
        sorted_times = sorted(time_groups.keys())
        
        # Tạo các entry VTT
        for i, start_time in enumerate(sorted_times):
            words = time_groups[start_time]
            
            # Xác định thời gian kết thúc của nhóm từ
            if i < len(sorted_times) - 1:
                end_time = sorted_times[i+1]
            else:
                end_time = words[-1].get('end_time', start_time)
            
            # Tạo nội dung có định dạng
            content = ""
            for word in words:
                style = word.get('style', {})
                color = style.get('color', '#000000')
                font_weight = style.get('font_weight', 'normal')
                
                # Xử lý icons thông minh hơn
                primary_icon = word.get('primary_icon', '')
                secondary_icons = word.get('secondary_icons', [])
                context_info = word.get('context_info', {})
                
                # Tạo chuỗi icon với thông tin bổ sung
                icon_str = primary_icon
                if secondary_icons:
                    categories = context_info.get('categories', [])
                    if categories:
                        icon_str += f" [{', '.join(categories[:1])}+{len(secondary_icons)}]"
                    else:
                        icon_str += f" [+{len(secondary_icons)}]"
                
                # Tạo định dạng cue với màu sắc và độ đậm
                styled_text = f"<c.{color.replace('#', '')}{font_weight.capitalize()}>{icon_str} {word.get('word', '')}</c>"
                content += styled_text + " "
            
            # Loại bỏ khoảng trắng cuối cùng
            content = content.rstrip()
            
            # Thêm entry vào output VTT
            vtt_output += f"{convert_to_vtt_time(start_time)} --> {convert_to_vtt_time(end_time)}\n"
            vtt_output += f"{content}\n\n"
    else:
        # Giữ định dạng 1 từ/dòng
        for word in styled_words:
            try:
                start_time = convert_to_vtt_time(word.get('start_time', '00:00:00,000'))
                end_time = convert_to_vtt_time(word.get('end_time', '00:00:00,000'))
                word_text = word.get('word', '')
                
                # Lấy thông tin style
                style = word.get('style', {})
                color = style.get('color', '#000000')
                font_weight = style.get('font_weight', 'normal')
                
                # Xử lý icons thông minh hơn
                primary_icon = word.get('primary_icon', '')
                secondary_icons = word.get('secondary_icons', [])
                context_info = word.get('context_info', {})
                
                # Tạo chuỗi icon với thông tin bổ sung
                icon_str = primary_icon
                if secondary_icons:
                    categories = context_info.get('categories', [])
                    if categories:
                        icon_str += f" [{', '.join(categories[:1])}+{len(secondary_icons)}]"
                    else:
                        icon_str += f" [+{len(secondary_icons)}]"
                
                # Tạo từ có style
                styled_word = f"<c.{color.replace('#', '')}{font_weight.capitalize()}>{icon_str} {word_text}</c>"
                
                # Thêm entry vào output VTT
                vtt_output += f"{start_time} --> {end_time}\n"
                vtt_output += f"{styled_word}\n\n"
            except Exception as e:
                print(f"Error formatting word in VTT: {e}")
                continue
    
    return vtt_output

def generate_ass_output(styled_words: List[Dict[str, Any]], group_words=False) -> str:
    """
    Generate Advanced SubStation Alpha (ASS) format output
    
    Args:
        styled_words: List of word dictionaries with style information
        group_words: Whether to group words by time
        
    Returns:
        ASS formatted string
    """
    # Tạo header cho file ASS
    ass_output = """[Script Info]
Title: Subtitle
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1280
PlayResY: 720
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # Chuyển đổi thời gian SRT (00:00:00,000) sang ASS (0:00:00.00)
    def convert_to_ass_time(srt_time):
        h, m, s_ms = srt_time.split(':')
        s, ms = s_ms.split(',')
        ms = ms[:2]  # Chỉ lấy 2 chữ số đầu tiên của millisecond
        return f"{int(h)}:{m}:{s}.{ms}"
    
    # Chuyển đổi màu từ HEX (#RRGGBB) sang ASS (&HBBGGRR)
    def convert_color_to_ass(hex_color):
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        r, g, b = hex_color[:2], hex_color[2:4], hex_color[4:6]
        return f"&H00{b}{g}{r}"
    
    if group_words:
        # Nhóm các từ theo thời gian bắt đầu
        time_groups = {}
        for word in styled_words:
            start_time = word.get('start_time', '00:00:00,000')
            if start_time not in time_groups:
                time_groups[start_time] = []
            time_groups[start_time].append(word)
        
        # Sắp xếp các nhóm thời gian
        sorted_times = sorted(time_groups.keys())
        
        # Tạo các entry ASS
        for i, start_time in enumerate(sorted_times):
            words = time_groups[start_time]
            
            # Xác định thời gian kết thúc của nhóm từ
            if i < len(sorted_times) - 1:
                end_time = sorted_times[i+1]
            else:
                end_time = words[-1].get('end_time', start_time)
            
            # Tạo nội dung có định dạng
            content = ""
            for word in words:
                style = word.get('style', {})
                color = style.get('color', '#000000')
                font_weight = style.get('font_weight', 'normal')
                
                # Xử lý icons thông minh hơn
                primary_icon = word.get('primary_icon', '')
                secondary_icons = word.get('secondary_icons', [])
                context_info = word.get('context_info', {})
                
                # Tạo chuỗi icon với thông tin bổ sung
                icon_str = primary_icon
                if secondary_icons:
                    categories = context_info.get('categories', [])
                    if categories:
                        icon_str += f" [{', '.join(categories[:1])}+{len(secondary_icons)}]"
                    else:
                        icon_str += f" [+{len(secondary_icons)}]"
                
                # Chuyển đổi màu và tạo định dạng
                ass_color = convert_color_to_ass(color)
                if font_weight == 'bold':
                    styled_text = f"{{\\c{ass_color}\\b1}}{icon_str}{{\\r}}"
                else:
                    styled_text = f"{{\\c{ass_color}}}{icon_str}{{\\r}}"
                
                content += styled_text + " "
            
            # Loại bỏ khoảng trắng cuối cùng
            content = content.rstrip()
            
            # Chuyển đổi thời gian
            ass_start = convert_to_ass_time(start_time)
            ass_end = convert_to_ass_time(end_time)
            
            # Thêm entry vào output ASS
            ass_output += f"Dialogue: 0,{ass_start},{ass_end},Default,,0,0,0,,{content}\n"
    else:
        # Giữ định dạng 1 từ/dòng
        for word in styled_words:
            try:
                # Chuyển đổi thời gian
                start_time = convert_to_ass_time(word.get('start_time', '00:00:00,000'))
                end_time = convert_to_ass_time(word.get('end_time', '00:00:00,000'))
                word_text = word.get('word', '')
                
                # Lấy thông tin style
                style = word.get('style', {})
                color = style.get('color', '#000000')
                font_weight = style.get('font_weight', 'normal')
                
                # Xử lý icons thông minh hơn
                primary_icon = word.get('primary_icon', '')
                secondary_icons = word.get('secondary_icons', [])
                context_info = word.get('context_info', {})
                
                # Tạo chuỗi icon với thông tin bổ sung
                icon_str = primary_icon
                if secondary_icons:
                    categories = context_info.get('categories', [])
                    if categories:
                        icon_str += f" [{', '.join(categories[:1])}+{len(secondary_icons)}]"
                    else:
                        icon_str += f" [+{len(secondary_icons)}]"
                
                # Chuyển đổi màu và tạo định dạng
                ass_color = convert_color_to_ass(color)
                if font_weight == 'bold':
                    styled_word = f"{{\\c{ass_color}\\b1}}{icon_str}{{\\r}}"
                else:
                    styled_word = f"{{\\c{ass_color}}}{icon_str}{{\\r}}"
                
                # Thêm entry vào output ASS
                ass_output += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{styled_word}\n"
            except Exception as e:
                print(f"Error formatting word in ASS: {e}")
                continue
    
    return ass_output

# Thêm vào file processing/formatter.py
def json_to_srt(json_data, group_words=True, include_styling=True):
    """
    Convert JSON data to SRT format
    
    Args:
        json_data: List of word dictionaries with styling information
        group_words: Whether to group words by time
        include_styling: Whether to include colors, bold text, and icons
        
    Returns:
        SRT formatted string
    """
    if not json_data:
        return "1\n00:00:00,000 --> 00:00:05,000\nKhông có dữ liệu phụ đề.\n\n"
    
    srt_content = ""
    
    try:
        if group_words:
            # Group words by start time
            time_groups = {}
            for word in json_data:
                start_time = word.get('start_time', '00:00:00,000')
                if start_time not in time_groups:
                    time_groups[start_time] = []
                time_groups[start_time].append(word)
            
            # Sort time groups
            sorted_times = sorted(time_groups.keys())
            
            # Create SRT entries
            entry_index = 1
            for i, start_time in enumerate(sorted_times):
                words = time_groups[start_time]
                
                # Determine end time for the group
                if i < len(sorted_times) - 1:
                    end_time = sorted_times[i+1]
                else:
                    # Use the end time of the last word in group
                    end_time = words[-1].get('end_time', start_time)
                
                # Create formatted content
                content = ""
                for word in words:
                    if include_styling:
                        style = word.get('style', {})
                        color = style.get('color', '#000000').replace('#', '')
                        font_weight = style.get('font_weight', 'normal')
                        
                        # Xử lý icons thông minh hơn
                        primary_icon = word.get('primary_icon', '')
                        secondary_icons = word.get('secondary_icons', [])
                        context_info = word.get('context_info', {})
                        
                        # Tạo chuỗi icon với thông tin bổ sung
                        icon_str = primary_icon
                        if secondary_icons:
                            categories = context_info.get('categories', [])
                            if categories:
                                icon_str += f" [{', '.join(categories[:1])}+{len(secondary_icons)}]"
                            else:
                                icon_str += f" [+{len(secondary_icons)}]"
                        
                        # Create font formatting with color and weight
                        if font_weight == 'bold':
                            styled_text = f"{icon_str} <font color=\"{color}\"><b>{word.get('word', '')}</b></font>"
                        else:
                            styled_text = f"{icon_str} <font color=\"{color}\">{word.get('word', '')}</font>"
                        
                        content += styled_text + " "
                    else:
                        content += word.get('word', '') + " "
                
                # Remove trailing whitespace
                content = content.rstrip()
                
                # Add entry to SRT output
                srt_content += f"{entry_index}\n"
                srt_content += f"{start_time} --> {end_time}\n"
                srt_content += f"{content}\n\n"
                
                entry_index += 1
        else:
            # Keep one word per line format
            for i, word in enumerate(json_data):
                # Ensure all required fields are available
                index = word.get('index', i+1)
                start_time = word.get('start_time', '00:00:00,000')
                end_time = word.get('end_time', '00:00:00,000')
                word_text = word.get('word', '')
                
                if include_styling:
                    # Get style information safely
                    style = word.get('style', {})
                    color_code = style.get('color', '#000000').replace('#', '')
                    font_weight = style.get('font_weight', 'normal')
                    
                    # Xử lý icons thông minh hơn
                    primary_icon = word.get('primary_icon', '')
                    secondary_icons = word.get('secondary_icons', [])
                    context_info = word.get('context_info', {})
                    
                    # Tạo chuỗi icon với thông tin bổ sung
                    icon_str = primary_icon
                    if secondary_icons:
                        categories = context_info.get('categories', [])
                        if categories:
                            icon_str += f" [{', '.join(categories[:1])}+{len(secondary_icons)}]"
                        else:
                            icon_str += f" [+{len(secondary_icons)}]"
                    
                    # Create styled word
                    if font_weight == 'bold':
                        styled_word = f"{icon_str} <font color=\"{color_code}\"><b>{word_text}</b></font>"
                    else:
                        styled_word = f"{icon_str} <font color=\"{color_code}\">{word_text}</font>"
                    
                    # Add entry to SRT output
                    srt_content += f"{index}\n"
                    srt_content += f"{start_time} --> {end_time}\n"
                    srt_content += f"{styled_word}\n\n"
                else:
                    # No styling
                    srt_content += f"{index}\n"
                    srt_content += f"{start_time} --> {end_time}\n"
                    srt_content += f"{word_text}\n\n"
        
        return srt_content
    except Exception as e:
        print(f"Error generating SRT from JSON: {e}")
        return f"1\n00:00:00,000 --> 00:00:05,000\nLỗi khi tạo SRT từ JSON: {str(e)}\n\n"