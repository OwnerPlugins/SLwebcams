#!/usr/bin/python3
# -*- coding: utf-8 -*-

from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry
from Components.ActionMap import ActionMap
from Components.Label import Label
from .settings import _


class SLwebcamsSettings(Screen, ConfigListScreen):
    skin = """
    <screen position="center,center" size="600,400" title="SkyLine Webcams - Settings">
        <widget name="config" position="10,10" size="580,330" scrollbarMode="showOnDemand" />
        <ePixmap pixmap="skin_default/buttons/red.png" position="10,360" size="140,40" alphatest="on" />
        <ePixmap pixmap="skin_default/buttons/green.png" position="160,360" size="140,40" alphatest="on" />
        <widget name="key_red" position="10,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
        <widget name="key_green" position="160,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        ConfigListScreen.__init__(self, [], session=session)
        self.createSetup()
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("Save"))
        self["actions"] = ActionMap(
            ["SetupActions", "ColorActions"],
            {
                "ok": self.save,
                "save": self.save,
                "cancel": self.cancel,
                "red": self.cancel,
                "green": self.save,
            }, -2
        )

        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("SkyLine Webcams - Settings"))

    def createSetup(self):
        """Create the settings list with all configuration entries"""
        self.list = []
        self.list.append(getConfigListEntry(_("Buffer size (KB)"), config.plugins.slwebcams.buffer_size))
        self.list.append(getConfigListEntry(_("Show information"), config.plugins.slwebcams.show_info))
        self.list.append(getConfigListEntry(_("Default view"), config.plugins.slwebcams.default_view))
        self.list.append(getConfigListEntry(_("Connection timeout (sec)"), config.plugins.slwebcams.timeout))

        self["config"].list = self.list
        self["config"].l.setList(self.list)

    def save(self):
        """Save all configuration settings"""
        for x in self["config"].list:
            x[1].save()

        self.close(True)

    def cancel(self):
        """Cancel changes and close the settings screen"""
        for x in self["config"].list:
            x[1].cancel()

        self.close(False)
