#!/usr/bin/env python3
"""
YenKey CLI Utility
Command-line interface for "Yenkey YKB3700 Rogue" keyboard - backlight and key remapping control

Author: Petr Palacky
AI Collaboration: DeepSeek
Date: 2025
Version: 0.1

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

IFACE = 1

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
    
    # Game colors
    'skyblue': '87ceeb', 'forestgreen': '228b22', 'firebrick': 'b22222',
    'royalblue': '4169e1', 'crimson': 'dc143c', 'tomato': 'ff6347',
    'springgreen': '00ff7f', 'deepskyblue': '00bfff', 'dodgerblue': '1e90ff',
    'mediumspringgreen': '00fa9a'
}


class YenkeeProto:
    """Protocol handler for YenKey keyboard communication"""
    
    def __init__(self, vid=0x3151, pid=0x4002):
        self.vid = vid
        self.pid = pid
        self.dev = None
        self.sysfs_path = None

    def get_sysfs_path(self, vid, pid):
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

            print("Keyboard found")
            self.sysfs_path = self.get_sysfs_path(self.vid, self.pid)
            return self._setup_communication()

        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def _setup_communication(self):
        """Setup USB communication on Interface 0"""
        try:
            if self.dev.is_kernel_driver_active(0):
                self.dev.detach_kernel_driver(0)
            if self.dev.is_kernel_driver_active(1):
                self.dev.detach_kernel_driver(1)
            return True
        except Exception as e:
            print(f"Communication setup error: {e}")
            return False

    def send_packet(self, hex_string, description="Command"):
        """Send packet to Interface IFACE - preserves Fn functions"""
        
        if not self.connect():
            sys.exit(1)
        
        if not self.dev:
            print("Device not connected")
            return False

        try:
            hex_clean = hex_string.replace(" ", "")
            main_data = bytes.fromhex(hex_clean)

            print(f"Sending: {description} [{hex_clean}]")

            if len(main_data) > 64:
                print("  Warning: Data longer than 64 bytes, truncating")
                main_data = main_data[:64]

            if len(main_data) < 64:
                checksum = bytes([(0x100 - ((sum(main_data) + 1) & 0xFF)) & 0xFF])
                main_data += checksum

            main_data += b"\x00" * (64 - len(main_data))

            self.dev.ctrl_transfer(0x21, 0x09, 0x0300, IFACE, main_data)
            print("  Command sent successfully\n")
            return True

        except Exception as e:
            print(f"  Send error: {e}")
            return False

    def send_multiple_packets(self, packets):
        """Send multiple packets sequentially with delay"""
        
        if not self.connect():
            sys.exit(1)
        
        success_count = 0
        for i, (hex_string, description) in enumerate(packets, 1):
            print(f"Packet {i}/{len(packets)}:")
            if self.send_packet(hex_string, description):
                success_count += 1
            time.sleep(0.1)
        print(f"Total successful: {success_count}/{len(packets)}")
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
                    with open("/sys/bus/usb/drivers/usb/unbind", "w") as f:
                        f.write(self.sysfs_path)
                    with open("/sys/bus/usb/drivers/usb/bind", "w") as f:
                        f.write(self.sysfs_path)
                except:
                    pass

    def set_backlight_combined(self, mode, speed=4, brightness=4, submode=0, color_flag=0, r=0, g=0, b=0):
        """Set combined backlight settings in one packet"""
        data_bytes = [
            0x07,  # Command ID
            mode,   # Mode
            speed,  # Speed (1-4)
            brightness,  # Brightness (1-4)
            (submode << 4) | color_flag,  # Combined: submode (high nibble) + color_flag (low nibble)
            r,      # Red
            g,      # Green
            b       # Blue
        ]
        
        hex_cmd = " ".join(f"{b:02x}" for b in data_bytes)
        description = f"Backlight: mode={mode:02x}, speed={speed}, brightness={brightness}, submode={submode}, color_flag={color_flag:02x}"
        if color_flag == 0x08:
            description += f", RGB=({r}, {g}, {b})"
        
        return self.send_packet(hex_cmd, description)

    def set_user_key_colors(self, key_colors):
        """Set user-defined key colors for user mode"""
        return self.send_multiple_packets(key_colors)

    def set_backlight_mode(self, mode, submode=0):
        """Set backlight mode with default speed/brightness"""
        return self.set_backlight_combined(mode, submode=submode)

    def set_backlight_color(self, r, g, b):
        """Set backlight color with current mode"""
        return self.set_backlight_combined(0x01, color_flag=0x08, r=r, g=g, b=b)

    def set_rainbow_mode(self):
        """Set rainbow color mode"""
        return self.set_backlight_combined(0x01, color_flag=0x07)

    def set_animation_speed(self, speed):
        """Set animation speed (1-4) with current mode"""
        return self.set_backlight_combined(0x01, speed=speed)

    def set_backlight_brightness(self, brightness):
        """Set backlight brightness (1-4) with current mode"""
        return self.set_backlight_combined(0x01, brightness=brightness)

    def send_remap_packets(self, remap_data):
        """Send all 9 remap packets with complete configuration"""
        
        #if not self.dev:
            #print("Device not connected")
            #return False
    
        # Packet headers for remap configuration (9 packets)
        packet_headers = [
            "09 00 f8 01 00 00 00 fd",  # Packet 0
            "09 00 f8 01 01 00 00 fc",  # Packet 1  
            "09 00 f8 01 02 00 00 fb",  # Packet 2
            "09 00 f8 01 03 00 00 fa",  # Packet 3
            "09 00 f8 01 04 00 00 f9",  # Packet 4
            "09 00 f8 01 05 00 00 f8",  # Packet 5
            "09 00 f8 01 06 00 00 f7",  # Packet 6
            "09 00 f8 01 07 00 00 f6",  # Packet 7
            "09 00 f8 01 08 00 00 f5"   # Packet 8
        ]
    
        packets = []
        
        # Create 9 packets, each with 14 positions (56 bytes data + 8 bytes header = 64 bytes)
        for packet_num in range(9):
            start_idx = packet_num * 56  # 14 positions * 4 bytes each
            end_idx = start_idx + 56
            
            packet_data = remap_data[start_idx:end_idx]
            data_hex = " ".join(f"{b:02x}" for b in packet_data)
            hex_cmd = f"{packet_headers[packet_num]} {data_hex}"
            
            packets.append((hex_cmd, f"Remap packet {packet_num}"))
        
        return self.send_multiple_packets(packets)

    def factory_reset(self):
        """Reset keyboard to factory settings"""
        hex_cmd = "02 00 00 00 00 00 00 fd"
        return self.send_packet(hex_cmd, "Factory reset")

    def reset_keymap(self):
        """Reset key mapping to default by sending complete default mapping"""
        return self.send_remap_packets(self.default_remap_data)


class YenKeyCLI:
    """Main CLI controller for YenKey keyboard"""
    
    def __init__(self):
        self.proto = YenkeeProto()
        
        # Mode mapping
        self.modes = {
            'off': 0x00, 'static': 0x01, 'breath': 0x02, 'neon': 0x03,
            'wave': 0x04, 'waterdrop': 0x05, 'rain': 0x06, 'snake': 0x07,
            'fadeout': 0x08, 'spiral': 0x09, 'sinusoid': 0x0a, 'kaleidoscope': 0x0b,
            'linear': 0x0c, 'user': 0x0d, 'laser': 0x0e, 'roundwave': 0x0f,
            'shining': 0x10, 'rain2': 0x11, 'horizontal': 0x12, 'staticfade': 0x13,
            'music-edm': 0x14, 'screen1': 0x15, 'music-standard': 0x16, 'surf': 0x17, 'skew': 0x18
        }
        
        # Effect submodes
        self.mode_submodes = {
            'wave': {'right': 0, 'left': 1, 'down': 2, 'up': 3},
            'snake': {'linear': 0, 'tocenter': 1},
            'kaleidoscope': {'fromcenter': 0, 'tocenter': 1},
            'roundwave': {'counterclockwise': 0, 'clockwise': 1},
            'music-edm': {'upright': 0, 'separate': 1, 'cross': 2}
        }
        
        # Predefined colors and their flags
        self.predefined_colors = {
            'red': (0x00, 0xFF, 0x00, 0x00),
            'green': (0x01, 0x00, 0xFF, 0x00),
            'blue': (0x02, 0x00, 0x00, 0xFF),
            'orange': (0x03, 0xFF, 0x69, 0x00),
            'pink': (0x04, 0xFF, 0x14, 0x93),
            'yellow': (0x05, 0xFF, 0xFF, 0x00),
            'white': (0x06, 0xFF, 0xFF, 0xFF),
            'rainbow': (0x07, 0x00, 0x00, 0x00)  # Special case
        }
        
        # User mode key position mapping (0-147 positions)
        self.user_key_positions = {
            'KEY_ESC': 0, 'KEY_GRAVE': 1, 'KEY_TAB': 2, 'KEY_CAPSLOCK': 3,
            'KEY_LEFTSHIFT': 4, 'KEY_LEFTCTRL': 5, 
            'KEY_1': 7, 'KEY_Q': 8, 'KEY_A': 9, 'KEY_F1': 12,
            'KEY_2': 13, 'KEY_W': 14, 'KEY_S': 15, 'KEY_Z': 16, 'KEY_LEFTMETA': 17, 'KEY_F2': 18,
            'KEY_3': 19, 'KEY_E': 20, 'KEY_D': 21, 'KEY_X': 22, 'KEY_LEFTALT': 23, 'KEY_F3': 24,
            'KEY_4': 25, 'KEY_R': 26, 'KEY_F': 27, 'KEY_C': 28, 'KEY_F4': 30,
            'KEY_5': 31, 'KEY_T': 32, 'KEY_G': 33, 'KEY_V': 34, 'KEY_F5': 36,
            'KEY_6': 37, 'KEY_Y': 38, 'KEY_H': 39, 'KEY_B': 40, 'KEY_SPACE': 41, 'KEY_F6': 42,
            'KEY_7': 43, 'KEY_U': 44, 'KEY_J': 45, 'KEY_N': 46, 'KEY_RIGHTALT': 47, 'KEY_F7': 48,
            'KEY_8': 49, 'KEY_I': 50, 'KEY_K': 51, 'KEY_M': 52, 'KEY_FN': 53, 'KEY_F8': 54,
            'KEY_9': 55, 'KEY_O': 56, 'KEY_L': 57, 'KEY_COMMA': 58, 'KEY_RIGHTCTRL': 59, 'KEY_F9': 60,
            'KEY_0': 61, 'KEY_P': 62, 'KEY_SEMICOLON': 63, 'KEY_DOT': 64, 'KEY_LEFT': 65, 'KEY_F10': 66,
            'KEY_MINUS': 67, 'KEY_LEFTBRACE': 68, 'KEY_APOSTROPHE': 69, 'KEY_SLASH': 70, 'KEY_DOWN': 71, 'KEY_F11': 72,
            'KEY_EQUAL': 73, 'KEY_RIGHTBRACE': 74, 'KEY_RIGHTSHIFT': 76, 'KEY_RIGHT': 77, 'KEY_F12': 78,
            'KEY_BACKSPACE': 79, 'KEY_BACKSLASH': 80, 'KEY_ENTER': 81, 'KEY_UP': 82, 'KEY_INSERT': 83, 'KEY_PRINTSCREEN': 84,
            'KEY_HOME': 85, 'KEY_END': 86, 'KEY_PAGEUP': 87, 'KEY_PAGEDOWN': 88, 'KEY_DELETE': 89
        }

        # Complete key position mapping for remapping (0-125 positions)
        self.key_remap_positions = {
            'KEY_ESC': 0, 'KEY_GRAVE': 1, 'KEY_TAB': 2, 'KEY_CAPSLOCK': 3,
            'KEY_LEFTSHIFT': 4, 'KEY_LEFTCTRL': 5, 'KEY_1': 7, 'KEY_Q': 8,
            'KEY_A': 9, 'KEY_102ND': 10, 'KEY_F1': 12, 'KEY_2': 13, 'KEY_W': 14,
            'KEY_S': 15, 'KEY_Z': 16, 'KEY_LEFTMETA': 17, 'KEY_F2': 18, 'KEY_3': 19,
            'KEY_E': 20, 'KEY_D': 21, 'KEY_X': 22, 'KEY_LEFTALT': 23, 'KEY_F3': 24,
            'KEY_4': 25, 'KEY_R': 26, 'KEY_F': 27, 'KEY_C': 28, 'KEY_F4': 30,
            'KEY_5': 31, 'KEY_T': 32, 'KEY_G': 33, 'KEY_V': 34, 'KEY_F5': 36,
            'KEY_6': 37, 'KEY_Y': 38, 'KEY_H': 39, 'KEY_B': 40, 'KEY_SPACE': 41,
            'KEY_F6': 42, 'KEY_7': 43, 'KEY_U': 44, 'KEY_J': 45, 'KEY_N': 46,
            'KEY_RIGHTALT': 47, 'KEY_F7': 48, 'KEY_8': 49, 'KEY_I': 50, 'KEY_K': 51,
            'KEY_M': 52, 'KEY_FN': 53, 'KEY_F8': 54, 'KEY_9': 55, 'KEY_O': 56,
            'KEY_L': 57, 'KEY_COMMA': 58, 'KEY_RIGHTCTRL': 59, 'KEY_F9': 60,
            'KEY_0': 61, 'KEY_P': 62, 'KEY_SEMICOLON': 63, 'KEY_DOT': 64,
            'KEY_LEFT': 65, 'KEY_F10': 66, 'KEY_MINUS': 67, 'KEY_LEFTBRACE': 68,
            'KEY_APOSTROPHE': 69, 'KEY_SLASH': 70, 'KEY_DOWN': 71, 'KEY_F11': 72,
            'KEY_EQUAL': 73, 'KEY_RIGHTBRACE': 74, 'KEY_HASHTILDE': 75,
            'KEY_RIGHTSHIFT': 76, 'KEY_RIGHT': 77, 'KEY_F12': 78, 'KEY_BACKSPACE': 79,
            'KEY_BACKSLASH': 80, 'KEY_ENTER': 81, 'KEY_UP': 82, 'KEY_INSERT': 83,
            'KEY_PRINTSCREEN': 84, 'KEY_HOME': 85, 'KEY_END': 86, 'KEY_PAGEUP': 87,
            'KEY_PAGEDOWN': 88, 'KEY_DELETE': 89
        }

            # Default values
        self.current_mode = 0x01  # static
        self.current_speed = 4
        self.current_brightness = 4
        self.current_submode = 0
        self.current_color_flag = 0x00
        self.current_r = 0
        self.current_g = 0
        self.current_b = 0

        # Modifier mapping
        self.modifier_codes = {
            'KEY_LEFTCTRL': 0xe0, 'KEY_RIGHTCTRL': 0xe4,
            'KEY_LEFTSHIFT': 0xe1, 'KEY_RIGHTSHIFT': 0xe5, 
            'KEY_LEFTALT': 0xe2, 'KEY_RIGHTALT': 0xe6,
            'KEY_LEFTMETA': 0xe3, 'KEY_RIGHTMETA': 0xe7
        }
        
        # Scan code mapping
        self.scan_codes = {

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
            'KEY_F13': 0x68, 'KEY_F14': 0x69, 'KEY_F15': 0x6a, 'KEY_F16': 0x6b,
            'KEY_F17': 0x6c, 'KEY_F18': 0x6d, 'KEY_F19': 0x6e, 'KEY_F20': 0x6f,
            'KEY_F21': 0x70, 'KEY_F22': 0x71, 'KEY_F23': 0x72, 'KEY_F24': 0x73,
            
            # Numpad keys
            'KEY_NUMLOCK': 0x53, 'KEY_KPSLASH': 0x54, 'KEY_KPASTERISK': 0x55,
            'KEY_KPMINUS': 0x56, 'KEY_KPPLUS': 0x57, 'KEY_KPENTER': 0x58,
            'KEY_KP1': 0x59, 'KEY_KP2': 0x5a, 'KEY_KP3': 0x5b, 'KEY_KP4': 0x5c,
            'KEY_KP5': 0x5d, 'KEY_KP6': 0x5e, 'KEY_KP7': 0x5f, 'KEY_KP8': 0x60,
            'KEY_KP9': 0x61, 'KEY_KP0': 0x62, 'KEY_KPDOT': 0x63,
            
            # Navigation keys
            'KEY_HOME': 0x4a,
            'KEY_END': 0x4d, 'KEY_PAGEUP': 0x4b, 'KEY_PAGEDOWN': 0x4e,
            'KEY_UP': 0x52, 'KEY_DOWN': 0x51, 'KEY_LEFT': 0x50, 'KEY_RIGHT': 0x4f,
            
            # Special keys
            'KEY_ENTER': 0x28, 'KEY_SPACE': 0x2c, 'KEY_CAPSLOCK': 0x39,
            'KEY_INSERT': 0x49, 'KEY_DELETE': 0x4c, 'KEY_PRINTSCREEN': 0x46,
            'KEY_SCROLLLOCK': 0x47, 'KEY_PAUSE': 0x48,
            'KEY_SYSRQ': 0x46,  # Usually the same as PRINTSCREEN
            
            # Modifiers
            'KEY_LEFTMETA': 0xe3, 'KEY_RIGHTMETA': 0xe7, 'KEY_LEFTCTRL': 0xe0, 'KEY_RIGHTCTRL': 0xe4,
            'KEY_LEFTALT': 0xe2, 'KEY_RIGHTALT': 0xe6, 'KEY_COMPOSE': 0x65, 'KEY_MENU': 0x65,
            'KEY_LEFTSHIFT': 0xe1, 'KEY_RIGHTSHIFT': 0xe5,
            
            
            # Special symbols and international keys
            'KEY_102ND': 0x64, 'KEY_HASHTILDE': 0x32, 'KEY_BACKSLASH_RT102': 0x64,
            'KEY_RO': 0x87, 'KEY_KATAKANAHIRAGANA': 0x88, 'KEY_YEN': 0x89,
            'KEY_HENKAN': 0x8a, 'KEY_MUHENKAN': 0x8b, 'KEY_KPJPCOMMA': 0x8c,
            
            # Multimedia keys
            'KEY_MUTE': 0x7f, 'KEY_VOLUMEUP': 0x80, 'KEY_VOLUMEDOWN': 0x81,
            'KEY_PLAYPAUSE': 0xe8, 'KEY_STOPCD': 0xe9, 'KEY_PREVIOUSSONG': 0xea,
            'KEY_NEXTSONG': 0xeb, 'KEY_EJECTCD': 0xec, 'KEY_WWW': 0xf0,
            'KEY_BACK': 0xf1, 'KEY_FORWARD': 0xf2, 'KEY_CALC': 0xfb,
            'KEY_SLEEP': 0xf8, 'KEY_COFFEE': 0xf9, 'KEY_REFRESH': 0xfa,
            'KEY_MAIL': 0xfd, 'KEY_SEARCH': 0xfe, 'KEY_MEDIA': 0x12c,
            
            # Function keys for laptops or special devices
            #'KEY_FN': 0x00, 'KEY_FN_ESC': 0x01,
            
            # Power management keys
            'KEY_POWER': 0x66, 'KEY_SUSPEND': 0x67, 'KEY_WAKEUP': 0x68,
            
            # Other special keys
            'KEY_ESC2': 0x76, 'KEY_AGAIN': 0x79, 'KEY_UNDO': 0x7a,
            'KEY_CUT': 0x7b, 'KEY_COPY': 0x7c, 'KEY_PASTE': 0x7d,
            'KEY_FIND': 0x7e, 'KEY_CANCEL': 0x9e, 'KEY_HELP': 0x9b,
            'KEY_PROPS': 0xa3, 'KEY_FRONT': 0xa5, 'KEY_OPEN': 0xa5,
            'KEY_SELECT': 0x77, 'KEY_EXECUTE': 0x74, 'KEY_REDO': 0x7a,

        }

        # Special codes
        self.special_codes = {
            
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
            
            # Additional Media Controls
            'EJECT': [0x03, 0x00, 0xb8, 0x00],
            'RECORD': [0x03, 0x00, 0xb2, 0x00],
            'REWIND': [0x03, 0x00, 0xb4, 0x00],
            'FAST_FORWARD': [0x03, 0x00, 0xb3, 0x00],
            
            # Display Controls
            'BRIGHTNESS_UP': [0x03, 0x00, 0x6f, 0x00],
            'BRIGHTNESS_DOWN': [0x03, 0x00, 0x70, 0x00],
            
            # Application Controls
            'APP_MAIL': [0x03, 0x00, 0x8a, 0x01],
            'APP_CALENDAR': [0x03, 0x00, 0x8d, 0x01],
            'APP_CONTACTS': [0x03, 0x00, 0x8e, 0x01],
            'APP_MESSENGER': [0x03, 0x00, 0x8f, 0x01],
            'APP_EXPLORER': [0x03, 0x00, 0x94, 0x01],
            'APP_CALCULATOR': [0x03, 0x00, 0x92, 0x01],
            'APP_MEDIA_PLAYER': [0x03, 0x00, 0x83, 0x01],
            
            # Browser Controls
            'BROWSER_BACK': [0x03, 0x00, 0x24, 0x02],
            'BROWSER_FORWARD': [0x03, 0x00, 0x25, 0x02],
            'BROWSER_REFRESH': [0x03, 0x00, 0x27, 0x02],  # Duplicate of RELOAD
            'BROWSER_STOP': [0x03, 0x00, 0x26, 0x02],
            'BROWSER_FAVORITES': [0x03, 0x00, 0x2a, 0x02],
            
            # System controls
            'SEARCH': [0x03, 0x00, 0x21, 0x02],
            'BROWSER_HOME': [0x03, 0x00, 0x23, 0x02],
            'RELOAD': [0x03, 0x00, 0x27, 0x02],
            
            # System Controls
            'SLEEP': [0x03, 0x00, 0x82, 0x02],
            'WAKE_UP': [0x03, 0x00, 0x83, 0x02],
            'POWER': [0x03, 0x00, 0x84, 0x02],
            
            # Gaming/Keyboard Controls
            'GAME_MODE': [0x03, 0x00, 0x85, 0x02],
            'MACRO_RECORD': [0x03, 0x00, 0x86, 0x02],
            'LED_EFFECT_NEXT': [0x03, 0x00, 0x87, 0x02],
            'LED_BRIGHTNESS_UP': [0x03, 0x00, 0x88, 0x02],
            'LED_BRIGHTNESS_DOWN': [0x03, 0x00, 0x89, 0x02],
            
            # Virtual Desktops/Workspaces
            'VIEW_DESKTOPS': [0x03, 0x00, 0x8a, 0x02],
            'SWITCH_DESKTOP_LEFT': [0x03, 0x00, 0x8b, 0x02],
            'SWITCH_DESKTOP_RIGHT': [0x03, 0x00, 0x8c, 0x02],
            
            # Window Management
            'SNAP_WINDOW_LEFT': [0x03, 0x00, 0x8d, 0x02],
            'SNAP_WINDOW_RIGHT': [0x03, 0x00, 0x8e, 0x02],
            'SNAP_WINDOW_UP': [0x03, 0x00, 0x8f, 0x02],
            'SNAP_WINDOW_DOWN': [0x03, 0x00, 0x90, 0x02],
            'MAXIMIZE_WINDOW': [0x03, 0x00, 0x91, 0x02],
            'MINIMIZE_WINDOW': [0x03, 0x00, 0x92, 0x02],
            
            # Zoom Functions
            'ZOOM_IN': [0x00, 0x00, 0xe3, 0x2d],
            'ZOOM_OUT': [0x00, 0x00, 0xe3, 0x2e],
            
            # Mouse Functions
            'MOUSE_LEFT': [0x01, 0x00, 0xf0, 0x00],
            'MOUSE_RIGHT': [0x01, 0x00, 0xf1, 0x00],
            'MOUSE_CENTER': [0x01, 0x00, 0xf2, 0x00],
            'MOUSE_LEFT_UP': [0x01, 0x00, 0xf4, 0x00],
            'MOUSE_LEFT_DOWN': [0x01, 0x00, 0xf3, 0x00],
            'MOUSE_SCROLL_UP': [0x01, 0x00, 0xf5, 0x01],
            'MOUSE_SCROLL_DOWN': [0x01, 0x00, 0xf5, 0xff],
            'MOUSE_BUTTON_LEFT': [0x01, 0x00, 0xf6, 0x01],
            'MOUSE_BUTTON_RIGHT': [0x01, 0x00, 0xf6, 0x02],
            'MOUSE_BUTTON_MIDDLE': [0x01, 0x00, 0xf6, 0x04],
        }

        # Complete default remap data for all 126 positions (4 bytes each)
        self.default_remap_data = [
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
        
        self.setup_argparse()

    def setup_argparse(self):
        """Setup argument parser with comprehensive help"""
        self.parser = argparse.ArgumentParser(
            description='YenKey Keyboard Control Utility - Complete backlight and key remapping control',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_help_epilog()
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
        backlight_group.add_argument('--speed', type=int, choices=[1, 2, 3, 4], 
                                   help='Set animation speed (1=slowest, 4=fastest)')
        backlight_group.add_argument('--brightness', type=int, choices=[1, 2, 3, 4], 
                                   help='Set backlight brightness (1=dim, 4=brightest)')
        
        # Key-specific controls group
        key_group = self.parser.add_argument_group('Key-specific Controls')
        key_group.add_argument('--key-color', action='append', 
                             help='Set individual key colors for user mode (KEY:COLOR,KEY2:COLOR)')
        key_group.add_argument('--key-remap', action='append', 
                             help='Remap key(s) (SOURCE:TARGET or SOURCE:MOD1:MOD2:TARGET)')
        
        # Reset commands group
        reset_group = self.parser.add_argument_group('Reset Commands')
        reset_group.add_argument('--factory-reset', action='store_true', 
                               help='Reset keyboard to factory settings')
        reset_group.add_argument('--keymap-reset', action='store_true', 
                               help='Reset key mapping to default')

        # Listing commands group
        listing_group = self.parser.add_argument_group('Listing Commands')
        listing_group.add_argument('--list-modes', action='store_true', 
                               help='List modes (with submodes) available')
        listing_group.add_argument('--list-colors', action='store_true', 
                               help='List special function keys available')
        listing_group.add_argument('--list-keys', action='store_true', 
                               help='List physical keys')
        listing_group.add_argument('--list-standard-keycodes', action='store_true', 
                               help='List standard keycodes available')
        listing_group.add_argument('--list-special-keycodes', action='store_true', 
                               help='List special function keycodes available')

    def _get_help_epilog(self):
        """Generate comprehensive help epilog"""
        return f"""
