# YenKey CLI Utility

A comprehensive Python command-line utility for controlling **Yenkee YKB3700 Rogue** (and probably others based on a similar ROYUAN chipset) keyboard backlight effects, key colors, and key remapping through reverse-engineered USB protocol.

**See source code:** [yenkey-cli.py](/src/yenkey-cli.py)

## Features

- Backlight Effects: 20+ customizable lighting effects (see `--list-modes`)
- Key Colors: Per-key RGB coloring with group support
- Key Remapping: Full key remapping including FN key and special function keys
- User Mode: Advanced per-key color customization
- Factory Reset: Restore original settings
- Keymap Reset: Restore original keymap

## Installation

### Requirements
```
sudo apt-get install python3-usb
# or
pip install pyusb
```

## Usage
```
# Run as root to access USB (or create appropriate UDEV rules)
sudo python3 yenkey-cli.py [OPTIONS]
```

### Backlight Controls

#### Effects
```
# Basic effects
--mode static --color blue --brightness 3
--mode wave --submode right --speed 2 --color rainbow
--mode breath --color red
```

```
# Advanced effects  
--mode snake --submode tocenter
--mode kaleidoscope --submode fromcenter
--mode roundwave --submode clockwise
```

##### Available Effects
- static, breath, neon, wave, waterdrop, rain, snake, fadeout, spiral, sinusoid, kaleidoscope, linear, user, laser, roundwave, shining, rain2, horizontal, staticfade, music-edm, music-standard, surf, skew

### Parameters
 - `--mode`: Lighting effect mode
 - `--color`: Predefined color, named color, or RRGGBB hex
 - `--speed`: Animation speed (1-4, 1=fastest)
 - `--brightness`: Backlight brightness (1-4, 1=dim)
 - `--submode`: Effect direction/variant

### Key Colors (User Mode)
Set individual key colors with group support:

```
# Enable user mode first
--mode user
```

```
# Basic color schemes
--key-color ALL:white,KEY_ESC:red
--key-color ALL_F:blue,ALL_MOD:green,ALL_WASD:lightblue
```

```
# Gaming setup
--key-color ALL:darkblue,ALL_ALPHA:skyblue,ALL_NUM:gold,ALL_SPECIAL:gray,ALL_WASD:red
```

```
# Custom colors
--key-color ALL:336699,ALL_ARROWS:ffff00,KEY_ENTER:00ff00
```

### Key Groups
- ALL - All keys
- ALL_F - Function keys F1-F12
- ALL_MOD - Modifier keys (Ctrl, Shift, Alt, Meta)
- ALL_NAV - Navigation keys (arrows, home, end, etc.)
- ALL_NUM - Number keys 1-9,0
- ALL_WASD - Gaming WASD keys
- ALL_ARROWS - Arrow keys only
- ALL_SPECIAL - Special keys (Esc, Enter, Space, etc.)
- ALL_ALPHA - All alphabetic keys A-Z

### Color Formats
- Hex colors: ff0000, 336699, ff00ff... (custom RGB in HEX format)
- 70+ predefined colors including web safe, pastel, and gaming colors... and many more (see `--list-colors`)

## Key Remapping

Remap keys (with or without modifier support):

### Simple remapping
```
--key-remap KEY_CAPSLOCK:KEY_RIGHTCTRL
--key-remap KEY_ESC:KEY_F1
```

### With modifiers
```
--key-remap KEY_ESC:KEY_LEFTALT:KEY_F1
--key-remap KEY_CAPSLOCK:KEY_LEFTSHIFT:KEY_B
```

### Multiple remaps
(you can use multple key definitions comma-delimited or multiple `--key-remap` arguments)
```
--key-remap KEY_A:disable,KEY_F1:KEY_ESC,KEY_ESC:KEY_FN --key-remap KEY_Y:KEY_Z
```

### Disable keys
```
--key-remap KEY_RIGHTCTRL:disable
```

### FN Key Control
```
# Move FN to another key
--key-remap KEY_ESC:KEY_FN

# Set FN to another functionality  
--key-remap KEY_FN:KEY_ESC
```

## Reset Commands

### Factory reset
```
--factory-reset
```

### Reset key mapping to the defaults
```
--keymap-reset
```

## Examples

### Gaming Setup
```
# Red backlight with custom key colors
sudo python3 yenkey-cli.py --brightness 4 \
  --key-color ALL_WASD:white,ALL_F:blue,ALL_MOD:green
```

```
# Remap CapsLock to Ctrl for gaming
sudo python3 yenkey-cli.py --key-remap KEY_CAPSLOCK:KEY_LEFTCTRL
```

### Productivity Setup
```
# Gentle wave effect
sudo python3 yenkey-cli.py --mode wave --submode right --color lightblue --speed 4 --brightness 2
```

