# -*- coding: utf-8 -*-
"""
  Copyright (C) 2017-2020 enen92
  Copyright (C) 2024 nvmd
  This file is part of kaster-ng

  SPDX-License-Identifier: GPL-2.0-or-later
  See LICENSE for more information.
"""

from .. import kodiutils
import xbmcvfs
import xbmc
import os
import json


class FileSystemImageSource:

    def __init__(self, path):
        self.path = path
        self.images = []

    def fetch(self):
        if not self.path or not xbmcvfs.exists(xbmcvfs.translatePath(self.path)):
            return
        self.images = self.get_own_pictures(self.path)


    def get_path(self):
        return self.path
    
    def get_all_images(self):
        return self.images


    def __get_images_recursively(self, path):
        folders, files = xbmcvfs.listdir(path)
        for _file in files:
            self.images.append(os.path.join(path, _file))
        for folder in folders:
            self.__get_images_recursively(os.path.join(path, folder))

    def get_own_pictures(self, path):
        self.images = []
        images_dict = {}

        image_file = os.path.join(xbmcvfs.translatePath(path), "images.json")
        if xbmcvfs.exists(image_file):
            f = xbmcvfs.File(image_file)
            try:
               images_dict = json.loads(f.read())
            except ValueError:
               kodiutils.log(kodiutils.get_string(32010), xbmc.LOGERROR)
            f.close()

        self.__get_images_recursively(xbmcvfs.translatePath(path))

        for _file in self.images:
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