AVAILABLE EFFECTS:

  Basic:       {', '.join(list(self.modes.keys())[:8])}
  Advanced:    {', '.join(list(self.modes.keys())[8:16])}
  Special:     {', '.join(list(self.modes.keys())[16:])}

COLOR NAMES:

  Basic:       {', '.join(list(NAMED_COLORS.keys())[:8])}
  Extended:    {', '.join(list(NAMED_COLORS.keys())[8:16])}
  Light:       {', '.join(list(NAMED_COLORS.keys())[16:24])}
  Dark:        {', '.join(list(NAMED_COLORS.keys())[24:32])}
  Full list:   {len(NAMED_COLORS)} named colors available (see --list-colors)

KEY GROUPS for --key-color:

  ALL          - All keys
  ALL_F        - Function keys F1-F12
  ALL_MOD      - Modifier keys (Ctrl, Shift, Alt, Meta)
  ALL_NAV      - Navigation keys (arrows, home, end, etc.)
  ALL_NUM      - Number keys 1-9,0
  ALL_WASD     - Gaming WASD keys
  ALL_ARROWS   - Arrow keys only
  ALL_SPECIAL  - Special keys (Esc, Enter, Space, etc.)
  ALL_ALPHA    - All alphabetic keys A-Z

SPECIAL FUNCTION KEYS for --key-remap:

  Full list:   {len(self.special_codes)} special function keys available (see --list-special-keys)

