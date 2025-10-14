# Yenkee 3700 Rogue Keyboard Protocol Documentation

## Reverse Engineering Project

This comprehensive documentation is the result of meticulous reverse engineering of the Yenkee 3700 Rogue (OEM ROGYUAN) keyboard protocol. Unlike many manufacturers who provide open APIs or cross-platform support, the vendor only offers proprietary Windows software, effectively locking out Linux, macOS, and other operating system users from customizing their RGB lighting experience.

**Our mission:** To liberate this excellent mechanical keyboard from its Windows-only shackles and empower the open-source community with complete control over its RGB lighting capabilities.

### Methodology

The protocol was reverse engineered using:
- **USBPcap** - For capturing raw USB traffic between the keyboard and official Windows software
- **Wireshark** - For detailed analysis of captured USB packets and protocol patterns
- **Systematic testing** - Methodical testing of each parameter to understand its function
- **Community collaboration** - Sharing findings and validating results across multiple keyboard units

### Documentation Structure

This documentation is divided into two main sections:

1. **Lighting Effects Protocol** - Control global effects, colors, brightness, and animation speeds
2. **Per-Key RGB Control** - Individual key color programming (see separate documentation)

### What We've Uncovered

Through careful analysis, we've successfully decoded:
- Complete packet structure for all lighting effects
- 25 different lighting modes with submode variations
- Custom RGB color implementation
- Speed and brightness control parameters
- Checksum calculation algorithm
- Proper packet sequencing and timing

### Why This Matters

This documentation enables:
- **Cross-platform support** - Linux, macOS, BSD, etc.
- **Custom software** - Create your own lighting controllers
- **Scripting integration** - Programmatic control for workflows
- **Open source projects** - Community-driven improvements
- **Long-term compatibility** - No reliance on vendor software updates

### ⚠️ Legal Notice

This documentation was created through clean-room reverse engineering for interoperability purposes. All trademarks remain property of their respective owners. This project aims to enhance user experience, not circumvent legitimate copyright protections.

*Join us in celebrating the spirit of open hardware and software freedom! Feel free to modify or for :-)*

*Continue reading to explore the complete lighting effects protocol...*

---

# Yenkee 3700 Rogue Keyboard - Communication protocols

## Lighting Effects Protocol

## Overview

This document describes the USB HID protocol for controlling RGB lighting effects, colors, brightness, and animation speed on the Yenkee 3700 Rogue keyboard.

### Packet Structure

#### Basic Format

```
07 [MODE] [SPEED] [BRIGHTNESS] [FLAGS] [RED] [GREEN] [BLUE] [CHECKSUM] [00...00]
```

#### Byte-by-Byte Breakdown

| Byte | Value | Description |
|------|-------|-------------|
| 0 | `0x07` | **COMMAND**: Always `0x07` for RGB control |
| 1 | `0x00-0x18` | **MODE**: Lighting effect type (see Mode table below) |
| 2 | `0x00-0xFF` | **SPEED**: Animation speed (meaningful range: `0x01-0x0B`) |
| 3 | `0x00-0x04` | **BRIGHTNESS**: `0x00` = Off, `0x01-0x04` = Brightness levels |
| 4 | `0x00-0x38` | **FLAGS**: Color preset or submode + custom color flag |
| 5 | `0x00-0xFF` | **RED**: Red component (only when FLAGS = `0x08`) |
| 6 | `0x00-0xFF` | **GREEN**: Green component (only when FLAGS = `0x08`) |
| 7 | `0x00-0xFF` | **BLUE**: Blue component (only when FLAGS = `0x08`) |
| 8 | `0x00-0xFF` | **CHECKSUM**: `0x100 - (sum(bytes 0-7) + 1) & 0xFF` |
| 9-63 | `0x00` | **PADDING**: Zero bytes to fill 64-byte packet |

### Mode Reference Table

