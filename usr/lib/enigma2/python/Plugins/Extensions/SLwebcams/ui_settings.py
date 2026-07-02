#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enigma import getDesktop

desktop_size = getDesktop(0).size()
desktop_width = desktop_size.width()
desktop_height = desktop_size.height()


def get_ui_settings():
    """
    Returns UI settings based on screen resolution.

    Returns:
        dict: UI configuration dictionaries for main screen, content screen and fullscreen.
    """
    if desktop_width >= 1920:  # Full HD or higher
        return {
            'main_screen': {
                'position': 'center,center',
                'size': '1500,900',
                'title_font': 'Regular;42',
                'menu_font': 'Regular;32',
                'button_font': 'Regular;28',
                'item_height': 44      # Row height for lists
            },
            'content_screen': {
                'position': 'center,center',
                'size': '1500,900',
                'title_font': 'Regular;42',
                'subtitle_font': 'Regular;32',
                'list_font': 'Regular;28',
                'description_font': 'Regular;24',
                'button_font': 'Regular;28',
                'video_size': '1000,560',
                'item_height': 40      # Row height for lists
            },
            'fullscreen': {
                'position': '0,0',
                'size': '1920,1080'
            }
        }
    elif desktop_width >= 1280:  # HD
        return {
            'main_screen': {
                'position': 'center,center',
                'size': '1200,700',
                'title_font': 'Regular;36',
                'menu_font': 'Regular;28',
                'button_font': 'Regular;24',
                'item_height': 38      # Row height for lists
            },
            'content_screen': {
                'position': 'center,center',
                'size': '1200,700',
                'title_font': 'Regular;36',
                'subtitle_font': 'Regular;28',
                'list_font': 'Regular;24',
                'description_font': 'Regular;20',
                'button_font': 'Regular;24',
                'video_size': '820,460',
                'item_height': 34      # Row height for lists
            },
            'fullscreen': {
                'position': '0,0',
                'size': '1280,720'
            }
        }
    else:  # SD or lower
        return {
            'main_screen': {
                'position': 'center,center',
                'size': '720,576',
                'title_font': 'Regular;28',
                'menu_font': 'Regular;22',
                'button_font': 'Regular;20',
                'item_height': 30      # Row height for lists
            },
            'content_screen': {
                'position': 'center,center',
                'size': '720,576',
                'title_font': 'Regular;28',
                'subtitle_font': 'Regular;24',
                'list_font': 'Regular;20',
                'description_font': 'Regular;18',
                'button_font': 'Regular;20',
                'video_size': '480,270',
                'item_height': 28      # Row height for lists
            },
            'fullscreen': {
                'position': '0,0',
                'size': '720,576'
            }
        }


UI_COLORS = {
    'background': '#000000',
    'title': '#FFFFFF',
    'text': '#FFFFFF',
    'selected': '#1E88E5',
    'button_red': '#FF0000',
    'button_green': '#00FF00',
    'button_yellow': '#FFFF00',
    'button_blue': '#0000FF'
}
