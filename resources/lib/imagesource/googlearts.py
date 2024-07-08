# -*- coding: utf-8 -*-
"""
  Copyright (C) 2017-2020 enen92
  Copyright (C) 2024 nvmd
  This file is part of kaster-ng

  SPDX-License-Identifier: GPL-2.0-or-later
  See LICENSE for more information.
"""

from .. import kodiutils
from ..kodiutils import log
import xbmc
import json
from random import shuffle

def empty():
    yield from ()

class GoogleArtsSource:

    def __init__(self, image_file_json_path):
        # self.images = []
        self.images = empty()
        self.image_file_json_path = image_file_json_path

    def fetch(self):
        self.images = self.get_google_images(self.image_file_json_path)

    def update(self):
        kodiutils.log("update")
        self.fetch()

    def get_path(self):
        return self.path
    
    def get_all_images(self):
        return self.images
    
    def get_image(self):
        return next(self.images)
    

    def get_google_images(self, IMAGE_FILE):
        # Read google images from json file
        try:
            try:
                with open(IMAGE_FILE, "r") as f:
                    images = f.read()
            except:
                with open(IMAGE_FILE, "r", encoding="utf-8") as f:
                    images = f.read()

            image_entries = json.loads(images)
            log("GA: Shuffling image entries")
            shuffle(image_entries)
            log("GA: Shuffled image entries: %s" % image_entries, xbmc.LOGDEBUG)
            for img in image_entries:
                yield { "url": img["image"] + "=s1200",
                        "metadata": {
                            "line1": img["title"],
                            "line2": img["creator"] + " | " + img["attribution"]
                        }
                      }
        except ValueError:
            kodiutils.log(kodiutils.get_string(32010), xbmc.LOGERROR)
            return empty()
