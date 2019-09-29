# Just a simple text filter
def apply_filter(input_stream, overlay_text, font_file, font_color, font_size):
    video_stream = input_stream.video.drawtext( 
        x="(w-text_w)/2",
        y="(h-text_h)/2",
        text=overlay_text, 
        fontfile=font_file,
        fontcolor=str(font_color),
        fontsize=str(font_size),
    )

    return video_stream