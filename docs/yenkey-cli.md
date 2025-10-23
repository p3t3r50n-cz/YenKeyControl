# YenKey CLI Utility

A comprehensive Python command-line utility for controlling **Yenkee YKB3700 Rogue** (and probably others based on a similar ROYUAN (maybe ROGYUAN?) chipset) keyboard backlight effects, per-key RGB colors, and advanced key remapping through reverse-engineered USB protocol.

**See source code:** [yenkey-cli.py](/src/yenkey-cli.py)

## Features

- **Backlight Effects**: 20+ customizable lighting effects with speed and brightness control
- **Per-Key RGB Coloring**: Individual key colors with comprehensive group support
- **Complete Key Remapping**: Full key remapping including modifiers and special functions
- **Multimedia Controls**: Volume, playback, brightness, and application controls
- **Mouse Click Emulation**: Mouse functions and scrolling capabilities
- **FN Key Customization**: Reposition and customize FN key behavior
- **Preset System**: Predefined configurations for common use cases
- **Live Configuration Reading**: Read current settings directly from keyboard
- **Factory or Keymap Reset**: Restore original settings and keymaps

## Installation

### Requirements
```bash
sudo apt-get install python3-usb
# or
pip install pyusb
```

## Basic Usage
```bash
# Run as root to access USB (or create appropriate UDEV rules)
sudo python3 yenkey-cli.py [OPTIONS]
```

### Quick Examples
```bash
# Apply gaming preset
sudo python3 yenkey-cli.py --preset gaming

# Read current settings
sudo python3 yenkey-cli.py --read-settings

# Simple backlight control
sudo python3 yenkey-cli.py --mode wave --color blue --speed 2

# Per-key colors
sudo python3 yenkey-cli.py --mode user
sudo python3 yenkey-cli.py --key-color "ALL_F:cyan,ALL_MOD:lightblue"

# Key remapping for productivity
sudo python3 yenkey-cli.py --key-remap "KEY_CAPSLOCK:KEY_ESC,KEY_F1:KEY_LEFTCTRL:KEY_S"
```

## Backlight Controls

### Basic Backlight
```bash
# Static color
--mode static --color blue --brightness 3

# Animated effects
--mode wave --submode right --speed 2 --color rainbow
--mode breath --color red --speed 1 --brightness 2
--mode snake --submode tocenter --color green
```

### Advanced Effects
```bash
--mode kaleidoscope --submode fromcenter
--mode roundwave --submode clockwise  
--mode music-edm --submode upright
--mode surf --color purple
```

### Available Effects
- **Static color**: `static`, `staticfade`, `fadeout`
- **Animated**: `wave`, `breath`, `neon`, `waterdrop`, `rain`, `rain2`, `snake`, `spiral`, `sinusoid`, `kaleidoscope`, `linear`, `laser`, `roundwave`, `shining`, `horizontal`, `skew`, `surf`
- **Music Reactive**: `music-edm`, `music-standard` (not tested)
- **Custom**: `user` (for per-key colors)

### Parameters
- `--mode`: Lighting effect mode (required for backlight changes)
- `--submode`: Effect direction/variant (see `--list-modes` for available submodes)
- `--speed`: Animation speed (1-11, 1=fast, 2=slow, 3=very slow, 4=slowest, 5=stopped, 6=fastest .. 10=super fast, 11=ultra fast)
- `--brightness`: Backlight brightness (1-4, 1=dim, 4=brightest)
- `--color`: Predefined color, named color, or RRGGBB hex

## Per-Key RGB Colors (User Mode)

Set individual key colors with extensive group support. **Requires `--mode user`**.

### Basic Color Schemes
```bash
# Enable user mode first
--mode user

# Basic highlighting
--key-color "ALL:silver,KEY_ESC:red,KEY_ENTER:green"

# Function keys (F1-F12)
--key-color "ALL_F:yellow"

# Function key groups (F1-F4, F5-F8, F9-F12)
--key-color "ALL_F:yellow,ALL_F1:red,ALL_F2:green,ALL_F3:blue"

# Modifier and navigation keys highlighting
--key-color "ALL_MOD:lightblue,ALL_NAV:336699"
```

