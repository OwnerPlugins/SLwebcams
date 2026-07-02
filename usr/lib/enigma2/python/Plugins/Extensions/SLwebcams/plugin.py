#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
    print(f"[SLwebcams] Error adding path: {e}")

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
    enhanced_log(f"Error reloading webcam_parser module: {e}")


class SLwebcamsMain(Screen):
    def __init__(self, session):
        enhanced_log("Initializing SLwebcamsMain")
        ui_settings = get_ui_settings()
        main_settings = ui_settings['main_screen']
        item_height = main_settings.get('item_height', 40)   # default 40

        # Calculate dimensions and positions
        width = int(main_settings['size'].split(',')[0])
        height = int(main_settings['size'].split(',')[1])
        content_width = width - 60
        content_height = height - 200
        button_y = height - 80
        button_width = 260
        # mod lululla
        button_positions = [i * content_width // 4 + 30 for i in range(4)]

        # Calculate three-column layout with adaptive widths
        total_width = content_width
        col1_width = int(total_width * 0.20)   # 20% for continents/categories
        col2_width = int(total_width * 0.25)   # 25% for countries
        col3_width = total_width - col1_width - col2_width - 60  # remaining for webcams
        col1_x = 30
        col2_x = col1_x + col1_width + 20
        col3_x = col2_x + col2_width + 20

        # Ensure minimum widths are respected
        if col1_width < 180:
            col1_width = 180
        if col2_width < 200:
            col2_width = 200
        if col3_width < 300:
            col3_width = 300

        # Skin with itemHeight
        self.skin = f"""
        <screen position="{main_settings['position']}" size="{main_settings['size']}" title="SkyLine Webcams" flags="wfNoBorder">
            <widget name="title" position="30,30" size="{content_width},50" font="{main_settings['title_font']}" halign="center" valign="center" foregroundColor="{UI_COLORS['title']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="continents_title" position="{col1_x},85" size="{col1_width},15" font="Regular;16" halign="center" valign="center" foregroundColor="{UI_COLORS['title']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="countries_title" position="{col2_x},85" size="{col2_width},15" font="Regular;16" halign="center" valign="center" foregroundColor="{UI_COLORS['text']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="webcams_title" position="{col3_x},85" size="{col3_width},15" font="Regular;16" halign="center" valign="center" foregroundColor="{UI_COLORS['text']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="main_title" position="30,85" size="{content_width},25" font="Regular;20" halign="center" valign="center" foregroundColor="{UI_COLORS['title']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />

            <widget name="webcam_list" position="{col1_x},100" size="{col1_width},{content_height - 100}" font="{main_settings['menu_font']}" itemHeight="{item_height}" scrollbarMode="showOnDemand" foregroundColor="{UI_COLORS['text']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="countries_list" position="{col2_x},100" size="{col2_width},{content_height - 100}" font="{main_settings['menu_font']}" itemHeight="{item_height}" scrollbarMode="showOnDemand" foregroundColor="{UI_COLORS['text']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="webcams_list" position="{col3_x},100" size="{col3_width},{content_height - 100}" font="{main_settings['menu_font']}" itemHeight="{item_height}" scrollbarMode="showOnDemand" foregroundColor="{UI_COLORS['text']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="main_list" position="30,120" size="{content_width},{content_height - 120}" font="{main_settings['menu_font']}" itemHeight="{item_height}" scrollbarMode="showOnDemand" foregroundColor="{UI_COLORS['text']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />

            <widget name="description" position="30,{100 + content_height - 100}" size="{content_width},40" font="Regular;18" foregroundColor="{UI_COLORS['text']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="status" position="30,{100 + content_height - 60}" size="{content_width},35" font="Regular;24" foregroundColor="{UI_COLORS['text']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="key_red" position="{button_positions[0]},{button_y}" size="{button_width},30" font="{main_settings['button_font']}" halign="center" valign="center" foregroundColor="{UI_COLORS['button_red']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="key_green" position="{button_positions[1]},{button_y}" size="{button_width},30" font="{main_settings['button_font']}" halign="center" valign="center" foregroundColor="{UI_COLORS['button_green']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="key_yellow" position="{button_positions[2]},{button_y}" size="{button_width},30" font="{main_settings['button_font']}" halign="center" valign="center" foregroundColor="{UI_COLORS['button_yellow']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
            <widget name="key_blue" position="{button_positions[3]},{button_y}" size="{button_width},30" font="{main_settings['button_font']}" halign="center" valign="center" foregroundColor="{UI_COLORS['button_blue']}" backgroundColor="{UI_COLORS['background']}" transparent="1" />
        </screen>
        """
        # Debug: write skin to /tmp for inspection
        try:
            with open('/tmp/skin_debug.txt', 'w') as f:
                f.write(self.skin)
            enhanced_log("Skin written to /tmp/skin_debug.txt")
        except Exception as e:
            enhanced_log(f"Error writing skin: {e}")

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
        self.current_window = 0  # 0=continents, 1=countries, 2=webcams
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
        self.setTitle(_("SkyLine Webcams - %s") % self.subcategory_name)
        self.update_ui_visibility()
        self.load_webcams()

    def update_ui_visibility(self):
        """Update UI element visibility based on current mode"""
        if not self.subcategory_code:  # Main menu
            # Hide three columns, show main list
            self["continents_title"].hide()
            self["countries_title"].hide()
            self["webcams_title"].hide()
            self["webcam_list"].hide()
            self["countries_list"].hide()
            self["webcams_list"].hide()
            self["main_title"].show()
            self["main_list"].show()
            # In main menu, blue button opens settings
            self["key_blue"].setText("Settings")
            self["key_blue"].show()
        elif self.subcategory_code == "live":
            # Show three columns, hide main list
            self["continents_title"].show()
            self["countries_title"].show()
            self["webcams_title"].show()
            self["webcam_list"].show()
            self["countries_list"].show()
            self["webcams_list"].show()
            self["main_title"].hide()
            self["main_list"].hide()
            # Hide blue button in webcam views
            self["key_blue"].hide()
            self.update_window_highlight()
        elif self.subcategory_code == "categories":
            # For categories, show 2 columns: Category and Webcam
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
            # Hide blue button in webcam views
            self["key_blue"].hide()
            # Keep webcam window active if webcams are loaded
            if not hasattr(self, 'current_category_webcams') or not self.current_category_webcams:
                self.current_window = 0  # Start from first column only if no webcams

            self.update_category_highlight()
        else:
            # For specific subcategories, show only webcam list
            self["continents_title"].hide()
            self["countries_title"].hide()
            self["webcams_title"].hide()
            self["webcam_list"].show()
            self["countries_list"].hide()
            self["webcams_list"].hide()
            self["main_title"].hide()
            self["main_list"].hide()
            # Hide blue button in webcam views
            self["key_blue"].hide()

    def update_window_highlight(self):
        """Update highlighting of the active window title"""
        try:
            if self.subcategory_code == "live":
                # Update texts with visual indicators
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
            enhanced_log(f"Error updating highlight: {e}")

    def update_category_highlight(self):
        """Update highlighting for category mode (2 columns)"""
        try:
            if self.subcategory_code == "categories":
                if self.current_window == 0:
                    self["continents_title"].setText(">>> CATEGORY <<<")
                    self["webcams_title"].setText("WEBCAMS")
                elif self.current_window == 1:
                    self["continents_title"].setText("CATEGORY")
                    self["webcams_title"].setText(">>> WEBCAMS <<<")
        except Exception as e:
            enhanced_log(f"Error updating category highlight: {e}")

    def move_up(self):
        if not self.subcategory_code:  # Main menu
            current_list = self["main_list"].list
            if current_list and self["main_list"].getSelectionIndex() > 0:
                self["main_list"].up()
        elif self.subcategory_code == "live":
            if self.current_window == 0:  # Continents
                current_list = self["webcam_list"].list
                if current_list and self["webcam_list"].getSelectionIndex() > 0:
                    self["webcam_list"].up()
                    self.update_preview()
            elif self.current_window == 1:  # Countries
                current_list = self["countries_list"].list
                if current_list and self["countries_list"].getSelectionIndex() > 0:
                    self["countries_list"].up()
                    self.update_webcams_for_country()
            elif self.current_window == 2:  # Webcams
                current_list = self["webcams_list"].list
                if current_list and self["webcams_list"].getSelectionIndex() > 0:
                    self["webcams_list"].up()
        elif self.subcategory_code == "categories":
            if self.current_window == 0:  # Category
                current_list = self["webcam_list"].list
                if current_list and self["webcam_list"].getSelectionIndex() > 0:
                    self["webcam_list"].up()
                    self.update_webcams_for_selected_category()
            elif self.current_window == 1:  # Webcams
                current_list = self["webcams_list"].list
                if current_list and self["webcams_list"].getSelectionIndex() > 0:
                    self["webcams_list"].up()
        else:
            current_list = self["webcam_list"].list
            if current_list and self["webcam_list"].getSelectionIndex() > 0:
                self["webcam_list"].up()
                self.update_preview()

    def move_down(self):
        if not self.subcategory_code:  # Main menu
            current_list = self["main_list"].list
            if current_list and self["main_list"].getSelectionIndex() < len(current_list) - 1:
                self["main_list"].down()
        elif self.subcategory_code == "live":
            if self.current_window == 0:  # Continents
                current_list = self["webcam_list"].list
                if current_list and self["webcam_list"].getSelectionIndex() < len(current_list) - 1:
                    self["webcam_list"].down()
                    self.update_preview()
            elif self.current_window == 1:  # Countries
                current_list = self["countries_list"].list
                if current_list and self["countries_list"].getSelectionIndex() < len(current_list) - 1:
                    self["countries_list"].down()
                    self.update_webcams_for_country()
            elif self.current_window == 2:  # Webcams
                current_list = self["webcams_list"].list
                if current_list and self["webcams_list"].getSelectionIndex() < len(current_list) - 1:
                    self["webcams_list"].down()
        elif self.subcategory_code == "categories":
            if self.current_window == 0:  # Category
                current_list = self["webcam_list"].list
                if current_list and self["webcam_list"].getSelectionIndex() < len(current_list) - 1:
                    self["webcam_list"].down()
                    self.update_webcams_for_selected_category()
            elif self.current_window == 1:  # Webcams
                current_list = self["webcams_list"].list
                if current_list and self["webcams_list"].getSelectionIndex() < len(current_list) - 1:
                    self["webcams_list"].down()
        else:
            current_list = self["webcam_list"].list
            if current_list and self["webcam_list"].getSelectionIndex() < len(current_list) - 1:
                self["webcam_list"].down()
                self.update_preview()

    def previous_webcam(self):
        # Move left between windows
        if self.subcategory_code == "live" and self.current_window > 0:
            self.current_window -= 1
            self.update_window_highlight()
        elif self.subcategory_code == "categories" and self.current_window > 0:
            self.current_window -= 1
            self.update_category_highlight()

    def next_webcam(self):
        # Move right between windows
        if self.subcategory_code == "live" and self.current_window < 2:
            self.current_window += 1
            self.update_window_highlight()
        elif self.subcategory_code == "categories" and self.current_window < 1:
            self.current_window += 1
            self.update_category_highlight()

    def jump_to_percent(self, percent):
        """Jump to a specific percentage of the active list"""
        if self.subcategory_code == "live":
            if self.current_window == 0:  # Continents
                current_list = self["webcam_list"].list
                if current_list:
                    target_index = int((len(current_list) - 1) * percent / 100)
                    self["webcam_list"].moveToIndex(target_index)
                    self.update_preview()
            elif self.current_window == 1:  # Countries
                current_list = self["countries_list"].list
                if current_list:
                    target_index = int((len(current_list) - 1) * percent / 100)
                    self["countries_list"].moveToIndex(target_index)
                    self.update_webcams_for_country()
            elif self.current_window == 2:  # Webcams
                current_list = self["webcams_list"].list
                if current_list:
                    target_index = int((len(current_list) - 1) * percent / 100)
                    self["webcams_list"].moveToIndex(target_index)
        elif self.subcategory_code == "categories":
            if self.current_window == 0:  # Category
                current_list = self["webcam_list"].list
                if current_list:
                    target_index = int((len(current_list) - 1) * percent / 100)
                    self["webcam_list"].moveToIndex(target_index)
                    self.update_webcams_for_selected_category()
            elif self.current_window == 1:  # Webcams
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
        """Load countries for the selected continent"""
        try:
            countries = self.parser.get_countries_by_continent(continent_item['continent_code'])
            country_names = [country['name'] for country in countries]
            self["countries_list"].setList(country_names)
            self.current_countries = countries
            self["description"].setText(f"Continent: {continent_item['title']} - {len(countries)} countries")
            self["webcams_list"].setList([])

        except Exception as e:
            self["countries_list"].setList([])
            self["description"].setText(f"Error loading countries: {str(e)}")

    def update_webcams_for_country(self):
        """Update webcams when a country is selected"""
        if hasattr(self, 'current_countries') and self.current_countries:
            country_index = self["countries_list"].getSelectionIndex()
            if 0 <= country_index < len(self.current_countries):
                selected_country = self.current_countries[country_index]
                try:
                    webcams = self.parser.get_city_webcams(selected_country['url'])
                    webcam_names = [webcam['title'] for webcam in webcams]
                    self["webcams_list"].setList(webcam_names)
                    self.current_webcams = webcams
                    self["description"].setText(f"Country: {selected_country['name']} - {len(webcams)} webcams")
                except Exception as e:
                    self["webcams_list"].setList([])
                    self["description"].setText(f"Error loading webcams: {str(e)}")

    def update_webcams_for_selected_category(self):
        """Update webcams when a category is selected"""
        if hasattr(self, 'current_categories') and self.current_categories:
            category_index = self["webcam_list"].getSelectionIndex()
            if 0 <= category_index < len(self.current_categories):
                selected_category = self.current_categories[category_index]
                try:
                    enhanced_log(f"Loading webcams for category: {selected_category['name']}")
                    webcams = self.parser.get_webcams_by_url(selected_category['url'])

                    # Convert to standard format if needed
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
                    self["description"].setText(f"Category: {selected_category['name']} - {len(formatted_webcams)} webcams")
                except Exception as e:
                    enhanced_log(f"Error loading category webcams: {e}")
                    self["webcams_list"].setList([])
                    self["description"].setText(f"Error loading webcams: {str(e)}")

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
            elif self.subcategory_code in ["top", "nuove", "spiagge", "paesaggi", "marine", "unesco", "sci", "animali", "vulcani", "laghi", "web"]:
                self.parent_category = "categories"

            if self.subcategory_code == "live":
                # Live Webcams - show continents
                enhanced_log("Loading Live Webcams")

                # Get all continents
                continents = self.parser.get_continents()
                enhanced_log(f"Found {len(continents)} continents")

                # Convert continents to webcam format for display
                for continent in continents:
                    continent_item = {
                        'title': continent['name'],
                        'subtitle': f"Continent: {continent['name']}",
                        'cover_image': '',
                        'url': continent['url'],
                        'alt_text': continent['name'],
                        'continent_code': continent['code'],
                        'parent_category': 'live',
                        'type': 'continent'
                    }
                    self.webcams.append(continent_item)

            elif self.subcategory_code == "citta":
                # Cities - use new methods
                enhanced_log("Loading Cities")

                # Get all continents
                continents = self.parser.get_continents()
                enhanced_log(f"Found {len(continents)} continents for cities")

                # Find a specific continent (e.g., Europe, America)
                target_continent = None
                for continent in continents:
                    if continent['name'].lower() in ['europe', 'america', 'asia', 'africa', 'oceania']:
                        target_continent = continent
                        break

                if target_continent:
                    # Get countries of the continent
                    countries = self.parser.get_countries_by_continent(target_continent['url'])

                    # For each country, get city webcams
                    for country in countries:
                        try:
                            city_webcams = self.parser.get_city_webcams(country['url'])
                            for webcam in city_webcams:
                                # Add country information
                                webcam['country'] = country['name']
                                webcam['continent'] = target_continent['name']
                                webcam['parent_category'] = 'citta'
                                self.webcams.append(webcam)
                        except Exception as e:
                            enhanced_log(f"Error loading webcams for {country['name']}: {e}")
                            continue

            elif self.subcategory_code == "categories":
                # Category webcams - show subcategories
                enhanced_log("Loading subcategories")

                # Clear previous state to avoid unwanted searches
                if hasattr(self, 'current_countries'):
                    delattr(self, 'current_countries')
                if hasattr(self, 'current_webcams'):
                    delattr(self, 'current_webcams')

                # Get categories from dropdown
                if hasattr(self.parser, 'get_dropdown_categories'):
                    dropdown_categories = self.parser.get_dropdown_categories()
                else:
                    # Fallback with hardcoded categories
                    dropdown_categories = [
                        {'name': 'TOP Webcams', 'url': f'{self.parser.BASE_URL}/it/top-live-cams.html'},
                        {'name': 'New Webcams', 'url': f'{self.parser.BASE_URL}/it/new-livecams.html'},
                        {'name': 'Cities', 'url': f'{self.parser.BASE_URL}/it/live-cams-category/city-cams.html'},
                        {'name': 'Beaches', 'url': f'{self.parser.BASE_URL}/it/live-cams-category/beach-cams.html'},
                        {'name': 'Landscapes', 'url': f'{self.parser.BASE_URL}/it/live-cams-category/nature-mountain-cams.html'},
                        {'name': 'Marinas', 'url': f'{self.parser.BASE_URL}/it/live-cams-category/seaport-cams.html'},
                        {'name': 'UNESCO', 'url': f'{self.parser.BASE_URL}/it/live-cams-category/unesco-cams.html'},
                        {'name': 'Ski Slopes', 'url': f'{self.parser.BASE_URL}/it/live-cams-category/ski-cams.html'},
                        {'name': 'Animals', 'url': f'{self.parser.BASE_URL}/it/live-cams-category/animals-cams.html'},
                        {'name': 'Volcanoes', 'url': f'{self.parser.BASE_URL}/it/live-cams-category/volcanoes-cams.html'}
                    ]
                enhanced_log(f"Found {len(dropdown_categories)} subcategories")

                # Save categories for later use
                self.current_categories = dropdown_categories

                # Convert categories to webcam format for display
                for category in dropdown_categories:
                    category_item = {
                        'title': category['name'],
                        'subtitle': f"Category: {category['name']}",
                        'cover_image': '',
                        'url': category['url'],
                        'alt_text': category['name'],
                        'parent_category': 'categories',
                        'type': 'category'
                    }
                    self.webcams.append(category_item)

                self["webcams_list"].setList([])

            elif self.subcategory_code in ["top", "nuove", "spiagge", "paesaggi", "marine", "unesco", "sci", "animali", "vulcani", "laghi", "web"]:
                enhanced_log(f"Loading webcams for category: {self.subcategory_code}")

                if hasattr(self, 'category_url') and self.category_url:
                    category_webcams = self.parser.get_webcams_by_url(self.category_url)

                    # Convert to expected format
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
                enhanced_log(f"Unsupported category: {self.subcategory_code}")
                self["status"].setText(_("Unsupported category: %s") % self.subcategory_code)
                return

            # Populate the menu list
            menu_list = []
            for webcam in self.webcams:
                title = webcam.get('title', 'Unknown webcam')

                if 'country' in webcam:
                    title += f" ({webcam['country']})"
                elif 'category' in webcam:
                    title += f" [{webcam['category']}]"

                menu_list.append(title)

            self["webcam_list"].setList(menu_list)

            enhanced_log(f"Loading completed: {len(self.webcams)} webcams found")
            self["status"].setText(_("Found %d webcams") % len(self.webcams))

            if len(self.webcams) > 0:
                self.update_preview()
            else:
                self["status"].setText(_("No webcams available in this category"))

        except Exception as e:
            self["status"].setText(_("Error loading webcams: %s") % str(e))
            enhanced_log(f"Error in load_webcams: {e}")

    def load_main_categories(self):
        """Load main categories from dynamic parsing"""
        try:
            enhanced_log("Starting main categories parsing")

            # Get categories from parser
            categories = self.parser.get_categories()
            enhanced_log(f"Parser found {len(categories)} categories")

            # Create main category menu
            main_menu = []
            self.category_mapping = {}  # Map name -> category data

            # Add categories from parsing
            for category in categories:
                category_name = category['name']
                main_menu.append(category_name)

                # Determine category code
                name_lower = category_name.lower()
                if "live" in name_lower:
                    code = "live"
                elif "categoria" in name_lower:
                    code = "categories"
                elif "top" in name_lower:
                    code = "top"
                elif "nuov" in name_lower:
                    code = "nuove"
                elif "citt" in name_lower:
                    code = "citta"
                elif "spiagge" in name_lower:
                    code = "spiagge"
                elif "paesaggi" in name_lower:
                    code = "paesaggi"
                elif "marine" in name_lower:
                    code = "marine"
                elif "unesco" in name_lower:
                    code = "unesco"
                elif "sci" in name_lower:
                    code = "sci"
                elif "animali" in name_lower:
                    code = "animali"
                elif "vulcani" in name_lower:
                    code = "vulcani"
                elif "laghi" in name_lower:
                    code = "laghi"
                else:
                    code = "web"

                self.category_mapping[category_name] = {
                    "code": code,
                    "name": category_name,
                    "url": category['url']
                }

            # If we didn't find categories from parser, use a fallback menu
            if len(main_menu) <= 1:  # Only "Live Webcams"
                enhanced_log("Using fallback menu")
                fallback_categories = ["Top Webcams", "New Webcams", "Cities", "Beaches", "Landscapes"]
                for cat in fallback_categories:
                    main_menu.append(cat)
                    code = cat.lower().replace(" webcams", "").replace(" ", "")
                    self.category_mapping[cat] = {"code": code, "name": cat}

            enhanced_log(f"Main menu created with {len(main_menu)} items: {main_menu}")

            # Update main list
            self["main_list"].setList(main_menu)
            self["status"].setText(_("Select a category ({} available)").format(len(main_menu)))

        except Exception as e:
            enhanced_log(f"Error loading main categories: {e}")
            # Fallback menu on error
            fallback_menu = ["Live Webcams", "Top Webcams"]
            self.category_mapping = {
                "Live Webcams": {"code": "live", "name": "Live Webcams"},
                "Top Webcams": {"code": "top", "name": "Top Webcams"}
            }
            self["main_list"].setList(fallback_menu)
            self["status"].setText(_("Basic menu loaded"))

    def cleanup_resources(self):
        # Stop current playback
        try:
            self.session.nav.stopService()
        except Exception as e:
            enhanced_log(f"Error while stopping service: {e}")

        # Clean resources when screen is closed
        self.webcams = []
        self.current_stream_url = None

        # Clear state attributes
        if hasattr(self, 'current_countries'):
            delattr(self, 'current_countries')
        if hasattr(self, 'current_webcams'):
            delattr(self, 'current_webcams')
        if hasattr(self, 'current_categories'):
            delattr(self, 'current_categories')
        if hasattr(self, 'current_category_webcams'):
            delattr(self, 'current_category_webcams')

        # Clean parsers and extractors after use
        if hasattr(self, 'parser') and self.parser is not None:
            self.parser = None

        if hasattr(self, 'extractor') and self.extractor is not None:
            self.extractor = None

    def play_selected_webcam(self):
        # If we are in the main menu, navigate to the selected category
        if not self.subcategory_code:
            self.select_category()
            return

        # If in Live Webcams mode
        if self.subcategory_code == "live":
            # Only if we are in the webcam window (window 2) start the player
            if self.current_window == 2 and hasattr(self, 'current_webcams') and self.current_webcams:
                try:
                    webcam_index = self["webcams_list"].getSelectionIndex()
                    if 0 <= webcam_index < len(self.current_webcams):
                        selected_webcam = self.current_webcams[webcam_index]

                        # Build stream URL
                        stream_url = self.parser.get_stream_url(selected_webcam['url'])
                        if stream_url:
                            selected_webcam['stream_url'] = stream_url

                        enhanced_log(f"Starting player for webcam: {selected_webcam['title']}")
                        self.start_video_playback(selected_webcam)

                except Exception as e:
                    enhanced_log(f"Error while opening player: {e}")
                    self.session.open(MessageBox, _('Error opening player: %s') % str(e), MessageBox.TYPE_ERROR, timeout=5)
            return

        # If in Categories mode
        if self.subcategory_code == "categories":
            # Only if we are in the webcam window (window 1) start the player
            if self.current_window == 1 and hasattr(self, 'current_category_webcams') and self.current_category_webcams:
                try:
                    webcam_index = self["webcams_list"].getSelectionIndex()
                    if 0 <= webcam_index < len(self.current_category_webcams):
                        selected_webcam = self.current_category_webcams[webcam_index]

                        # Build stream URL
                        stream_url = self.parser.get_stream_url(selected_webcam['url'])
                        if stream_url:
                            selected_webcam['stream_url'] = stream_url

                        enhanced_log(f"Starting player for category webcam: {selected_webcam.get('title', 'N/A')}")
                        self.start_video_playback(selected_webcam)

                except Exception as e:
                    enhanced_log(f"Error while opening category player: {e}")
                    self.session.open(MessageBox, _('Error opening player: %s') % str(e), MessageBox.TYPE_ERROR, timeout=5)
            return

        # For other categories, normal behaviour
        if self.webcams:
            try:
                current_index = self["webcam_list"].getSelectionIndex()
                if 0 <= current_index < len(self.webcams):
                    selected_item = self.webcams[current_index]
                    self.current_webcam_index = current_index
                else:
                    return

                # If it's a continent, show countries
                if selected_item.get('type') == 'continent':
                    self.show_countries_for_continent(selected_item)
                    return

                # If it's a category, show webcams of that category
                if selected_item.get('type') == 'category':
                    self.show_webcams_for_category(selected_item)
                    return

                # Otherwise play the selected webcam
                self.session.open(
                    SLwebcamsPlayer,
                    selected_item,
                    self.webcams,
                    current_index,
                    self.subcategory_code,
                    self.subcategory_name)

            except Exception as e:
                enhanced_log(f"Error while opening player: {e}")
                self.session.open(MessageBox, _('Error opening player: %s') % str(e), MessageBox.TYPE_ERROR, timeout=5)

    def select_category(self):
        """Select a category from the main menu"""
        try:
            current_index = self["main_list"].getSelectionIndex()
            menu_list = self["main_list"].list

            if 0 <= current_index < len(menu_list):
                selected_item = menu_list[current_index]
                enhanced_log(f"Selected category: {selected_item}")

                # Use dynamic category mapping
                if hasattr(self, 'category_mapping') and selected_item in self.category_mapping:
                    category_data = self.category_mapping[selected_item]
                    self.subcategory_code = category_data['code']
                    self.subcategory_name = category_data['name']
                    if 'url' in category_data:
                        self.category_url = category_data['url']
                else:
                    # Fallback for unmapped categories
                    self.subcategory_code = "top"
                    self.subcategory_name = selected_item

                # Reload with the new category
                enhanced_log(f"Loading category: {self.subcategory_code}")
                self.load_webcams()
                self.update_ui_visibility()

        except Exception as e:
            enhanced_log(f"Error selecting category: {e}")

    def reload_webcams(self):
        enhanced_log("Reload webcams requested")
        if not self.subcategory_code:
            # If we are in the main menu, reload categories
            self.load_main_categories()
        else:
            # Otherwise reload webcams of current category
            self.load_webcams()

    def show_info(self):
        enhanced_log("Info requested")
        if not self.subcategory_code:
            # In main menu, show short plugin info
            info_text = "Plugin to view webcams from skylinewebcams.com"
            self.session.open(MessageBox, info_text, MessageBox.TYPE_INFO, timeout=5)
        else:
            # In webcam lists, show numeric key legend
            info_text = "Quick navigation: Keys 1-9 jump to 10%-90% of list, 0 to start"
            self.session.open(MessageBox, info_text, MessageBox.TYPE_INFO, timeout=8)

    def show_countries_for_continent(self, continent_item):
        """Show countries for the selected continent"""
        try:
            enhanced_log(f"Loading countries for continent: {continent_item['title']}")

            # Get countries of the continent
            countries = self.parser.get_countries_by_continent(continent_item['continent_code'])
            enhanced_log(f"Found {len(countries)} countries")

            # Replace current list with countries
            self.webcams = []
            for country in countries:
                country_item = {
                    'title': country['name'],
                    'subtitle': f"Country: {country['name']}",
                    'cover_image': '',
                    'url': country['url'],
                    'alt_text': country['name'],
                    'parent_category': 'live',
                    'type': 'country',
                    'continent': continent_item['title']
                }
                self.webcams.append(country_item)

            # Update menu list
            menu_list = [country['title'] for country in countries]
            self["webcam_list"].setList(menu_list)

            # Update status
            self["status"].setText(_("Found %d countries in %s") % (len(countries), continent_item['title']))

        except Exception as e:
            enhanced_log(f"Error loading countries: {e}")
            self.session.open(MessageBox, _('Error loading countries: %s') % str(e), MessageBox.TYPE_ERROR, timeout=5)

    def start_video_playback(self, webcam):
        """Start video playback and make plugin transparent"""
        try:
            # Use stream URL if already available
            if 'stream_url' in webcam and webcam['stream_url']:
                stream_url = webcam['stream_url']
            else:
                stream_url = self.parser.get_stream_url(webcam['url'])

            if stream_url:
                enhanced_log(f"Starting transparent playback: {stream_url}")
                service_ref = eServiceReference(4097, 0, stream_url)
                self.session.nav.playService(service_ref)
                self.video_playing = True
                self.make_transparent()
            else:
                enhanced_log(f"Stream not available for: {webcam.get('title', 'N/A')}")
                self.session.open(MessageBox, "Stream not available for this webcam", MessageBox.TYPE_INFO, timeout=3)
        except Exception as e:
            enhanced_log(f"Webcam playback error: {e}")
            self.session.open(MessageBox, f"Playback error: {str(e)}", MessageBox.TYPE_ERROR, timeout=5)

    def make_transparent(self):
        """Make plugin transparent to show video"""
        try:
            # Hide all widgets
            widgets_to_hide = ['title', 'continents_title', 'countries_title', 'webcams_title',
                               'webcam_list', 'countries_list', 'webcams_list', 'description', 'status',
                               'key_red', 'key_green', 'key_yellow', 'key_blue']
            for widget_name in widgets_to_hide:
                if widget_name in self:
                    self[widget_name].hide()
            # Make background transparent
            self.instance.setTransparent(1)
            enhanced_log("Plugin made transparent")
        except Exception as e:
            enhanced_log(f"Error making transparent: {e}")

    def make_visible(self):
        """Restore plugin visibility"""
        try:
            # Show base widgets
            base_widgets = ['title', 'description', 'status', 'key_red', 'key_green', 'key_yellow', 'key_blue']
            for widget_name in base_widgets:
                if widget_name in self:
                    self[widget_name].show()

            # Restore opacity
            self.instance.setTransparent(0)
            # For categories, keep webcam window active if webcams were loaded
            if self.subcategory_code == "categories" and hasattr(self, 'current_category_webcams') and self.current_category_webcams:
                self.current_window = 1  # Webcam window

            # Update specific visibility for current mode
            self.update_ui_visibility()

            enhanced_log("Plugin restored")
        except Exception as e:
            enhanced_log(f"Error restoring visibility: {e}")

    def handle_cancel(self):
        if self.video_playing:
            self.session.nav.stopService()
            self.session.nav.playService(self.srefInit)
            self.srefInit = None
            self.video_playing = False
            self.make_visible()
            enhanced_log("Video stopped, service restored, plugin visible")
        elif self.subcategory_code:
            # Return to main menu
            self.subcategory_code = ""
            self.subcategory_name = ""
            self.current_window = 0
            # Clear state attributes
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
            # Normal close behaviour
            self.session.nav.playService(self.srefInit)
            self.close()

    def show_webcams_for_category(self, category_item):
        """Show webcams for the selected category"""
        try:
            enhanced_log(f"Loading webcams for category: {category_item['title']}")

            # Determine category code from name
            name_lower = category_item['title'].lower()
            if "top" in name_lower:
                code = "top"
            elif "nuov" in name_lower:
                code = "nuove"
            elif "citt" in name_lower:
                code = "citta"
            elif "spiagge" in name_lower:
                code = "spiagge"
            elif "paesaggi" in name_lower or "nature" in name_lower:
                code = "paesaggi"
            elif "marine" in name_lower or "seaport" in name_lower:
                code = "marine"
            elif "unesco" in name_lower:
                code = "unesco"
            elif "sci" in name_lower or "ski" in name_lower:
                code = "sci"
            elif "animali" in name_lower:
                code = "animali"
            elif "vulcani" in name_lower:
                code = "vulcani"
            else:
                code = "web"

            # Set new category
            self.subcategory_code = code
            self.subcategory_name = category_item['title']
            self.category_url = category_item['url']

            # Reload with the new category
            self.load_webcams()
            self.update_ui_visibility()

        except Exception as e:
            enhanced_log(f"Error loading category: {e}")
            self.session.open(MessageBox, _('Error loading category: %s') % str(e), MessageBox.TYPE_ERROR, timeout=5)

    def open_fullscreen_player(self):
        enhanced_log("Settings requested")
        if not self.subcategory_code:
            # If in main menu, open settings
            try:
                self.session.open(SLwebcamsSettings)
            except Exception as e:
                enhanced_log(f"Error opening settings: {e}")
                self.session.open(MessageBox, "Settings not available", MessageBox.TYPE_INFO, timeout=5)


class SLwebcamsPlayer(Screen):
    CONTROLS_HIDE_TIMEOUT = 5000

    def __init__(self, session, current_webcam, webcams_list, current_index, category_code, category_name, fullscreen=False):
        enhanced_log(f"Initializing player - Webcam: {current_webcam.get('title', 'N/A')}, Fullscreen: {fullscreen}")
        try:
            enhanced_log("Getting UI settings...")
            ui_settings = get_ui_settings()
            if 'player' in ui_settings:
                player_settings = ui_settings['player']
            else:
                enhanced_log("Key 'player' not found, using fallback settings")
                player_settings = {
                    'position': '0,0',
                    'size': '1920,1080'
                }
            enhanced_log("UI settings obtained successfully")
        except Exception as e:
            enhanced_log(f"Error getting UI settings: {e}")
            # Complete fallback
            player_settings = {
                'position': '0,0',
                'size': '1920,1080'
            }
            enhanced_log("Using complete fallback settings")

        if fullscreen:
            # Fullscreen mode - use dynamic resolution
            desktop_size = getDesktop(0).size()
            screen_width = desktop_size.width()
            screen_height = desktop_size.height()
            self.skin = f"""
            <screen position="0,0" size="{screen_width},{screen_height}" title="SkyLine Webcams Player" flags="wfNoBorder" backgroundColor="#000000">
                <eVideoPlayer name="video" position="0,0" size="{screen_width},{screen_height}" backgroundColor="#000000" />
                <widget name="info" position="50,50" size="800,40" font="Regular;32" foregroundColor="white" backgroundColor="#80000000" transparent="1" />
                <widget name="controls" position="50,{screen_height - 80}" size="800,30" font="Regular;24" foregroundColor="white" backgroundColor="#80000000" transparent="1" />
            </screen>
            """
        else:
            # Windowed mode (almost fullscreen)
            width = int(player_settings['size'].split(',')[0])
            height = int(player_settings['size'].split(',')[1])
            self.skin = f"""
            <screen position="{player_settings['position']}" size="{player_settings['size']}" title="SkyLine Webcams Player" backgroundColor="#000000">
                <eVideoPlayer name="video" position="0,0" size="{width},{height}" backgroundColor="#000000" />
                <widget name="info" position="50,30" size="{width - 100},40" font="Regular;32" foregroundColor="white" backgroundColor="#80000000" transparent="1" />
                <widget name="controls" position="50,{height - 100}" size="{width - 100},30" font="Regular;24" foregroundColor="white" backgroundColor="#80000000" transparent="1" />
                <widget name="red_label" position="50,{height - 60}" size="150,30" font="Regular;20" foregroundColor="red" backgroundColor="#80000000" transparent="1" />
                <widget name="green_label" position="220,{height - 60}" size="150,30" font="Regular;20" foregroundColor="green" backgroundColor="#80000000" transparent="1" />
                <widget name="yellow_label" position="390,{height - 60}" size="150,30" font="Regular;20" foregroundColor="yellow" backgroundColor="#80000000" transparent="1" />
                <widget name="blue_label" position="560,{height - 60}" size="150,30" font="Regular;20" foregroundColor="cyan" backgroundColor="#80000000" transparent="1" />
            </screen>
            """

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

            # Initialize UI components
            enhanced_log("Initializing UI components...")
            self["info"] = Label("")
            self["controls"] = Label("")
            enhanced_log("UI components initialized")
        except Exception as e:
            enhanced_log(f"Error during Screen or component initialization: {e}")
            raise

        try:
            if not fullscreen:
                enhanced_log("Initializing button labels...")
                self["red_label"] = Label("Exit")
                self["green_label"] = Label("Previous")
                self["yellow_label"] = Label("Next")
                self["blue_label"] = Label("Fullscreen")
                enhanced_log("Button labels initialized")

            # Define actions
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

            # Store currently playing service
            self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()

            enhanced_log("Setting callbacks...")
            self.onLayoutFinish.append(self.play_current_webcam)

            enhanced_log("Callbacks set")
            enhanced_log("Controls timer removed - controls always visible")
            enhanced_log("Player initialization completed successfully")
        except Exception as e:
            enhanced_log(f"Error during final player initialization: {e}")
            raise

    def play_current_webcam(self):
        try:
            # Update info
            webcam_title = self.current_webcam.get('title', 'Unknown webcam')
            if 'country' in self.current_webcam:
                webcam_title += f" ({self.current_webcam['country']})"

            enhanced_log(f"Playing webcam: {webcam_title}")
            self["info"].setText(webcam_title)
            self.update_controls_text()

            # Use stream URL if already available, otherwise extract it
            if 'stream_url' in self.current_webcam:
                stream_url = self.current_webcam['stream_url']
                enhanced_log(f"Using pre-built stream URL: {stream_url}")
            else:
                # Extract stream URL using parser
                from webcam_parser import WebcamParser
                parser = WebcamParser()
                enhanced_log(f"Extracting stream URL from: {self.current_webcam['url']}")
                stream_url = parser.get_stream_url(self.current_webcam['url'])
                enhanced_log(f"Extracted stream URL: {stream_url}")

            self.current_stream_url = stream_url

            if stream_url:
                # Create service and play
                enhanced_log(f"Starting playback service for: {stream_url}")
                service_ref = eServiceReference(4097, 0, stream_url)
                self.session.nav.playService(service_ref)
            else:
                enhanced_log("Stream URL not available")
                self.session.open(MessageBox, _('Stream not available for this webcam'), MessageBox.TYPE_INFO, timeout=5)

        except Exception as e:
            enhanced_log(f"Error during playback: {e}")
            self.session.open(MessageBox, _('Error during playback: %s') % str(e), MessageBox.TYPE_ERROR, timeout=5)

    def update_controls_text(self):
        controls_text = f"Webcam {self.current_index + 1} of {len(self.webcams_list)}"
        if 'category' in self.current_webcam:
            controls_text += f" | Category: {self.current_webcam['category']}"
        elif 'country' in self.current_webcam:
            controls_text += f" | Country: {self.current_webcam['country']}"
        self["controls"].setText(controls_text)

    def toggle_controls(self):
        # Controls always visible
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
            # Switch to fullscreen
            self.close()
            self.session.open(
                SLwebcamsPlayer,
                self.current_webcam,
                self.webcams_list,
                self.current_index,
                self.category_code,
                self.category_name,
                fullscreen=True)

    def close_player(self):
        self.stop_stream()
        self.close()

    def stop_stream(self):
        self.session.nav.stopService()
        self.session.nav.playService(self.srefInit)
        self.srefInit = None


class SLwebcamsFullscreen(Screen):
    def __init__(self, session, service_ref):
        # Get UI settings based on screen resolution
        ui_settings = get_ui_settings()
        fullscreen_settings = ui_settings.get('fullscreen', {})

        # Define skin dynamically in a simpler way
        self.skin = """
        <screen position="0,0" size="1920,1080" title="SkyLine Webcams Fullscreen" flags="wfNoBorder" backgroundColor="#000000">
            <eVideoPlayer name="video" position="0,0" size="1920,1080" backgroundColor="#000000" />
        </screen>
        """

        # If custom settings are available, use them
        if fullscreen_settings and 'position' in fullscreen_settings and 'size' in fullscreen_settings:
            self.skin = f"""
            <screen position="{fullscreen_settings['position']}" size="{fullscreen_settings['size']}" title="SkyLine Webcams Fullscreen" flags="wfNoBorder" backgroundColor="{UI_COLORS['background']}">
                <eVideoPlayer name="video" position="0,0" size="{fullscreen_settings['size']}" backgroundColor="{UI_COLORS['background']}" />
            </screen>
            """

        Screen.__init__(self, session)
        self.session = session
        self.service_ref = service_ref

        self["video"] = Label("")

        self["actions"] = ActionMap(
            ["OkCancelActions"],
            {
                "cancel": self.close,
            }, -1
        )
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.play_stream)
        self.onClose.append(self.stop_stream)

    def play_stream(self):
        try:
            self.session.nav.playService(self.service_ref)
        except Exception as e:
            self.session.open(MessageBox, _('Error during fullscreen playback: %s') % str(e), MessageBox.TYPE_ERROR, timeout=5)
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
