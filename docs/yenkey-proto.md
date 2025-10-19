# Yenkee 3700 Rogue Keyboard - Prototyping Controller Utility

Simple prototyping script for functionality verification and packet debugging.

**See source code:** [yeneky-proto.py](/src/yenkey-proto.py)

## Overview

A Python utility for controlling RGB lighting effects and key remapping on the Yenkee 3700 Rogue mechanical keyboard. This tool enables cross-platform control without relying on the vendor's Windows-only software.

## Features

- **RGB Lighting Control**: Set static colors, breathing effects, wave patterns, and more
- **Key Remapping**: Customize keyboard layout and assign macros
- **Cross-Platform**: Works on Linux, macOS, and other systems
- **Preset Commands**: Pre-configured lighting effects for quick use
- **Custom Packets**: Send raw HID packets for advanced customization

## Supported Lighting Effects

- Static colors
- Breathing effects  
- Wave patterns (multiple directions)
- Disco/rainbow effects
- Neon, snake, spiral, and more
- Sound-reactive modes (EDM/Standard)
- Custom RGB color support
- ... and more

## Usage

### Basic Usage

Help & usage (without arguments)
```bash
./yenkey-proto.py
```

Predefined actions
```bash
./yenkey-proto.py <action>
```

Custom packets
```bash
./yenkey-proto.py <packet> [packet1] ... [packetN]
```

## Set effect and colors

```
# horizontal wave in rainbow
./yenkey-proto.py "0704020417000000"

# snake in yellow
yenkey-proto.py "07 07 04 04 08 ff ff 00"

# kaleidoscope (to center) in default red
yenkey-proto.py "07 0b 02 04 10 ff 45 6e"
```

## Key Remapping

Use with key mapping packets to customize keyboard layout:

`./yenkey-proto.py "packet0" "packet1" ... "packet8"`

## Protocol Support
- Complete RGB lighting protocol (25+ effects)
- Per-key RGB customization
- Key remapping and disable functionality
- Brightness and speed control
- Modifier key combinations

## Requirements
- Python 3.x
- pyusb (pip install pyusb)
- USB access permissions
- Yenkee 3700 Rogue keyboard

## Technical Details
- Uses USB HID SET_REPORT commands
- Maintains Fn key functionality
- Proper checksum calculation
- 64-byte packet structure
- Interface 1 communication

## Documentation

For complete protocol documentation, see the accompanying markdown files detailing:
- RGB lighting packet structure
- Key remapping protocol
- Scan code references
- Modifier key codes
- Example configurations

## Legal

This software was created through clean-room reverse engineering for interoperability purposes. All trademarks belong to their respective owners.