### Gaming Setup
```bash
--key-color "ALL:black,ALL_WASD:red,ALL_ARROWS:yellow,ALL_F:orange"
```

### Programming Setup
```bash
--key-color "ALL:silver,ALL_NUM:lightyellow,ALL_F:cyan,KEY_LEFTBRACE:magenta,KEY_RIGHTBRACE:magenta"
```

### Complete Key Groups
- `ALL` - All keys
- `ALL_F` - All function keys F1-F12
- `ALL_F1` - Function keys F1-F4
- `ALL_F2` - Function keys F5-F8  
- `ALL_F3` - Function keys F9-F12
- `ALL_MOD` - All modifier keys (Ctrl, Shift, Alt, Meta)
- `ALL_NAV` - Navigation keys (arrows, home, end, page up/down, etc.)
- `ALL_NUM` - Number keys 1-9,0
- `ALL_WASD` - Gaming WASD keys
- `ALL_ARROWS` - Arrow keys only
- `ALL_SPECIAL` - Special keys (Esc, Enter, Space, Backspace, Tab, etc.)
- `ALL_ALPHA` - All alphabetic keys A-Z

### Color Formats
- **Hex colors**: `ff0000`, `336699`, `ff00ff` (custom RGB in HEX format)
- **70+ named colors**: Including web safe, pastel, and gaming colors (see `--list-colors`)
- **RGB prefix**: `rgb:ff0000`

  **Color Accuracy Note**: Some colors may not appear exactly as expected due to hardware limitations of the keyboard's RGB LEDs. The color rendering can vary depending on the specific LED components used in your keyboard model.

## Key Remapping

### Simple Remapping
```bash
# Single key remapping
--key-remap "KEY_CAPSLOCK:KEY_RIGHTCTRL"
--key-remap "KEY_ESC:KEY_F1"

# Disable keys
--key-remap "KEY_RIGHTCTRL:disable"
```

### Modifier Combinations
```bash
# Single modifier
--key-remap "KEY_F1:KEY_LEFTALT:KEY_F1"

# Multiple modifiers
--key-remap "KEY_F12:KEY_LEFTCTRL:KEY_LEFTSHIFT:KEY_S"
```

### Special Functions
```bash
# Multimedia controls
--key-remap "KEY_F1:VOLUME_DOWN,KEY_F2:VOLUME_UP,KEY_F3:MUTE"

# Application launchers
--key-remap "KEY_F4:APP_CALCULATOR,KEY_F5:APP_MAIL"

# Browser controls
--key-remap "KEY_F6:BROWSER_BACK,KEY_F7:BROWSER_FORWARD"

# Mouse functions
--key-remap "KEY_F8:MOUSE_LEFT,KEY_F9:MOUSE_RIGHT"
```

### FN Key Control
```bash
# Move FN to another key
--key-remap "KEY_ESC:KEY_FN"

# Set FN key to special function
--key-remap "KEY_FN:PLAY_PAUSE"
```

### Multiple Remaps
```bash
# Comma-separated in one argument
--key-remap "KEY_A:disable,KEY_F1:KEY_ESC,KEY_ESC:KEY_FN"

# Multiple --key-remap arguments
--key-remap "KEY_CAPSLOCK:KEY_ESC" --key-remap "KEY_F1:KEY_LEFTCTRL:KEY_S"
```

### Direct Hex Values
```bash
# Use raw hex values for advanced remapping
--key-remap "KEY_F1:00e23a00"
```

## Preset System

### Built-in Presets
```bash
# List available presets
--list-presets

# Apply presets
--preset office
--preset gaming  
--preset programming
--preset media
--preset writing
--preset presentation
--preset night
--preset minimal
--preset productivity
```

### Custom Presets
```bash
# Save current settings as preset
--save-preset my-custom-preset.json

# Load custom preset from file
--load-preset my-custom-preset.json
```

## Read Commands

