# Snapchat-like textbox filter
def apply_filter(input_stream, overlay_text, font_file, font_color, font_size):
    box_height = int(font_size * 1.5)
    video_stream = input_stream.video.drawbox(
        x="0",
        y="(ih-h)/2",
        color="black@0.5",
        width="iw",
        height=str(box_height),
        t="fill"
    ).drawtext( 
        x="(w-text_w)/2",
        y="(h-text_h)/2",
        text=overlay_text, 
        fontfile=font_file,
        fontcolor=str(font_color),
        fontsize=str(font_size),
    )

    return video_stream