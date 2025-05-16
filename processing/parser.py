# processing/parser.py
import re
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """Clean subtitle text by removing HTML tags and extra whitespace"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove multiple spaces and trim
    text = ' '.join(text.split())
    return text

def parse_srt(srt_file: str) -> List[Dict[str, Any]]:
    """
    Parse SRT file and extract words with timing
    
    Args:
        srt_file: Path to the SRT file
        
    Returns:
        List of dictionaries containing word data
    """
    words = []
    
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                if lines[i].strip().isdigit():  # Entry number
                    index = int(lines[i].strip())
                    i += 1
                    if i >= len(lines): break
                    
                    # Time codes
                    time_line = lines[i].strip()
                    time_pattern = r'(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)'
                    match = re.match(time_pattern, time_line)
                    if not match: 
                        i += 1
                        continue
                        
                    start_time, end_time = match.groups()
                    i += 1
                    if i >= len(lines): break
                    
                    # Collect all subtitle text until empty line
                    subtitle_text = []
                    while i < len(lines) and lines[i].strip():
                        subtitle_text.append(lines[i].strip())
                        i += 1
                    
                    # Clean and split text into words
                    text = clean_text(' '.join(subtitle_text))
                    if text:
                        # Split into words and preserve punctuation
                        word_pattern = r'\b\w+\b|[.,!?;]'
                        found_words = re.findall(word_pattern, text)
                        
                        # Calculate approximate timing for each word
                        if found_words:
                            start_ms = time_to_ms(start_time)
                            end_ms = time_to_ms(end_time)
                            ms_per_word = (end_ms - start_ms) / len(found_words)
                            
                            for word_idx, word in enumerate(found_words):
                                word_start_ms = start_ms + (word_idx * ms_per_word)
                                word_end_ms = word_start_ms + ms_per_word
                                
                                words.append({
                                    'index': index,
                                    'start_time': ms_to_time(word_start_ms),
                                    'end_time': ms_to_time(word_end_ms),
                                    'word': word
                                })
                    
                    # Skip empty line
                    i += 1
                else:
                    i += 1
    except Exception as e:
        print(f"Error parsing SRT file: {e}")
        return []
                    
    return words

def parse_srt_content(content: str) -> List[Dict[str, Any]]:
    """
    Parse SRT content from a string
    
    Args:
        content: SRT content as string
        
    Returns:
        List of dictionaries containing word data
    """
    words = []
    
    try:
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            if lines[i].strip().isdigit():  # Entry number
                index = int(lines[i].strip())
                i += 1
                if i >= len(lines): break
                
                # Time codes
                time_line = lines[i].strip()
                time_pattern = r'(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)'
                match = re.match(time_pattern, time_line)
                if not match: 
                    i += 1
                    continue
                    
                start_time, end_time = match.groups()
                i += 1
                if i >= len(lines): break
                
                # Collect all subtitle text until empty line
                subtitle_text = []
                while i < len(lines) and lines[i].strip():
                    subtitle_text.append(lines[i].strip())
                    i += 1
                
                # Clean and split text into words
                text = clean_text(' '.join(subtitle_text))
                if text:
                    # Split into words and preserve punctuation
                    word_pattern = r'\b\w+\b|[.,!?;]'
                    found_words = re.findall(word_pattern, text)
                    
                    # Calculate approximate timing for each word
                    if found_words:
                        start_ms = time_to_ms(start_time)
                        end_ms = time_to_ms(end_time)
                        ms_per_word = (end_ms - start_ms) / len(found_words)
                        
                        for word_idx, word in enumerate(found_words):
                            word_start_ms = start_ms + (word_idx * ms_per_word)
                            word_end_ms = word_start_ms + ms_per_word
                            
                            words.append({
                                'index': index,
                                'start_time': ms_to_time(word_start_ms),
                                'end_time': ms_to_time(word_end_ms),
                                'word': word
                            })
                
                # Skip empty line
                i += 1
            else:
                i += 1
    except Exception as e:
        print(f"Error parsing SRT content: {e}")
        return []
                
    return words

def time_to_ms(time_str: str) -> int:
    """Convert SRT time format to milliseconds"""
    h, m, s = time_str.replace(',', '.').split(':')
    s, ms = s.split('.')
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)

def ms_to_time(ms: float) -> str:
    """Convert milliseconds to SRT time format"""
    h = int(ms / 3600000)
    m = int((ms % 3600000) / 60000)
    s = int((ms % 60000) / 1000)
    ms = int(ms % 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"