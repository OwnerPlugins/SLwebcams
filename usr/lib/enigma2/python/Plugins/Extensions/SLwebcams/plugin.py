#!/usr/bin/python3
# -*- coding: utf-8 -*-

# mod lululla 2026.07.01
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from enigma import eServiceReference, getDesktop
import os
import sys


try:
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    if plugin_dir not in sys.path:
        sys.path.insert(0, plugin_dir)

    parent_dir = os.path.dirname(plugin_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

except Exception as e:
    print("[SLwebcams] Error adding path: {}".format(e))

from .webcam_parser import WebcamParser
from .stream_extractor import StreamExtractor
from .settings import _
from .settings_screen import SLwebcamsSettings
from .ui_settings import get_ui_settings, UI_COLORS
from .sl_logger import SLLogger, enhanced_log

try:
    import importlib
    import webcam_parser
    importlib.reload(webcam_parser)
except Exception as e:
    enhanced_log("Error reloading webcam_parser module: {}".format(e))


class SLwebcamsMain(Screen):
    def __init__(self, session):
        enhanced_log("Initializing SLwebcamsMain")
        ui_settings = get_ui_settings()
        main_settings = ui_settings['main_screen']
        item_height = main_settings.get('item_height', 40)

        # Calculate dimensions and positions
        width = int(main_settings['size'].split(',')[0])
        height = int(main_settings['size'].split(',')[1])
        content_width = width - 60
        content_height = height - 200
        button_y = height - 80
        button_width = 260
        button_positions = [i * content_width // 4 + 30 for i in range(4)]

        # Calculate three-column layout with adaptive widths

        total_width = content_width
        # col1_width = int(total_width * 0.20)
        # col2_width = int(total_width * 0.25)
        # col3_width = total_width - col1_width - col2_width - 60
        # col1_x = 30
        # col2_x = col1_x + col1_width + 20
        # col3_x = col2_x + col2_width + 20
        # if col1_width < 180:
            # col1_width = 180
        # if col2_width < 200:
            # col2_width = 200
        # if col3_width < 300:
            # col3_width = 300

        col1_width = int(total_width * 0.30)   # 30% per la colonna di sinistra (era 20%)
        col2_width = int(total_width * 0.25)   # 25% per la colonna centrale
        col3_width = total_width - col1_width - col2_width - 60  # resto per webcam

        col1_x = 30
        col2_x = col1_x + col1_width + 20
        col3_x = col2_x + col2_width + 20

        # cambia le larghezze minime
        if col1_width < 220:    # era 180
            col1_width = 220
        if col2_width < 200:    # invariato
            col2_width = 200
        if col3_width < 250:    # era 300 (più stretta)
            col3_width = 250

        # Skin with itemHeight
        self.skin = """
        <screen position="{pos}" size="{size}" title="SkyLine Webcams" flags="wfNoBorder">
            <widget name="title" position="30,30" size="{cw},50" font="{tf}" halign="center" valign="center" foregroundColor="{tc}" backgroundColor="{bc}" transparent="1" />
            <widget name="continents_title" position="{c1x},85" size="{c1w},15" font="Regular;16" halign="center" valign="center" foregroundColor="{tc}" backgroundColor="{bc}" transparent="1" />
            <widget name="countries_title" position="{c2x},85" size="{c2w},15" font="Regular;16" halign="center" valign="center" foregroundColor="{txt}" backgroundColor="{bc}" transparent="1" />
            <widget name="webcams_title" position="{c3x},85" size="{c3w},15" font="Regular;16" halign="center" valign="center" foregroundColor="{txt}" backgroundColor="{bc}" transparent="1" />
            <widget name="main_title" position="30,85" size="{cw},25" font="Regular;20" halign="center" valign="center" foregroundColor="{tc}" backgroundColor="{bc}" transparent="1" />

            <widget name="webcam_list" position="{c1x},100" size="{c1w},{ch}" font="{mf}" itemHeight="{ih}" scrollbarMode="showOnDemand" foregroundColor="{txt}" backgroundColor="{bc}" transparent="1" />
            <widget name="countries_list" position="{c2x},100" size="{c2w},{ch}" font="{mf}" itemHeight="{ih}" scrollbarMode="showOnDemand" foregroundColor="{txt}" backgroundColor="{bc}" transparent="1" />
            <widget name="webcams_list" position="{c3x},100" size="{c3w},{ch}" font="{mf}" itemHeight="{ih}" scrollbarMode="showOnDemand" foregroundColor="{txt}" backgroundColor="{bc}" transparent="1" />
            <widget name="main_list" position="30,120" size="{cw},{ch2}" font="{mf}" itemHeight="{ih}" scrollbarMode="showOnDemand" foregroundColor="{txt}" backgroundColor="{bc}" transparent="1" />

            <widget name="description" position="30,{d1}" size="{cw},40" font="Regular;18" foregroundColor="{txt}" backgroundColor="{bc}" transparent="1" />
            <widget name="status" position="30,{d2}" size="{cw},35" font="Regular;24" foregroundColor="{txt}" backgroundColor="{bc}" transparent="1" />
            <widget name="key_red" position="{bp0},{by}" size="{bw},30" font="{bf}" halign="center" valign="center" foregroundColor="{br}" backgroundColor="{bc}" transparent="1" />
            <widget name="key_green" position="{bp1},{by}" size="{bw},30" font="{bf}" halign="center" valign="center" foregroundColor="{bg}" backgroundColor="{bc}" transparent="1" />
            <widget name="key_yellow" position="{bp2},{by}" size="{bw},30" font="{bf}" halign="center" valign="center" foregroundColor="{byc}" backgroundColor="{bc}" transparent="1" />
            <widget name="key_blue" position="{bp3},{by}" size="{bw},30" font="{bf}" halign="center" valign="center" foregroundColor="{bl}" backgroundColor="{bc}" transparent="1" />
        </screen>
        """.format(
            pos=main_settings['position'],
            size=main_settings['size'],
            cw=content_width,
            ch=content_height - 100,
            ch2=content_height - 120,
            d1=100 + content_height - 100,
            d2=100 + content_height - 60,
            tf=main_settings['title_font'],
            mf=main_settings['menu_font'],
            bf=main_settings['button_font'],
            ih=item_height,
            by=button_y,
            bw=button_width,
            bp0=button_positions[0],
            bp1=button_positions[1],
            bp2=button_positions[2],
            bp3=button_positions[3],
            c1x=col1_x,
            c2x=col2_x,
            c3x=col3_x,
            c1w=col1_width,
            c2w=col2_width,
            c3w=col3_width,
            tc=UI_COLORS['title'],
            txt=UI_COLORS['text'],
            bc=UI_COLORS['background'],
            br=UI_COLORS['button_red'],
            bg=UI_COLORS['button_green'],
            byc=UI_COLORS['button_yellow'],
            bl=UI_COLORS['button_blue']
        )

        # Debug: save rendered skin
        try:
            with open('/tmp/skin_debug.txt', 'w') as f:
                f.write(self.skin)
            enhanced_log("Skin written to /tmp/skin_debug.txt")
        except Exception as e:
            enhanced_log("Error writing skin: {}".format(e))

        Screen.__init__(self, session)
        self.session = session
        self.subcategory_code = ""
        self.subcategory_name = ""
        self.webcams = []
        self.current_stream_url = None
        self.current_webcam_index = 0
        self.parent_category = None
        self.parser = WebcamParser()
        self.extractor = StreamExtractor()
        self["title"] = Label("SkyLine Webcams")
        self["description"] = Label("")
        self["status"] = Label(_("Initializing..."))
        self["webcam_list"] = MenuList([])
        self["countries_list"] = MenuList([])
        self["webcams_list"] = MenuList([])
        self["continents_title"] = Label("CONTINENTS")
        self["countries_title"] = Label("COUNTRIES")
        self["webcams_title"] = Label("WEBCAMS")
        self["main_title"] = Label("What to watch")
        self["main_list"] = MenuList([])
        self.video_playing = False
        self.current_window = 0
        self["key_red"] = Label("Exit")
        self["key_green"] = Label("Reload")
        self["key_yellow"] = Label("Info")
        self["key_blue"] = Label("Settings")
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions", "NumberActions"],
            {
                "ok": self.play_selected_webcam,
                "cancel": self.handle_cancel,
                "up": self.move_up,
                "down": self.move_down,
                "left": self.previous_webcam,
                "right": self.next_webcam,
                "red": self.close,
                "green": self.reload_webcams,
                "yellow": self.show_info,
                "blue": self.open_fullscreen_player,
                "1": self.jump_to_10_percent,
                "2": self.jump_to_20_percent,
                "3": self.jump_to_30_percent,
                "4": self.jump_to_40_percent,
                "5": self.jump_to_50_percent,
                "6": self.jump_to_60_percent,
                "7": self.jump_to_70_percent,
                "8": self.jump_to_80_percent,
                "9": self.jump_to_90_percent,
                "0": self.jump_to_start,
            }, -1
        )
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.layoutFinished)
        self.onClose.append(self.cleanup_resources)

    def layoutFinished(self):
        enhanced_log("Layout finished, starting webcam loading")
        self.setTitle(_("SkyLine Webcams - {}").format(self.subcategory_name))
        self.update_ui_visibility()
        self.load_webcams()

    def update_ui_visibility(self):
        if not self.subcategory_code:
            self["continents_title"].hide()
            self["countries_title"].hide()
            self["webcams_title"].hide()
            self["webcam_list"].hide()
            self["countries_list"].hide()
            self["webcams_list"].hide()
            self["main_title"].show()
            self["main_list"].show()
            self["key_blue"].setText("Settings")
            self["key_blue"].show()
        elif self.subcategory_code == "live":
            self["continents_title"].show()
            self["countries_title"].show()
            self["webcams_title"].show()
            self["webcam_list"].show()
            self["countries_list"].show()
            self["webcams_list"].show()
            self["main_title"].hide()
            self["main_list"].hide()
            self["key_blue"].hide()
            self.update_window_highlight()
        elif self.subcategory_code == "categories":
            self["continents_title"].setText("CATEGORY")
            self["continents_title"].show()
            self["countries_title"].hide()
            self["webcams_title"].setText("WEBCAMS")
            self["webcams_title"].show()
            self["webcam_list"].show()
            self["countries_list"].hide()
            self["webcams_list"].show()
            self["main_title"].hide()
            self["main_list"].hide()
            self["key_blue"].hide()
            if not hasattr(self, 'current_category_webcams') or not self.current_category_webcams:
                self.current_window = 0
            self.update_category_highlight()
        else:
            self["continents_title"].hide()
            self["countries_title"].hide()
            self["webcams_title"].hide()
            self["webcam_list"].show()
            self["countries_list"].hide()
            self["webcams_list"].hide()
            self["main_title"].hide()
            self["main_list"].hide()
            self["key_blue"].hide()

    def update_window_highlight(self):
        try:
            if self.subcategory_code == "live":
                if self.current_window == 0:
                    self["continents_title"].setText(">>> CONTINENTS <<<")
                    self["countries_title"].setText("COUNTRIES")
                    self["webcams_title"].setText("WEBCAMS")
                elif self.current_window == 1:
                    self["continents_title"].setText("CONTINENTS")
                    self["countries_title"].setText(">>> COUNTRIES <<<")
                    self["webcams_title"].setText("WEBCAMS")
                elif self.current_window == 2:
                    self["continents_title"].setText("CONTINENTS")
                    self["countries_title"].setText("COUNTRIES")
                    self["webcams_title"].setText(">>> WEBCAMS <<<")
        except Exception as e:
            enhanced_log("Error updating highlight: {}".format(e))

    def update_category_highlight(self):
        try:
            if self.subcategory_code == "categories":
                if self.current_window == 0:
                    self["continents_title"].setText(">>> CATEGORY <<<")
                    self["webcams_title"].setText("WEBCAMS")
                elif self.current_window == 1:
                    self["continents_title"].setText("CATEGORY")
                    self["webcams_title"].setText(">>> WEBCAMS <<<")
        except Exception as e:
            enhanced_log("Error updating category highlight: {}".format(e))

    def move_up(self):
        if not self.subcategory_code:
            current_list = self["main_list"].list
            if current_list and self["main_list"].getSelectionIndex() > 0:
                self["main_list"].up()
        elif self.subcategory_code == "live":
            if self.current_window == 0:
                current_list = self["webcam_list"].list
                if current_list and self["webcam_list"].getSelectionIndex() > 0:
                    self["webcam_list"].up()
                    self.update_preview()
            elif self.current_window == 1:
                current_list = self["countries_list"].list
                if current_list and self["countries_list"].getSelectionIndex() > 0:
                    self["countries_list"].up()
                    self.update_webcams_for_country()
            elif self.current_window == 2:
                current_list = self["webcams_list"].list
                if current_list and self["webcams_list"].getSelectionIndex() > 0:
                    self["webcams_list"].up()
        elif self.subcategory_code == "categories":
            if self.current_window == 0:
                current_list = self["webcam_list"].list
                if current_list and self["webcam_list"].getSelectionIndex() > 0:
                    self["webcam_list"].up()
                    self.update_webcams_for_selected_category()
            elif self.current_window == 1:
                current_list = self["webcams_list"].list
                if current_list and self["webcams_list"].getSelectionIndex() > 0:
                    self["webcams_list"].up()
        else:
            current_list = self["webcam_list"].list
            if current_list and self["webcam_list"].getSelectionIndex() > 0:
                self["webcam_list"].up()
                self.update_preview()

    def move_down(self):
        if not self.subcategory_code:
            current_list = self["main_list"].list
            if current_list and self["main_list"].getSelectionIndex() < len(current_list) - 1:
                self["main_list"].down()
        elif self.subcategory_code == "live":
            if self.current_window == 0:
                current_list = self["webcam_list"].list
                if current_list and self["webcam_list"].getSelectionIndex() < len(current_list) - 1:
                    self["webcam_list"].down()
                    self.update_preview()
            elif self.current_window == 1:
                current_list = self["countries_list"].list
                if current_list and self["countries_list"].getSelectionIndex() < len(current_list) - 1:
                    self["countries_list"].down()
                    self.update_webcams_for_country()
            elif self.current_window == 2:
                current_list = self["webcams_list"].list
                if current_list and self["webcams_list"].getSelectionIndex() < len(current_list) - 1:
                    self["webcams_list"].down()
        elif self.subcategory_code == "categories":
            if self.current_window == 0:
                current_list = self["webcam_list"].list
                if current_list and self["webcam_list"].getSelectionIndex() < len(current_list) - 1:
                    self["webcam_list"].down()
                    self.update_webcams_for_selected_category()
            elif self.current_window == 1:
                current_list = self["webcams_list"].list
                if current_list and self["webcams_list"].getSelectionIndex() < len(current_list) - 1:
                    self["webcams_list"].down()
        else:
            current_list = self["webcam_list"].list
            if current_list and self["webcam_list"].getSelectionIndex() < len(current_list) - 1:
                self["webcam_list"].down()
                self.update_preview()

    def previous_webcam(self):
        if self.subcategory_code == "live" and self.current_window > 0:
            self.current_window -= 1
            self.update_window_highlight()
        elif self.subcategory_code == "categories" and self.current_window > 0:
            self.current_window -= 1
            self.update_category_highlight()

    def next_webcam(self):
        if self.subcategory_code == "live" and self.current_window < 2:
            self.current_window += 1
            self.update_window_highlight()
        elif self.subcategory_code == "categories" and self.current_window < 1:
            self.current_window += 1
            self.update_category_highlight()

    def jump_to_percent(self, percent):
        if self.subcategory_code == "live":
            if self.current_window == 0:
                current_list = self["webcam_list"].list
                if current_list:
                    target_index = int((len(current_list) - 1) * percent / 100)
                    self["webcam_list"].moveToIndex(target_index)
                    self.update_preview()
            elif self.current_window == 1:
                current_list = self["countries_list"].list
                if current_list:
                    target_index = int((len(current_list) - 1) * percent / 100)
                    self["countries_list"].moveToIndex(target_index)
                    self.update_webcams_for_country()
            elif self.current_window == 2:
                current_list = self["webcams_list"].list
                if current_list:
                    target_index = int((len(current_list) - 1) * percent / 100)
                    self["webcams_list"].moveToIndex(target_index)
        elif self.subcategory_code == "categories":
            if self.current_window == 0:
                current_list = self["webcam_list"].list
                if current_list:
                    target_index = int((len(current_list) - 1) * percent / 100)
                    self["webcam_list"].moveToIndex(target_index)
                    self.update_webcams_for_selected_category()
            elif self.current_window == 1:
                current_list = self["webcams_list"].list
                if current_list:
                    target_index = int((len(current_list) - 1) * percent / 100)
                    self["webcams_list"].moveToIndex(target_index)

    def jump_to_10_percent(self):
        self.jump_to_percent(10)

    def jump_to_20_percent(self):
        self.jump_to_percent(20)

    def jump_to_30_percent(self):
        self.jump_to_percent(30)

    def jump_to_40_percent(self):
        self.jump_to_percent(40)

    def jump_to_50_percent(self):
        self.jump_to_percent(50)

    def jump_to_60_percent(self):
        self.jump_to_percent(60)

    def jump_to_70_percent(self):
        self.jump_to_percent(70)

    def jump_to_80_percent(self):
        self.jump_to_percent(80)

    def jump_to_90_percent(self):
        self.jump_to_percent(90)

    def jump_to_start(self):
        self.jump_to_percent(0)

    def update_preview(self):
        if self.webcams and self.subcategory_code == "live":
            current_index = self["webcam_list"].getSelectionIndex()
            if 0 <= current_index < len(self.webcams):
                selected_item = self.webcams[current_index]
                if selected_item.get('type') == 'continent':
                    self.load_countries_for_continent(selected_item)
        self.update_webcams_for_country()

    def load_countries_for_continent(self, continent_item):
        try:
            countries = self.parser.get_countries_by_continent(continent_item['continent_code'])
            country_names = [country['name'] for country in countries]
            self["countries_list"].setList(country_names)
            self.current_countries = countries
            self["description"].setText("Continent: {} - {} countries".format(continent_item['title'], len(countries)))
            self["webcams_list"].setList([])
        except Exception as e:
            self["countries_list"].setList([])
            self["description"].setText("Error loading countries: {}".format(str(e)))

    def update_webcams_for_country(self):
        if hasattr(self, 'current_countries') and self.current_countries:
            country_index = self["countries_list"].getSelectionIndex()
            if 0 <= country_index < len(self.current_countries):
                selected_country = self.current_countries[country_index]
                try:
                    webcams = self.parser.get_city_webcams(selected_country['url'])
                    webcam_names = [webcam['title'] for webcam in webcams]
                    self["webcams_list"].setList(webcam_names)
                    self.current_webcams = webcams
                    self["description"].setText("Country: {} - {} webcams".format(selected_country['name'], len(webcams)))
                except Exception as e:
                    self["webcams_list"].setList([])
                    self["description"].setText("Error loading webcams: {}".format(str(e)))

    def update_webcams_for_selected_category(self):
        if hasattr(self, 'current_categories') and self.current_categories:
            category_index = self["webcam_list"].getSelectionIndex()
            if 0 <= category_index < len(self.current_categories):
                selected_category = self.current_categories[category_index]
                try:
                    enhanced_log("Loading webcams for category: {}".format(selected_category['name']))
                    webcams = self.parser.get_webcams_by_url(selected_category['url'])
                    formatted_webcams = []
                    for webcam in webcams:
                        formatted_webcam = {
                            'title': webcam.get('title', 'Webcam'),
                            'subtitle': webcam.get('subtitle', ''),
                            'url': webcam.get('url', ''),
                            'image_url': webcam.get('image_url', ''),
                            'alt_text': webcam.get('alt_text', webcam.get('title', '')),
                            'category': selected_category['name']
                        }
                        formatted_webcams.append(formatted_webcam)
                    webcam_names = [webcam['title'] for webcam in formatted_webcams]
                    self["webcams_list"].setList(webcam_names)
                    self.current_category_webcams = formatted_webcams
                    self["description"].setText("Category: {} - {} webcams".format(selected_category['name'], len(formatted_webcams)))
                except Exception as e:
                    enhanced_log("Error loading category webcams: {}".format(e))
                    self["webcams_list"].setList([])
                    self["description"].setText("Error loading webcams: {}".format(str(e)))

    def load_webcams(self):
        try:
            self["status"].setText(_("Loading webcams..."))
            self.webcams = []

            if not self.subcategory_code:
                enhanced_log("Loading main menu")
                self.load_main_categories()
                return

            # Determine parent category for return
            if self.subcategory_code in ["live"]:
                self.parent_category = "live"
            elif self.subcategory_code in ["citta"]:
                self.parent_category = "citta"
            elif self.subcategory_code in ["categories", "category"]:
                self.parent_category = "categories"

            if self.subcategory_code == "live":
                enhanced_log("Loading Live Webcams")
                continents = self.parser.get_continents()
                enhanced_log("Found {} continents".format(len(continents)))
                for continent in continents:
                    continent_item = {
                        'title': continent['name'],
                        'subtitle': "Continent: {}".format(continent['name']),
                        'cover_image': '',
                        'url': continent['url'],
                        'alt_text': continent['name'],
                        'continent_code': continent['code'],
                        'parent_category': 'live',
                        'type': 'continent'
                    }
                    self.webcams.append(continent_item)

            elif self.subcategory_code == "citta":
                enhanced_log("Loading Cities")
                continents = self.parser.get_continents()
                enhanced_log("Found {} continents for cities".format(len(continents)))
                target_continent = None
                for continent in continents:
                    if continent['name'].lower() in ['europe', 'america', 'asia', 'africa', 'oceania']:
                        target_continent = continent
                        break
                if target_continent:
                    countries = self.parser.get_countries_by_continent(target_continent['url'])
                    for country in countries:
                        try:
                            city_webcams = self.parser.get_city_webcams(country['url'])
                            for webcam in city_webcams:
                                webcam['country'] = country['name']
                                webcam['continent'] = target_continent['name']
                                webcam['parent_category'] = 'citta'
                                self.webcams.append(webcam)
                        except Exception as e:
                            enhanced_log("Error loading webcams for {}: {}".format(country['name'], e))
                            continue

            elif self.subcategory_code == "categories":
                enhanced_log("Loading subcategories")
                if hasattr(self, 'current_countries'):
                    delattr(self, 'current_countries')
                if hasattr(self, 'current_webcams'):
                    delattr(self, 'current_webcams')
                if hasattr(self.parser, 'get_dropdown_categories'):
                    dropdown_categories = self.parser.get_dropdown_categories()
                else:
                    dropdown_categories = [
                        {'name': 'TOP Webcams', 'url': '{}/it/top-live-cams.html'.format(self.parser.BASE_URL)},
                        {'name': 'New Webcams', 'url': '{}/it/new-livecams.html'.format(self.parser.BASE_URL)},
                        {'name': 'Cities', 'url': '{}/it/live-cams-category/city-cams.html'.format(self.parser.BASE_URL)},
                        {'name': 'Beaches', 'url': '{}/it/live-cams-category/beach-cams.html'.format(self.parser.BASE_URL)},
                        {'name': 'Landscapes', 'url': '{}/it/live-cams-category/nature-mountain-cams.html'.format(self.parser.BASE_URL)},
                        {'name': 'Marinas', 'url': '{}/it/live-cams-category/seaport-cams.html'.format(self.parser.BASE_URL)},
                        {'name': 'UNESCO', 'url': '{}/it/live-cams-category/unesco-cams.html'.format(self.parser.BASE_URL)},
                        {'name': 'Ski Slopes', 'url': '{}/it/live-cams-category/ski-cams.html'.format(self.parser.BASE_URL)},
                        {'name': 'Animals', 'url': '{}/it/live-cams-category/animals-cams.html'.format(self.parser.BASE_URL)},
                        {'name': 'Volcanoes', 'url': '{}/it/live-cams-category/volcanoes-cams.html'.format(self.parser.BASE_URL)}
                    ]
                enhanced_log("Found {} subcategories".format(len(dropdown_categories)))
                self.current_categories = dropdown_categories
                for category in dropdown_categories:
                    category_item = {
                        'title': category['name'],
                        'subtitle': "Category: {}".format(category['name']),
                        'cover_image': '',
                        'url': category['url'],
                        'alt_text': category['name'],
                        'parent_category': 'categories',
                        'type': 'category'
                    }
                    self.webcams.append(category_item)
                self["webcams_list"].setList([])

            elif self.subcategory_code == "category":
                enhanced_log("Loading category from URL: {}".format(self.category_url))
                if hasattr(self, 'category_url') and self.category_url:
                    category_webcams = self.parser.get_webcams_by_url(self.category_url)
                    for webcam in category_webcams:
                        formatted_webcam = {
                            'title': webcam.get('title', 'Webcam'),
                            'subtitle': webcam.get('subtitle', ''),
                            'cover_image': webcam.get('image_url', ''),
                            'url': webcam.get('url', ''),
                            'alt_text': webcam.get('alt_text', webcam.get('title', '')),
                            'category': self.subcategory_name,
                            'parent_category': 'categories'
                        }
                        self.webcams.append(formatted_webcam)
                else:
                    enhanced_log("No category_url set for category mode")

            else:
                enhanced_log("Unsupported category: {}".format(self.subcategory_code))
                self["status"].setText(_("Unsupported category: {}").format(self.subcategory_code))
                return

            # Populate menu list
            menu_list = []
            for webcam in self.webcams:
                title = webcam.get('title', 'Unknown webcam')
                if 'country' in webcam:
                    title = title + " ({})".format(webcam['country'])
                elif 'category' in webcam:
                    title = title + " [{}]".format(webcam['category'])
                menu_list.append(title)

            self["webcam_list"].setList(menu_list)
            enhanced_log("Loading completed: {} webcams found".format(len(self.webcams)))
            self["status"].setText(_("Found {} webcams").format(len(self.webcams)))

            if len(self.webcams) > 0:
                self.update_preview()
            else:
                self["status"].setText(_("No webcams available in this category"))

        except Exception as e:
            self["status"].setText(_("Error loading webcams: {}").format(str(e)))
            enhanced_log("Error in load_webcams: {}".format(e))

    def load_main_categories(self):
        try:
            enhanced_log("Starting main categories parsing")
            categories = self.parser.get_categories()
            enhanced_log("Parser found {} categories".format(len(categories)))

            main_menu = []
            self.category_mapping = {}

            for category in categories:
                category_name = category['name']
                main_menu.append(category_name)
                self.category_mapping[category_name] = {
                    "name": category_name,
                    "url": category['url']
                }

            if len(main_menu) <= 1:
                enhanced_log("Using fallback menu")
                fallback_categories = ["Live Webcams", "Webcams by category"]
                for cat in fallback_categories:
                    if cat not in main_menu:
                        main_menu.append(cat)
                        if "live" in cat.lower():
                            url = "{}/it/".format(self.parser.BASE_URL)
                        else:
                            url = "{}/it/webcam/".format(self.parser.BASE_URL)
                        self.category_mapping[cat] = {"name": cat, "url": url}

            enhanced_log("Main menu created with {} items".format(len(main_menu)))
            self["main_list"].setList(main_menu)
            self["status"].setText(_("Select a category ({} available)").format(len(main_menu)))

        except Exception as e:
            enhanced_log("Error loading main categories: {}".format(e))
            fallback_menu = ["Live Webcams", "Webcams by category"]
            self.category_mapping = {
                "Live Webcams": {"name": "Live Webcams", "url": "{}/it/".format(self.parser.BASE_URL)},
                "Webcams by category": {"name": "Webcams by category", "url": "{}/it/webcam/".format(self.parser.BASE_URL)}
            }
            self["main_list"].setList(fallback_menu)
            self["status"].setText(_("Basic menu loaded"))

    def cleanup_resources(self):
        try:
            self.session.nav.stopService()
        except Exception as e:
            enhanced_log("Error while stopping service: {}".format(e))
        self.webcams = []
        self.current_stream_url = None
        if hasattr(self, 'current_countries'):
            delattr(self, 'current_countries')
        if hasattr(self, 'current_webcams'):
            delattr(self, 'current_webcams')
        if hasattr(self, 'current_categories'):
            delattr(self, 'current_categories')
        if hasattr(self, 'current_category_webcams'):
            delattr(self, 'current_category_webcams')
        if hasattr(self, 'parser') and self.parser is not None:
            self.parser = None
        if hasattr(self, 'extractor') and self.extractor is not None:
            self.extractor = None

    def play_selected_webcam(self):
        if not self.subcategory_code:
            self.select_category()
            return
        if self.subcategory_code == "live":
            if self.current_window == 2 and hasattr(self, 'current_webcams') and self.current_webcams:
                try:
                    webcam_index = self["webcams_list"].getSelectionIndex()
                    if 0 <= webcam_index < len(self.current_webcams):
                        selected_webcam = self.current_webcams[webcam_index]
                        stream_url = self.parser.get_stream_url(selected_webcam['url'])
                        if stream_url:
                            selected_webcam['stream_url'] = stream_url
                        enhanced_log("Starting player for webcam: {}".format(selected_webcam['title']))
                        self.start_video_playback(selected_webcam)
                except Exception as e:
                    enhanced_log("Error while opening player: {}".format(e))
                    self.session.open(MessageBox, _('Error opening player: {}').format(str(e)), MessageBox.TYPE_ERROR, timeout=5)
            return
        if self.subcategory_code == "categories":
            if self.current_window == 1 and hasattr(self, 'current_category_webcams') and self.current_category_webcams:
                try:
                    webcam_index = self["webcams_list"].getSelectionIndex()
                    if 0 <= webcam_index < len(self.current_category_webcams):
                        selected_webcam = self.current_category_webcams[webcam_index]
                        stream_url = self.parser.get_stream_url(selected_webcam['url'])
                        if stream_url:
                            selected_webcam['stream_url'] = stream_url
                        enhanced_log("Starting player for category webcam: {}".format(selected_webcam.get('title', 'N/A')))
                        self.start_video_playback(selected_webcam)
                except Exception as e:
                    enhanced_log("Error while opening category player: {}".format(e))
                    self.session.open(MessageBox, _('Error opening player: {}').format(str(e)), MessageBox.TYPE_ERROR, timeout=5)
            return
        if self.webcams:
            try:
                current_index = self["webcam_list"].getSelectionIndex()
                if 0 <= current_index < len(self.webcams):
                    selected_item = self.webcams[current_index]
                    self.current_webcam_index = current_index
                else:
                    return
                if selected_item.get('type') == 'continent':
                    self.show_countries_for_continent(selected_item)
                    return
                if selected_item.get('type') == 'category':
                    self.show_webcams_for_category(selected_item)
                    return
                self.session.open(SLwebcamsPlayer, selected_item, self.webcams, current_index, self.subcategory_code, self.subcategory_name)
            except Exception as e:
                enhanced_log("Error while opening player: {}".format(e))
                self.session.open(MessageBox, _('Error opening player: {}').format(str(e)), MessageBox.TYPE_ERROR, timeout=5)

    def select_category(self):
        try:
            current_index = self["main_list"].getSelectionIndex()
            menu_list = self["main_list"].list
            if 0 <= current_index < len(menu_list):
                selected_item = menu_list[current_index]
                enhanced_log("Selected category: {}".format(selected_item))
                if selected_item in self.category_mapping:
                    data = self.category_mapping[selected_item]
                    if "live" in selected_item.lower():
                        self.subcategory_code = "live"
                    else:
                        self.subcategory_code = "categories"
                    self.subcategory_name = data['name']
                    self.category_url = data['url']
                else:
                    if "live" in selected_item.lower():
                        self.subcategory_code = "live"
                    else:
                        self.subcategory_code = "categories"
                    self.subcategory_name = selected_item
                    self.category_url = "{}/it/".format(self.parser.BASE_URL)
                enhanced_log("Loading category: {} with code: {}".format(self.subcategory_name, self.subcategory_code))
                self.load_webcams()
                self.update_ui_visibility()
        except Exception as e:
            enhanced_log("Error selecting category: {}".format(e))

    def reload_webcams(self):
        enhanced_log("Reload webcams requested")
        if not self.subcategory_code:
            self.load_main_categories()
        else:
            self.load_webcams()

    def show_info(self):
        enhanced_log("Info requested")
        if not self.subcategory_code:
            info_text = "Plugin to view webcams from skylinewebcams.com"
            self.session.open(MessageBox, info_text, MessageBox.TYPE_INFO, timeout=5)
        else:
            info_text = "Quick navigation: Keys 1-9 jump to 10%-90% of list, 0 to start"
            self.session.open(MessageBox, info_text, MessageBox.TYPE_INFO, timeout=8)

    def show_countries_for_continent(self, continent_item):
        try:
            enhanced_log("Loading countries for continent: {}".format(continent_item['title']))
            countries = self.parser.get_countries_by_continent(continent_item['continent_code'])
            enhanced_log("Found {} countries".format(len(countries)))
            self.webcams = []
            for country in countries:
                country_item = {
                    'title': country['name'],
                    'subtitle': "Country: {}".format(country['name']),
                    'cover_image': '',
                    'url': country['url'],
                    'alt_text': country['name'],
                    'parent_category': 'live',
                    'type': 'country',
                    'continent': continent_item['title']
                }
                self.webcams.append(country_item)
            menu_list = [country['title'] for country in countries]
            self["webcam_list"].setList(menu_list)
            self["status"].setText(_("Found {} countries in {}").format(len(countries), continent_item['title']))
        except Exception as e:
            enhanced_log("Error loading countries: {}".format(e))
            self.session.open(MessageBox, _('Error loading countries: {}').format(str(e)), MessageBox.TYPE_ERROR, timeout=5)

    def start_video_playback(self, webcam):
        try:
            if 'stream_url' in webcam and webcam['stream_url']:
                stream_url = webcam['stream_url']
            else:
                stream_url = self.parser.get_stream_url(webcam['url'])
            if stream_url:
                enhanced_log("Starting transparent playback: {}".format(stream_url))
                service_ref = eServiceReference(4097, 0, stream_url)
                self.session.nav.playService(service_ref)
                self.video_playing = True
                self.make_transparent()
            else:
                enhanced_log("Stream not available for: {}".format(webcam.get('title', 'N/A')))
                self.session.open(MessageBox, "Stream not available for this webcam", MessageBox.TYPE_INFO, timeout=3)
        except Exception as e:
            enhanced_log("Webcam playback error: {}".format(e))
            self.session.open(MessageBox, "Playback error: {}".format(str(e)), MessageBox.TYPE_ERROR, timeout=5)

    def make_transparent(self):
        try:
            widgets_to_hide = ['title', 'continents_title', 'countries_title', 'webcams_title',
                               'webcam_list', 'countries_list', 'webcams_list', 'description', 'status',
                               'key_red', 'key_green', 'key_yellow', 'key_blue']
            for widget_name in widgets_to_hide:
                if widget_name in self:
                    self[widget_name].hide()
            self.instance.setTransparent(1)
            enhanced_log("Plugin made transparent")
        except Exception as e:
            enhanced_log("Error making transparent: {}".format(e))

    def make_visible(self):
        try:
            base_widgets = ['title', 'description', 'status', 'key_red', 'key_green', 'key_yellow', 'key_blue']
            for widget_name in base_widgets:
                if widget_name in self:
                    self[widget_name].show()
            self.instance.setTransparent(0)
            if self.subcategory_code == "categories" and hasattr(self, 'current_category_webcams') and self.current_category_webcams:
                self.current_window = 1
            self.update_ui_visibility()
            enhanced_log("Plugin restored")
        except Exception as e:
            enhanced_log("Error restoring visibility: {}".format(e))

    def handle_cancel(self):
        if self.video_playing:
            self.session.nav.stopService()
            self.session.nav.playService(self.srefInit)
            self.srefInit = None
            self.video_playing = False
            self.make_visible()
            enhanced_log("Video stopped, service restored, plugin visible")
        elif self.subcategory_code:
            self.subcategory_code = ""
            self.subcategory_name = ""
            self.current_window = 0
            if hasattr(self, 'current_countries'):
                delattr(self, 'current_countries')
            if hasattr(self, 'current_webcams'):
                delattr(self, 'current_webcams')
            if hasattr(self, 'current_categories'):
                delattr(self, 'current_categories')
            if hasattr(self, 'current_category_webcams'):
                delattr(self, 'current_category_webcams')
            self.load_webcams()
            self.update_ui_visibility()
            enhanced_log("Returned to main menu")
        else:
            self.session.nav.playService(self.srefInit)
            self.close()

    def show_webcams_for_category(self, category_item):
        try:
            category_name = category_item['title']
            category_url = category_item['url']
            enhanced_log("Loading webcams for category: {}".format(category_name))
            self.subcategory_code = "category"
            self.subcategory_name = category_name
            self.category_url = category_url
            self.load_webcams()
            self.update_ui_visibility()
        except Exception as e:
            enhanced_log("Error loading category: {}".format(e))
            self.session.open(MessageBox, _('Error loading category: {}').format(str(e)), MessageBox.TYPE_ERROR, timeout=5)

    def open_fullscreen_player(self):
        enhanced_log("Settings requested")
        if not self.subcategory_code:
            try:
                self.session.open(SLwebcamsSettings)
            except Exception as e:
                enhanced_log("Error opening settings: {}".format(e))
                self.session.open(MessageBox, "Settings not available", MessageBox.TYPE_INFO, timeout=5)


