# SkyLine Webcams - Enigma2 Plugin

![SkyLine Webcams](https://img.shields.io/badge/Enigma2-Plugin-blue)
![Version](https://img.shields.io/badge/version-1.0.2-green)
![Python](https://img.shields.io/badge/python-3.x-yellow)
![License](https://img.shields.io/badge/license-GPLv2-blue)

**Watch live webcams from skylinewebcams.com directly on your Enigma2 receiver.**

---

## 📖 Description

SkyLine Webcams is a comprehensive Enigma2 plugin that allows you to browse and watch thousands of live webcams from around the world. 
With an intuitive three-column interface, you can easily navigate through continents, countries, and individual webcams to find the perfect live view.

Whether you want to check beach conditions, watch city skylines, monitor ski slopes, or observe wildlife - SkyLine Webcams brings the world to your TV screen.

---

## ✨ Features

- **🌍 Global Coverage**: Access thousands of webcams from all continents and countries
- **📊 Three-Column Navigation**: Intuitive interface with continents, countries, and webcams
- **🎥 Live Streaming**: Watch HLS (m3u8) streams directly on your receiver
- **🏷️ Category Browsing**: Explore webcams by categories (Beaches, Cities, UNESCO, Ski, Animals, Volcanoes, etc.)
- **🔢 Quick Navigation**: Jump to any position in lists using number keys (1-9, 0)
- **🎛️ Configurable Settings**: Adjust buffer size, timeout, default view, and more
- **🌐 Multi-language Support**: Ready for localization (English, Italian)
- **📝 Advanced Logging**: Built-in logging system for debugging and troubleshooting
- **🖼️ Responsive UI**: Adapts to different screen resolutions (SD, HD, Full HD)
- **🎨 Transparent Video Overlay**: Watch webcams while browsing the interface

---

## 📋 Requirements

- Enigma2 based receiver (OpenPLi, OpenATV, OpenVision, VTi, etc.)
- Python 3.x
- Internet connection
- `python3-requests` and `python3-beautifulsoup4` (installed automatically with the plugin)
- `ffmpeg` (for some stream formats)

---

## 🚀 Installation

### Manual Installation

1. Download the plugin archive from the [releases page](https://github.com/OwnerPlugins/SLwebcams/releases)
2. Extract the archive
3. Copy the `SLwebcams` folder to `/usr/lib/enigma2/python/Plugins/Extensions/`
4. Restart Enigma2 (GUI restart or full reboot)

### Via Telnet/SSH

```bash
cd /tmp
wget https://github.com/OwnerPlugins/SLwebcams/releases/latest/download/SLwebcams.zip
unzip SLwebcams.zip -d /usr/lib/enigma2/python/Plugins/Extensions/
rm SLwebcams.zip
init 4 && init 3
```

### Via Plugin Manager

1. Press the **Menu** button on your remote
2. Go to **Plugins** → **Download plugins** (if available)
3. Find **SkyLine Webcams** in the extensions section
4. Press **OK** to install
5. Restart Enigma2

---

## 🎮 How to Use

### Starting the Plugin

- **From Plugin Menu**: Press **Menu** → **Plugins** → **SkyLine Webcams**
- **From Extensions Menu**: Press the **Extensions** button (Blue or Green depending on your skin) and select **SkyLine Webcams**

### Navigation Modes

The plugin features two main navigation modes:

#### 1. Main Menu
The first screen displays available categories:
- **Live Webcams**: Browse by continent → country → city webcams
- **Webcams by Category**: Browse by thematic categories

#### 2. Live Webcams (Continent → Country → Webcam)
In **Live Webcams** mode:
- **First Column (CONTINENTS)**: Select a continent
- **Second Column (COUNTRIES)**: Select a country within the continent
- **Third Column (WEBCAMS)**: Browse and select individual webcams

#### 3. Category View
In **Webcams by Category** mode:
- **First Column (CATEGORY)**: Select a category
- **Second Column (WEBCAMS)**: Browse webcams in that category

### Webcam Playback

- Press **OK** on a webcam to start streaming
- The video plays in the background while the interface becomes transparent
- Press **Cancel** to stop the video and return to the interface
- In the player window:
  - **Green/Yellow/Left/Right/Up/Down**: Navigate between webcams
  - **Blue**: Toggle fullscreen mode
  - **Red/Cancel**: Close the player

---

## 🎯 Remote Control Key Mapping

### Main Interface

| Key | Function |
|-----|----------|
| **OK** | Select item / Play webcam |
| **Cancel / Exit** | Return to previous screen / Stop video |
| **Up / Down** | Navigate lists |
| **Left / Right** | Switch between columns |
| **Red** | Exit plugin |
| **Green** | Reload current list |
| **Yellow** | Show information (key legend) |
| **Blue** | Open settings (main menu only) |
| **1-9** | Jump to 10%-90% of the list |
| **0** | Jump to the start of the list |

### Player Interface

| Key | Function |
|-----|----------|
| **OK** | Toggle controls visibility |
| **Cancel / Exit** | Close player and return |
| **Red** | Close player |
| **Green / Left / Up** | Previous webcam |
| **Yellow / Right / Down** | Next webcam |
| **Blue** | Toggle fullscreen |

---

## ⚙️ Configuration

Press the **Blue** button from the main menu to open the settings screen.

| Setting | Description | Options |
|---------|-------------|---------|
| **Buffer Size** | Size of the streaming buffer in KB | 1MB, 2MB, 4MB, 8MB, 16MB |
| **Show Information** | Display webcam information overlay | Yes / No |
| **Default View** | Default view when starting the plugin | Live Webcams / Category-based |
| **Connection Timeout** | Timeout for network requests | 5s, 10s, 15s, 20s |
| **User Agent** | Custom User-Agent for HTTP requests | Text field |

---

## 📝 Logging and Debugging

The plugin includes an advanced logging system for troubleshooting.

### Log File Location
```
/usr/lib/enigma2/python/Plugins/Extensions/SLwebcams/logs/sl_logs.txt
```

### Log Rotation
- Maximum log size: 1MB
- When the log exceeds 1MB, the first half is truncated
- A rotation message is added to indicate truncation

### Debug Skin
For debugging the interface skin, the plugin writes the skin XML to:
```
/tmp/skin_debug.txt
```

### Using Logs for Troubleshooting
If you encounter issues:
1. Check the log file for error messages
2. Look for lines marked `[ERROR]` or `[WARNING]`
3. The log includes file names, function names, and line numbers for easy debugging

---

## 🛠️ Troubleshooting

### Webcam Not Playing
- Ensure your internet connection is active
- Check if the stream URL is accessible (check logs)
- Try increasing the buffer size in settings
- Verify that the webcam is online

### No Webcams Loaded
- Press the **Green** button to reload the list
- Check your internet connection
- Verify that skylinewebcams.com is accessible
- Check logs for parsing errors

### Plugin Not Starting
- Verify the plugin is installed in the correct directory
- Check Python dependencies (`requests`, `beautifulsoup4`)
- Look for errors in the Enigma2 crash log
- Check the plugin logs in `/tmp/skin_debug.txt`

### Stream Buffering/Lag
- Increase the buffer size in settings
- Reduce the connection timeout if too high
- Check your internet speed
- Try a different webcam

---

## 📁 Plugin Structure

```
SLwebcams/
├── plugin.py                 # Main plugin file
├── settings.py              # Configuration and translations
├── settings_screen.py       # Settings UI
├── webcam_parser.py         # Web scraping and parsing
├── stream_extractor.py      # Stream URL extraction
├── ui_settings.py           # UI configuration (responsive)
├── sl_logger.py             # Logging system
├── utils.py                 # Utility functions
├── icon.svg                 # Plugin icon
├── locale/                  # Translation files
│   ├── it/
│   │   └── LC_MESSAGES/
│   │       └── SLwebcams.po
│   └── en/
│       └── LC_MESSAGES/
│           └── SLwebcams.po
└── logs/                    # Log directory (created at runtime)
    └── sl_logs.txt          # Log file
```

---

## 🔧 Development Notes

### Adding New Categories
Categories are parsed from the skylinewebcams.com website. To add new categories:

1. Edit the `get_categories()` method in `webcam_parser.py`
2. Add the category name and URL to the list
3. The plugin will automatically detect the category type

### Customizing UI Colors
Edit the `UI_COLORS` dictionary in `ui_settings.py`:
```python
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
```

### Adding Translations
1. Create a `.po` file in the appropriate locale directory
2. Use `msgfmt` to compile to `.mo`
3. The plugin will automatically use the translation based on the system language

Example for Italian:
```bash
msgfmt -o locale/it/LC_MESSAGES/SLwebcams.mo locale/it/LC_MESSAGES/SLwebcams.po
```

---

## 🔄 Updating

### From GitHub
```bash
cd /tmp
wget https://github.com/OwnerPlugins/SLwebcams/releases/latest/download/SLwebcams.zip
unzip -o SLwebcams.zip -d /usr/lib/enigma2/python/Plugins/Extensions/
rm SLwebcams.zip
init 4 && init 3
```

### From Plugin Manager
Check for updates in the plugin manager and install the new version.

---

## 📄 License

This plugin is released under the GNU General Public License v2.0.

---

## 👥 Credits

- **Developer**: [SkyLine Team](https://github.com/OlinadWiz)
- **Webcam Source**: [skylinewebcams.com](https://www.skylinewebcams.com)
- **Special Thanks**: All contributors and testers

---

## 📞 Support

- **GitHub Issues**: [https://github.com/OwnerPlugins/SLwebcams/issues](https://github.com/OwnerPlugins/SLwebcams/issues)
- **Enigma2 Forums**: Check the plugin section on popular Enigma2 forums
- **Email**: your-email@example.com

---

## 🙏 Acknowledgments

- Enigma2 community for the excellent framework
- OpenPLi team for the development environment
- All testers who helped improve the plugin

---

**Enjoy watching live webcams from around the world! 🌍📺**
