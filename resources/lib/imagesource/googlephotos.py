# -*- coding: utf-8 -*-
"""
  Copyright (C) 2017-2020 enen92
  Copyright (C) 2024 nvmd
  This file is part of kaster-ng

  SPDX-License-Identifier: GPL-2.0-or-later
  See LICENSE for more information.
"""

from .. import kodiutils
import xbmc
import os
import json


class GooglePhotosSource:

    def __init__(self, image_file_json_path):
        self.images = []
        self.image_file_json_path = image_file_json_path

    def fetch(self):
        self.images = self.get_google_images(self.image_file_json_path)


    def get_path(self):
        return self.path
    
    def get_all_images(self):
        return self.images
    

    def get_google_images(self, IMAGE_FILE):
        # Read google images from json file
        try:
            try:
                with open(IMAGE_FILE, "r") as f:
                    images = f.read()
            except:
                with open(IMAGE_FILE, "r", encoding="utf-8") as f:
                    images = f.read()
        except ValueError:
            kodiutils.log(kodiutils.get_string(32010), xbmc.LOGERROR)
        return json.loads(images)
