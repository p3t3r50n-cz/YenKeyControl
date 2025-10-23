#!/usr/bin/env python3
"""
YenKey CLI Utility
Command-line interface for "Yenkey YKB3700 Rogue" keyboard - backlight and key colors and remapping control

Author: Petr Palacky
AI Collaboration: DeepSeek, GPT
Date: 2025
Version: 0.2

Project page: https://github.com/p3t3r50n-cz/YenKeyControl

Description:
Comprehensive Python utility for controlling YenKey keyboard features through
reverse-engineered USB protocol. Supports backlight effects, per-key RGB coloring,
key remapping, special multimedia functions, and FN key customization.

Features:
- 20+ backlight effects with customizable speed and brightness
- Per-key RGB coloring with group support (ALL_F, ALL_MOD, ALL_WASD, etc.)
- Complete key remapping including modifiers and special functions
- Multimedia controls (volume, playback, brightness)
- Mouse emulation and application launchers
- FN key repositioning and customization
- Read current settings directly from keyboard

License:
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Disclaimer:
This software is the result of reverse engineering and is provided for
educational and personal use. Respect your hardware manufacturer's
warranties and terms of service. The authors are not responsible for
any damage caused by using this software.

USB Protocol:
Vendor ID: 0x3151, Product ID: 0x4002
Interface: 1, Packet size: 64 bytes
"""

import argparse
import sys
import re
import usb.core
import usb.util
import time
import glob
import os
import json
from pathlib import Path

IFACE = 1

CONFIG_DIR = Path.home() / '.config' / 'yenkey'

# Preset configurations
PRESETS = {
    'office': {
        'name': 'Office Work',
        'description': 'Clean professional setup for office work with highlighted function keys',
        'mode': 'user',
        'brightness': 3,
        'key-colors': [
            'ALL:silver',             # Default color for all keys
            'ALL_F:yellow',           # Function keys for shortcuts
            'ALL_MOD:lightblue',      # Modifiers highlighted
            'ALL_NAV:336699',         # Navigation keys in blue-gray
            'KEY_ENTER:green',        # Enter key stands out
            'KEY_SPACE:royalblue'     # Space bar accent
        ],
        'key-remap': [
            'KEY_CAPSLOCK:KEY_LEFTCTRL',  # CapsLock as Ctrl (ergonomic)
            'KEY_F1:KEY_LEFTALT:KEY_F1',  # Alt+F1 shortcut
            'KEY_F2:KEY_LEFTALT:KEY_F2'   # Alt+F2 shortcut
        ]
    },
    'gaming': {
        'name': 'Gaming',
        'description': 'Dynamic gaming setup with highlighted gaming keys',
        'mode': 'user',
        'brightness': 4,
        'key-colors': [
            'ALL:black',             # Default color for all keys
            'ALL_WASD:red',
            'ALL_ARROWS:yellow',
            'KEY_F1:orange',
            'KEY_F12:green',
        ],
        'key-remap': [
            'KEY_CAPSLOCK:KEY_LEFTSHIFT',  # Gaming-friendly CapsLock as Shift
            'KEY_F1:GAME_MODE',            # Quick game mode toggle
            'KEY_F12:KEY_LEFTCTRL:KEY_S'   # Quick save shortcut
        ]
    },
    'programming': {
        'name': 'Programming',
        'description': 'Focused setup for coding with highlighted programming keys',
        'mode': 'user',
        'brightness': 3,
        'key-colors': [
            'ALL:silver',                   # Default color for all keys
            'ALL_NUM:lightyellow',          # Numbers
            'ALL_F:cyan',                   # Function keys for IDE shortcuts
            'ALL_NAV:lightblue',            # Navigation keys
            'KEY_LEFTBRACE:magenta',        # Brackets highlighted
            'KEY_RIGHTBRACE:magenta',
            'KEY_LEFTBRACE:magenta',
            'KEY_RIGHTBRACE:magenta',
            'KEY_SEMICOLON:lightgreen',     # Semicolon for coding
            'KEY_APOSTROPHE:lightgreen',    # Quotes for strings
            'KEY_ENTER:blue',               # Enter key
            'KEY_TAB:orange',               # Tab for indentation
            'KEY_BACKSLASH:purple',         # Backslash for paths
            'KEY_GRAVE:darkcyan',           # Backtick for templates
            'KEY_DELETE:red',
            'KEY_BACKSPACE:red',
            'KEY_ESC:orange',
        ],
        'key-remap': [
            'KEY_CAPSLOCK:KEY_ESC',         # Vim-style Esc on CapsLock
            'KEY_F12:KEY_LEFTCTRL:KEY_S',   # Quick save
            'KEY_F5:KEY_LEFTCTRL:KEY_R'     # Run/debug shortcut
        ]
    },
    'writing': {
        'name': 'Writing',
        'description': 'Calm setup for writing and documentation',
        'mode': 'staticfade',
        'submode': None,
        'brightness': 2,
        'speed': 2,
        'color': 'silver',
        'key-colors': [],  # Only supported with mode 'user'
        'key-remap': [
            'KEY_F5:KEY_LEFTCTRL:KEY_S',    # Quick save
            'KEY_F7:KEY_LEFTCTRL:KEY_Z',    # Undo shortcut
            'KEY_F8:KEY_LEFTCTRL:KEY_Y'     # Redo shortcut
        ]
    },
    'media': {
        'name': 'Media Center',
        'description': 'Media controls with relaxing light effects',
        'mode': 'breath',
        'submode': None,
        'brightness': 2,
        'speed': 1,
        'color': 'purple',
        'key-colors': [],  # Breathing mode override
        'key-remap': [
            'KEY_F1:VOLUME_DOWN',
            'KEY_F2:VOLUME_UP',
            'KEY_F3:MUTE',
            'KEY_F4:PLAY_PAUSE',
            'KEY_F5:PREV_TRACK',
            'KEY_F6:NEXT_TRACK',
            'KEY_F7:BROWSER_HOME'  # Quick media browser access
        ]
    },
    'presentation': {
        'name': 'Presentation',
        'description': 'Professional setup for presentations with discrete lighting',
        'mode': 'user',
        'submode': None,
        'brightness': 1,
        'speed': 2,
        'key-colors': [
            'ALL:darkblue',
            'ALL_ARROWS:white',     # Only arrows visible for slide control
            'KEY_F5:red',           # F5 for start presentation
            'KEY_ESC:red'           # ESC to exit
        ],
        'key-remap': [
            'KEY_F5:KEY_LEFTCTRL:KEY_F5',  # Start presentation
            'KEY_PAGEUP:KEY_LEFT',         # Previous slide
            'KEY_PAGEDOWN:KEY_RIGHT'       # Next slide
        ]
    },
    'night': {
        'name': 'Night Mode',
        'description': 'Low-light setup for nighttime use',
        'mode': 'user',
        'submode': None,
        'brightness': 1,
        'speed': 2,
        'key-colors': [
            'ALL:darkred',
            'ALL_MOD:violet',       # Only modifiers slightly visible
            'ALL_ARROWS:darkmagenta',
            'KEY_ESC:red'
        ],
        'key-remap': []  # No remapping needed
    },
    'minimal': {
        'name': 'Minimal',
        'description': 'Clean minimal setup with essential keys only',
        'mode': 'static',
        'submode': None,
        'brightness': 1,
        'speed': 2,
        'color': 'white',
    },
    'productivity': {
        'name': 'Productivity',
        'description': 'Optimized for multitasking and productivity apps',
        'mode': 'user',
        'submode': None,
        'brightness': 3,
        'speed': 2,
        'key-colors': [
            'ALL:teal',
            'ALL_F:orange',         # Function keys for app switching
            'ALL_MOD:teal',         # Modifiers match theme
            'ALL_NAV:steelblue',    # Navigation cluster
            'KEY_LEFTMETA:gold',    # Windows/Super key highlighted
            'KEY_TAB:lightblue'     # Tab for window switching
        ],
        'key-remap': [
            'KEY_CAPSLOCK:KEY_LEFTMETA',   # Quick app launcher
            'KEY_F1:KEY_LEFTALT:KEY_TAB',  # Alt+Tab shortcut
            'KEY_F2:KEY_LEFTMETA:KEY_D'    # Show desktop
        ]
    }
}

# Named colors - Web safe colors and common names
NAMED_COLORS = {
    # Basic colors
    'black': '000000', 'white': 'ffffff', 'red': 'ff0000', 'green': '00ff00', 
    'blue': '0000ff', 'yellow': 'ffff00', 'cyan': '00ffff', 'magenta': 'ff00ff',

    # Extended basic colors
    'orange': 'ffa500', 'purple': '800080', 'pink': 'ffc0cb', 'brown': 'a52a2a',
    'gray': '808080', 'grey': '808080', 'maroon': '800000', 'olive': '808000',
    'lime': '00ff00', 'aqua': '00ffff', 'teal': '008080', 'navy': '000080',
    'fuchsia': 'ff00ff',

    # Light colors
    'lightred': 'ff6666', 'lightgreen': '66ff66', 'lightblue': '6666ff',
    'lightyellow': 'ffff66', 'lightcyan': '66ffff', 'lightmagenta': 'ff66ff',
    'lightorange': 'ffb366', 'lightpink': 'ffb6c1',

    # Dark colors  
    'darkred': '8b0000', 'darkgreen': '006400', 'darkblue': '00008b',
    'darkyellow': 'cccc00', 'darkcyan': '008b8b', 'darkmagenta': '8b008b',
    'darkorange': 'ff8c00', 'darkpurple': '4b0082',

    # Pastel colors
    'pastelred': 'ff7f7f', 'pastelgreen': '7fff7f', 'pastelblue': '7f7fff',
    'pastelyellow': 'ffff7f', 'pastelorange': 'ffbf7f', 'pastelpink': 'ffb6c1',

    # Special colors
    'gold': 'ffd700', 'silver': 'c0c0c0', 'bronze': 'cd7f32', 'violet': 'ee82ee',
    'indigo': '4b0082', 'turquoise': '40e0d0', 'coral': 'ff7f50', 'salmon': 'fa8072',
    'khaki': 'f0e68c', 'lavender': 'e6e6fa', 'plum': 'dda0dd', 'orchid': 'da70d6',
    'steelblue': '4682b4',

    # Game colors
    'skyblue': '87ceeb', 'forestgreen': '228b22', 'firebrick': 'b22222',
    'royalblue': '4169e1', 'crimson': 'dc143c', 'tomato': 'ff6347',
    'springgreen': '00ff7f', 'deepskyblue': '00bfff', 'dodgerblue': '1e90ff',
    'mediumspringgreen': '00fa9a'
}

