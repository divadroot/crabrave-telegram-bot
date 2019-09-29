#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import threading
import time
import json
import hashlib
import ffmpeg

from uuid import uuid4
from urllib import parse
from flask import Flask, request, send_file, abort
from waitress import serve
from colorlist import FFMPEG_COLORS
from filter import *

from telegram import InlineQueryResultVideo, InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler


ENABLED_FILTERS = { 
    "classic": classic,
    "simple": simple,
    "snapchat": snapchat,
    "textbox": textbox,
    "topbottom": topbottom
}

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

    font_size = request.args.get("size", default=48, type=int)

    # check if text size is in range
    if font_size > 72:
        return abort(400)

    filter_name = request.args.get("filter", default="classic")

    # check if filter is enabled
    if filter_name not in ENABLED_FILTERS:
        return abort(400)

    overlay_text = parse.unquote_plus(overlay_text).strip()

    # check if overlay text is 2-40 chars long
    if len(overlay_text) < 2 or len(overlay_text) > 40:
        return abort(400)

    # generate filename based on selected options
    filename = f"{generate_filename(style, overlay_text, font, font_color, font_size, filter_name)}.mp4"

    # check if video has already been rendered
    output_file = os.path.join("output", filename)
    if os.path.exists(output_file):
        return send_file(output_file)

    # render video
    selected_filter = ENABLED_FILTERS[filter_name]
    input_stream = ffmpeg.input(input_file)
    output = ffmpeg.output(
        selected_filter.apply_filter(input_stream, overlay_text, font_file, font_color, font_size), 
        input_stream.audio, 
        output_file,
        **{"codec:a": "copy"}
    )

    output.run()
    return send_file(output_file)
            

def inlinequery(update, context):
    # get entered text message
    query = update.inline_query.query.strip()

    if len(query) < 2 or len(query) > 40:
        update.inline_query.answer([
            InlineQueryResultArticle(
                id=uuid4(),
                title="Not enough arguments",
                description="Text must be between 2 and 40 characters long.",
                thumb_url="https://cdn.pixabay.com/photo/2013/07/12/18/09/help-153094__340.png",
                input_message_content=InputTextMessageContent(
                    "Usage: @papiezbot <overlay text>\n\nText must be between 2 and 40 characters long.",
                    parse_mode=ParseMode.MARKDOWN
                )
            )
        ])
        return

    # generate query results
    results = [
        InlineQueryResultVideo(
            id=uuid4(),
            title="🦀🦀 PAPAJ IS GONE 🦀🦀",
            description=query,
            thumb_url=f"{BASE_URL}/thumb/papaj.jpg?t={time.time()}",
            video_url=f"{BASE_URL}/video/{parse.quote_plus(query)}.mp4?style=papaj&font=comicsans&color=white&size=52&filter=classic",
            mime_type="video/mp4"
        ),
        InlineQueryResultVideo(
            id=uuid4(),
            title="🦀🦀 DESPACITO IS GONE 🦀🦀",
            description=query,
            thumb_url=f"{BASE_URL}/thumb/classic.jpg?t={time.time()}",
            video_url=f"{BASE_URL}/video/{parse.quote_plus(query)}.mp4?style=classic&font=raleway&color=white&size=52&filter=classic",
            mime_type="video/mp4"
        ),
        InlineQueryResultVideo(
            id=uuid4(),
            title="🦀🦀 KEBAB IS GONE 🦀🦀",
            description=query,
            thumb_url=f"{BASE_URL}/thumb/kebab.jpg?t={time.time()}",
            video_url=f"{BASE_URL}/video/{parse.quote_plus(query)}.mp4?style=kebab&font=impact&color=white&size=48&filter=snapchat",
            mime_type="video/mp4"
        ),
        InlineQueryResultVideo(
            id=uuid4(),
            title="🦀🦀 STONOGA IS GONE 🦀🦀",
            description=query,
            thumb_url=f"{BASE_URL}/thumb/stonoga.jpg?t={time.time()}",
            video_url=f"{BASE_URL}/video/{parse.quote_plus(query)}.mp4?style=stonoga&font=timesnewroman&color=white&size=48&filter=topbottom",
            mime_type="video/mp4"
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bot made by @divadsn",
            description="Check out my source code on GitHub!",
            thumb_url="https://avatars2.githubusercontent.com/u/28547847?s=460&v=4",
            input_message_content=InputTextMessageContent(
                "https://github.com/divadsn/crabrave-telegram-bot\n\nDonate me via PayPal: https://paypal.me/divadsn",
                parse_mode=ParseMode.MARKDOWN
            )
        )
    ]

    update.inline_query.answer(results)


def generate_filename(style, overlay_text, font, font_color, font_size, filter_name):
    # generate sha256 hash based on selected parameters
    selection = {
        "style": style,
        "overlay_text": overlay_text,
        "font": font,
        "font_color": font_color,
        "font_size": font_size,
        "filter_name": filter_name
    }

    return hashlib.sha256(json.dumps(selection).encode("utf-8")).hexdigest()


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