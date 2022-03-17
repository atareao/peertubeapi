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

import requests

URL = 'https://www.googleapis.com/youtube/v3'
YTURL = 'https://www.youtube.com'


class YT:
    def __init__(self, key):
        self.key = key

    def get_videos_from_playlist(self, playlist_id):
        return self.__get_videos_from_playlist(playlist_id)

    def __get_videos_from_playlist(self, playlist_id, next_page_token=None):
        videos = []
        url = (f"{URL}/playlistItems?part=snippet&maxResults=50&"
               f"playlistId={playlist_id}&key={self.key}")
        print(url)
        if next_page_token:
            url += f"&pageToken={next_page_token}"
        response = requests.get(url=url)
        if response.status_code == 200:
            data = response.json()
            for item in data['items']:
                if item['snippet']['title'].lower() == 'private video' or \
                        item['snippet']['title'].lower() == 'deleted video':
                            continue
                video_id = item['snippet']['resourceId']['videoId']
                download_link = f"{YTURL}/watch?v={video_id}"
                link = f"{YTURL}/watch?v={video_id}&list={playlist_id}"
                video = {
                        "title": item['snippet']['title'],
                        "description": item['snippet']['description'],
                        "id": video_id,
                        "position": item['snippet']['position'],
                        "download_link": download_link,
                        "link": link
                        }
                videos.append(video)
            if 'nextPageToken' in data and data['nextPageToken']:
                more_videos = self.__get_videos_from_playlist(playlist_id,
                        data['nextPageToken'])
                if more_videos:
                    videos += more_videos
        else:
            print(response.status_code)
            print(response.content)
        return videos


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")
    LIST_ID = os.getenv("LIST_ID")
    yt = YT(YOUTUBE_KEY)
    list_of_videos = yt.get_videos_from_playlist(LIST_ID)
    for avideo in list_of_videos:
        print(avideo)
