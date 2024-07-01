# -*- coding: utf-8 -*-
"""
  Copyright (C) 2017-2020 enen92
  This file is part of kaster

  SPDX-License-Identifier: GPL-2.0-or-later
  See LICENSE for more information.
"""
import xbmc
import os
import json
import itertools
import requests
import xbmcgui
import xbmcaddon
import xbmcvfs
from . import kodiutils
from random import randint, shuffle
from .screensaverutils import ScreenSaverUtils

PATH = xbmcaddon.Addon().getAddonInfo("path")

if not kodiutils.get_setting_as_bool("enable-hq"):
    IMAGE_FILE = os.path.join(PATH, "resources", "images", "chromecast.json")
else:
    IMAGE_FILE = os.path.join(PATH, "resources", "images", "chromecast-hq.json")


class Kaster(xbmcgui.WindowXMLDialog):

    class ExitMonitor(xbmc.Monitor):

        def __init__(self, exit_callback):
            self.exit_callback = exit_callback

        def onScreensaverDeactivated(self):
            try:
                self.exit_callback()
            except AttributeError:
                xbmc.log(
                    msg="exit_callback method not yet available",
                    level=xbmc.LOGWARNING
                )


    def __init__(self, *args, **kwargs):
        self.exit_monitor = None
        self.images = []
        self.set_property()
        self.utils = ScreenSaverUtils()

    def onInit(self):
        self._isactive = True
        # Register screensaver deactivate callback function
        self.exit_monitor = self.ExitMonitor(self.exit)
        # Init controls

        self.imageBuffers = [32500,32501]
        self.currentImgId = self.imageBuffers[0]
        self.nextImgId = self.imageBuffers[1]
        
        self.metadata_line2 = self.getControl(32503)
        self.metadata_line3 = self.getControl(32504)

        # Start Image display loop
        self.update_image()


    def setImage(self, image):
        self.getControl(self.currentImgId).setImage(image)

        self.getControl(self.nextImgId).setVisible(False)
        self.getControl(self.currentImgId).setVisible(True)

        self.nextImgId = self.currentImgId
        self.currentImgId = itertools.cycle(self.imageBuffers).__next__


    def update_image(self):
        while self._isactive and not self.exit_monitor.abortRequested():
            self.get_images()
            for img in self.images:
                current_image = img
        if self.images and self.exit_monitor:
            while self._isactive and not self.exit_monitor.abortRequested():
                rand_index = randint(0, len(self.images) - 1)
                current_image = self.images[rand_index]

                if self.set_image(current_image) == False:
                    continue
                self.set_metadata(current_image)

                # keep image on the screen for the configured time
                wait_time = kodiutils.get_setting_as_int("wait-time-before-changing-image")
                if self.exit_monitor.waitForAbort(wait_time) == True or self._isactive == False:
                    self._isactive = False
                    break

    def set_image(self, current_image):
        if "private" not in current_image:
            # if it is a google image....
            # check that kodi won't get 429 when fetching image
            req = requests.head(url=current_image["url"])
            if req.status_code == 429:   # (too many requests)
                if self.exit_monitor.waitForAbort(5) == True:
                    self._isactive = False
                    return False    # skip if abort
            elif req.status_code != 200:
                return False    # skip if smth else and not 200

        self.setImage(current_image["url"])
        return True

    def set_metadata(self, current_image):
                metadata = []
                # if it is a google image....
                if "private" not in current_image:
                    req = requests.head(url=current_image["url"])
                    if req.status_code != 200:
                        # sleep for a bit to avoid 429 (too many requests)
                        if req.status_code == 429:
                            if self.exit_monitor.waitForAbort(5) == True or self._isactive == False:
                                break
                        continue

                    if "location" in list(current_image.keys()):
                        metadata.append(current_image["location"])
                    if "photographer" in list(current_image.keys()):
                        metadata.append("%s %s" % (kodiutils.get_string(32001),
                                                                self.utils.remove_unknown_author(current_image["photographer"])))
                else:
                    # Logic for user owned photos - custom information
                    if "line1" in current_image:
                        metadata.append(current_image["line1"])
                    if "line2" in current_image:
                        metadata.append(current_image["line2"])
        metadata = []
        # if it is a google image....
        if "private" not in current_image:
            if "location" in list(current_image.keys()):
                metadata.append(current_image["location"])
            if "photographer" in list(current_image.keys()):
                metadata.append("%s %s" % (kodiutils.get_string(32001),
                                                        self.utils.remove_unknown_author(current_image["photographer"])))
        else:
            # Logic for user owned photos - custom information
            if "line1" in current_image:
                metadata.append(current_image["line1"])
            if "line2" in current_image:
                metadata.append(current_image["line2"])

        metadata.extend(["",""])
        metadata_fields = [self.metadata_line2, self.metadata_line3]
        for f,t in list(zip(metadata_fields,metadata)):
            f.setLabel(t)

    def get_images(self, override=False):
        # Read google images from json file
        self.images = []
        if kodiutils.get_setting_as_int("screensaver-mode") == 0 or kodiutils.get_setting_as_int("screensaver-mode") == 2 or override:
            try:
                with open(IMAGE_FILE, "r") as f:
                    images = f.read()
            except:
                with open(IMAGE_FILE, "r", encoding="utf-8") as f:
                    images = f.read()
            self.images = json.loads(images)
        # Check if we have images to append
        if kodiutils.get_setting_as_int("screensaver-mode") == 1 or kodiutils.get_setting_as_int("screensaver-mode") == 2 and not override:
            if kodiutils.get_setting("my-pictures-folder") and xbmcvfs.exists(xbmcvfs.translatePath(kodiutils.get_setting("my-pictures-folder"))):
                for image in self.utils.get_own_pictures(kodiutils.get_setting("my-pictures-folder")):
                    self.images.append(image)
            else:
                return self.get_images(override=True)
        shuffle(self.images)
        return

    def set_property(self):
        # Kodi does not yet allow scripts to ship font definitions
        skin = xbmc.getSkinDir()
        if "estuary" in skin:
            self.setProperty("clockfont", "fontclock")
        elif "zephyr" in skin:
            self.setProperty("clockfont", "fontzephyr")
        elif "eminence" in skin:
            self.setProperty("clockfont", "fonteminence")
        elif "aura" in skin:
            self.setProperty("clockfont", "fontaura")
        elif "box" in skin:
            self.setProperty("clockfont", "box")
        else:
            self.setProperty("clockfont", "fontmainmenu")
        # Set skin properties as settings
        for setting in ["hide-clock-info", "hide-kodi-logo", "hide-weather-info", "hide-pic-info", "hide-overlay", "show-blackbackground"]:
            self.setProperty(setting, kodiutils.get_setting(setting))
        # Set animations
        if kodiutils.get_setting_as_int("animation") == 1:
            self.setProperty("animation","panzoom")
        return


    def exit(self):
        self._isactive = False
        # Delete the monitor from memory so we can gracefully remove
        # the screensaver window from memory too
        if self.exit_monitor:
            del self.exit_monitor
        # Finally call close so doModal returns
        self.close()