# Debug levels
DEBUG_LEVELS = {
    'NONE': 0,
    'ERROR': 1,
    'WARNING': 2,
    'INFO': 3,
    'DEBUG': 4,
    'VERBOSE': 5
}

# Global debug settings
DEBUG_LEVEL = DEBUG_LEVELS['INFO']

def debugPrint(level, message, *args):
    """Global debug print function with levels"""
    if DEBUG_LEVEL >= level:
        prefix = {
            DEBUG_LEVELS['ERROR']: 'ERROR:',
            DEBUG_LEVELS['WARNING']: 'WARNING:',
            DEBUG_LEVELS['INFO']: 'INFO:',
            DEBUG_LEVELS['DEBUG']: 'DEBUG:',
            DEBUG_LEVELS['VERBOSE']: 'VERBOSE:'
        }.get(level, '')
        print(f"{prefix} {message}", *args)

def setDebugLevel(levelName):
    """Set global debug level by name"""
    global DEBUG_LEVEL
    levelName = levelName.upper()
    if levelName in DEBUG_LEVELS:
        DEBUG_LEVEL = DEBUG_LEVELS[levelName]
        debugPrint(DEBUG_LEVELS['DEBUG'], f"Debug level set to: {levelName}")
    else:
        print(f"Unknown debug level: {levelName}. Available: {', '.join(DEBUG_LEVELS.keys())}")

# YenkeeProto provides low-level USB HID communication helpers for the keyboard.
class YenkeeProto:
    """Protocol handler for YenKey keyboard communication"""

    def __init__(self, vid=0x3151, pid=0x4002):
        self.vid = vid
        self.pid = pid
        self.dev = None
        self.sysfs_path = None

    def getSysfsPath(self, vid, pid):
        """Find sysfs path for USB device by vendor and product ID"""
        vid_hex = f"{vid:04x}"
        pid_hex = f"{pid:04x}"

        for path in glob.glob("/sys/bus/usb/drivers/usb/*/uevent"):
            try:
                with open(path, "r") as f:
                    content = f.read()
                if f"PRODUCT={vid_hex}/{pid_hex}/" in content:
                    return os.path.basename(os.path.dirname(path))
            except:
                continue
        return None

    def connect(self):
        """Connect to keyboard device"""
        try:
            self.dev = usb.core.find(idVendor=self.vid, idProduct=self.pid)
            if not self.dev:
                print("Keyboard not found")
                return False

            debugPrint(DEBUG_LEVELS['DEBUG'], f"Keyboard found")
            self.sysfs_path = self.getSysfsPath(self.vid, self.pid)
            return self._setupCommunication()

        except Exception as e:
            debugPrint(DEBUG_LEVELS['ERROR'], f"Connection error: {e}")
            return False

    def _setupCommunication(self):
        """Setup USB communication on Interface 0"""
        try:
            if self.dev.is_kernel_driver_active(0):
                self.dev.detach_kernel_driver(0)
            if self.dev.is_kernel_driver_active(1):
                self.dev.detach_kernel_driver(1)
            return True
        except Exception as e:
            debugPrint(DEBUG_LEVELS['ERROR'], f"Communication setup error: {e}")
            return False

    def setReport(self, data, description="Command"):
        """Send SET_REPORT command to keyboard"""
        if not self.connect():
            sys.exit(1)

        if not self.dev:
            print("Device not connected")
            return False

        try:
            hex_clean = data.replace(" ", "")
            main_data = bytes.fromhex(hex_clean)

            debugPrint(DEBUG_LEVELS['DEBUG'], f"Sending: {description} [{hex_clean}]")

            if len(main_data) > 64:
                print("  Warning: Data longer than 64 bytes, truncating")
                main_data = main_data[:64]

            if len(main_data) < 64:
                checksum = bytes([(0x100 - ((sum(main_data) + 1) & 0xFF)) & 0xFF])
                main_data += checksum

            main_data += b"\x00" * (64 - len(main_data))

            response = self.dev.ctrl_transfer(0x21, 0x09, 0x0300, IFACE, main_data)
            debugPrint(DEBUG_LEVELS['DEBUG'], f"  Command sent successfully\n")
            return response

        except Exception as e:
            debugPrint(DEBUG_LEVELS['ERROR'], f"  SET_REPORT error: {e}")
            return False

    def getReport(self, length=64, description="Command", report_id=0x00):
        """Send GET_REPORT request and receive data from keyboard"""
        if not self.connect():
            sys.exit(1)

        if not self.dev:
            print("Device not connected")
            return False

        try:
            # USB HID GET_REPORT request
            result = self.dev.ctrl_transfer(
                0xA1,                # bmRequestType (IN/Class/Interface)
                0x01,                # bRequest (GET_REPORT)
                0x0300 | report_id,  # wValue (Feature report + Report ID)
                IFACE,               # wIndex (Interface)
                length               # wLength (data size)
            )
            return bytes(result)

        except Exception as e:
            debugPrint(DEBUG_LEVELS['ERROR'], f"  GET_REPORT Error: {e}")
            return None

    def sendMultiplePackets(self, packets):
        """Send multiple packets sequentially with delay"""
        if not self.connect():
            sys.exit(1)

        success_count = 0
        for i, (hex_string, description) in enumerate(packets, 1):
            debugPrint(DEBUG_LEVELS['DEBUG'], f"Packet {i}/{len(packets)}:")
            if self.setReport(hex_string, description):
                success_count += 1
            time.sleep(0.1)  # Small delay between packets
        debugPrint(DEBUG_LEVELS['DEBUG'], f"Total successful: {success_count}/{len(packets)}")
        return success_count == len(packets)

    def disconnect(self):
        """Clean up USB communication"""
        if self.dev:
            try:
                self.dev.attach_kernel_driver(1)
                self.dev.attach_kernel_driver(0)
            except:
                pass
            if self.dev:
                usb.util.dispose_resources(self.dev)
                self.dev = None
            if self.sysfs_path:
                try:
                    # Rebind USB device to refresh connection
                    with open("/sys/bus/usb/drivers/usb/unbind", "w") as f:
                        f.write(self.sysfs_path)
                    with open("/sys/bus/usb/drivers/usb/bind", "w") as f:
                        f.write(self.sysfs_path)
                except:
                    pass

