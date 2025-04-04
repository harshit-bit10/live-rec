import os
import requests
import json
import pytz
import time
from datetime import datetime
from subprocess import check_output
from pytz import timezone 
from urllib.request import urlopen, Request
import shlex
import ffmpeg
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


def fetch_data(url):
    data = requests.get(url)
    data = data.text
    return json.loads(data)

def getChannels(app, message):
    data = fetch_data(iptv_link)
    channelsList = ""
    for i in data:
        channelsList += f"{i}\n"
    message.reply_text(text=f"Available Channels:\n\n{channelsList}")
