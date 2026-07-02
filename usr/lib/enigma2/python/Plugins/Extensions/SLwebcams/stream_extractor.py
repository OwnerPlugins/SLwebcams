#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import ssl
import urllib.request
import urllib.parse
import json
from .sl_logger import enhanced_log, log_exception


class StreamExtractor:
    """
    Extracts streaming URLs (HLS/m3u8, RTMP, MP4) from webcam pages.
    Handles various stream formats and iframe embedding.
    """

    def __init__(self):
        # Ignore SSL certificates to simplify requests
        enhanced_log("Initializing StreamExtractor", processo="__init__")
        self.context = ssl._create_unverified_context()

    def extract_stream_url(self, webcam_url):
        """
        Extract the m3u stream URL from a webcam page.

        Args:
            webcam_url (str): The URL of the webcam page

        Returns:
            str: The extracted stream URL, or None if not found
        """
        enhanced_log("Extracting stream URL from: {}".format(webcam_url), processo="extract_stream_url")
        html_content = self._fetch_url(webcam_url)

        if not html_content:
            enhanced_log("No HTML content found for: {}".format(webcam_url), "WARNING", processo="extract_stream_url")
            return None

        # First look for the HLS stream (m3u8) pattern with dynamic token
        m3u8_pattern = r'source:\s*\'livee\.m3u8\?a=([^\']+)\''
        m3u8_match = re.search(m3u8_pattern, html_content)

        if m3u8_match:
            token = m3u8_match.group(1)
            final_url = "https://hd-auth.skylinewebcams.com/live.m3u8?a={}".format(token)
            enhanced_log("Found m3u8 URL with token: {}".format(final_url), processo="extract_stream_url")
            return final_url

        # Alternative pattern for full m3u8 URL
        m3u8_full_pattern = r'source:\s*[\'"](https://hd-auth\.skylinewebcams\.com/live\.m3u8\?a=[^\'"]+)[\'"]'
        m3u8_full_match = re.search(m3u8_full_pattern, html_content)

        if m3u8_full_match:
            final_url = m3u8_full_match.group(1)
            enhanced_log("Found full m3u8 URL: {}".format(final_url), processo="extract_stream_url")
            return final_url

        # If dynamic token not found, try legacy patterns for compatibility
        m3u8_pattern = r'source:\s*\{\s*hls:\s*["\']([^"\']+)["\']'
        m3u8_match = re.search(m3u8_pattern, html_content)

        if m3u8_match:
            enhanced_log("Found legacy m3u8 URL: {}".format(m3u8_match.group(1)), processo="extract_stream_url")
            return m3u8_match.group(1)

        # If HLS stream not found, look for RTMP stream pattern
        rtmp_pattern = r'source:\s*\{\s*rtmp:\s*["\']([^"\']+)["\']'
        rtmp_match = re.search(rtmp_pattern, html_content)

        if rtmp_match:
            enhanced_log("Found RTMP URL: {}".format(rtmp_match.group(1)), processo="extract_stream_url")
            return rtmp_match.group(1)

        # If neither HLS nor RTMP found, look for iframe pattern
        iframe_pattern = r'<iframe[^>]*src=["\']([^"\']+)["\'][^>]*>'
        iframe_match = re.search(iframe_pattern, html_content)

        if iframe_match:
            iframe_url = iframe_match.group(1)
            enhanced_log("Found iframe: {}".format(iframe_url), processo="extract_stream_url")
            if not iframe_url.startswith('http'):
                if iframe_url.startswith('//'):
                    iframe_url = 'https:' + iframe_url
                else:
                    base_url = self._get_base_url(webcam_url)
                    iframe_url = base_url + iframe_url

            # Extract stream from iframe
            enhanced_log("Extracting stream from iframe: {}".format(iframe_url), processo="extract_stream_url")
            return self._extract_stream_from_iframe(iframe_url)

        # Also look for embedded JSON data pattern
        json_pattern = r'var\s+webcamData\s*=\s*(\{[^;]+\});'
        json_match = re.search(json_pattern, html_content)

        if json_match:
            try:
                webcam_data = json.loads(json_match.group(1))
                if 'stream' in webcam_data and webcam_data['stream']:
                    enhanced_log("Found stream in JSON: {}".format(webcam_data['stream']), processo="extract_stream_url")
                    return webcam_data['stream']
            except Exception:
                pass

        # If no stream found, return None
        enhanced_log("No stream found", "WARNING", processo="extract_stream_url")
        return None

    def _extract_stream_from_iframe(self, iframe_url):
        """
        Extract stream URL from an iframe page.

        Args:
            iframe_url (str): The URL of the iframe

        Returns:
            str: The extracted stream URL, or None if not found
        """
        enhanced_log("Analyzing iframe: {}".format(iframe_url), processo="_extract_stream_from_iframe")
        html_content = self._fetch_url(iframe_url)

        if not html_content:
            enhanced_log("No HTML content found in iframe: {}".format(iframe_url), "WARNING", processo="_extract_stream_from_iframe")
            return None

        # Look for HLS stream (m3u8) pattern with token in iframe
        m3u8_token_pattern = r'source:\s*\'livee\.m3u8\?a=([^\']+)\''
        m3u8_token_match = re.search(m3u8_token_pattern, html_content)

        if m3u8_token_match:
            token = m3u8_token_match.group(1)
            final_url = "https://hd-auth.skylinewebcams.com/live.m3u8?a={}".format(token)
            enhanced_log("Found m3u8 URL with token in iframe: {}".format(final_url), processo="_extract_stream_from_iframe")
            return final_url

        # Look for HLS stream (m3u8) pattern in iframe
        m3u8_pattern = r'source:\s*["\']([^"\']+\.m3u8[^"\']*)["\']'
        m3u8_match = re.search(m3u8_pattern, html_content)

        if m3u8_match:
            enhanced_log("Found m3u8 URL in iframe: {}".format(m3u8_match.group(1)), processo="_extract_stream_from_iframe")
            return m3u8_match.group(1)

        # Look for MP4 stream pattern in iframe
        mp4_pattern = r'source:\s*["\']([^"\']+\.mp4[^"\']*)["\']'
        mp4_match = re.search(mp4_pattern, html_content)

        if mp4_match:
            enhanced_log("Found MP4 URL in iframe: {}".format(mp4_match.group(1)), processo="_extract_stream_from_iframe")
            return mp4_match.group(1)

        # Look for any generic stream URL pattern in iframe
        stream_pattern = r'source:\s*["\']([^"\']+)["\']'
        stream_match = re.search(stream_pattern, html_content)

        if stream_match:
            enhanced_log("Found generic stream URL in iframe: {}".format(stream_match.group(1)), processo="_extract_stream_from_iframe")
            return stream_match.group(1)

        # If no stream found, return None
        enhanced_log("No stream found in iframe", "WARNING", processo="_extract_stream_from_iframe")
        return None

    def _fetch_url(self, url):
        """
        Fetch HTML content from a URL.

        Args:
            url (str): The URL to fetch

        Returns:
            str: The HTML content, or None if an error occurs
        """
        enhanced_log("Fetching content from: {}".format(url), processo="_fetch_url")
        try:
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

            with urllib.request.urlopen(request, context=self.context) as response:
                enhanced_log("Content fetched successfully from: {}".format(url), processo="_fetch_url")
                return response.read().decode('utf-8')
        except Exception as e:
            log_exception(e, "Error fetching URL {}".format(url))
            return None

    def _get_base_url(self, url):
        """
        Extract the base URL from a full URL.

        Args:
            url (str): The full URL

        Returns:
            str: The base URL (scheme + netloc)
        """
        parsed_url = urllib.parse.urlparse(url)
        return "{}://{}".format(parsed_url.scheme, parsed_url.netloc)
        