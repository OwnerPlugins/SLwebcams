#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import ssl
import urllib.request
import urllib.parse
from enigma import ePicLoad, eSize
from Components.AVSwitch import AVSwitch
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

PLUGIN_PATH = resolveFilename(SCOPE_PLUGINS, "Extensions/SLwebcams/")


def get_plugin_path():
    """Return the plugin path."""
    return PLUGIN_PATH


def download_image(url, target_path, timeout=10):
    """
    Download an image from a URL and save it to the specified path.

    Args:
        url (str): The image URL
        target_path (str): The local path to save the image
        timeout (int): Download timeout in seconds

    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        context = ssl._create_unverified_context()
        request = urllib.request.Request(url)
        request.add_header(
            'User-Agent',
            config.plugins.slwebcams.user_agent.value)

        with urllib.request.urlopen(request, timeout=int(timeout), context=context) as response:
            img_data = response.read()

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Save the image
            with open(target_path, 'wb') as f:
                f.write(img_data)

            return True
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return False


def scale_image(picload, image_path, size):
    """
    Scale an image to the specified dimensions.

    Args:
        picload (ePicLoad): The ePicLoad instance
        image_path (str): Path to the image file
        size (eSize): Target dimensions

    Returns:
        object: The scaled image data
    """
    sc = AVSwitch().getFramebufferScale()
    picload.setPara((
        size.width(),
        size.height(),
        sc[0],
        sc[1],
        False,
        1,
        '#00000000'
    ))
    picload.startDecode(image_path)
    return picload.getData()


def clean_html(html_text):
    """
    Remove HTML tags from a string and decode common HTML entities.

    Args:
        html_text (str): The HTML text to clean

    Returns:
        str: The cleaned text
    """
    if not html_text:
        return ""

    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', html_text)

    # Replace common HTML entities
    clean_text = clean_text.replace('&nbsp;', ' ')
    clean_text = clean_text.replace('&amp;', '&')
    clean_text = clean_text.replace('&lt;', '<')
    clean_text = clean_text.replace('&gt;', '>')
    clean_text = clean_text.replace('&quot;', '"')
    clean_text = clean_text.replace('&#39;', "'")

    # Remove multiple spaces
    clean_text = re.sub(r'\s+', ' ', clean_text)

    return clean_text.strip()


def create_cache_dir():
    """
    Create the cache directory for images.

    Returns:
        str: The path to the cache directory
    """
    cache_dir = os.path.join(get_plugin_path(), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_cached_image_path(url):
    """
    Get the cache path for an image based on its URL.

    Args:
        url (str): The image URL

    Returns:
        str: The cache file path
    """
    # Create a filename based on the URL
    filename = re.sub(r'[^a-zA-Z0-9]', '_', url) + ".jpg"
    return os.path.join(create_cache_dir(), filename)


def is_image_cached(url):
    """
    Check if an image is already in the cache.

    Args:
        url (str): The image URL

    Returns:
        bool: True if the image is cached, False otherwise
    """
    cache_path = get_cached_image_path(url)
    return os.path.exists(cache_path) and os.path.getsize(cache_path) > 0


def get_image(url, size, callback=None):
    """
    Get an image, scale it and return it.

    Args:
        url (str): The image URL
        size (tuple): Target size as (width, height)
        callback (callable, optional): Callback for image data

    Returns:
        object: The scaled image data, or None if the image couldn't be loaded
    """
    cache_path = get_cached_image_path(url)

    # If the image is not in cache, download it
    if not is_image_cached(url):
        if not download_image(url, cache_path):
            return None

    # Load and scale the image
    picload = ePicLoad()
    if callback:
        picload.PictureData.get().append(callback)

    return scale_image(picload, cache_path, eSize(size[0], size[1]))
