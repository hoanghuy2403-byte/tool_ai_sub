# processing/video_player.py
def generate_video_player(styled_words, video_path=None):
    """
    Tạo trang HTML chứa trình phát video và phụ đề được làm nổi bật
    
    Args:
        styled_words: Danh sách từ đã được phân tích và định dạng
        video_path: Đường dẫn đến video (nếu có)
        
    Returns:
        HTML cho trình phát video
    """
    # Xây dựng nội dung phụ đề theo thời gian
    subtitles_by_time = {}
    for word in styled_words:
        time_key = word['start_time']
        if time_key not in subtitles_by_time:
            subtitles_by_time[time_key] = []
        
        style = word['style']
        icon = style['icon']
        styled_word = f'<span style="color:{style["color"]};font-weight:{style["font_weight"]};">{icon} {word["word"]}</span>'
        subtitles_by_time[time_key].append(styled_word)
    
    # Chuyển đổi hh:mm:ss,ms thành số giây
    def time_to_seconds(time_str):
        h, m, s = time_str.replace(',', '.').split(':')
        return float(h) * 3600 + float(m) * 60 + float(s)
    
    # Tạo JavaScript để đồng bộ phụ đề với video
    subtitle_js = "const subtitles = {\n"
    for time_str, words in subtitles_by_time.items():
        seconds = time_to_seconds(time_str)
        words_html = " ".join(words)
        subtitle_js += f'  {seconds}: "{words_html}",\n'
    subtitle_js += "};\n"
    
    # HTML cho trình phát video
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video Player with Enhanced Subtitles</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                background-color: #f5f5f5;
            }}
            .video-container {{
                width: 80%;
                max-width: 800px;
                margin-bottom: 20px;
            }}
            video {{
                width: 100%;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            .subtitle-container {{
                width: 80%;
                max-width: 800px;
                min-height: 100px;
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                font-size: 1.2em;
                text-align: center;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .word {{
                margin: 0 5px;
                transition: transform 0.2s;
            }}
            .word:hover {{
                transform: scale(1.1);
            }}
        </style>
    </head>
    <body>
        <h1>Enhanced Subtitle Video Player</h1>
        <div class="video-container">
            <video id="video" controls>
                <source src="{video_path if video_path else '#'}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <div class="subtitle-container" id="subtitles">
            Phụ đề sẽ hiển thị ở đây khi video phát...
        </div>
        
        <script>
            {subtitle_js}
            
            const video = document.getElementById('video');
            const subtitleContainer = document.getElementById('subtitles');
            
            let currentSubtitle = null;
            
            // Cập nhật phụ đề khi video đang phát
            video.addEventListener('timeupdate', function() {{
                const currentTime = Math.floor(video.currentTime * 10) / 10;
                
                // Tìm phụ đề gần nhất
                let nearestTime = null;
                let minDiff = 1.0; // Trong khoảng 1 giây
                
                for (const time in subtitles) {{
                    const diff = Math.abs(currentTime - parseFloat(time));
                    if (diff < minDiff) {{
                        minDiff = diff;
                        nearestTime = time;
                    }}
                }}
                
                // Hiển thị phụ đề nếu tìm thấy
                if (nearestTime !== null && nearestTime !== currentSubtitle) {{
                    subtitleContainer.innerHTML = subtitles[nearestTime];
                    currentSubtitle = nearestTime;
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return html