| ID | Hex | Mode Name | Description | Submodes Available |
|----|-----|-----------|-------------|-------------------|
| 1 | `0x00` | Backlight OFF | Turns off all lighting | No |
| 2 | `0x01` | Static color | Solid color across all keys | No |
| 3 | `0x02` | Breathing | Pulsing fade in/out effect | No |
| 4 | `0x03` | Neon | Neon-like glow effect | No |
| 5 | `0x04` | Wave | Moving wave pattern | Yes (direction) |
| 6 | `0x05` | Waterdrop | Ripple effect on keypress | No |
| 7 | `0x06` | Rain | Falling raindrop effect | No |
| 8 | `0x07` | Snake | Snake-like moving pattern | Yes (linear/center) |
| 9 | `0x08` | Fade-out | Keys fade after press | No |
| 10 | `0x09` | Spiral | From center to sides | No |
| 11 | `0x0a` | Sinusoid | Sine wave pattern | No |
| 12 | `0x0b` | Kaleidoscope | Symmetrical pattern | Yes (from/to center) |
| 13 | `0x0c` | Linear wave | Linear wave motion | No |
| 14 | `0x0d` | User mod | WSAD + Arrows highlighted | No |
| 15 | `0x0e` | Laser | Laser beam on keypress | No |
| 16 | `0x0f` | Round wave | Circular wave pattern | Yes (direction) |
| 17 | `0x10` | Shining | Bright shining effect | No |
| 18 | `0x11` | Rain | Alternative rain effect | No |
| 19 | `0x12` | Horizontal wave | Random row wave | No |
| 20 | `0x13` | Static fade-in | Fade in on keypress | No |
| 21 | `0x14` | EDM sound reaction | Music visualization (EDM) | Yes |
| 22 | `0x15` | Unknown | "Screen1" mode in original SW | No |
| 23 | `0x16` | Standard sound reaction | Music visualization (Standard) | No |
| 24 | `0x17` | Surf/breakers | Horizontal wave breakers | No |
| 25 | `0x18` | Skew stripes | Diagonal stripe pattern | No |

### Speed Values

| Value | Effect | Notes |
|-------|--------|-------|
| `0x00` | No effect | May not work |
| `0x01` | Speed 1 | Slow |
| `0x02` | Speed 2 | Medium |
| `0x03` | Slow | Very slow |
| `0x04` | Very slow | Extremely slow |
| `0x05` | Stopped? | May pause animation |
| `0x06` | Speed 1 | Fast |
| `0x07` | Speed 2 | Faster |
| `0x08` | Speed 3 | Fast |
| `0x09` | Speed 4 | Very fast |
| `0x0a` | Speed 5 | Extremely fast |
| `0x0b` | Speed 6 | Maximum speed |
| `0x0c` | Same as `0x00` | No effect |
| `0x0d` | Similar to `0x01` | Slightly faster |

**Note:** Values above `0x0B` may work but ranges appear to repeat in blocks.

### Flags Reference

#### Basic Color Presets
| Value | Color | Example |
|-------|-------|---------|
| `0x00` | Preset Red | `07 01 00 04 00 00 00 00` |
| `0x01` | Preset Green | `07 01 00 04 01 00 00 00` |
| `0x02` | Preset Blue | `07 01 00 04 02 00 00 00` |
| `0x03` | Preset Orange | `07 01 00 04 03 00 00 00` |
| `0x04` | Preset Pink | `07 01 00 04 04 00 00 00` |
| `0x05` | Preset Yellow | `07 01 00 04 05 00 00 00` |
| `0x06` | Preset White | `07 01 00 04 06 00 00 00` |
| `0x07` | Preset Rainbow | `07 01 00 04 07 00 00 00` |
| `0x08` | Custom RGB | `07 01 00 04 08 RR GG BB` |

#### Submode Encoding
For modes with submodes (direction, pattern variation), modify the flags byte:
- `0x00-0x08`: Default submode
- `0x10-0x18`: Submode 1 (e.g., left direction)
- `0x20-0x28`: Submode 2 (e.g., down direction)  
- `0x30-0x38`: Submode 3 (e.g., up direction)

### Examples

| Description | Packet |
|-------------|--------|
| Static Custom Color (Red) | `07 01 04 04 08 ff 00 00` |
| Wave Effect with Rainbow (Right Direction) | `07 04 02 04 07 00 00 00` |
| Wave Effect with Custom Color (Left Direction) | `07 04 02 04 17 00 ff 00` |
| Wave Effect with Custom Color (Up Direction) | `07 04 02 04 38 00 ff 00` |
| Snake Effect with Custom Color | `07 07 04 04 08 ff ff 00` |
| Kaleidoscope with Rainbow | `07 0b 02 04 07 ff 45 6e` |
| Round Wave with Custom Color (Clockwise) | `07 0f 02 04 17 ff 45 6e` |

### Checksum Calculation

The checksum is calculated as:
```python
checksum = bytes([(0x100 - ((sum(main_data) + 1) & 0xFF)) & 0xFF])
```
#### Example for `07 01 04 04 08 ff 00 00`:
```
sum = 0x07 + 0x01 + 0x04 + 0x04 + 0x08 + 0xff + 0x00 + 0x00 = 279 (0x117)
sum & 0xFF = 0x17
(0x17 + 1) = 0x18
0x100 - 0x18 = 0xE8
checksum = 0xE8
```

