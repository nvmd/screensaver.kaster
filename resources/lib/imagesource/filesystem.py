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
import xbmcvfs
import xbmc
import os
import json
from random import shuffle


def empty():
    yield from ()


class FileSystemImageSource:

    def __init__(self, path):
        self.path = path
        self.images = empty()
        self.image_files = []

    def fetch(self):
        kodiutils.log("fetch")
        if not self.path or not xbmcvfs.exists(xbmcvfs.translatePath(self.path)):
            self.images = empty()
            return
        self.images = self.get_own_pictures(self.path)
        
    def update(self):
        kodiutils.log("update")
        self.fetch()

    def get_path(self):
        return self.path
    
    def get_all_images(self):
        all_images = []
        for img in self.images:
            all_images.append(img)
        return all_images
    
    def get_image(self):
        return next(self.images)

    def __get_images_recursively(self, path):
        folders, files = xbmcvfs.listdir(path)
        for _file in files:
            self.image_files.append(os.path.join(path, _file))
        for folder in folders:
            self.__get_images_recursively(os.path.join(path, folder))

    def get_own_pictures(self, path):
        self.image_files = []
        images_dict = {}

        images_json = os.path.join(xbmcvfs.translatePath(path), "images.json")
        if xbmcvfs.exists(images_json):
            f = xbmcvfs.File(images_json)
            try:
               images_dict = json.loads(f.read())
            except ValueError:
               kodiutils.log(kodiutils.get_string(32010), xbmc.LOGERROR)
            f.close()

        self.__get_images_recursively(xbmcvfs.translatePath(path))

        log("FS: Shuffling image file list")
        shuffle(self.image_files)
        log("FS: Shuffled image file list: %s" % self.image_files, xbmc.LOGDEBUG)

        for _file in self.image_files:
            if _file.lower().endswith(('.png', '.jpg', '.jpeg')):
                returned_dict = {
                    "url": _file,
                    "private": True
                }
                if images_dict:
                    for image in images_dict:
                        if "image" in list(image.keys()) and os.path.join(xbmcvfs.translatePath(path),image["image"]) == _file:
                            if "line1" in list(image.keys()):
                                returned_dict["line1"] = image["line1"]
                            if "line2" in list(image.keys()):
                                returned_dict["line2"] = image["line2"]
                yield returned_dict