### Read Current Settings
```bash
# Read all settings
--read-settings

# Read specific sections
--read-backlight
--read-key-colors  
--read-key-remap
```

## Reset Commands

### Factory Reset
```bash
# Complete factory reset (all custom settings lost!)
--factory-reset
```

### Keymap Reset
```bash
# Reset only key mapping to defaults
--keymap-reset
```

## Listing Commands

### Available Options
```bash
# List all modes with submodes
--list-modes

# List all named colors
--list-colors

# List physical keys and functions
--list-keys

# List standard keycodes and modifiers
--list-standard-keycodes

# List special function keycodes
--list-special-keycodes

# List all presets
--list-presets
```

## Debug Options

### Debug Levels
```bash
--debug NONE      # No debug output
--debug ERROR     # Only errors
--debug WARNING   # Errors and warnings
--debug INFO      # Informational messages (default)
--debug DEBUG     # Detailed debugging
--debug VERBOSE   # Maximum verbosity
```

## Complete Examples

### Gaming Setup
```bash
# Apply gaming preset
sudo python3 yenkey-cli.py --preset gaming

# Or build manually
sudo python3 yenkey-cli.py --mode user --brightness 4
sudo python3 yenkey-cli.py --key-color "ALL:black,ALL_WASD:red,ALL_ARROWS:yellow"
sudo python3 yenkey-cli.py --key-remap "KEY_CAPSLOCK:KEY_LEFTSHIFT,KEY_F1:GAME_MODE"
```

### Office/Productivity Setup
```bash
# Professional office setup
sudo python3 yenkey-cli.py --preset office

# Or custom setup
sudo python3 yenkey-cli.py --mode user --brightness 3
sudo python3 yenkey-cli.py --key-color "ALL:silver,ALL_F:yellow,ALL_MOD:lightblue"
sudo python3 yenkey-cli.py --key-remap "KEY_CAPSLOCK:KEY_LEFTCTRL,KEY_F1:KEY_LEFTALT:KEY_F1"
```

### Programming Setup
```bash
# Optimized for coding
sudo python3 yenkey-cli.py --preset programming

# Custom programming setup
sudo python3 yenkey-cli.py --mode user --brightness 3
sudo python3 yenkey-cli.py --key-color "ALL:silver,ALL_F:cyan,KEY_LEFTBRACE:magenta,KEY_RIGHTBRACE:magenta"
sudo python3 yenkey-cli.py --key-remap "KEY_CAPSLOCK:KEY_ESC,KEY_F12:KEY_LEFTCTRL:KEY_S"
```

### Media Center Setup
```bash
# Media controls with relaxing lights
sudo python3 yenkey-cli.py --preset media

# Custom media setup
sudo python3 yenkey-cli.py --mode breath --color purple --speed 1 --brightness 2
sudo python3 yenkey-cli.py --key-remap "KEY_F1:VOLUME_DOWN,KEY_F2:VOLUME_UP,KEY_F3:MUTE,KEY_F4:PLAY_PAUSE"
```

## Technical Details

### Protocol Information
- **USB Vendor ID**: `0x3151`
- **USB Product ID**: `0x4002` 
- **Interface**: `1`
- **Packet Size**: `64 bytes`
- **Communication**: USB control transfers only (wired connection required)

### Configuration Storage
- Settings are stored directly in keyboard memory
- Persist across computer restarts and keyboard reconnects
- No local configuration file required

### Command Structure
- Each configuration type requires separate commands
- Backlight, key colors, and remapping cannot be combined in single command
- Complete configuration packets sent for each operation

## Important Usage Notes

### Separate Configuration Commands

**Backlight, key colors, and key remapping must be configured in separate commands** due to keyboard firmware limitations. Each configuration type triggers an internal reset.

```bash
# ✅ CORRECT - Separate commands
sudo python3 yenkey-cli.py --mode user --brightness 3
sudo python3 yenkey-cli.py --key-color "ALL:red,ALL_F:blue" 
sudo python3 yenkey-cli.py --key-remap "KEY_ESC:KEY_FN"

# ❌ INCORRECT - Combined commands (will fail)
sudo python3 yenkey-cli.py --mode user --key-color "ALL:red" --key-remap "KEY_ESC:KEY_FN"
```