### Sound Reaction Mode Note
When using sound reaction modes (0x14 or 0x16), the original software sends an additional sequence:
```
0d 00 00 00 00 00 00 f2 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
```
This appears to be a SET_REPORT request for audio input configuration and requires further investigation. Not yet tested.

### Implementation Notes
- Always send complete 64-byte packets
- Use custom RGB color only when FLAGS = 0x08 (if FLAGS is not 0x08, or 0x[0-3]8 for submode, you can specify RGB values but they will be ignored)
- Submode values are mode-specific and control direction/pattern variations
- Brightness 0x00 turns off lighting regardless of other settings
- Speed values are relative and effect varies by mode

----


## User-mode Backlight Protocol - setting custom color for each key

### Overview

The Yenkee 3700 Rogue keyboard uses a proprietary USB HID protocol for RGB lighting control of each key. The protocol is optimized for 64-byte HID packets and employs advanced RGB data packing with overflow between packets.

### Protocol Structure

#### Basic Format
- **Packets per complete setup:** 7
- **Each packet size:** 64 bytes
- **Packet header:** 8 bytes
- **RGB data:** 56 bytes (with overflow)

#### Packet Headers
- Packet 0: 0c00800100000072
- Packet 1: 0c00800101000071
- Packet 2: 0c00800102000070
- Packet 3: 0c0080010300006f
- Packet 4: 0c0080010400006e
- Packet 5: 0c0080010500006d
- Packet 6: 0c0080010600006c


### Key Mapping

#### Complete Position List (0-147)

