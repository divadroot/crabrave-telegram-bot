# Top text bottom text style filter
def apply_filter(input_stream, overlay_text, font_file, font_color, font_size):
    text_lines = overlay_text.split("\n")
    video_stream = input_stream.video.drawtext( 
        x="(w-text_w)/2",
        y="text_h*0.5",
        text=text_lines[0], 
        fontfile=font_file,
        fontcolor=str(font_color),
        fontsize=str(font_size)
    )

    # ffmpeg does not support multiline text with vertical align
    if len(text_lines) >= 2:
        video_stream = video_stream.drawtext(
            x="(w-text_w)/2",
            y="h-(text_h*1.5)",
            text=text_lines[1], 
            fontfile=font_file,
            fontcolor=str(font_color),
            fontsize=str(font_size)
        )

    return video_stream