### Office Setup
```
# Enable user mode
sudo python3 yenkey-cli.py --mode user

# Set groups of keys in different colors
sudo python yenkey-cli.py --key-color ALL:lightyellow,ALL_F:ff00ff,ALL_MOD:ffff00,ALL_NUM:orange,ALL_NAV:gray,ALL_SPECIAL:black \
                          --key-color ALL_ALPHA:336699,KEY_LEFTMETA:blue,ALL_ARROWS:gray,KEY_DELETE:red,KEY_BACKSPACE:red \
                          --key-color KEY_PRINTSCREEN:blue,KEY_ENTER:green,ALL_ARROWS:white,KEY_INSERT:blue,KEY_ESC:red,KEY_FN:blue

# Remap RightAlt to Menu key
sudo python3 yenkey-cli.py --key-remap KEY_RIGHTALT:KEY_MENU
```

## Advanced Features

### Protocol Details

- Uses USB Vendor ID: 0x3151, Product ID: 0x4002
- Communication via USB control transfers on interface 1 (**Using USB cable only!** - over 2.4G dongle or Bluetooth will not work)
- 64-byte packet structure with checksum
- 9 packets for complete key remapping configuration
- 7 packets for user mode key colors

## Special Notes

- FN Key: Can be moved but not combined with other keys
- User Mode: Key colors (`--key-color`) only work with `--mode user`
- Root Access: Required for USB device communication (or create appropriate UDEV rules)
- Multiple Key Colors: Separate with commas or use multiple --key-color options
- Multiple Remaps: Separate with commas or use multiple --key-remap options

## Important Usage Notes

### Separate Configuration Commands

**Backlight, key colors, and remapping require separate commands** because each configuration type triggers an internal keyboard reset. After each command, the keyboard temporarily disconnects and reconnects, making subsequent packets in the same command fail.

- Backlight effects (--mode, --speed, --brightness, --color)
- Key colors (--key-color) - requires --mode user command first
- Key remapping (--key-remap)

#### Required workflow:

```
# ✅ CORRECT - Separate commands
sudo python3 yenkey-cli.py --mode wave --color blue --speed 2
sudo python3 yenkey-cli.py --key-color "ALL:red,ALL_F:blue"
sudo python3 yenkey-cli.py --key-remap "KEY_ESC:KEY_FN,KEY_CAPSLOCK:KEY_LEFTCTRL"

# ❌ INCORRECT - Combined commands (only last setting applies)
sudo python3 yenkey-cli.py \
  --mode user \
  --key-color "ALL:red" \
  --key-remap "KEY_ESC:KEY_FN"
```

  *Note: Each configuration type uses different USB command packets and must be sent independently to the keyboard.*

### Backlight Configuration

Backlight settings must be sent as a complete configuration package. The utility does not store configuration locally and cannot read current settings from the keyboard. Therefore:

- Always use `--mode` when changing other backlight parameters
- `--speed`, `--brightness`, and `--color` arguments require `--mode` to be specified

Each command sends the complete current backlight state to the keyboard

#### Examples:

```
# ✅ CORRECT - complete configuration
sudo python3 yenkey-cli.py --mode wave --speed 2 --brightness 3 --color blue

# ✅ CORRECT - partial update (uses current mode with new speed)
sudo python3 yenkey-cli.py --mode wave --speed 3

# ❌ INCORRECT - missing effect mode
sudo python3 yenkey-cli.py --speed 2 --color red  # Will not work!
```

### Key Remapping

Key remapping requires sending the complete keymap configuration:

- Multiple --key-remap arguments are combined into one complete configuration
- Each remap operation sends the entire keymap, not incremental changes
- Previous remaps are not preserved between commands

#### Examples:

```
# ✅ CORRECT - multiple remaps in one command
sudo python3 yenkey-cli.py --key-remap "KEY_ESC:KEY_FN,KEY_CAPSLOCK:KEY_LEFTCTRL"

# ✅ CORRECT - multiple --key-remap arguments (combined)
sudo python3 yenkey-cli.py \
  --key-remap "KEY_ESC:KEY_FN" \
  --key-remap "KEY_CAPSLOCK:KEY_LEFTCTRL"

# ❌ INCORRECT - sequential commands don't combine
sudo python3 yenkey-cli.py --key-remap "KEY_ESC:KEY_FN"
sudo python3 yenkey-cli.py --key-remap "KEY_CAPSLOCK:KEY_LEFTCTRL"  # First remap is lost!
```

## Current Limitations

- No configuration persistence - Settings are not saved between utility runs
- No read capability - Cannot query current keyboard state
- Complete updates only - No incremental configuration changes
- Keyboard memory only - Settings persist on keyboard but not in utility

## Workflow Recommendation

For complex configurations, create script files with complete settings:

```
# gaming-setup.sh
sudo python3 yenkey-cli.py \
  --mode static \
  --color red \
  --brightness 4

sudo python3 yenkey-cli.py \
  --key-color "ALL_WASD:white,ALL_F:blue"

sudo python3 yenkey-cli.py \
  --key-remap "KEY_CAPSLOCK:KEY_LEFTCTRL,KEY_ESC:PLAY_PAUSE"
```

## License

This project is licensed under GPLv3. Respect your hardware manufacturer's warranties and terms of service.

## Contributing

Contributions and testing welcome! This utility was created through extensive USB protocol reverse engineering.

**Note: This utility provides capabilities beyond the original OEM software, including FN key remapping and advanced color control. Use responsibly!**