class SLwebcamsPlayer(Screen):
    CONTROLS_HIDE_TIMEOUT = 5000

    def __init__(self, session, current_webcam, webcams_list, current_index, category_code, category_name, fullscreen=False):
        enhanced_log("Initializing player - Webcam: {}, Fullscreen: {}".format(current_webcam.get('title', 'N/A'), fullscreen))
        try:
            enhanced_log("Getting UI settings...")
            ui_settings = get_ui_settings()
            if 'player' in ui_settings:
                player_settings = ui_settings['player']
            else:
                enhanced_log("Key 'player' not found, using fallback settings")
                player_settings = {'position': '0,0', 'size': '1920,1080'}
            enhanced_log("UI settings obtained successfully")
        except Exception as e:
            enhanced_log("Error getting UI settings: {}".format(e))
            player_settings = {'position': '0,0', 'size': '1920,1080'}
            enhanced_log("Using complete fallback settings")

        if fullscreen:
            desktop_size = getDesktop(0).size()
            screen_width = desktop_size.width()
            screen_height = desktop_size.height()
            self.skin = """
            <screen position="0,0" size="{sw},{sh}" title="SkyLine Webcams Player" flags="wfNoBorder" backgroundColor="#000000">
                <eVideoPlayer name="video" position="0,0" size="{sw},{sh}" backgroundColor="#000000" />
                <widget name="info" position="50,50" size="800,40" font="Regular;32" foregroundColor="white" backgroundColor="#80000000" transparent="1" />
                <widget name="controls" position="50,{sh2}" size="800,30" font="Regular;24" foregroundColor="white" backgroundColor="#80000000" transparent="1" />
            </screen>
            """.format(sw=screen_width, sh=screen_height, sh2=screen_height - 80)
        else:
            width = int(player_settings['size'].split(',')[0])
            height = int(player_settings['size'].split(',')[1])
            self.skin = """
            <screen position="{pos}" size="{size}" title="SkyLine Webcams Player" backgroundColor="#000000">
                <eVideoPlayer name="video" position="0,0" size="{w},{h}" backgroundColor="#000000" />
                <widget name="info" position="50,30" size="{w2},40" font="Regular;32" foregroundColor="white" backgroundColor="#80000000" transparent="1" />
                <widget name="controls" position="50,{h2}" size="{w2},30" font="Regular;24" foregroundColor="white" backgroundColor="#80000000" transparent="1" />
                <widget name="red_label" position="50,{h3}" size="150,30" font="Regular;20" foregroundColor="red" backgroundColor="#80000000" transparent="1" />
                <widget name="green_label" position="220,{h3}" size="150,30" font="Regular;20" foregroundColor="green" backgroundColor="#80000000" transparent="1" />
                <widget name="yellow_label" position="390,{h3}" size="150,30" font="Regular;20" foregroundColor="yellow" backgroundColor="#80000000" transparent="1" />
                <widget name="blue_label" position="560,{h3}" size="150,30" font="Regular;20" foregroundColor="cyan" backgroundColor="#80000000" transparent="1" />
            </screen>
            """.format(
                pos=player_settings['position'],
                size=player_settings['size'],
                w=width,
                h=height,
                w2=width - 100,
                h2=height - 100,
                h3=height - 60
            )

        try:
            enhanced_log("Initializing Screen...")
            Screen.__init__(self, session)
            enhanced_log("Screen initialized successfully")
            enhanced_log("Setting instance variables...")
            self.session = session
            self.current_webcam = current_webcam
            self.webcams_list = webcams_list
            self.current_index = current_index
            self.category_code = category_code
            self.category_name = category_name
            self.fullscreen = fullscreen
            self.extractor = StreamExtractor()
            self.current_stream_url = None
            enhanced_log("Instance variables set")
            enhanced_log("Initializing UI components...")
            self["info"] = Label("")
            self["controls"] = Label("")
            enhanced_log("UI components initialized")
        except Exception as e:
            enhanced_log("Error during Screen or component initialization: {}".format(e))
            raise

        try:
            if not fullscreen:
                enhanced_log("Initializing button labels...")
                self["red_label"] = Label("Exit")
                self["green_label"] = Label("Previous")
                self["yellow_label"] = Label("Next")
                self["blue_label"] = Label("Fullscreen")
                enhanced_log("Button labels initialized")
            enhanced_log("Initializing ActionMap...")
            self["actions"] = ActionMap(
                ["OkCancelActions", "ColorActions", "DirectionActions"],
                {
                    "ok": self.toggle_controls,
                    "cancel": self.close_player,
                    "red": self.close_player,
                    "green": self.previous_webcam,
                    "yellow": self.next_webcam,
                    "blue": self.toggle_fullscreen,
                    "left": self.previous_webcam,
                    "right": self.next_webcam,
                    "up": self.previous_webcam,
                    "down": self.next_webcam,
                }, -1
            )
            enhanced_log("ActionMap initialized")
            self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
            enhanced_log("Setting callbacks...")
            self.onLayoutFinish.append(self.play_current_webcam)
            enhanced_log("Callbacks set")
            enhanced_log("Controls timer removed - controls always visible")
            enhanced_log("Player initialization completed successfully")
        except Exception as e:
            enhanced_log("Error during final player initialization: {}".format(e))
            raise

    def play_current_webcam(self):
        try:
            webcam_title = self.current_webcam.get('title', 'Unknown webcam')
            if 'country' in self.current_webcam:
                webcam_title = webcam_title + " ({})".format(self.current_webcam['country'])
            enhanced_log("Playing webcam: {}".format(webcam_title))
            self["info"].setText(webcam_title)
            self.update_controls_text()
            if 'stream_url' in self.current_webcam:
                stream_url = self.current_webcam['stream_url']
                enhanced_log("Using pre-built stream URL: {}".format(stream_url))
            else:
                from .webcam_parser import WebcamParser
                parser = WebcamParser()
                enhanced_log("Extracting stream URL from: {}".format(self.current_webcam['url']))
                stream_url = parser.get_stream_url(self.current_webcam['url'])
                enhanced_log("Extracted stream URL: {}".format(stream_url))
            self.current_stream_url = stream_url
            if stream_url:
                enhanced_log("Starting playback service for: {}".format(stream_url))
                service_ref = eServiceReference(4097, 0, stream_url)
                self.session.nav.playService(service_ref)
            else:
                enhanced_log("Stream URL not available")
                self.session.open(MessageBox, _('Stream not available for this webcam'), MessageBox.TYPE_INFO, timeout=5)
        except Exception as e:
            enhanced_log("Error during playback: {}".format(e))
            self.session.open(MessageBox, _('Error during playback: {}').format(str(e)), MessageBox.TYPE_ERROR, timeout=5)

    def update_controls_text(self):
        controls_text = "Webcam {} of {}".format(self.current_index + 1, len(self.webcams_list))
        if 'category' in self.current_webcam:
            controls_text = controls_text + " | Category: {}".format(self.current_webcam['category'])
        elif 'country' in self.current_webcam:
            controls_text = controls_text + " | Country: {}".format(self.current_webcam['country'])
        self["controls"].setText(controls_text)

    def toggle_controls(self):
        pass

    def previous_webcam(self):
        if self.current_index > 0 and self.webcams_list:
            self.current_index -= 1
            if 0 <= self.current_index < len(self.webcams_list):
                self.current_webcam = self.webcams_list[self.current_index]
                self.play_current_webcam()

    def next_webcam(self):
        if self.webcams_list and self.current_index < len(self.webcams_list) - 1:
            self.current_index += 1
            if 0 <= self.current_index < len(self.webcams_list):
                self.current_webcam = self.webcams_list[self.current_index]
                self.play_current_webcam()

    def toggle_fullscreen(self):
        if not self.fullscreen:
            self.close()
            self.session.open(SLwebcamsPlayer, self.current_webcam, self.webcams_list, self.current_index, self.category_code, self.category_name, fullscreen=True)

    def close_player(self):
        self.stop_stream()
        self.close()

    def stop_stream(self):
        self.session.nav.stopService()
        self.session.nav.playService(self.srefInit)
        self.srefInit = None


