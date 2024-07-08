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
import requests
import xbmcgui
import xbmcaddon
import xbmcvfs
from . import kodiutils
from .kodiutils import log
from random import randint, shuffle
from .screensaverutils import ScreenSaverUtils
from .imagesource.filesystem import FileSystemImageSource
from .imagesource.googlephotos import GooglePhotosSource
from .imagesource.googlearts import GoogleArtsSource

PATH = xbmcaddon.Addon().getAddonInfo("path")

if not kodiutils.get_setting_as_bool("google-photos-hq"):
    IMAGE_FILE = os.path.join(PATH, "resources", "images", "chromecast.json")
else:
    IMAGE_FILE = os.path.join(PATH, "resources", "images", "chromecast-hq.json")

ARTS_IMAGE_FILE = os.path.join(PATH, "resources", "images", "google-arts-and-culture.json")

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
        self.migrate_settings()
        # Init controls
        self.backgroud = self.getControl(32500)
        self.metadata_line2 = self.getControl(32503)
        self.metadata_line3 = self.getControl(32504)

        # Start Image display loop
        self.update_image(self.get_image_sources())

    def update_image(self,image_sources):
        image_source = image_sources[0]
        image_source.update()
        while self._isactive and not self.exit_monitor.abortRequested():
            try:
                current_image = image_source.get_image()
                log("current_image: %s" % current_image, xbmc.LOGDEBUG)

                if self.set_image(current_image) == False:
                    continue
                self.set_metadata(current_image)

                # keep image on the screen for the configured time
                wait_time = kodiutils.get_setting_as_int("wait-time-before-changing-image")
                if self.exit_monitor.waitForAbort(wait_time) == True or self._isactive == False:
                    self._isactive = False
                    break
            except StopIteration:
                log("StopIteration: image source exhausted, needs refreshing", xbmc.LOGINFO)
                image_source.update()
                continue

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

        log("Setting image %s" % current_image["url"], xbmc.LOGDEBUG)
        self.backgroud.setImage(current_image["url"])
        return True

    def set_metadata(self, current_image):
        image_metadata = current_image["metadata"]
        metadata = []

        if "line1" in image_metadata and image_metadata["line1"]:
            metadata.append(image_metadata["line1"])
        if "line2" in image_metadata and image_metadata["line2"]:
            metadata.append(image_metadata["line2"])

        metadata.extend(["",""])
        metadata_fields = [self.metadata_line2, self.metadata_line3]
        for field,text in list(zip(metadata_fields,metadata)):
            field.setLabel(text)

    def get_image_sources(self):
        image_sources = []

        fallback_to_google_arts = not self.is_google_photos_enabled() and not self.is_user_photos_enabled()

        if self.is_google_arts_enabled() or fallback_to_google_arts:
            image_sources.append(GoogleArtsSource(ARTS_IMAGE_FILE))

        if self.is_google_photos_enabled():
            image_sources.append(GooglePhotosSource(IMAGE_FILE))

        if self.is_user_photos_enabled():
            image_sources.append(FileSystemImageSource(kodiutils.get_setting("user-images-fs-directory")))

        return image_sources


    def migrate_settings(self):
        log("Migrating settings", xbmc.LOGINFO)
        if kodiutils.get_setting("enable-google-photos") or  kodiutils.get_setting("enable-user-images-fs"):
            return

        if kodiutils.get_setting_as_int("screensaver-mode") == 0 or kodiutils.get_setting_as_int("screensaver-mode") == 2:
            kodiutils.set_setting("enable-google-photos", True)
        if kodiutils.get_setting_as_int("screensaver-mode") == 1 or kodiutils.get_setting_as_int("screensaver-mode") == 2:
            kodiutils.set_setting("enable-user-images-fs", True)

        if kodiutils.get_setting_as_bool("enable-hq"):
            kodiutils.set_setting("google-photos-hq", True)

        user_images_dir = kodiutils.get_setting("my-pictures-folder")
        if user_images_dir:
            kodiutils.set_setting("user-images-fs-directory", user_images_dir)

    def is_google_arts_enabled(self):
        return kodiutils.get_setting_as_bool("enable-google-arts")
    def is_google_photos_enabled(self):
        return kodiutils.get_setting_as_bool("enable-google-photos")
    def is_user_photos_enabled(self):
        return kodiutils.get_setting_as_bool("enable-user-images-fs")

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