### Backlight Configuration

Backlight settings can be configured separately:

```bash
# Complete configuration
sudo python3 yenkey-cli.py --mode wave --speed 2 --brightness 3 --color blue

# Mode with partial updates
sudo python3 yenkey-cli.py --mode wave --speed 3

# Only color
sudo python3 yenkey-cli.py --color red
```

### Key Remapping Behavior

Key remapping supports incremental configuration:

```bash
# Multiple remaps in one command
sudo python3 yenkey-cli.py --key-remap "KEY_ESC:KEY_FN,KEY_CAPSLOCK:KEY_LEFTCTRL"

# Sequential commands (preserves previous remaps)
sudo python3 yenkey-cli.py --key-remap "KEY_ESC:KEY_FN"
sudo python3 yenkey-cli.py --key-remap "KEY_CAPSLOCK:KEY_LEFTCTRL"  # Both remaps are preserved
```

## Testing on Different Hardware

The utility supports custom Vendor and Product IDs for testing on other keyboards with similar ROYUAN chipsets:

```bash
# Test on different hardware
sudo python3 yenkey-cli.py --vid 1234 --pid 5678 --read-settings
sudo python3 yenkey-cli.py --vid abcd --pid ef01 --mode wave --color blue
```

Parameters:
 - `--vid` - USB Vendor ID (default: 0x3151)
 - `--pid` - USB Product ID (default: 0x4002)

## Troubleshooting

### Common Issues

1. **"Keyboard not found"**
   - Ensure keyboard is connected via USB cable (not wireless)
   - Run with `sudo` for USB device access (or create appropriate UDEV rules for non-root access - see bellow)
   - Check USB vendor/product IDs match

2. **Key colors not working**
   - Must use `--mode user` for per-key colors
   - Send key colors command after enabling user mode

3. **Settings not persisting**
   - Each configuration type requires separate commands
   - Wait for keyboard to reconnect between commands

4. **FN key limitations**
   - FN key can be moved but not combined with modifiers
   - Some FN combinations may have hardware limitations

## UDEV rules example

```bash
cat /etc/udev/rules.d/99-yenkee-keyboard.rules
# Yenkee keyboard - full access
SUBSYSTEM=="usb", ATTR{idVendor}=="3151", ATTR{idProduct}=="4002", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb_device", ATTR{idVendor}=="3151", ATTR{idProduct}=="4002", MODE="0666", GROUP="plugdev"

# Allow USB unbind/bind for specific device
SUBSYSTEM=="usb", ATTR{idVendor}=="3151", ATTR{idProduct}=="4002", ACTION=="add", RUN+="/bin/chgrp plugdev /sys/bus/usb/drivers/usb/unbind"
SUBSYSTEM=="usb", ATTR{idVendor}=="3151", ATTR{idProduct}=="4002", ACTION=="add", RUN+="/bin/chgrp plugdev /sys/bus/usb/drivers/usb/bind"
SUBSYSTEM=="usb", ATTR{idVendor}=="3151", ATTR{idProduct}=="4002", ACTION=="add", RUN+="/bin/chmod g+w /sys/bus/usb/drivers/usb/unbind"
SUBSYSTEM=="usb", ATTR{idVendor}=="3151", ATTR{idProduct}=="4002", ACTION=="add", RUN+="/bin/chmod g+w /sys/bus/usb/drivers/usb/bind"
```

## License

This project is licensed under GPLv3. See source code for complete license details.

**Disclaimer**: This software is the result of reverse engineering and is provided for educational and personal use. Respect your hardware manufacturer's warranties and terms of service.

## Contributing

**Contributions and testing welcome!** Feel free to test, fork, and modify to make it even better. Testing on other ROYUAN chipset-based keyboards would be very helpful for expanding compatibility.

**Project Page**: https://github.com/p3t3r50n-cz/YenKeyControl
