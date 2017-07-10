#!/usr/bin/python3

from __future__ import unicode_literals
import youtube_dl
import sys
import json
from getopt import getopt
import time
import tamer
from os import path
import logging
import traceback

output = "/tmp/reaped"
lastchecked = None

consoleLog = logging.StreamHandler(stream=sys.stdout)
consoleLog.setLevel("DEBUG")

logFormatter = logging.Formatter("[{levelname:^7}] {message}", style='{')
consoleLog.setFormatter(logFormatter)

rootLogger = logging.getLogger()
rootLogger.setLevel("DEBUG")
rootLogger.handlers = []
rootLogger.addHandler(consoleLog)

def my_hook(d):
    if d['status'] == 'finished':
        logging.info('Done downloading, now converting ...')

opts, args = getopt(sys.argv[1:], "l:p:", ["link=", "path="])
for opt, arg in opts:
    if opt in ("-l", "--link"):
        link = arg
        list_id = link[link.find("?link=")+6:]
    elif opt in ("-p", "--path"):
        output = arg

if path.isfile("playlists.json"):
    with open("playlists.json") as f:
        savedStates = json.load(f)
else:
    savedStates = {}


# -f 'bestaudio' -x --audio-format "mp3" -o "$OUTPUT_FOLDER/%(title)s.%(ext)s" $PLAYLIST_LINK
# https://www.youtube.com/playlist?list=PLvlw_ICcAI4ermdmmjtr6uxYj0eZ_nKc4
# 20170602
ydlOpts = {
    'format': 'bestaudio',
    'outtmpl': '/{}/%(title)s.%(ext)s'.format(output),
    'simulate': False,
    'ignoreerrors': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'progress_hooks': [my_hook],
    'logger': rootLogger,
}

if list_id in savedStates:
    lastchecked = time.strptime(savedStates[list_id]["lastchecked"], '%Y%m%d')
    #ydlOpts['daterange'] = youtube_dl.utils.DateRange(savedStates[list_id]["lastchecked"])


with youtube_dl.YoutubeDL(ydlOpts) as ydl:
    info_dict = ydl.extract_info(link, download=False)
    report = {'total': len(info_dict["entries"]), 'empty': 0, 'obtained': 0, 'downloaded': 0, 'tagged': 0}
    for entry in info_dict["entries"]:
        if entry == None:
            logging.error("Empty entry!")
            report['empty'] += 1
            continue
        elif " - " not in entry["title"]:
            logging.error("Looks like {} video does not contain a song.".format(entry["title"]))
            report['empty'] += 1
            continue
        if path.isfile("{}/{}.mp3".format(output, entry["title"])):
            logging.warning("\t{} already downloaded.".format(entry["title"]))
            continue
        logging.info("Processing {} [{}]".format(entry["webpage_url"], entry["title"]))
        if lastchecked:
            if time.strptime(entry["upload_date"], '%Y%m%d') < lastchecked:
                logging.debug("Skipped entry by date.")
                report['empty'] += 1
                continue
        for i in range(0,5):
            try:
                ydl.download([entry["webpage_url"]])
                report['obtained'] += 1
                break
            except:
                logging.error("Problem downloading {}\n\t".format(entry["title", traceback.print_exc()]))
                time.sleep(3)
        tamer.tagIt(output, entry)


savedStates[list_id] = {}
savedStates[list_id]["title"] = info_dict["title"]
savedStates[list_id]["url"] = info_dict["webpage_url"]
savedStates[list_id]["lastchecked"] = time.strftime("%Y%m%d")
with open("playlists.json", "w") as f:
    json.dump(savedStates, f, indent=4)
    logging.debug("State saved.")

logging.info("REPORT:\n\t\t{} total\n\t\t{} obtained\n\t\t{} empty".format(report['total'], report['obtained'], report['empty']))
