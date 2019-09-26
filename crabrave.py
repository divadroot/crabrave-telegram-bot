#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import threading
import time
import unicodedata
import ffmpeg

from uuid import uuid4
from urllib import parse
from flask import Flask, request, send_file, abort
from waitress import serve
from colorlist import FFMPEG_COLORS

from telegram import InlineQueryResultVideo, InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler

# https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words
INVALID_FILE_CHARS = '/\\?%*:|"<>'

# enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
PORT = int(os.environ.get("PORT", "3000"))
BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")

app = Flask(__name__, static_url_path="")
updater = Updater(BOT_TOKEN, use_context=True)

if not os.path.isdir("output"):
    os.path.mkdir("output")


@app.route("/thumb/<name>.jpg", methods=['GET'])
def thumbnail(name):
    return send_file(os.path.join("thumb", f"{name}.jpg"))


@app.route("/video/<overlay_text>.mp4", methods=['GET'])
def crabrave(overlay_text):
    style = request.args.get("style", default="papaj")
    input_file = os.path.join("input", f"{style}.mp4")

    # check if input file exists
    if not os.path.exists(input_file):
        return abort(400)

    font = request.args.get("font", default="comicsans")
    font_file = os.path.join("font", f"{font}.ttf")

    # check if font file exists
    if not os.path.exists(font_file):
        return abort(400)

    font_color = request.args.get("color", default="white")

    # check if text color is available
    if font_color not in FFMPEG_COLORS:
        return abort(400)

    font_size = request.args.get("size", default=36, type=int)

    # check if text size is in range
    if font_size > 72:
        return abort(400)

    overlay_text = parse.unquote_plus(overlay_text).strip()

    # check if overlay text is 0-40 chars long
    if len(overlay_text) == 0 or len(overlay_text) > 40:
        return abort(400)

    # generate filename based on selected options
    filename = f"{style}-{secure_filename(overlay_text)}_{font}_{font_color}_{font_size}.mp4"

    # check if video has already been rendered
    output_file = os.path.join("output", filename)
    if os.path.exists(output_file):
        return send_file(output_file)

    # render video
    box_height = int(font_size * 1.5)
    input_stream = ffmpeg.input(input_file)
    (
        input_stream.drawbox(
            x="0",
            y="(ih-h)/2",
            color="black@0.5",
            width="iw",
            height=str(box_height),
            t="fill"
        )
        .drawtext( 
            x="(w-text_w)/2",
            y="(h-text_h)/2",
            text=overlay_text, 
            fontfile=font_file,
            fontcolor=str(font_color),
            fontsize=str(font_size),
        )
        .output(input_stream.audio, output_file, **{"codec:a": "copy"})
        .run()
    )

    return send_file(output_file)
            

def inlinequery(update, context):
    # get entered text message
    query = update.inline_query.query.strip()

    if len(query) == 0 or len(query) > 40:
        update.inline_query.answer([])
        return

    # generate query results
    results = [
        InlineQueryResultVideo(
            id=uuid4(),
            title="🦀🦀 PAPAJ IS GONE 🦀🦀",
            description=query,
            thumb_url=f"{BASE_URL}/thumb/papaj.jpg?t={time.time()}",
            video_url=f"{BASE_URL}/video/{parse.quote_plus(query)}.mp4?style=papaj&font=comicsans&color=white&size=36",
            mime_type="video/mp4"
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bot made by @divadsn",
            description="Check my source code on GitHub!",
            thumb_url="https://avatars2.githubusercontent.com/u/28547847?s=460&v=4",
            input_message_content=InputTextMessageContent(
                "https://github.com/divadsn/crabrave-telegram-bot\n\nDonate me via PayPal: https://paypal.me/divadsn",
                parse_mode=ParseMode.MARKDOWN
            ),
        )
    ]

    update.inline_query.answer(results)


def secure_filename(filename):
    # keep only valid ascii chars
    output = list(unicodedata.normalize("NFKD", filename))

    # special case characters that don't get stripped by the above technique
    for pos, char in enumerate(output):
        if char == '\u0141':
            output[pos] = 'L'
        elif char == '\u0142':
            output[pos] = 'l'

    # remove unallowed characters
    output = [c if c not in INVALID_FILE_CHARS else '_' for c in output]
    return "".join(output).encode("ASCII", "ignore").decode().replace(" ", "_")


def start_bot():    
    # add inlinequery handler
    dp = updater.dispatcher
    dp.add_handler(InlineQueryHandler(inlinequery))

    # start the bot
    updater.start_polling()


def main():
    print("Starting Telegram bot...")
    bot = threading.Thread(target=start_bot)
    bot.start()
    
    # start web server and idle
    print(f"Listening on {BASE_URL} for requests, press CTRL+C to stop")
    serve(app, port=PORT, _quiet=True)

    # finish thread by stopping the bot
    updater.stop()


if __name__ == '__main__':
    main()