| Position | Key | Notes |
|----------|-----|-------|
| 0 | ESC | Row 1, Column 0 |
| 1 | Grave (`, ~) | Row 2, Column 0 |
| 2 | Tab | Row 3, Column 0 |
| 3 | Caps Lock | Row 4, Column 0 |
| 4 | L-Shift | Row 5, Column 0 |
| 5 | L-Ctrl | Row 6, Column 0 |
| 6 | NOT_APPLICABLE | Reserved |
| 7 | 1 | Row 2, Column 1 |
| 8 | Q | Row 3, Column 1 |
| 9 | A | Row 4, Column 1 |
| 10 | NOT_APPLICABLE | Reserved |
| 11 | NOT_APPLICABLE | Reserved |
| 12 | F1 | Row 1, Column 1 |
| 13 | 2 | Row 2, Column 2 |
| 14 | W | Row 3, Column 2 |
| 15 | S | Row 4, Column 2 |
| 16 | Z | Row 5, Column 2 |
| 17 | L-Meta (Win) | Row 6, Column 2 |
| 18 | F2 | Row 1, Column 2 |
| 19 | 3 | Row 2, Column 3 |
| 20 | E | Row 3, Column 3 |
| 21 | D | Row 4, Column 3 |
| 22 | X | Row 5, Column 3 |
| 23 | L-Alt | Row 6, Column 3 |
| 24 | F3 | Row 1, Column 3 |
| 25 | 4 | Row 2, Column 4 |
| 26 | R | Row 3, Column 4 |
| 27 | F | Row 4, Column 4 |
| 28 | C | Row 5, Column 4 |
| 29 | NOT_APPLICABLE | Reserved |
| 30 | F4 | Row 1, Column 4 |
| 31 | 5 | Row 2, Column 5 |
| 32 | T | Row 3, Column 5 |
| 33 | G | Row 4, Column 5 |
| 34 | V | Row 5, Column 5 |
| 35 | NOT_APPLICABLE | Reserved |
| 36 | F5 | Row 1, Column 5 |
| 37 | 6 | Row 2, Column 6 |
| 38 | Y | Row 3, Column 6 |
| 39 | H | Row 4, Column 6 |
| 40 | B | Row 5, Column 6 |
| 41 | Space | Row 6, Column 6 |
| 42 | F6 | Row 1, Column 6 |
| 43 | 7 | Row 2, Column 7 |
| 44 | U | Row 3, Column 7 |
| 45 | J | Row 4, Column 7 |
| 46 | N | Row 5, Column 7 |
| 47 | R-Alt | Row 6, Column 7 |
| 48 | F7 | Row 1, Column 7 |
| 49 | 8 | Row 2, Column 8 |
| 50 | I | Row 3, Column 8 |
| 51 | K | Row 4, Column 8 |
| 52 | M | Row 5, Column 8 |
| 53 | Fn | Row 6, Column 8 |
| 54 | F8 | Row 1, Column 8 |
| 55 | 9 | Row 2, Column 9 |
| 56 | O | Row 3, Column 9 |
| 57 | L | Row 4, Column 9 |
| 58 | , | Row 5, Column 9 |
| 59 | R-Ctrl | Row 6, Column 9 |
| 60 | F9 | Row 1, Column 9 |
| 61 | 0 | Row 2, Column 10 |
| 62 | P | Row 3, Column 10 |
| 63 | ; | Row 4, Column 10 |
| 64 | . | Row 5, Column 10 |
| 65 | Left | Row 6, Column 10 |
| 66 | F10 | Row 1, Column 10 |
| 67 | - | Row 2, Column 11 |
| 68 | [ | Row 3, Column 11 |
| 69 | ' | Row 4, Column 11 |
| 70 | / | Row 5, Column 11 |
| 71 | Down | Row 6, Column 11 |
| 72 | F11 | Row 1, Column 11 |
| 73 | = | Row 2, Column 12 |
| 74 | ] | Row 3, Column 12 |
| 75 | NOT_APPLICABLE | Reserved |
| 76 | R-Shift | Row 5, Column 12 |
| 77 | Right | Row 6, Column 12 |
| 78 | F12 | Row 1, Column 12 |
| 79 | Backspace | Row 2, Column 13 |
| 80 | \ | Row 3, Column 13 |
| 81 | Enter | Row 4, Column 13 |
| 82 | Up | Row 5, Column 13 |
| 83 | Ins | Row 6, Column 13 |
| 84 | PrtSc | Row 1, Column 13 |
| 85 | Home | Row 2, Column 14 |
| 86 | End | Row 3, Column 14 |
| 87 | PgUp | Row 4, Column 14 |
| 88 | PgDown | Row 5, Column 14 |
| 89 | Del | Row 6, Column 14 |
| 90-147 | NOT_APPLICABLE | Reserved |

### RGB Data Format

#### RGB Value Structure
- **3 bytes per key** in order `RR GG BB`
- **Range:** 0x00-0xFF for each component
- **Examples:** Red = `FF0000`, Green = `00FF00`, Blue = `0000FF`

#### Data Packing Algorithm

The protocol uses dynamic RGB value overflow between packets:

- Packet 0: [Header] [RGB0] [RGB1] ... [RGB17] [First 2 bytes of RGB18]
- Packet 1: [Header] [Remaining 1 byte of RGB18] [RGB19] ... [RGB35] [First 1 byte of RGB36]
- Packet 2: [Header] [Remaining 2 bytes of RGB36] [RGB37] ... [RGB54]
- ... and so on.

**Calculation for each packet:**
- 8 bytes header
- 17-18 complete RGB values (51-54 bytes)
- 0-2 bytes overflow from previous/next value
- **Always exactly 64 bytes total**

### Implementation Example

#### Generating Packets for Single Red Key

**Position 0 (ESC) red; Position 18 (F2) blue - overflowing into next Packet; others black**

*examples in brackets - see overflowing of last position from Packet0 into Packet1*
```
Packet 0: 0c00800100000072 | [ff0000] 000000 000000 000000 000000 000000 000000 000000 000000 000200 000000 000000 000000 000000 000000 000000 000000 000000 [0000
Packet 1: 0c00800101000071 | ff] 000000 000000 000000 000000 000000 000000 000000 000000 000000 020000 000000 000000 000000 000000 000000 000000 000000 000000 00
Packet 2: 0c00800102000070 | 0000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000
Packet 3: 0c00800102000070 | 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 0000
Packet 4: 0c0080010300006f | 00 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 00
Packet 5: 0c0080010400006e | 0000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000
Packet 6: 0c0080010500006d | 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 0000
Packet 7: 0c0080010600006c | 00 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 00
```

### Technical Details

#### Compatibility

- Protocol supports up to 148 key positions
- For 84-key 75% keyboard, first ~90 positions are used (including Reserved)
- Remaining positions reserved for (probably) full-size keyboards

#### Sequence Numbers

The sequence number in the header decreases with each packet (72, 71, 70, ..., 6c), likely as a security feature or integrity check.

#### Performance Optimization

- Packing into 64-byte packets maximizes HID protocol usage
- Overflow minimizes number of required packets
- One sequence of 7 packets sets entire keyboard

#### Security Warning

⚠️ Important:

- Always send complete sequence of 7 packets
- Maintain correct packet order
- Respect overflow between packets
- Test with hardware reset capability available
