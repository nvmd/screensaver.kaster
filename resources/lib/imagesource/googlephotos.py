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

def localize_unknown(maybe_unknown):
    if "unknown" in maybe_unknown.lower():
        return kodiutils.get_string(32007)
    else:
        return maybe_unknown

class GooglePhotosSource:

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
            log("GP: Shuffling image entries")
            shuffle(image_entries)
            log("GP: Shuffled image entries: %s" % image_entries, xbmc.LOGDEBUG)
            for img in image_entries:
                yield { "url": img["url"],
                            "metadata": {
                                "line1": img.get("location",""),
                                "line2": localize_unknown(img.get("photographer",""))
                            }
                      }
        except ValueError:
            kodiutils.log(kodiutils.get_string(32010), xbmc.LOGERROR)
            return empty()
