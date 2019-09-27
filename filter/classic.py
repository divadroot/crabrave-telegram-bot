# Classic crab rave text filter
def apply_filter(input_stream, overlay_text, font_file, font_color, font_size):
    text_lines = overlay_text.split("\\n")
    text_shadow = int(font_size / 16)

    # ffmpeg does not support multiline text with vertical align
    if len(text_lines) >= 2:
        video_stream = input_stream.video.drawtext( 
            x="(w-text_w)/2",
            y="(h-text_h)/2-text_h",
            text=text_lines[0], 
            fontfile=font_file,
            fontcolor=font_color,
            fontsize=font_size,
            shadowcolor="black@0.6",
            shadowx=str(text_shadow),
            shadowy=str(text_shadow)
        ).drawtext( 
            x="(w-text_w)/2",
            y="(h-text_h)/2+text_h",
            text=text_lines[1], 
            fontfile=font_file,
            fontcolor=font_color,
            fontsize=font_size,
            shadowcolor="black@0.6",
            shadowx=str(text_shadow),
            shadowy=str(text_shadow)
        )
    else:
        video_stream = input_stream.video.drawtext( 
            x="(w-text_w)/2",
            y="(h-text_h)/2",
            text=overlay_text, 
            fontfile=font_file,
            fontcolor=font_color,
            fontsize=font_size,
            shadowcolor="black@0.6",
            shadowx=str(text_shadow),
            shadowy=str(text_shadow)
        )

    return video_stream