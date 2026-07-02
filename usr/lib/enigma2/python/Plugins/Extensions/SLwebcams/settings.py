#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigText

from . import __version__
import gettext

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

PluginLanguageDomain = "SLwebcams"
PluginLanguagePath = "Extensions/SLwebcams/locale"
print('SLWebcams version %s' % __version__)


def localeInit():
    """Initialize gettext with the plugin's locale path"""
    if PluginLanguageDomain and PluginLanguagePath:
        gettext.bindtextdomain(
            PluginLanguageDomain,
            resolveFilename(
                SCOPE_PLUGINS,
                PluginLanguagePath))


def _(txt):
    """Translation function with fallback to default gettext"""
    translated = gettext.dgettext(PluginLanguageDomain, txt)
    if translated:
        return translated
    else:
        print(
            "[%s] fallback to default translation for %s" %
            (PluginLanguageDomain, txt))
        return gettext.gettext(txt)


# Initialize localization
localeInit()
language.addCallback(localeInit)


# Plugin configuration
config.plugins.slwebcams = ConfigSubsection()

# Buffer size selection
config.plugins.slwebcams.buffer_size = ConfigSelection(
    default="8192",
    choices=[
        ("1024", "1 MB"),
        ("2048", "2 MB"),
        ("4096", "4 MB"),
        ("8192", "8 MB"),
        ("16384", "16 MB")
    ]
)

# Show information overlay
config.plugins.slwebcams.show_info = ConfigYesNo(default=True)

# Default view mode
config.plugins.slwebcams.default_view = ConfigSelection(
    default="live",
    choices=[
        ("live", _("Live Webcams")),
        ("category", _("Category-based Webcams"))
    ]
)

# Connection timeout
config.plugins.slwebcams.timeout = ConfigSelection(
    default="10",
    choices=[
        ("5", "5 sec"),
        ("10", "10 sec"),
        ("15", "15 sec"),
        ("20", "20 sec")
    ]
)

# Custom User-Agent
config.plugins.slwebcams.user_agent = ConfigText(
    default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)