EXAMPLES:

  Basic backlight:
    yenkey-cli.py --mode=static --color=blue --brightness=3
    yenkey-cli.py --mode=wave --submode=right --speed=2 --color=rainbow

  Key colors (user mode):
    yenkey-cli.py --mode=user --key-color=ALL:white,KEY_ESC:red
    yenkey-cli.py --key-color=ALL_F:blue,ALL_MOD:green,ALL_WASD:lightblue
    yenkey-cli.py --key-color=ALL:darkblue,ALL_ALPHA:skyblue,ALL_NUM:gold

  Key remapping:
    yenkey-cli.py --key-remap=KEY_CAPSLOCK:KEY_RIGHTCTRL
    yenkey-cli.py --key-remap=KEY_ESC:KEY_LEFTALT:KEY_F1
    yenkey-cli.py --key-remap=KEY_A:disable,KEY_CAPSLOCK:KEY_LEFTSHIFT:KEY_B

  Reset commands:
    yenkey-cli.py --factory-reset
    yenkey-cli.py --keymap-reset

NOTES:

  - Key colors only work in 'user' mode (--mode=user) which must be enabled first
  - Use quotes around complex --key-color and --key-remap values
  - Multiple --key-remap options can be combined
  - Run as root/sudo for USB device access
"""

    def resolve_color(self, color_str):
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

    def parse_mode(self, mode_str):
        """Parse mode string into mode code"""
        if mode_str not in self.modes:
            raise ValueError(f"Unknown mode: {mode_str}. Available: {', '.join(self.modes.keys())}")
        return self.modes[mode_str]

    def parse_submode(self, submode_str, mode):
        """Parse submode string for specific mode"""
        # Find mode name from mode code
        mode_name = next((name for name, mode_code in self.modes.items()
                          if mode_code == mode), None)

        if not mode_name or mode_name not in self.mode_submodes:
            return 0  # Default submode
        
        if submode_str in self.mode_submodes[mode_name]:
            return self.mode_submodes[mode_name][submode_str]
        
        available = ', '.join(self.mode_submodes[mode_name].keys())
        raise ValueError(f"Unknown submode '{submode_str}' for mode '{mode_name}'. Available: {available}")

    def parse_color(self, color_str):
        """Parse color string into flag and RGB values"""
        color_lower = color_str.lower()
        
        # Predefined colors
        if color_lower in self.predefined_colors:
            return self.predefined_colors[color_lower]
        
        # Custom RGB colors
        try:
            hex_color = self.resolve_color(color_str)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return 0x08, r, g, b  # Custom RGB flag
        except ValueError:
            pass
        
        raise ValueError(f"Invalid color: {color_str}")

    def parse_user_key_colors(self, key_color_args):
        """Parse user key colors string into 7 packets with support for ALL:COLOR and key groups"""
        if not key_color_args:
            return []
        
        # Define key groups
        key_groups = {
            'ALL_F': [  # All function keys F1-F12
                'KEY_F1', 'KEY_F2', 'KEY_F3', 'KEY_F4', 'KEY_F5', 'KEY_F6',
                'KEY_F7', 'KEY_F8', 'KEY_F9', 'KEY_F10', 'KEY_F11', 'KEY_F12'
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
        
        # Initialize all positions to black (0x000000) by default
        rgb_data = [0x00] * (148 * 3)  # 148 positions * 3 bytes each
        
        # Parse key:color pairs and update RGB data
        all_color = None  # Store the ALL color if specified
        
        for key_color_str in key_color_args:
            for pair in key_color_str.split(','):
                if ':' not in pair:
                    raise ValueError(f"Invalid key-color pair: {pair}. Use KEY:COLOR")
                
                key_name, color_value = pair.split(':', 1)
                key_name = key_name.upper()
                
                # Resolve color (supports named colors and hex)
                try:
                    hex_color = self.resolve_color(color_value)
                except ValueError as e:
                    raise ValueError(f"Invalid color in pair {pair}: {e}")
                
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                
                # Handle ALL:COLOR - set as default color for all keys
                if key_name == 'ALL':
                    all_color = (r, g, b)
                    continue
                
                # Handle key groups
                if key_name in key_groups:
                    group_keys = key_groups[key_name]
                    for group_key in group_keys:
                        if group_key in self.user_key_positions:
                            position = self.user_key_positions[group_key]
                            rgb_data[position * 3] = r
                            rgb_data[position * 3 + 1] = g
                            rgb_data[position * 3 + 2] = b
                    continue
                
                # Handle individual keys
                if key_name not in self.user_key_positions:
                    # Check if it might be a group that doesn't exist
                    if key_name.startswith('ALL_'):
                        available_groups = ', '.join(key_groups.keys())
                        raise ValueError(f"Unknown key group: {key_name}. Available groups: {available_groups}")
                    else:
                        raise ValueError(f"Unknown key for user mode: {key_name}")
                
                position = self.user_key_positions[key_name]
                
                # Update RGB data for this position
                rgb_data[position * 3] = r
                rgb_data[position * 3 + 1] = g
                rgb_data[position * 3 + 2] = b
        
        # If ALL color was specified, apply it to all positions
        if all_color:
            r_all, g_all, b_all = all_color
            for position in range(148):
                # Only set positions that weren't explicitly set by individual keys or groups
                current_r = rgb_data[position * 3]
                current_g = rgb_data[position * 3 + 1] 
                current_b = rgb_data[position * 3 + 2]
                
                # If this position is still black (default), apply the ALL color
                if current_r == 0x00 and current_g == 0x00 and current_b == 0x00:
                    rgb_data[position * 3] = r_all
                    rgb_data[position * 3 + 1] = g_all
                    rgb_data[position * 3 + 2] = b_all
        
        # Create 7 packets
        packets = []
        packet_headers = [
            "0c 00 80 01 00 00 00 72",
            "0c 00 80 01 01 00 00 71", 
            "0c 00 80 01 02 00 00 70",
            "0c 00 80 01 03 00 00 6f",
            "0c 00 80 01 04 00 00 6e",
            "0c 00 80 01 05 00 00 6d",
            "0c 00 80 01 06 00 00 6c"
        ]
        
        for packet_num in range(7):
            # Each packet contains 56 bytes of RGB data (8 header + 56 data = 64 bytes)
            start_idx = packet_num * 56
            end_idx = start_idx + 56
            
            # Get RGB data for this packet
            packet_rgb_data = rgb_data[start_idx:end_idx]
            
            # Convert to hex string
            rgb_hex = " ".join(f"{b:02x}" for b in packet_rgb_data)
            
            # Combine header and RGB data
            hex_cmd = f"{packet_headers[packet_num]} {rgb_hex}"
            
            packets.append((hex_cmd, f"User key colors packet {packet_num}"))
        
        return packets

    def _define_key_groups(self):
        """Define key groups for batch color assignment"""
        return {
            'ALL_F': [12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84],  # F1-F12, PrintScreen
            'ALL_MOD': [4, 5, 17, 23, 41, 47, 53, 59, 76],  # Shift, Ctrl, Alt, Meta, Space, Fn
            'ALL_NAV': [65, 71, 77, 82, 83, 85, 86, 87, 88, 89],  # Arrows, Insert, Home, End, PgUp, PgDown, Delete
            'ALL_NUM': [7, 13, 19, 25, 31, 37, 43, 49, 55, 61, 67, 73],  # 1-9,0,-,=
            'ALL_WASD': [14, 9, 15, 16],  # W, A, S, Z (QWERTY layout)
            'ALL_ARROWS': [65, 71, 77, 82],  # Left, Down, Right, Up
            'ALL_SPECIAL': [0, 1, 2, 3, 10, 79, 80, 81, 83, 84, 85, 86, 87, 88, 89],  # Esc, Tab, Caps, Backspace, etc.
            'ALL_ALPHA': [8, 9, 14, 15, 20, 21, 26, 27, 32, 33, 38, 39, 44, 45, 50, 51, 56, 57, 62, 63, 68, 69, 74, 75, 80, 81]  # A-Z
        }

    def parse_key_remap(self, remap_args):
        """Parse key remapping arguments"""
        if not remap_args:
            return []
        
        all_remap_commands = []
        
        for remap_str in remap_args:
            # Split multiple remap commands by comma within each --key-remap argument
            for single_remap in remap_str.split(','):
                if ':' not in single_remap:
                    raise ValueError(f"Invalid key-remap format: {single_remap}. Use KEY:[MOD1[:MOD2]]:TARGET_KEY")
                    
                parts = single_remap.split(':')
                source_key = parts[0].upper()
                
                # Check if we're disabling the key
                if len(parts) >= 2 and parts[1].lower() == 'disable':
                    all_remap_commands.append((source_key, [0x00, 0x00, 0x00, 0x00]))
                    continue
                
                # Check if last part is a target key
                if len(parts) >= 2 and parts[-1].upper().startswith('KEY_'):
                    target_key = parts[-1].upper()
                    modifiers = parts[1:-1] if len(parts) > 2 else []
                else:
                    target_key = parts[1].upper()
                    modifiers = []
                
                # Convert modifiers to codes (handles special FN modifier)
                mod_codes = []
                for mod in modifiers:
                    mod_upper = mod.upper()
                    if mod_upper in self.modifier_codes:
                        mod_codes.append(self.modifier_codes[mod_upper])
                    else:
                        raise ValueError(f"Unknown modifier: {mod}")
                
                # Get target scan code (handles special keys)
                if target_key in self.special_codes:
                    special_code = self.special_codes[target_key.upper()]
                    position_data = [special_code[0], special_code[1], special_code[2], special_code[3]]
                # Common keys
                elif target_key in self.scan_codes:
                    ending = 0x00
                    target_scan = self.scan_codes[target_key]
                    if len(mod_codes) == 1:
                        position_data = [0x00, mod_codes[0], target_scan, 0x00]
                    elif len(mod_codes) == 2:
                        position_data = [0x00, mod_codes[0], mod_codes[1], target_scan]
                    else:
                        position_data = [0x00, 0x00, target_scan, 0x00]
                    
                else:
                    raise ValueError(f"Unknown target key: {target_key}")
                
                all_remap_commands.append((source_key, position_data))
        
        return all_remap_commands
    
    def execute_remap_commands(self, remap_commands):
        """Execute multiple remap commands and send complete configuration"""
        # Start with default mapping
        remap_data = self.default_remap_data.copy()
        
        # Apply each remap command
        for source_key, new_data in remap_commands:
            if source_key not in self.key_remap_positions:
                raise ValueError(f"Unknown source key for remapping: {source_key}")
            
            position = self.key_remap_positions[source_key]
            data_index = position * 4  # 4 bytes per position
            
            # Replace the 4 bytes for this position
            remap_data[data_index:data_index+4] = new_data
        
        # Send all 9 packets
        return self.proto.send_remap_packets(remap_data)

    def _parse_single_remap(self, remap_str, remap_data):
        """Parse single remap specification"""
        parts = remap_str.split(':')
        
        if len(parts) < 2:
            raise ValueError(f"Invalid remap format: {remap_str}")
        
        source_key = parts[0].strip().upper()
        target_keys = [p.strip().upper() for p in parts[1:]]
        
        # Handle disable
        if len(target_keys) == 1 and target_keys[0] == 'DISABLE':
            self._disable_key(source_key, remap_data)
            return
        
        # Handle normal remapping
        self._remap_key(source_key, target_keys, remap_data)

    def _disable_key(self, source_key, remap_data):
        """Disable a key"""
        if source_key not in self.key_remap_positions:
            raise ValueError(f"Unknown source key: {source_key}")
        
        position = self.key_remap_positions[source_key]
        data_index = position * 4
        
        # Set to disabled state (all zeros)
        remap_data[data_index:data_index+4] = [0x00, 0x00, 0x00, 0x00]
        
        print(f"Disabled key: {source_key}")

    def _remap_key(self, source_key, target_keys, remap_data):
        """Remap a key to target key(s)"""
        if source_key not in self.key_remap_positions:
            raise ValueError(f"Unknown source key: {source_key}")
        
        # Validate target keys
        for target_key in target_keys:
            if target_key not in self.scan_codes and target_key not in self.modifier_codes:
                raise ValueError(f"Unknown target key: {target_key}")
        
        position = self.key_remap_positions[source_key]
        data_index = position * 4
        
        # Handle different numbers of target keys
        if len(target_keys) == 1:
            # Single key mapping
            scan_code = self._get_scan_code(target_keys[0])
            remap_data[data_index:data_index+4] = [0x00, 0x00, scan_code, 0x00]
            
        elif len(target_keys) == 2:
            # Key with modifier
            mod_code = self._get_modifier_code(target_keys[0])
            scan_code = self._get_scan_code(target_keys[1])
            remap_data[data_index:data_index+4] = [mod_code, 0x00, scan_code, 0x00]
            
        elif len(target_keys) >= 3:
            # Key with two modifiers
            mod1_code = self._get_modifier_code(target_keys[0])
            mod2_code = self._get_modifier_code(target_keys[1])
            scan_code = self._get_scan_code(target_keys[2])
            remap_data[data_index:data_index+4] = [mod1_code, mod2_code, scan_code, 0x00]
        
        print(f"Remapped {source_key} -> {':'.join(target_keys)}")

    def _get_scan_code(self, key_name):
        """Get scan code for key name"""
        if key_name in self.scan_codes:
            return self.scan_codes[key_name]
        if key_name in self.modifier_codes:
            return self.modifier_codes[key_name]
        raise ValueError(f"Unknown key: {key_name}")

    def _get_modifier_code(self, key_name):
        """Get modifier code for key name"""
        if key_name in self.modifier_codes:
            return self.modifier_codes[key_name]
        raise ValueError(f"Not a modifier key: {key_name}")

    def run(self):
        """Main CLI execution"""
        args = self.parser.parse_args()
        
        # Connect to device
        #if not self.proto.connect():
        #    sys.exit(1)
        
        success = True
        
        try:
            # Handle reset commands first
            if args.factory_reset:
                success = self.proto.factory_reset() and success
                if success:
                    print("Factory reset completed")
                return
            
            if args.keymap_reset:
                print("Resetting key mapping to default...")
                if self.proto.send_remap_packets(self.default_remap_data):
                    print("Key mapping reset completed successfully")
                else:
                    print("Key mapping reset failed")
                return
            
            if args.list_modes:
                  print("Modes (with submodes) available:")
                  print("-" * 50)
                  for mode in self.modes:
                      print(f" - {mode}")
                      if mode in self.mode_submodes:
                          print("   -", "\n   - ".join(self.mode_submodes[mode]))
                  return
            
            if args.list_colors:
                  print("Colors (names) available:")
                  print("-" * 50)
                  print(" -", "\n - ".join(sorted(NAMED_COLORS)))
                  return
            
            if args.list_keys:
                  print("Physical keys available for remapping:")
                  print("-" * 50)
                  print(" -", "\n - ".join(sorted(self.key_remap_positions)))
                  return
            
            if args.list_standard_keycodes:
                  print("Standard keycodes available:")
                  print("-" * 50)
                  print(" -", "\n - ".join(sorted(self.scan_codes)))
                  return
            
            if args.list_special_keycodes:
                  print("Special keycodes (events) available:")
                  print("-" * 50)
                  print(" -", "\n - ".join(sorted(self.special_codes)))
                  return
            
            # Handle backlight modes
            if args.mode:
                mode = self.parse_mode(args.mode)
                submode = 0
                
                if args.submode:
                    submode = self.parse_submode(args.submode, mode)
                
                # Update current settings
                self.current_mode = mode
                self.current_submode = submode
                
                # Handle color if specified
                if args.color:
                    color_flag, r, g, b = self.parse_color(args.color)
                    self.current_color_flag = color_flag
                    self.current_r = r
                    self.current_g = g
                    self.current_b = b
                else:
                    # Keep current color settings
                    pass
                
                # Apply speed and brightness
                speed = args.speed if args.speed else self.current_speed
                brightness = args.brightness if args.brightness else self.current_brightness
                
                success = self.proto.set_backlight_combined(
                    self.current_mode, speed, brightness, 
                    self.current_submode, self.current_color_flag,
                    self.current_r, self.current_g, self.current_b
                ) and success
            
            # Handle key colors (user mode only)
            if args.key_color:
                key_color_packets = self.parse_user_key_colors(args.key_color)
                if key_color_packets:
                    success = self.proto.set_user_key_colors(key_color_packets) and success
            
            # Handle key remapping
            if args.key_remap:
                remap_commands = self.parse_key_remap(args.key_remap)
                
                # Print each remap command
                for source_key, position_data in remap_commands:
                    mod_str = " -> disabled" if position_data == [0x00, 0x00, 0x00, 0x00] else " -> remapped"
                    print(f"Remap {source_key}{mod_str}")
                
                if remap_commands:
                    print("Applying key remapping configuration...")
                    if self.execute_remap_commands(remap_commands):
                        print(f"Key remapping completed successfully ({len(remap_commands)} changes)")
            
            if success:
                print("All operations completed successfully")
            else:
                print("Some operations failed")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error: {e}")
            success = False
            sys.exit(1)
            
        finally:
            self.proto.disconnect()


if __name__ == "__main__":
    cli = YenKeyCLI()
    cli.run()
