# Centered text with box filter
def apply_filter(input_stream, overlay_text, font_file, font_color, font_size):
    box_border = int(font_size / 8)
    video_stream = input_stream.video.drawtext( 
        x="(w-text_w)/2",
        y="(h-text_h)/2",
        box="1",
        boxcolor="black@0.5",
        boxborderw=str(box_border),
        text=overlay_text, 
        fontfile=font_file,
        fontcolor=str(font_color),
        fontsize=str(font_size)
    )

    return video_stream