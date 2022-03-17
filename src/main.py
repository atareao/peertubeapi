#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2022 Lorenzo Carbonell <a.k.a. atareao>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import glob
import youtube_dl
from time import sleep
from dotenv import load_dotenv
from ytapi import YT
from api import PeerTube

TRIES = 3
TIME_SLEEP = 60


def clean():
    files = glob.glob('/tmp/original*')
    for file in files:
        os.remove(file)


def download(avideo):
    success = False
    ydl_opts = {'outtmpl': '/tmp/original',
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'}
    download_link = avideo['download_link']
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        tries = 0
        while tries < TRIES:
            try:
                ydl.download([download_link])
                success = True
                tries = TRIES
            except:
                tries += 1
        sleep(TIME_SLEEP)
    return success


def main(ytkey, list_id, pt_path, channel_id):
    youtube = YT(ytkey)
    peer_tube = PeerTube(pt_path)
    list_of_videos = youtube.get_videos_from_playlist(list_id)
    for avideo in list_of_videos:
        print(avideo)
        success = download(avideo)
        if success:
            name = avideo["title"]
            description = avideo["description"]
            filepath = '/tmp/original.mp4'
            peer_tube.upload(channel_id, filepath, name, description)
        clean()


if __name__ == '__main__':
    load_dotenv()
    PT_PATH = os.getenv("PT_PATH")
    PT_CHANNEL_ID = os.getenv("PT_CHANNEL_ID")
    YT_KEY = os.getenv("YT_KEY")
    YT_LIST_ID = os.getenv("YT_LIST_ID")
    main(YT_KEY, YT_LIST_ID, PT_PATH, PT_CHANNEL_ID)

