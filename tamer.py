#!/usr/bin/python3

from __future__ import unicode_literals
import taglib
import logging

def tagIt(path, entry):

    title = entry["title"].replace("/","_").replace("?","")
    mp3File = "{}/{}.mp3".format(path, title)
    logging.debug("Tagging file {}".format(mp3File))
    sanitized_title = sanitizeTitle(entry["title"])
    artist, title = sanitized_title.split(" - ")
    logging.debug("Artist : {}\t Title : {}".format(artist, title))
    album = "{}:{}".format(entry["uploader"], entry["playlist_title"])
    logging.debug("Album : {}".format(album))

    tags = {"ARTIST": [artist],
            "TITLE": [title],
            "ALBUM": [album]
            }

    song = taglib.File(mp3File)
    logging.debug("Tags read.")
    song.tags.update(tags)
    logging.debug("Tags updated.")
    song.save()

def sanitizeTitle(title):
    s = title.replace("【Future Bass】", "").replace("[Free Download]", "").replace("[PREMIERE]", "").replace("\\xc2\\xa0", " ").replace("\\xc2\\xa0", " ")
    return s
