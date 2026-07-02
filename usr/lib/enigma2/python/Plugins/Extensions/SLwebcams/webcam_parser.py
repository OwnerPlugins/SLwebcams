#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import ssl
import urllib.request
import urllib.parse
from .sl_logger import SLLogger


class WebcamParser:
    """
    Parser for the skylinewebcams.com website.
    Extracts continents, countries, cities, categories and webcams.
    """

    BASE_URL = "https://www.skylinewebcams.com"

    def __init__(self):
        self.logger = SLLogger()
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def get_continents(self):
        """Extract continents from the main page"""
        try:
            url = "{}/it/".format(self.BASE_URL)
            html = self._fetch_url(url)

            continents = []
            # Pattern to find continents in the continent class
            pattern = r'<div class="continent ([^"]+)"><strong>([^<]+)</strong></div>'

            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

            for continent_class, name in matches:
                # Build the continent URL based on the class
                continent_url = "{}/it/webcam/{}.html".format(
                    self.BASE_URL, continent_class)
                continents.append({
                    'name': name.strip(),
                    'url': continent_url,
                    'code': continent_class
                })

            self.logger.enhanced_log(
                "Found {} continents".format(
                    len(continents)))
            return continents

        except Exception as e:
            self.logger.enhanced_log(
                "Error retrieving continents: {}".format(e))
            return []

    def get_countries_by_continent(self, continent_code):
        """Extract countries of a continent from the main page"""
        try:
            url = "{}/it/".format(self.BASE_URL)
            html = self._fetch_url(url)

            countries = []

            # Find the continent and then look for countries in subsequent rows
            continent_pattern = '<div class="continent {}"><strong>([^<]+)</strong></div>'.format(
                continent_code)
            continent_match = re.search(
                continent_pattern, html, re.IGNORECASE | re.DOTALL)

            if continent_match:
                # Find the position of the continent
                continent_pos = continent_match.end()

                # Search the content until the next continent
                remaining_html = html[continent_pos:]
                next_continent_pos = remaining_html.find('class="continent')

                if next_continent_pos != -1:
                    content_to_parse = remaining_html[:next_continent_pos]
                else:
                    content_to_parse = remaining_html[:2000]  # Increase limit

                # Extract country links from all columns
                country_pattern = r'<a href="(/it/webcam/[^"]+\.html)">([^<]+)</a>'
                country_matches = re.findall(
                    country_pattern, content_to_parse, re.IGNORECASE)

                for href, name in country_matches:
                    full_url = self.BASE_URL + href
                    countries.append({
                        'name': name.strip(),
                        'url': full_url
                    })

            self.logger.enhanced_log(
                "Found {} countries in continent {}".format(
                    len(countries), continent_code))
            return countries

        except Exception as e:
            self.logger.enhanced_log(
                "Error retrieving countries: {}".format(e))
            return []

    def get_city_webcams(self, country_url):
        """Extract webcams from cities of a country"""
        try:
            html = self._fetch_url(country_url)

            webcams = []
            # Pattern for webcams in cities
            pattern = r'<a href="([^"]+)"[^>]*class="[^"]*col-xs-12[^"]*"[^>]*>\s*<div[^>]*cam-light[^>]*>\s*<img src="([^"]+)"[^>]*loading="lazy"[^>]*alt="([^"]*)"[^>]*>\s*<p[^>]*class="tcam"[^>]*>([^<]+)</p>\s*<p[^>]*class="subt"[^>]*>([^<]+)</p>'

            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

            for href, img_src, alt_text, tcam_title, subt_desc in matches:
                full_url = self.BASE_URL + \
                    href if href.startswith('/') else self.BASE_URL + '/' + href

                webcam = {
                    'title': tcam_title.strip(),
                    'subtitle': subt_desc.strip(),
                    'cover_image': img_src.strip(),
                    'url': full_url,
                    'alt_text': alt_text.strip()
                }
                webcams.append(webcam)

            # Alternative simpler pattern for special cases
            if not webcams:
                alt_pattern = r'<div[^>]*cam-light[^>]*>\s*<img src="([^"]+)"[^>]*>\s*<p[^>]*class="tcam"[^>]*>([^<]+)</p>\s*<p[^>]*class="subt"[^>]*>([^<]+)</p>'
                alt_matches = re.findall(
                    alt_pattern, html, re.IGNORECASE | re.DOTALL)

                for img_src, tcam_title, subt_desc in alt_matches:
                    webcam = {
                        'title': tcam_title.strip(),
                        'subtitle': subt_desc.strip(),
                        'cover_image': img_src.strip(),
                        'url': country_url,  # Fallback URL
                        'alt_text': tcam_title.strip()
                    }
                    webcams.append(webcam)

            self.logger.enhanced_log(
                "Found {} city webcams".format(
                    len(webcams)))
            return webcams

        except Exception as e:
            self.logger.enhanced_log(
                "Error retrieving city webcams: {}".format(e))
            return []

    def get_categories(self):
        """Return the main categories from the menu"""
        try:
            # Use hardcoded categories since dynamic parsing doesn't work
            # correctly
            categories = [{'name': 'Live Webcams',
                           'url': '{}/it/'.format(self.BASE_URL),
                           'image': ''},
                          {'name': 'Webcams by category',
                           'url': '{}/it/webcam/'.format(self.BASE_URL),
                           'image': ''}]

            self.logger.enhanced_log(
                "Found {} categories".format(
                    len(categories)))
            return categories

        except Exception as e:
            self.logger.enhanced_log(
                "Error retrieving categories: {}".format(e))
            return []

    def get_dropdown_categories(self):
        """Extract categories from the dropdown menu"""
        try:
            url = "{}/it/".format(self.BASE_URL)
            html = self._fetch_url(url)

            categories = []
            # Pattern to find categories in the dropdown
            pattern = r'<a href="([^"]+)" class="[^"]*col-xs-6[^"]*"><p class="tcam">([^<]+)</p>'

            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

            for href, name in matches:
                full_url = self.BASE_URL + \
                    href if href.startswith('/') else href
                categories.append({
                    'name': name.strip(),
                    'url': full_url
                })

            self.logger.enhanced_log(
                "Found {} dropdown categories".format(
                    len(categories)))
            return categories

        except Exception as e:
            self.logger.enhanced_log(
                "Error retrieving dropdown categories: {}".format(e))
            return []

    def get_webcams_by_url(self, url):
        """Extract webcams from a specific page"""
        try:
            html = self._fetch_url(url)
            return self._parse_category_webcams_from_html(html)

        except Exception as e:
            self.logger.enhanced_log("Error retrieving webcams: {}".format(e))
            return []

    def get_subcategories_by_url(self, url):
        """Extract subcategories from a specific page"""
        try:
            html = self._fetch_url(url)
            return self._parse_subcategories_from_html(html)

        except Exception as e:
            self.logger.enhanced_log(
                "Error retrieving subcategories: {}".format(e))
            return []

    def _fetch_url(self, url):
        """Fetch HTML content from a URL"""
        try:
            self.logger.enhanced_log("Fetching URL: {}".format(url))

            request = urllib.request.Request(url)
            request.add_header(
                'User-Agent',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            with urllib.request.urlopen(request, context=self.ssl_context, timeout=10) as response:
                content = response.read().decode('utf-8')

            self.logger.enhanced_log(
                "Content fetched: {} characters".format(
                    len(content)))
            return content

        except Exception as e:
            self.logger.enhanced_log(
                "Error fetching URL {}: {}".format(
                    url, e))
            raise

    def _parse_category_webcams_from_html(self, html):
        """Specific parser for webcams from category pages"""
        webcams = []

        # Pattern for category format: <a href="url" class="col-xs-12 col-sm-6
        # col-md-4"><div class="cam-light">...
        pattern = r'<a href="([^"]+)" class="[^"]*col-xs-12[^"]*">\s*<div class="cam-light">.*?<img src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>\s*<p class="tcam">([^<]+)</p>\s*<p class="subt">([^<]+)</p>'

        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

        for href, img_src, alt_text, title, subtitle in matches:
            # Build full URL
            if href.startswith('/'):
                full_url = self.BASE_URL + href
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = self.BASE_URL + '/' + href

            webcam = {
                'title': title.strip(),
                'subtitle': subtitle.strip(),
                'url': full_url,
                'image_url': img_src.strip(),
                'alt_text': alt_text.strip()
            }
            webcams.append(webcam)

        # If the main pattern doesn't find anything, try alternative patterns
        if not webcams:
            # Simplified pattern
            alt_pattern = r'<a href="([^"]+)"[^>]*>.*?<p class="tcam">([^<]+)</p>'
            alt_matches = re.findall(
                alt_pattern, html, re.IGNORECASE | re.DOTALL)

            for href, title in alt_matches:
                if 'webcam' in href or 'live' in href:
                    full_url = self.BASE_URL + \
                        href if href.startswith('/') else href
                    webcam = {
                        'title': title.strip(),
                        'subtitle': '',
                        'url': full_url,
                        'image_url': '',
                        'alt_text': title.strip()
                    }
                    webcams.append(webcam)

        self.logger.enhanced_log(
            "Category parser found {} webcams".format(
                len(webcams)))
        return webcams

    def get_webcam_stream_param(self, webcam_url):
        """Extract the 'a' parameter from the webcam page to build the stream link"""
        try:
            html = self._fetch_url(webcam_url)

            # Specific pattern for source:'livee.m3u8?a=parameter'
            pattern = r"source:\s*['\"]livee\.m3u8\?a=([^'\"&]+)['\"]?"
            match = re.search(pattern, html, re.IGNORECASE)

            if match:
                param_a = match.group(1)
                self.logger.enhanced_log(
                    "Found parameter 'a': {}".format(param_a))
                return param_a

            self.logger.enhanced_log(
                "Parameter 'a' not found in source pattern")
            return None

        except Exception as e:
            self.logger.enhanced_log(
                "Error extracting stream parameter: {}".format(e))
            return None

    def get_stream_url(self, webcam_url):
        """Build the stream URL for the webcam"""
        param_a = self.get_webcam_stream_param(webcam_url)
        if param_a:
            stream_url = "https://hd-auth.skylinewebcams.com/live.m3u8?a={}".format(
                param_a)
            self.logger.enhanced_log("Stream URL built: {}".format(stream_url))
            return stream_url
        return None

    def _parse_webcams_from_html(self, html):
        """Basic parser for webcams (fallback)"""
        webcams = []

        # Pattern for webcams with images
        pattern = r'<img[^>]*src="([^"]+)"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

        for img_src, href, title in matches:
            if 'webcam' in href.lower() or 'live' in href.lower():
                webcam = {
                    'title': title.strip(),
                    'url': self.BASE_URL + href if href.startswith('/') else href,
                    'image': img_src.strip()}
                webcams.append(webcam)

        return webcams

    def _parse_subcategories_from_html(self, html):
        """Basic parser for subcategories"""
        subcategories = []

        # Pattern for subcategories
        pattern = r'<a[^>]*href="(/it/webcam/[^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)

        for href, name in matches:
            if not any(ext in href.lower() for ext in ['.html', '.htm']):
                continue

            subcategory = {
                'name': name.strip(),
                'url': self.BASE_URL + href
            }
            subcategories.append(subcategory)

        return subcategories