class YenKeyCLI:
    """Main CLI controller for YenKey keyboard"""

    def __init__(self):

        self.backlightSettings = {}
        self.keyColorSettings = {}
        self.keyRemapSettings = {}

        self.presets = PRESETS

        # Mode mapping - backlight effects
        self.modes = {
            'off': 0x00, 'static': 0x01, 'breath': 0x02, 'neon': 0x03,
            'wave': 0x04, 'waterdrop': 0x05, 'rain': 0x06, 'snake': 0x07,
            'fadeout': 0x08, 'spiral': 0x09, 'sinusoid': 0x0a, 'kaleidoscope': 0x0b,
            'linear': 0x0c, 'user': 0x0d, 'laser': 0x0e, 'roundwave': 0x0f,
            'shining': 0x10, 'rain2': 0x11, 'horizontal': 0x12, 'staticfade': 0x13,
            'music-edm': 0x14,
            #'screen1': 0x15,
            'music-standard': 0x16, 'surf': 0x17, 'skew': 0x18
        }

        # Effect submodes for directional/pattern variants
        self.modeSubmodes = {
            'wave': {'right': 0, 'left': 1, 'down': 2, 'up': 3},
            'snake': {'linear': 0, 'tocenter': 1},
            'kaleidoscope': {'fromcenter': 0, 'tocenter': 1},
            'roundwave': {'counterclockwise': 0, 'clockwise': 1},
            'music-edm': {'upright': 0, 'separate': 1, 'cross': 2}
        }

        # Predefined colors and their flags
        self.predefinedColors = {
            'red': (0x00, 0xFF, 0x00, 0x00),
            'green': (0x01, 0x00, 0xFF, 0x00),
            'blue': (0x02, 0x00, 0x00, 0xFF),
            'orange': (0x03, 0xFF, 0x69, 0x00),
            'pink': (0x04, 0xFF, 0x14, 0x93),
            'yellow': (0x05, 0xFF, 0xFF, 0x00),
            'white': (0x06, 0xFF, 0xFF, 0xFF),
            'rainbow': (0x07, 0x00, 0x00, 0x00)  # Special case
        }

        self.keyPositions = {
            0: 'KEY_ESC', 1: 'KEY_GRAVE', 2: 'KEY_TAB', 3: 'KEY_CAPSLOCK',
            4: 'KEY_LEFTSHIFT', 5: 'KEY_LEFTCTRL', 6: 'RESERVED',
            7: 'KEY_1', 8: 'KEY_Q', 9: 'KEY_A', 10: 'KEY_102ND', 11: 'RESERVED',
            12: 'KEY_F1', 13: 'KEY_2', 14: 'KEY_W', 15: 'KEY_S', 16: 'KEY_Z',
            17: 'KEY_LEFTMETA', 18: 'KEY_F2', 19: 'KEY_3', 20: 'KEY_E',
            21: 'KEY_D', 22: 'KEY_X', 23: 'KEY_LEFTALT', 24: 'KEY_F3',
            25: 'KEY_4', 26: 'KEY_R', 27: 'KEY_F', 28: 'KEY_C', 29: 'RESERVED',
            30: 'KEY_F4', 31: 'KEY_5', 32: 'KEY_T', 33: 'KEY_G', 34: 'KEY_V',
            35: 'RESERVED', 36: 'KEY_F5', 37: 'KEY_6', 38: 'KEY_Y', 39: 'KEY_H',
            40: 'KEY_B', 41: 'KEY_SPACE', 42: 'KEY_F6', 43: 'KEY_7', 44: 'KEY_U',
            45: 'KEY_J', 46: 'KEY_N', 47: 'KEY_RIGHTALT', 48: 'KEY_F7',
            49: 'KEY_8', 50: 'KEY_I', 51: 'KEY_K', 52: 'KEY_M', 53: 'KEY_FN',
            54: 'KEY_F8', 55: 'KEY_9', 56: 'KEY_O', 57: 'KEY_L', 58: 'KEY_COMMA',
            59: 'KEY_RIGHTCTRL', 60: 'KEY_F9', 61: 'KEY_0', 62: 'KEY_P',
            63: 'KEY_SEMICOLON', 64: 'KEY_DOT', 65: 'KEY_LEFT', 66: 'KEY_F10',
            67: 'KEY_MINUS', 68: 'KEY_LEFTBRACE', 69: 'KEY_APOSTROPHE',
            70: 'KEY_SLASH', 71: 'KEY_DOWN', 72: 'KEY_F11', 73: 'KEY_EQUAL',
            74: 'KEY_RIGHTBRACE', 75: 'KEY_HASHTILDE', 76: 'KEY_RIGHTSHIFT',
            77: 'KEY_RIGHT', 78: 'KEY_F12', 79: 'KEY_BACKSPACE',
            80: 'KEY_BACKSLASH', 81: 'KEY_ENTER', 82: 'KEY_UP', 83: 'KEY_INSERT',
            84: 'KEY_PRINTSCREEN', 85: 'KEY_HOME', 86: 'KEY_END', 87: 'KEY_PAGEUP',
            88: 'KEY_PAGEDOWN', 89: 'KEY_DELETE',
            90: 'RESERVED', 91: 'RESERVED', 92: 'RESERVED', 93: 'RESERVED',
            94: 'RESERVED', 95: 'RESERVED', 96: 'RESERVED', 97: 'RESERVED',
            98: 'RESERVED', 99: 'RESERVED', 100: 'RESERVED', 101: 'RESERVED',
            102: 'RESERVED', 103: 'RESERVED', 104: 'RESERVED', 105: 'RESERVED',
            106: 'RESERVED', 107: 'RESERVED', 108: 'RESERVED', 109: 'RESERVED',
            110: 'RESERVED', 111: 'RESERVED', 112: 'RESERVED', 113: 'RESERVED',
            114: 'RESERVED', 115: 'RESERVED', 116: 'RESERVED', 117: 'RESERVED',
            118: 'RESERVED', 119: 'RESERVED', 120: 'RESERVED', 121: 'RESERVED',
            122: 'RESERVED', 123: 'RESERVED', 124: 'RESERVED', 125: 'RESERVED',
            126: 'RESERVED', 127: 'RESERVED'
        }

        # Modifier key codes
        self.modifierCodes = {
            'KEY_LEFTCTRL': 0xe0, 'KEY_RIGHTCTRL': 0xe4,
            'KEY_LEFTSHIFT': 0xe1, 'KEY_RIGHTSHIFT': 0xe5, 
            'KEY_LEFTALT': 0xe2, 'KEY_RIGHTALT': 0xe6,
            'KEY_LEFTMETA': 0xe3, 'KEY_RIGHTMETA': 0xe7
        }

        # USB HID scan code mapping
        self.scanCodes = {
            # Common alphabetic keys
            'KEY_ESC': 0x29, 'KEY_1': 0x1e, 'KEY_2': 0x1f, 'KEY_3': 0x20,
            'KEY_4': 0x21, 'KEY_5': 0x22, 'KEY_6': 0x23, 'KEY_7': 0x24,
            'KEY_8': 0x25, 'KEY_9': 0x26, 'KEY_0': 0x27, 'KEY_MINUS': 0x2d,
            'KEY_EQUAL': 0x2e, 'KEY_BACKSPACE': 0x2a, 'KEY_TAB': 0x2b,
            'KEY_Q': 0x14, 'KEY_W': 0x1a, 'KEY_E': 0x08, 'KEY_R': 0x15,
            'KEY_T': 0x17, 'KEY_Y': 0x1c, 'KEY_U': 0x18, 'KEY_I': 0x0c,
            'KEY_O': 0x12, 'KEY_P': 0x13, 'KEY_LEFTBRACE': 0x2f,
            'KEY_RIGHTBRACE': 0x30, 'KEY_A': 0x04, 'KEY_S': 0x16,
            'KEY_D': 0x07, 'KEY_F': 0x09, 'KEY_G': 0x0a, 'KEY_H': 0x0b,
            'KEY_J': 0x0d, 'KEY_K': 0x0e, 'KEY_L': 0x0f, 'KEY_SEMICOLON': 0x33,
            'KEY_APOSTROPHE': 0x34, 'KEY_GRAVE': 0x35, 'KEY_BACKSLASH': 0x31,
            'KEY_Z': 0x1d, 'KEY_X': 0x1b, 'KEY_C': 0x06, 'KEY_V': 0x19,
            'KEY_B': 0x05, 'KEY_N': 0x11, 'KEY_M': 0x10, 'KEY_COMMA': 0x36,
            'KEY_DOT': 0x37, 'KEY_SLASH': 0x38,

            # Function keys
            'KEY_F1': 0x3a, 'KEY_F2': 0x3b, 'KEY_F3': 0x3c, 'KEY_F4': 0x3d,
            'KEY_F5': 0x3e, 'KEY_F6': 0x3f, 'KEY_F7': 0x40, 'KEY_F8': 0x41,
            'KEY_F9': 0x42, 'KEY_F10': 0x43, 'KEY_F11': 0x44, 'KEY_F12': 0x45,

            # Navigation keys
            'KEY_HOME': 0x4a, 'KEY_END': 0x4d, 'KEY_PAGEUP': 0x4b, 'KEY_PAGEDOWN': 0x4e,
            'KEY_UP': 0x52, 'KEY_DOWN': 0x51, 'KEY_LEFT': 0x50, 'KEY_RIGHT': 0x4f,

            # Special keys
            'KEY_ENTER': 0x28, 'KEY_SPACE': 0x2c, 'KEY_CAPSLOCK': 0x39,
            'KEY_INSERT': 0x49, 'KEY_DELETE': 0x4c, 'KEY_PRINTSCREEN': 0x46,
            'KEY_SCROLLLOCK': 0x47, 'KEY_PAUSE': 0x48,

            # Multimedia keys
            'KEY_MUTE': 0x7f, 'KEY_VOLUMEUP': 0x80, 'KEY_VOLUMEDOWN': 0x81,
            'KEY_PLAYPAUSE': 0xe8, 'KEY_STOPCD': 0xe9, 'KEY_PREVIOUSSONG': 0xea,
            'KEY_NEXTSONG': 0xeb, 'KEY_EJECTCD': 0xec, 'KEY_WWW': 0xf0,
            'KEY_BACK': 0xf1, 'KEY_FORWARD': 0xf2, 'KEY_CALC': 0xfb,
            'KEY_SLEEP': 0xf8, 'KEY_COFFEE': 0xf9, 'KEY_REFRESH': 0xfa,
            'KEY_MAIL': 0xfd, 'KEY_SEARCH': 0xfe,
            
            # Language-specific keys
            'KEY_HASHTILDE': 0x32, 'KEY_102ND': 0x64,
        }

        # Special function codes (multimedia, system controls, etc.)
        self.specialCodes = {
            # FN key
            'KEY_FN': [0x0a, 0x01, 0x00, 0x00],

            # Media Controls
            'PLAY_PAUSE': [0x03, 0x00, 0xcd, 0x00],
            'STOP': [0x03, 0x00, 0xb7, 0x00],
            'PREV_TRACK': [0x03, 0x00, 0xb6, 0x00],
            'NEXT_TRACK': [0x03, 0x00, 0xb5, 0x00],
            'VOLUME_DOWN': [0x03, 0x00, 0xea, 0x00],
            'VOLUME_UP': [0x03, 0x00, 0xe9, 0x00],
            'MUTE': [0x03, 0x00, 0xe2, 0x00],
            'MIC_MUTE': [0x03, 0x00, 0x93, 0x02],
            'AUDIO_SOURCE_NEXT': [0x03, 0x00, 0x94, 0x02],

            # Display Controls
            'BRIGHTNESS_UP': [0x03, 0x00, 0x6f, 0x00],
            'BRIGHTNESS_DOWN': [0x03, 0x00, 0x70, 0x00],

            # Application Controls
            'APP_MAIL': [0x03, 0x00, 0x8a, 0x01],
            'APP_CALENDAR': [0x03, 0x00, 0x8d, 0x01],
            'APP_CALCULATOR': [0x03, 0x00, 0x92, 0x01],
            'APP_MEDIA_PLAYER': [0x03, 0x00, 0x83, 0x01],

            # Browser Controls
            'BROWSER_BACK': [0x03, 0x00, 0x24, 0x02],
            'BROWSER_FORWARD': [0x03, 0x00, 0x25, 0x02],
            'BROWSER_REFRESH': [0x03, 0x00, 0x27, 0x02],
            'BROWSER_STOP': [0x03, 0x00, 0x26, 0x02],
            'BROWSER_FAVORITES': [0x03, 0x00, 0x2a, 0x02],

            # System controls
            'SEARCH': [0x03, 0x00, 0x21, 0x02],
            'BROWSER_HOME': [0x03, 0x00, 0x23, 0x02],

            # Gaming/Keyboard Controls
            'GAME_MODE': [0x03, 0x00, 0x85, 0x02],
            'MACRO_RECORD': [0x03, 0x00, 0x86, 0x02],
            'LED_EFFECT_NEXT': [0x03, 0x00, 0x87, 0x02],
            'LED_BRIGHTNESS_UP': [0x03, 0x00, 0x88, 0x02],
            'LED_BRIGHTNESS_DOWN': [0x03, 0x00, 0x89, 0x02],

            # Mouse Functions
            'MOUSE_LEFT': [0x01, 0x00, 0xf0, 0x00],
            'MOUSE_RIGHT': [0x01, 0x00, 0xf1, 0x00],
            'MOUSE_CENTER': [0x01, 0x00, 0xf2, 0x00],
            'MOUSE_SCROLL_UP': [0x01, 0x00, 0xf5, 0x01],
            'MOUSE_SCROLL_DOWN': [0x01, 0x00, 0xf5, 0xff],
        }

        # Complete default remap data for all 126 positions (4 bytes each)
        self.defaultRemapData = [
            # Packet 0 - Positions 0-13
            0x00, 0x00, 0x29, 0x00,  # 0: ESC
            0x00, 0x00, 0x35, 0x00,  # 1: Grave
            0x00, 0x00, 0x2b, 0x00,  # 2: Tab
            0x00, 0x00, 0x39, 0x00,  # 3: CapsLock
            0x00, 0x00, 0xe1, 0x00,  # 4: L-Shift
            0x00, 0x00, 0xe0, 0x00,  # 5: L-Ctrl
            0x00, 0x00, 0x00, 0x00,  # 6: DISABLED
            0x00, 0x00, 0x1e, 0x00,  # 7: 1
            0x00, 0x00, 0x14, 0x00,  # 8: Q
            0x00, 0x00, 0x04, 0x00,  # 9: A
            0x00, 0x00, 0x64, 0x00,  # 10: KEY_102ND
            0x00, 0x00, 0x00, 0x00,  # 11: DISABLED
            0x00, 0x00, 0x3a, 0x00,  # 12: F1
            0x00, 0x00, 0x1f, 0x00,  # 13: 2

            # Packet 1 - Positions 14-27
            0x00, 0x00, 0x1a, 0x00,  # 14: W
            0x00, 0x00, 0x16, 0x00,  # 15: S
            0x00, 0x00, 0x1d, 0x00,  # 16: Z
            0x00, 0x00, 0xe3, 0x00,  # 17: L-Meta
            0x00, 0x00, 0x3b, 0x00,  # 18: F2
            0x00, 0x00, 0x20, 0x00,  # 19: 3
            0x00, 0x00, 0x08, 0x00,  # 20: E
            0x00, 0x00, 0x07, 0x00,  # 21: D
            0x00, 0x00, 0x1b, 0x00,  # 22: X
            0x00, 0x00, 0xe2, 0x00,  # 23: L-Alt
            0x00, 0x00, 0x3c, 0x00,  # 24: F3
            0x00, 0x00, 0x21, 0x00,  # 25: 4
            0x00, 0x00, 0x15, 0x00,  # 26: R
            0x00, 0x00, 0x09, 0x00,  # 27: F

            # Packet 2 - Positions 28-41
            0x00, 0x00, 0x06, 0x00,  # 28: C
            0x00, 0x00, 0x00, 0x00,  # 29: DISABLED
            0x00, 0x00, 0x3d, 0x00,  # 30: F4
            0x00, 0x00, 0x22, 0x00,  # 31: 5
            0x00, 0x00, 0x17, 0x00,  # 32: T
            0x00, 0x00, 0x0a, 0x00,  # 33: G
            0x00, 0x00, 0x19, 0x00,  # 34: V
            0x00, 0x00, 0x00, 0x00,  # 35: DISABLED
            0x00, 0x00, 0x3e, 0x00,  # 36: F5
            0x00, 0x00, 0x23, 0x00,  # 37: 6
            0x00, 0x00, 0x1c, 0x00,  # 38: Y
            0x00, 0x00, 0x0b, 0x00,  # 39: H
            0x00, 0x00, 0x05, 0x00,  # 40: B
            0x00, 0x00, 0x2c, 0x00,  # 41: Space

            # Packet 3 - Positions 42-55
            0x00, 0x00, 0x3f, 0x00,  # 42: F6
            0x00, 0x00, 0x24, 0x00,  # 43: 7
            0x00, 0x00, 0x18, 0x00,  # 44: U
            0x00, 0x00, 0x0d, 0x00,  # 45: J
            0x00, 0x00, 0x11, 0x00,  # 46: N
            0x00, 0x00, 0xe6, 0x00,  # 47: R-Alt
            0x00, 0x00, 0x40, 0x00,  # 48: F7
            0x00, 0x00, 0x25, 0x00,  # 49: 8
            0x00, 0x00, 0x0c, 0x00,  # 50: I
            0x00, 0x00, 0x0e, 0x00,  # 51: K
            0x00, 0x00, 0x10, 0x00,  # 52: M
            0x0a, 0x01, 0x00, 0x00,  # 53: Fn (special value)
            0x00, 0x00, 0x41, 0x00,  # 54: F8
            0x00, 0x00, 0x26, 0x00,  # 55: 9

            # Packet 4 - Positions 56-69
            0x00, 0x00, 0x12, 0x00,  # 56: O
            0x00, 0x00, 0x0f, 0x00,  # 57: L
            0x00, 0x00, 0x36, 0x00,  # 58: Comma
            0x00, 0x00, 0xe4, 0x00,  # 59: R-Ctrl
            0x00, 0x00, 0x42, 0x00,  # 60: F9
            0x00, 0x00, 0x27, 0x00,  # 61: 0
            0x00, 0x00, 0x13, 0x00,  # 62: P
            0x00, 0x00, 0x33, 0x00,  # 63: Semicolon
            0x00, 0x00, 0x37, 0x00,  # 64: Dot
            0x00, 0x00, 0x50, 0x00,  # 65: Left
            0x00, 0x00, 0x43, 0x00,  # 66: F10
            0x00, 0x00, 0x2d, 0x00,  # 67: Minus
            0x00, 0x00, 0x2f, 0x00,  # 68: LeftBrace
            0x00, 0x00, 0x34, 0x00,  # 69: Apostrophe

            # Packet 5 - Positions 70-83
            0x00, 0x00, 0x38, 0x00,  # 70: Slash
            0x00, 0x00, 0x51, 0x00,  # 71: Down
            0x00, 0x00, 0x44, 0x00,  # 72: F11
            0x00, 0x00, 0x2e, 0x00,  # 73: Equal
            0x00, 0x00, 0x30, 0x00,  # 74: RightBrace
            0x00, 0x00, 0x32, 0x00,  # 75: HashTilde
            0x00, 0x00, 0xe5, 0x00,  # 76: R-Shift
            0x00, 0x00, 0x4f, 0x00,  # 77: Right
            0x00, 0x00, 0x45, 0x00,  # 78: F12
            0x00, 0x00, 0x2a, 0x00,  # 79: Backspace
            0x00, 0x00, 0x31, 0x00,  # 80: Backslash
            0x00, 0x00, 0x28, 0x00,  # 81: Enter
            0x00, 0x00, 0x52, 0x00,  # 82: Up
            0x00, 0x00, 0x49, 0x00,  # 83: Insert

            # Packet 6 - Positions 84-97
            0x00, 0x00, 0x46, 0x00,  # 84: PrintScreen
            0x00, 0x00, 0x4a, 0x00,  # 85: Home
            0x00, 0x00, 0x4d, 0x00,  # 86: End
            0x00, 0x00, 0x4b, 0x00,  # 87: PageUp
            0x00, 0x00, 0x4e, 0x00,  # 88: PageDown
            0x00, 0x00, 0x4c, 0x00,  # 89: Delete
            # Positions 90-97: DISABLED
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,

            # Packets 7-8 - Positions 98-125: DISABLED
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ]

        self.setupArgparse()

    def setupArgparse(self):
        """Setup argument parser with comprehensive help"""
        self.parser = argparse.ArgumentParser(
            description='YenKey Keyboard Control Utility - Complete backlight and key remapping control',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._getHelpEpilog()
        )

        # Backlight modes group
        backlight_group = self.parser.add_argument_group('Backlight Controls')
        backlight_group.add_argument('--mode', 
                                   choices=list(self.modes.keys()),
                                   help='Set backlight mode')
        backlight_group.add_argument('--submode', 
                                   help='Set mode submode (direction/variant)')
        backlight_group.add_argument('--color', 
                                   help='Set backlight color (predefined, named color, or RRGGBB hex)')
        backlight_group.add_argument('--speed', type=int, choices=range(1, 12),
                                   help='Set animation speed (1=fast, 2=slow, 3=very slow, 4=slowest, 5=stopped, 6=fastest .. 11=ultra fast)')
        backlight_group.add_argument('--brightness', type=int, choices=[0, 1, 2, 3, 4], 
                                   help='Set backlight brightness (0=off, 1=dim, 4=brightest)')

        # Key-specific controls group
        key_group = self.parser.add_argument_group('Key-specific Controls')
        key_group.add_argument('--key-color', action='append', 
                             help='Set individual key colors for user mode (KEY:COLOR,KEY2:COLOR)')
        key_group.add_argument('--key-remap', action='append', 
                             help='Remap key(s) (FORMATS: KEY:disable, KEY:TARGET, KEY:MOD:TARGET, KEY:MOD1:MOD2:TARGET, KEY:HEXVALUE)')

        # Reset commands group
        reset_group = self.parser.add_argument_group('Reset Commands')
        reset_group.add_argument('--factory-reset', action='store_true', 
                               help='Reset keyboard to factory settings')
        reset_group.add_argument('--keymap-reset', action='store_true', 
                               help='Reset key mapping to default')

        # Read config commands group
        read_group = self.parser.add_argument_group('Read Config Commands')
        read_group.add_argument('--read-settings', action='store_true',
                              help='Read all current settings from keyboard')
        read_group.add_argument('--read-backlight', action='store_true',
                              help='Read global backlight settings')
        read_group.add_argument('--read-key-colors', action='store_true',
                              help='Read per-key RGB color settings')
        read_group.add_argument('--read-key-remap', action='store_true',
                              help='Read key remapping settings')

        # Listing commands group
        listing_group = self.parser.add_argument_group('Listing Commands')
        listing_group.add_argument('--list-modes', action='store_true', 
                               help='List modes (with submodes) available')
        listing_group.add_argument('--list-colors', action='store_true', 
                               help='List named colors available')
        listing_group.add_argument('--list-keys', action='store_true', 
                               help='List physical keys and functions')
        listing_group.add_argument('--list-standard-keycodes', action='store_true', 
                               help='List standard keycodes available')
        listing_group.add_argument('--list-special-keycodes', action='store_true', 
                               help='List special function keycodes available')

        # Presets commands group
        presets_group = self.parser.add_argument_group('Preset Commands')
        presets_group.add_argument('--preset', 
                                choices=list(self.presets.keys()),
                                help='Apply a preset configuration')
        presets_group.add_argument('--list-presets', action='store_true',
                                help='List all available presets')
        presets_group.add_argument('--save-preset', 
                                help='Save current settings as a new preset into [file]')
        presets_group.add_argument('--load-preset', 
                                help='Apply a preset configuration from [file]')

        # Hardware identification group
        hardware_group = self.parser.add_argument_group('Hardware Identification')
        hardware_group.add_argument('--vid', type=lambda x: int(x, 16), default=0x3151,
                                  help='USB Vendor ID (hexadecimal, default: 0x3151)')
        hardware_group.add_argument('--pid', type=lambda x: int(x, 16), default=0x4002,
                                  help='USB Product ID (hexadecimal, default: 0x4002)')

        # Debug groups
        debugGroup = self.parser.add_argument_group('Debug Options')
        debugGroup.add_argument('--debug',
                               choices=list(DEBUG_LEVELS.keys()),
                               default='INFO',
                               help='Set debug output level (default: INFO)')

    def _getHelpEpilog(self):
        """Generate comprehensive help epilog"""
        return f"""
READ CONFIGURATION COMMANDS:
  --read-settings      - Read all current settings
  --read-backlight     - Read global backlight settings  
  --read-key-colors    - Read per-key RGB colors
  --read-key-remap     - Read key remapping settings

SET CONFIGURATION COMMANDS:
  Backlight settings can be set incrementally - you can use just --mode, --color, etc.

RESET COMMANDS:
  --factory-reset      - Perform complete factory reset. All custom settings will be lost!
  --keymap-reset       - Reset key remapping to default

PRESET COMMANDS:
  --preset NAME        - Apply a preset configuration
  --list-presets       - List all available presets
  --save-preset FILE   - Save current settings as a new preset into file
  --load-preset FILE   - Apply a preset configuration from file

HARDWARE IDENTIFICATION:
  --vid VID            - USB Vendor ID in hexadecimal (default: 0x3151)
  --pid PID            - USB Product ID in hexadecimal (default: 0x4002)

DEBUG OPTIONS:
  --debug LEVEL        - Set debug output level: {', '.join(DEBUG_LEVELS.keys())}

EXAMPLES:
  Incremental backlight control:
    yenkey-cli.py --mode=wave
    yenkey-cli.py --color=blue
    yenkey-cli.py --speed=2

  Key colors (requires '--mode user' to be set first):
    yenkey-cli.py --key-color=ALL:white,KEY_ESC:red \\
                  --key-color=ALL_F1:red,ALL_F2:green,ALL_F3:blue

  Key remapping:
    yenkey-cli.py --key-remap=KEY_CAPSLOCK:KEY_RIGHTCTRL
    yenkey-cli.py --key-remap=KEY_F1:KEY_RIGHTCTRL:KEY_RIGHTALT:KEY_F1
    yenkey-cli.py --key-remap=KEY_F1:00e23a00

  Presets:
    yenkey-cli.py --list-presets
    yenkey-cli.py --preset=gaming
    yenkey-cli.py --preset=office
    yenkey-cli.py --save-preset /path/to/file.preset
    yenkey-cli.py --load-preset /path/to/file.preset

NOTES:
  - Key colors only work in 'user' mode (--mode=user)
  - Each configuration area (Backlight, Key colors, Key remaps) must be run as separate commands:
      Backlight:  --mode --submode --speed --brightness --color
      Key colors: --key-color
      Key remaps: --key-remap
  - Use quotes around complex --key-color and --key-remap values
  - Multiple --key-colors options can be combined
  - Multiple --key-remap options can be combined
  - Run as root/sudo for USB device access
"""

    def factoryReset(self):
        """Reset keyboard to factory settings"""
        hexCmd = "02 00 00 00 00 00 00 fd"
        return self.proto.setReport(hexCmd, "Factory reset")

    def resolveColor(self, color_str):
        """Resolve color string to hex RGB, supporting named colors and hex formats"""
        color_str_lower = color_str.lower()

        # Check named colors
        if color_str_lower in NAMED_COLORS:
            return NAMED_COLORS[color_str_lower]

        # Check hex color (6 digits)
        if re.match(r'^[0-9A-Fa-f]{6}$', color_str):
            return color_str

        # Check rgb: prefix format
        if color_str_lower.startswith('rgb:'):
            hex_part = color_str[4:]
            if re.match(r'^[0-9A-Fa-f]{6}$', hex_part):
                return hex_part

        raise ValueError(f"Unknown color format: {color_str}")

    def readKeyboardBacklightSettings(self):
        """Read global backlight settings (mode, speed, brightness, color) from keyboard"""
        try:
            # Send SET_REPORT for global backlight settings
            setReportData = "87000000000000"
            if not self.proto.setReport(setReportData, 'SET_REPORT: backlight config'):
                print("SET_REPORT for global backlight failed")
                return None

            time.sleep(0.1)

            # Read GET_REPORT response
            response_b = self.proto.getReport(64, 'GET_REPORT: backlight config')
            response = bytes(response_b)
            if not response:
                print("GET_REPORT for global backlight failed")
                return None

            debugPrint(DEBUG_LEVELS['DEBUG'], f"Global backlight response: {response.hex()}")

            # Parse response and update current settings
            if len(response) >= 7:
                self.backlightSettings.update({
                    'mode': response[1],
                    'speed': response[2],
                    'brightness': response[3],
                    #'submode_color_flags': response[4],
                    'submode': (response[4] >> 4) & 0x0F,
                    'color_flag': response[4] & 0x0F,
                    'r': response[5],
                    'g': response[6],
                    'b': response[7] if len(response) > 7 else 0
                })

                debugPrint(DEBUG_LEVELS['DEBUG'], f"Current backlight settings: {self.backlightSettings}")
                return True
            else:
                debugPrint(DEBUG_LEVELS['ERROR'], f"Unexpected response length: {len(response)}")
                return None

        except Exception as e:
            debugPrint(DEBUG_LEVELS['ERROR'], f"Error reading global backlight: {e}")
            return None

    def readKeyboardKeycolorSettings(self):
        """Read global key-color settings"""
        try:
            # Send SET_REPORT for global key-color settings
            packets = [
                "8c000000000000",
                "8c000100000000",
                "8c000200000000",
                "8c000300000000",
                "8c000400000000",
                "8c000500000000"
            ]

            seqData = []
            for packet in packets:
                setReportData = packet
                if not self.proto.setReport(setReportData, 'SET_REPORT: key-color config'):
                    print("SET_REPORT for global key-color failed")
                    return None

                time.sleep(0.1)

                # Read GET_REPORT response
                response_b = self.proto.getReport(64, 'GET_REPORT: key-color config')
                response = bytes(response_b)
                debugPrint(DEBUG_LEVELS['DEBUG'], f"Global key-color response: {response.hex()}")
                if not response:
                    print("GET_REPORT for global key-color failed")
                    return None

                seqData.append(response)

            allData = b''.join(seqData)

            keysReaded = [allData[i:i+3] for i in range(0, len(allData), 3)]

            for i, keyColorReaded in enumerate(keysReaded):
                #keyName = keysIdx.get(i)
                keyName = self.keyPositions.get(i)
                if keyName:
                    self.keyColorSettings.update({keyName: keyColorReaded.hex()})

            hexKeys = [allData.hex()[i:i+6] for i in range(0, len(allData.hex()), 6)]
            debugPrint(DEBUG_LEVELS['DEBUG'], f"\nHEX keys: {hexKeys}\n")

            debugPrint(DEBUG_LEVELS['DEBUG'], f"Global key-color response: {allData.hex()}")

            debugPrint(DEBUG_LEVELS['DEBUG'], f"Global key-color readed: {self.keyColorSettings}")

            return True

        except Exception as e:
            debugPrint(DEBUG_LEVELS['ERROR'], f"Error reading global key-color: {e}")
            return None

    def readKeyboardKeyremapSettings(self):
        """Read global key-remap settings"""
        try:
            # Send SET_REPORT for global key-remap settings
            packets = [
                "89000000000000",
                "89000100000000",
                "89000200000000",
                "89000300000000",
                "89000400000000",
                "89000500000000",
                "89000600000000",
                "89000700000000"
            ]

            seqData = []
            for packet in packets:
                setReportData = packet
                if not self.proto.setReport(setReportData, 'SET_REPORT: key-remap config'):
                    print("SET_REPORT for global key-remap failed")
                    return None

                time.sleep(0.1)

                # Read GET_REPORT response
                response_b = self.proto.getReport(64, 'GET_REPORT: key-remap config')
                response = bytes(response_b)
                debugPrint(DEBUG_LEVELS['DEBUG'], f"Global key-remap response: {response.hex()}")
                if not response:
                    print("GET_REPORT for global key-remap failed")
                    return None

                seqData.append(response)

            allData = b''.join(seqData)

            keysReaded = [allData[i:i+4] for i in range(0, len(allData), 4)]

            for i, keyRemapReaded in enumerate(keysReaded):
                keyName = self.keyPositions.get(i)
                if keyName:
                    self.keyRemapSettings.update({keyName: keyRemapReaded.hex()})
                    debugPrint(DEBUG_LEVELS['DEBUG'], f"SUCCESS: keyName {keyName} at index {i} with scancode {keyRemapReaded.hex()}")
                else:
                    debugPrint(DEBUG_LEVELS['WARNING'], f"no keyName at index {i}")

            hexKeys = [allData.hex()[i:i+8] for i in range(0, len(allData.hex()), 8)]
            debugPrint(DEBUG_LEVELS['DEBUG'], f"\nHEX keys: {hexKeys}\n")

            debugPrint(DEBUG_LEVELS['DEBUG'], f"Global key-remap response: {allData.hex()}")

            debugPrint(DEBUG_LEVELS['DEBUG'], f"Global key-remap readed: {self.keyRemapSettings}")

            return True

        except Exception as e:
            debugPrint(DEBUG_LEVELS['ERROR'], f"Error reading global keycolor: {e}")
            return None

    def readKeyboardAllSettings(self):
        """Read all current settings from keyboard"""
        debugPrint(DEBUG_LEVELS['INFO'], f"Reading current settings from keyboard...\n")

        # Read global backlight settings
        success = self.readKeyboardBacklightSettings()
        if success:
            debugPrint(DEBUG_LEVELS['DEBUG'], f"Backlight settings read successfully")
        else:
            debugPrint(DEBUG_LEVELS['ERROR'], f"Failed to read global backlight settings")

        # Read global key-color settings
        success = self.readKeyboardKeycolorSettings()
        if success:
            debugPrint(DEBUG_LEVELS['DEBUG'], f"Key-color settings read successfully")
        else:
            debugPrint(DEBUG_LEVELS['ERROR'], f"Failed to read global key-color settings")

        # Read global key-remap settings
        success = self.readKeyboardKeyremapSettings()
        if success:
            debugPrint(DEBUG_LEVELS['DEBUG'], f"Key-remap settings read successfully")
        else:
            debugPrint(DEBUG_LEVELS['ERROR'], f"Failed to read global key-remap settings")

    def parseMode(self, mode_str):
        """Parse mode string into mode code"""
        if mode_str not in self.modes:
            raise ValueError(f"Unknown mode: {mode_str}. Available: {', '.join(self.modes.keys())}")
        return self.modes[mode_str]

    def parseSubmode(self, submode_str, mode):
        """Parse submode string for specific mode"""
        # Find mode name from mode code
        mode_name = next((name for name, mode_code in self.modes.items() 
                          if mode_code == mode), None)

        if not mode_name or mode_name not in self.modeSubmodes:
            return 0  # Default submode

        if submode_str in self.modeSubmodes[mode_name]:
            return self.modeSubmodes[mode_name][submode_str]

        available = ', '.join(self.modeSubmodes[mode_name].keys())
        raise ValueError(f"Unknown submode '{submode_str}' for mode '{mode_name}'. Available: {available}")

    def parseColor(self, color_str):
        """Parse color string into flag and RGB values"""
        color_lower = color_str.lower()

        # Predefined colors
        if color_lower in self.predefinedColors:
            return self.predefinedColors[color_lower]

        # Custom RGB colors
        try:
            hexColor = self.resolveColor(color_str)
            r = int(hexColor[0:2], 16)
            g = int(hexColor[2:4], 16)
            b = int(hexColor[4:6], 16)
            return 0x08, r, g, b  # Custom RGB flag
        except ValueError:
            pass

        raise ValueError(f"Invalid color: {color_str}")

    def setBacklight(self):
        """Send current backlight settings to keyboard"""
        data_bytes = [
            0x07,  # Command ID
            self.backlightSettings['mode'],
            self.backlightSettings['speed'], 
            self.backlightSettings['brightness'],
            (self.backlightSettings['submode'] << 4) | self.backlightSettings['color_flag'],
            self.backlightSettings['r'],
            self.backlightSettings['g'], 
            self.backlightSettings['b']
        ]

        hexCmd = " ".join(f"{b:02x}" for b in data_bytes)
        description = f"Backlight: mode={self.backlightSettings['mode']:02x}, speed={self.backlightSettings['speed']}, brightness={self.backlightSettings['brightness']}"
        if self.backlightSettings['color_flag'] == 0x08:
            description += f", RGB=({self.backlightSettings['r']}, {self.backlightSettings['g']}, {self.backlightSettings['b']})"

        return self.proto.setReport(hexCmd, description)

    def setKeyColors(self, key_color_args):
        """Parse user key colors string into 7 packets with support for ALL:COLOR and key groups"""
        if not key_color_args:
            return []

        # Define key groups for batch color assignment
        keyGroups = {
            'ALL_F': [  # All function keys F1-F12
                'KEY_F1', 'KEY_F2', 'KEY_F3', 'KEY_F4', 'KEY_F5', 'KEY_F6',
                'KEY_F7', 'KEY_F8', 'KEY_F9', 'KEY_F10', 'KEY_F11', 'KEY_F12'
            ],
            'ALL_F1': [  # All function keys F1-F4
                'KEY_F1', 'KEY_F2', 'KEY_F3', 'KEY_F4'
            ],
            'ALL_F2': [  # All function keys F5-F8
                'KEY_F5', 'KEY_F6', 'KEY_F7', 'KEY_F8'
            ],
            'ALL_F3': [  # All function keys F9-F12
                'KEY_F9', 'KEY_F10', 'KEY_F11', 'KEY_F12'
            ],
            'ALL_MOD': [  # All modifier keys
                'KEY_LEFTCTRL', 'KEY_RIGHTCTRL', 'KEY_LEFTSHIFT', 'KEY_RIGHTSHIFT',
                'KEY_LEFTALT', 'KEY_RIGHTALT', 'KEY_LEFTMETA', 'KEY_RIGHTMETA'
            ],
            'ALL_NAV': [  # All navigation keys
                'KEY_LEFT', 'KEY_RIGHT', 'KEY_UP', 'KEY_DOWN', 
                'KEY_HOME', 'KEY_END', 'KEY_PAGEUP', 'KEY_PAGEDOWN',
                'KEY_INSERT', 'KEY_DELETE'
            ],
            'ALL_NUM': [  # Number keys 1-9 (not numpad)
                'KEY_1', 'KEY_2', 'KEY_3', 'KEY_4', 'KEY_5', 
                'KEY_6', 'KEY_7', 'KEY_8', 'KEY_9', 'KEY_0'
            ],
            'ALL_WASD': [  # Gaming WASD keys
                'KEY_W', 'KEY_A', 'KEY_S', 'KEY_D'
            ],
            'ALL_ARROWS': [  # Arrow keys
                'KEY_LEFT', 'KEY_RIGHT', 'KEY_UP', 'KEY_DOWN'
            ],
            'ALL_SPECIAL': [  # Special keys
                'KEY_ESC', 'KEY_ENTER', 'KEY_SPACE', 'KEY_BACKSPACE', 'KEY_TAB',
                'KEY_CAPSLOCK', 'KEY_PRINTSCREEN'
            ],
            'ALL_ALPHA': [  # All alphabetic keys A-Z
                'KEY_A', 'KEY_B', 'KEY_C', 'KEY_D', 'KEY_E', 'KEY_F', 'KEY_G', 'KEY_H', 'KEY_I',
                'KEY_J', 'KEY_K', 'KEY_L', 'KEY_M', 'KEY_N', 'KEY_O', 'KEY_P', 'KEY_Q', 'KEY_R',
                'KEY_S', 'KEY_T', 'KEY_U', 'KEY_V', 'KEY_W', 'KEY_X', 'KEY_Y', 'KEY_Z'
            ]
        }

        for key_color_str in key_color_args:
            for pair in key_color_str.split(','):
                if ':' not in pair:
                    raise ValueError(f"Invalid key-color pair: {pair}. Use KEY:COLOR")

                key_name, color_value = pair.split(':', 1)
                key_name = key_name.upper()

                # Resolve color (supports named colors and hex)
                try:
                    hexColor = self.resolveColor(color_value)
                except ValueError as e:
                    raise ValueError(f"Invalid color in pair {pair}: {e}")

                # Handle ALL colors - set as default color for all keys
                if key_name == 'ALL':
                    for k in self.keyColorSettings:
                          self.keyColorSettings[k] = hexColor
                    continue

                # Handle key groups
                if key_name in keyGroups:
                    group_keys = keyGroups[key_name]
                    for group_key in group_keys:
                        if group_key in self.keyColorSettings:
                            self.keyColorSettings[group_key] = hexColor
                    continue

                # Handle individual keys
                if key_name not in self.keyPositions.values():
                    if key_name.startswith('ALL_'):
                        available_groups = ', '.join(keyGroups.keys())
                        raise ValueError(f"Unknown key group: {key_name}. Available groups: {available_groups}")
                    else:
                        raise ValueError(f"Unknown key for user mode: {key_name}")

                if key_name in self.keyColorSettings:
                      self.keyColorSettings[key_name] = hexColor

        # Prepare data for all positions
        seqData = []
        for position in range(148):
            if position in self.keyPositions and self.keyPositions[position] in self.keyColorSettings:
                  keyName = self.keyPositions[position]
                  seqData.append(bytes.fromhex(self.keyColorSettings[keyName]))
            else:
                  seqData.append(b'\x00\x00\x00')

        rgb_data = b''.join(seqData)

        return rgb_data

    def setUserKeyRemap(self, remap_args):
        """Parse user key remap string into 9 packets"""
        if not remap_args:
            return []

        for remap_str in remap_args:
            for single_remap in remap_str.split(','):
                if ':' not in single_remap:
                    raise ValueError(f"Invalid key-remap format: {single_remap}. Use KEY:[MOD1[:MOD2]]:TARGET_KEY or KEY:HEXVALUE")

                parts = single_remap.split(':')
                source_key = parts[0].upper()

                # Check if we're disabling the key
                if len(parts) >= 2 and parts[1].lower() == 'disable':
                    if source_key in self.keyPositions.values():
                        self.keyRemapSettings[source_key] = "00000000"
                        continue

                # Check if it's a direct hex value (8 hex characters)
                if len(parts) >= 2 and re.match(r'^[0-9a-fA-F]{8}$', parts[1]):
                    hex_value = parts[1].lower()
                    try:
                        # Convert hex string to list of 4 bytes
                        position_data = ''.join([
                            hex_value[0:2],
                            hex_value[2:4],
                            hex_value[4:6],
                            hex_value[6:8]
                        ])
                        self.keyRemapSettings[source_key] = position_data
                        continue
                    except ValueError:
                        raise ValueError(f"Invalid hex value: {parts[1]}")

                # Standard key remapping with modifiers
                if len(parts) >= 2 and parts[-1].upper().startswith('KEY_'):
                    target_key = parts[-1].upper()
                    modifiers = parts[1:-1] if len(parts) > 2 else []
                else:
                    target_key = parts[1].upper()
                    modifiers = []

                # Convert modifiers to codes
                mod_codes = []
                for mod in modifiers:
                    mod_upper = mod.upper()
                    if mod_upper in self.modifierCodes:
                        mod_codes.append(self.modifierCodes[mod_upper])
                    else:
                        raise ValueError(f"Unknown modifier: {mod}")

                # Get target scan code (handles special keys)
                allScanCodes = {**self.scanCodes, **self.modifierCodes}
                if target_key in self.specialCodes:
                    special_code = self.specialCodes[target_key.upper()]
                    position_data = ''.join(f"{b:02x}" for b in [special_code[0], special_code[1], special_code[2], special_code[3]])
                elif target_key in allScanCodes:
                    target_scan = allScanCodes[target_key]
                    if len(mod_codes) == 1:
                        position_data = ''.join(f"{b:02x}" for b in [0x00, mod_codes[0], target_scan, 0x00])
                    elif len(mod_codes) == 2:
                        position_data = ''.join(f"{b:02x}" for b in [0x00, mod_codes[0], mod_codes[1], target_scan])
                    else:
                        position_data = ''.join(f"{b:02x}" for b in [0x00, 0x00, target_scan, 0x00])
                else:
                    raise ValueError(f"Unknown target key: {target_key}")

                self.keyRemapSettings[source_key] = position_data

        # Prepare data for all positions
        seqData = []
        for position in range(126):
            if position in self.keyPositions and self.keyPositions[position] in self.keyRemapSettings:
                  keyName = self.keyPositions[position]
                  seqData.append(bytes.fromhex(self.keyRemapSettings[keyName]))
            else:
                  seqData.append(b'\x00\x00\x00\x00')

        map_data = b''.join(seqData)

        return map_data

    def sendUserKeyColorPackets(self, packetData):
        """Send all 9 remap packets with complete configuration"""

        packetHeaders = [
            "0c 00 80 01 00 00 00",
            "0c 00 80 01 01 00 00", 
            "0c 00 80 01 02 00 00",
            "0c 00 80 01 03 00 00",
            "0c 00 80 01 04 00 00",
            "0c 00 80 01 05 00 00",
            "0c 00 80 01 06 00 00"
        ]

        return self.sendAllKeyPackets(packetHeaders, packetData)

    def sendKeyRemapPackets(self, packetData):
        """Send all 9 remap packets with complete configuration"""

        packetHeaders = [
            "09 00 f8 01 00 00 00",
            "09 00 f8 01 01 00 00",
            "09 00 f8 01 02 00 00",
            "09 00 f8 01 03 00 00",
            "09 00 f8 01 04 00 00", 
            "09 00 f8 01 05 00 00",
            "09 00 f8 01 06 00 00",
            "09 00 f8 01 07 00 00",
            "09 00 f8 01 08 00 00"
        ]

        return self.sendAllKeyPackets(packetHeaders, packetData)

    def sendAllKeyPackets(self, packetHeaders, packetData, description = 'Command'):

        packets = []

        for packetNum in range(len(packetHeaders)):
            start_idx = packetNum * 56
            end_idx = start_idx + 56
            header = bytes.fromhex(packetHeaders[packetNum].replace(" ", ""))
            data = packetData[start_idx:end_idx]
            checksum = (0x100 - ((sum(header) + 1) & 0xFF)) & 0xFF

            completePacket = header + bytes([checksum]) + data

            # Format for display/output
            hexCmd = " ".join(f"{b:02x}" for b in completePacket)

            packets.append((hexCmd, f"User key remap packet {packetNum}"))

        return self.proto.sendMultiplePackets(packets)

    def colorHexToName(self, hex_value):
        # Normalize hex (lowercase, no #)
        hex_value = hex_value.lower().lstrip('#')
        
        # Create reverse map: hex → name
        reverse_colors = {v.lower(): k for k, v in NAMED_COLORS.items()}
        
        # Return color name if found, otherwise original hex
        return reverse_colors.get(hex_value)

    def printKeyboardBacklightSettings(self):
        label_width = 20
        settings = self.backlightSettings
        
        print("=== Backlight settings ===\n")
        
        # Reverse lookup map for modes
        modesMap = {v: k for k, v in self.modes.items()}
    
        # Reverse lookup for colors
        colorMap = {v[0]: name for name, v in self.predefinedColors.items()}
    
        # Mode
        mode_name = modesMap.get(settings['mode'], 'Unknown')
    
        # Submode lookup only within current mode
        submode_dict = getattr(self, 'modeSubmodes', {}).get(mode_name, {})
        submode_name = None
        for name, val in submode_dict.items():
            if val == settings['submode']:
                submode_name = name
                break
    
        if submode_name:
            print(f"{'Mode:':<{label_width}}{mode_name} / {submode_name}")
        else:
            #print(f"{'Submode:':<{label_width}}Default ({settings['submode']})")
            print(f"{'Mode:':<{label_width}}{mode_name}")
        print(f"{'Speed:':<{label_width}}{settings['speed']}")
        print(f"{'Brightness:':<{label_width}}{settings['brightness']}")
    
        # Color handling
        color_flag = settings.get('color_flag', 0)
        if color_flag == 8:
            # Custom RGB color
            r, g, b = settings.get('r', 0), settings.get('g', 0), settings.get('b', 0)
            colorName = self.colorHexToName(f"{r:02x}{g:02x}{b:02x}")
            print(f"{'Color:':<{label_width}}Custom RGB:({r}, {g}, {b}), #{r:02x}{g:02x}{b:02x}" +
                  (f", {colorName}" if colorName is not None else ""))
        else:
            # Predefined color
            color_name = colorMap.get(color_flag, f"Unknown ({color_flag})")
            print(f"{'Color:':<{label_width}}{color_name}")
        
        print("\n")


    def printKeyboardKeycolorSettings(self):
        label_width = 20
        settings = self.keyColorSettings
    
        print("=== Key color settings ===\n")
    
        print(f"{'Key name':<{label_width}} {'RGB value':<{label_width}} HEX value   Color name")
        print("-" * 65)
    
        for key, hex_color in settings.items():
            hexColor = hex_color.lower()
            colorName = self.colorHexToName(hexColor)
            r, g, b = (int(hexColor[i:i+2], 16) for i in (0, 2, 4))
    
            # Print formatted line
            print(
                f"{key:<{label_width}} "
                f"RGB ({r}, {g}, {b})".ljust(label_width + 20)
                + f"  #{hexColor.upper():<10}"
                + (f" {colorName}" if colorName else "")
            )

        print("\n")

    def printKeyboardKeyremapSettings(self):
        label_width = 20
        
        print("=== Key remap settings ===\n")
        
        print(f"{'Key name':<{label_width}} {'Modifier 2':<15} {'Modifier 1':<15} Target key")
        print("-" * 70)
    
        # Reverse mapping for modifier codes
        modifier_names = {v: k for k, v in self.modifierCodes.items()}
    
        for key in sorted(self.keyRemapSettings.keys()):
          
            if key == 'RESERVED':
                continue
          
            hex_value = self.keyRemapSettings[key]
            bytes_val = [int(hex_value[i:i+2], 16) for i in range(0, 8, 2)]
            b1, b2, b3, b4 = bytes_val
            mod1 = mod2 = ""
            target_key_name = None
    
            # Special / custom keys
            if b1 != 0x00:
                for name, seq in self.specialCodes.items():
                    if bytes_val == seq:
                        target_key_name = f"Special: {name}"
                        break
                else:
                    target_key_name = f"Special/Custom: {hex_value.upper()}"
    
            # Normal keys
            else:
                # Two modifiers
                if b2 in modifier_names and b3 in modifier_names:
                    mod2 = modifier_names[b2]
                    mod1 = modifier_names[b3]
                    target_key_name = self.getKeyNameByScanCode(b4)
                # One modifier
                elif b2 in modifier_names and b4 == 0x00:
                    mod1 = modifier_names[b2]
                    target_key_name = self.getKeyNameByScanCode(b3)
                # No modifier
                elif b2 == 0x00 and b4 == 0x00:
                    target_key_name = self.getKeyNameByScanCode(b3)
                # Unknown / custom
                else:
                    target_key_name = f"Unknown (0x{hex_value[2:]})"
    
            # Filter: only if changed from default (key != target) or has modifier
            if (mod1 or mod2) or (target_key_name != key):
                print(
                    f"{key:<{label_width}} "
                    f"{(mod2 or ''):<15} "
                    f"{(mod1 or ''):<15} "
                    f"{target_key_name or 'Unknown'}"
                )
                
        print("\n")
    
    def getKeyNameByScanCode(self, scancode):
        """Find the key name by scan code."""
        allScanCodes = {**self.scanCodes, **self.modifierCodes}
        for name, code in allScanCodes.items():
            if code == scancode:
                return name
        return f"Unknown (0x{scancode:02X})"
    
    def getModifierName(self, code):
        """Find the modifier name by code."""
        for name, val in self.modifierCodes.items():
            if val == code:
                return name
        return ""

    def printKeyboardAllSettings(self):
        self.printKeyboardBacklightSettings()
        self.printKeyboardKeycolorSettings()
        self.printKeyboardKeyremapSettings()

    def applyPreset(self, preset_name):
        """Apply a preset configuration"""
        if preset_name not in self.presets:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {', '.join(self.presets.keys())}")
        
        preset = self.presets[preset_name]
        debugPrint(DEBUG_LEVELS['INFO'], f"Applying preset: {preset['name']} - {preset['description']}")
        
        success = True
        
        # Apply backlight settings
        if any(key in preset for key in ['mode', 'submode', 'brightness', 'speed', 'color']):
            
            debugPrint(DEBUG_LEVELS['INFO'], "Setting mode ...")
            
            # Read current settings first
            self.readKeyboardBacklightSettings()
            
            if 'mode' in preset:
                self.backlightSettings['mode'] = self.parseMode(preset['mode'])
            if 'submode' in preset and preset['submode']:
                self.backlightSettings['submode'] = self.parseSubmode(preset['submode'], self.backlightSettings['mode'])
            if 'brightness' in preset:
                self.backlightSettings['brightness'] = preset['brightness']
            if 'speed' in preset:
                self.backlightSettings['speed'] = preset['speed']
            if 'color' in preset:
                color_flag, r, g, b = self.parseColor(preset['color'])
                self.backlightSettings['color_flag'] = color_flag
                self.backlightSettings['r'] = r
                self.backlightSettings['g'] = g
                self.backlightSettings['b'] = b
            
            success = self.setBacklight() and success
        
            time.sleep(1)
        
        # Apply key colors
        if 'key-colors' in preset and preset['key-colors']:
            
            debugPrint(DEBUG_LEVELS['INFO'], "Setting key colors ...")
            
            self.readKeyboardKeycolorSettings()
            keyColorPackets = self.setKeyColors(preset['key-colors'])
            if keyColorPackets:
                success = self.sendUserKeyColorPackets(keyColorPackets) and success
        
            self.proto.disconnect()
            time.sleep(1)
            self.proto = YenkeeProto()
        
        # Apply key remapping
        if 'key-remap' in preset and preset['key-remap']:
            
            debugPrint(DEBUG_LEVELS['INFO'], "Setting key remaps ...")
            
            self.readKeyboardKeyremapSettings()
            keyRemapPackets = self.setUserKeyRemap(preset['key-remap'])
            if keyRemapPackets:
                success = self.sendKeyRemapPackets(keyRemapPackets) and success
        
            self.proto.disconnect()
            time.sleep(1)
            self.proto = YenkeeProto()
        
        return success
    
    def listPresets(self):
        """List all available presets"""
        print("Available presets:")
        print("-" * 50)
        for preset_id, preset_info in self.presets.items():
            print(f"  {preset_id:<15} - {preset_info['name']}")
            print(f"    {preset_info['description']}")
            
            # Show settings summary
            settings = []
            if 'mode' in preset_info:
                settings.append(f"mode: {preset_info['mode']}")
            if 'brightness' in preset_info:
                settings.append(f"brightness: {preset_info['brightness']}")
            if 'key-colors' in preset_info:
                settings.append(f"key-colors: {len(preset_info['key-colors'])} rules")
            if 'key-remap' in preset_info:
                settings.append(f"key-remap: {len(preset_info['key-remap'])} rules")
            
            print(f"    Settings: {', '.join(settings)}")
            print()
    
    def saveCurrentPreset(self, presetFile):
        """Save current settings as a new preset"""
        # This would require reading all current settings first
        debugPrint(DEBUG_LEVELS['INFO'], f"Saving current settings into file: {presetFile}")
        
        # For now, just show a message that this feature needs implementation
        print("Feature --save-preset is not yet implemented.")
        print("To create custom presets, modify the PRESETS dictionary in the script.")
        
        self.readKeyboardAllSettings()
        
        # Reverse lookup map for modes
        modesMap = {v: k for k, v in self.modes.items()}
    
        # Reverse lookup for colors
        colorMap = {v[0]: name for name, v in self.predefinedColors.items()}
    
        # Mode
        mode_name = modesMap.get(self.backlightSettings['mode'], 'Unknown')
    
        # Submode lookup only within current mode
        submode_dict = getattr(self, 'modeSubmodes', {}).get(mode_name, {})
        submode_name = None
        for name, val in submode_dict.items():
            if val == self.backlightSettings['submode']:
                submode_name = name
                break
        
        preset = {
            'name': 'custom',
            'description': f'Custom preset',
            'mode': mode_name,
            'submode': submode_name,
            'brightness': self.backlightSettings['brightness']
        }
        
        if mode_name == 'user':
            preset['key-colors'] = self.keyColorSettings
        else:
            preset['speed'] = self.backlightSettings['speed']
        
        allKeys = {**self.scanCodes, **self.modifierCodes}
        allKeys = {k: f"0000{v:02x}00" for k, v in allKeys.items()}
        setKeys = self.keyRemapSettings
        diffMap = {
            k: f"{setKeys[k]}"
            for k in allKeys
            if k in setKeys and allKeys[k] != setKeys[k]
        }
        preset['key-remap'] = diffMap
        
        with open(presetFile, 'w') as f:
            json.dump(preset, f, indent=2)
        
        return True

    def loadPresetFromFile(self, presetFile):
        """Load user preset from file"""
        try:
            file = Path(presetFile)
            if file.exists():
                with open(file, 'r') as f:
                    preset = json.load(f)
                
                if 'key-colors' in preset and preset["key-colors"]:
                    preset["key-colors"] = [f"{k}:{v}" for k, v in preset["key-colors"].items()]
                    
                if 'key-remap' in preset and preset["key-remap"]:
                    preset["key-remap"] = [f"{k}:{v}" for k, v in preset["key-remap"].items()]
                    
                self.presets['_loaded_'] = preset
                self.applyPreset('_loaded_')
                debugPrint(DEBUG_LEVELS['INFO'], f"Loaded preset from file: {file.name}")
                return True
            else:
                debugPrint(DEBUG_LEVELS['ERROR'], f"Preset file not found: {file}")
        except Exception as e:
            debugPrint(DEBUG_LEVELS['ERROR'], f"Error loading preset from file '{presetFile}': {e}")

    def run(self):
        """Main CLI execution"""
        args = self.parser.parse_args()

        # Set debug level
        setDebugLevel(args.debug)
        debugPrint(DEBUG_LEVELS['INFO'], f"Starting YenKey CLI")

        # Initialize protocol with custom VID/PID if provided
        self.proto = YenkeeProto(vid=args.vid, pid=args.pid)
        debugPrint(DEBUG_LEVELS['DEBUG'], f"Using VID: 0x{args.vid:04x}, PID: 0x{args.pid:04x}")

        success = True

        try:
            # Handle reset commands first
            if args.factory_reset:
                success = self.factoryReset() and success
                if success:
                    print("Factory reset completed")
                return

            if args.keymap_reset:
                print("Resetting key mapping to default...")
                if self.sendKeyRemapPackets(bytes(self.defaultRemapData)):
                    print("Key mapping reset completed successfully")
                else:
                    print("Key mapping reset failed")
                return

            # Handle read commands
            if args.read_settings:
                self.readKeyboardAllSettings()
                self.printKeyboardAllSettings()
                return

            if args.read_backlight:
                self.readKeyboardBacklightSettings()
                self.printKeyboardBacklightSettings()
                return

            if args.read_key_colors:
                self.readKeyboardKeycolorSettings()
                self.printKeyboardKeycolorSettings()
                return

            if args.read_key_remap:
                self.readKeyboardKeyremapSettings()
                self.printKeyboardKeyremapSettings()
                return

            # Handle listing commands
            if args.list_modes:
                print("Modes (with submodes) available:")
                print("-" * 50)
                for mode in self.modes:
                    print(f" - {mode}")
                    if mode in self.modeSubmodes:
                        print("   -", "\n   - ".join(self.modeSubmodes[mode]))
                return

            if args.list_colors:
                print("Colors (names) available:")
                print("-" * 50)
                print(" -", "\n - ".join(sorted(NAMED_COLORS)))
                return

            if args.list_keys:
                print("Physical keys available for remapping:")
                print("-" * 50)
                print(" -", "\n - ".join([key for key in sorted(self.keyPositions.values()) if key != "RESERVED"]), "\n")

                print("Standard functions available for remapping:")
                print("-" * 50)
                max_key_length = max(len(key) for key in self.scanCodes.keys())
                for key in sorted(self.scanCodes):
                    print(f" - {key:<{max_key_length}} (0x{self.scanCodes[key]:02x})")
                print()

                print("Special functions available for remapping:")
                print("-" * 50)
                max_key_length = max(len(key) for key in self.specialCodes.keys())
                for key in sorted(self.specialCodes):
                    hex_bytes = self.specialCodes[key]
                    hex_string = "0x" + "".join(f"{b:02x}" for b in hex_bytes)
                    print(f" - {key:<{max_key_length}} ({hex_string})")
                return

            if args.list_standard_keycodes:
                print("Standard keycodes available:")
                print("-" * 50)
                print(" -", "\n - ".join(sorted(self.scanCodes)), "\n")

                print("Standard modifiers available:")
                print("-" * 50)
                print(" -", "\n - ".join(sorted(self.modifierCodes)))
                return

            if args.list_special_keycodes:
                print("Special keycodes (events) available:")
                print("-" * 50)
                print(" -", "\n - ".join(sorted(self.specialCodes)))
                return

            # Handle incremental backlight configuration
            config_updated = False

            # Backlight settings
            if args.mode or args.submode or args.color or args.speed is not None or args.brightness is not None:

                # Read current backlight settings from keyboard
                self.readKeyboardBacklightSettings()

                # Set backlight mode
                if args.mode:
                    self.backlightSettings['mode'] = self.parseMode(args.mode)
                    self.backlightSettings['submode'] = 0
                    config_updated = True

                # Set backlight submode
                if args.submode:
                    self.backlightSettings['submode'] = self.parseSubmode(args.submode, self.backlightSettings['mode'])
                    config_updated = True

                # Set backlight color
                if args.color:
                    color_flag, r, g, b = self.parseColor(args.color)
                    self.backlightSettings['color_flag'] = color_flag
                    self.backlightSettings['r'] = r
                    self.backlightSettings['g'] = g
                    self.backlightSettings['b'] = b
                    config_updated = True

                # Set backlight animation speed
                if args.speed is not None:
                    self.backlightSettings['speed'] = args.speed
                    config_updated = True

                # Set backlight brightness
                if args.brightness is not None:
                    self.backlightSettings['brightness'] = args.brightness
                    config_updated = True

                # Send backlight configuration if any parameter was updated
                if config_updated:
                    success = self.setBacklight() and success

            # Handle key colors (user mode only)
            if args.key_color:
                self.readKeyboardKeycolorSettings()
                keyColorPackets = self.setKeyColors(args.key_color)
                if keyColorPackets:
                    success = self.sendUserKeyColorPackets(keyColorPackets)

            # Handle key remapping
            if args.key_remap:
                self.readKeyboardKeyremapSettings()
                keyRemapPackets = self.setUserKeyRemap(args.key_remap)
                if keyRemapPackets:
                    success = self.sendKeyRemapPackets(keyRemapPackets)

            # Handle preset commands
            if args.preset:
                success = self.applyPreset(args.preset) and success
                if success:
                    debugPrint(DEBUG_LEVELS['INFO'], f"Preset '{args.preset}' applied successfully")
                else:
                    debugPrint(DEBUG_LEVELS['ERROR'], f"Failed to apply preset '{args.preset}'")
                return
            
            if args.list_presets:
                self.listPresets()
                return
            
            if args.save_preset:
                preset_file = args.save_preset
                success = self.saveCurrentPreset(preset_file) and success
                if success:
                    debugPrint(DEBUG_LEVELS['INFO'], f"Preset saved successfully into file: '{preset_file}'")
                else:
                    debugPrint(DEBUG_LEVELS['ERROR'], f"Failed to save preset into file '{preset_file}'")
                return

            if args.load_preset:
                preset_file = args.load_preset
                success = self.loadPresetFromFile(preset_file) and success
                if success:
                    debugPrint(DEBUG_LEVELS['INFO'], f"Preset successfully loaded and applied from file: '{preset_file}'")
                else:
                    debugPrint(DEBUG_LEVELS['ERROR'], f"Failed to load and apply preset from file '{preset_file}'")
                return

            if success:
                debugPrint(DEBUG_LEVELS['INFO'], "All operations completed successfully")
            else:
                debugPrint(DEBUG_LEVELS['ERROR'], "Some operations failed")
                sys.exit(1)

        except Exception as e:
            debugPrint(DEBUG_LEVELS['ERROR'], f"Error: {e}")
            success = False
            sys.exit(1)

        finally:
            self.proto.disconnect()


if __name__ == "__main__":
    cli = YenKeyCLI()
    cli.run()