class SLwebcamsFullscreen(Screen):
    def __init__(self, session, service_ref):
        ui_settings = get_ui_settings()
        fullscreen_settings = ui_settings.get('fullscreen', {})
        self.skin = """
        <screen position="0,0" size="1920,1080" title="SkyLine Webcams Fullscreen" flags="wfNoBorder" backgroundColor="#000000">
            <eVideoPlayer name="video" position="0,0" size="1920,1080" backgroundColor="#000000" />
        </screen>
        """
        if fullscreen_settings and 'position' in fullscreen_settings and 'size' in fullscreen_settings:
            self.skin = """
            <screen position="{pos}" size="{size}" title="SkyLine Webcams Fullscreen" flags="wfNoBorder" backgroundColor="{bc}">
                <eVideoPlayer name="video" position="0,0" size="{size}" backgroundColor="{bc}" />
            </screen>
            """.format(
                pos=fullscreen_settings['position'],
                size=fullscreen_settings['size'],
                bc=UI_COLORS['background']
            )
        Screen.__init__(self, session)
        self.session = session
        self.service_ref = service_ref
        self["video"] = Label("")
        self["actions"] = ActionMap(["OkCancelActions"], {"cancel": self.close}, -1)
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.play_stream)
        self.onClose.append(self.stop_stream)

    def play_stream(self):
        try:
            self.session.nav.playService(self.service_ref)
        except Exception as e:
            self.session.open(MessageBox, _('Error during fullscreen playback: {}').format(str(e)), MessageBox.TYPE_ERROR, timeout=5)
            self.close()

    def stop_stream(self):
        self.session.nav.stopService()
        self.session.nav.playService(self.srefInit)
        self.srefInit = None


def main(session):
    SLLogger.initialize()
    enhanced_log("Plugin SLwebcams started")
    enhanced_log("Opening main screen")
    session.open(SLwebcamsMain)


def Plugins(**kwargs):
    return [
        PluginDescriptor(
            name="SkyLine Webcams",
            description=_("Watch webcams from skylinewebcams.com"),
            where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
            icon="icon.svg",
            fnc=main
        )
    ]
