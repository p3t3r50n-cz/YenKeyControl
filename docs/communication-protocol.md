# Yenkee 3700 Rogue Keyboard - Communication protocols

This documentation is divided into main sections:

1. [**Backlight Effects Protocol**](#backlight-effects-protocol) - Control global effects, colors, brightness, and animation speeds
2. [**Per-Key RGB Control**](#key-color-protocol) - Individual key color programming (see separate documentation)
3. [**Per-Key remapping**](#key-remapping-protocol) - Describes the options for reassigning individual keys to different functions (e.g., sending different scancodes)
4. [**Read Configuration from keyboard**](#read-configuration-protocol)) - Describes the options for reassigning individual keys to different functions (e.g., sending different scancodes)

----

## Backlight Effects Protocol

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

| ID | Hex | Mode Name | Description | Submode 0<br>(flag: `0x`) | Submode 1<br>(flag: `1x`) | Submode 2<br>(flag: `2x`) | Submode 3<br>(flag: `3x`) |
|----|-----|-----------|-------------|-----------|-----------|-----------|-----------|
| 1 | `0x00` | Backlight OFF | Turns off all lighting | | | | |
| 2 | `0x01` | Static color | Solid color across all keys | | | | |
| 3 | `0x02` | Breathing | Pulsing fade in/out effect | | | | | |
| 4 | `0x03` | Neon | Neon-like glow effect | | | | | |
| 5 | `0x04` | Wave | Moving wave pattern | right | left | down | up |
| 6 | `0x05` | Waterdrop | Ripple effect on keypress |  | | | |
| 7 | `0x06` | Rain | Falling raindrop effect |  | | | |
| 8 | `0x07` | Snake | Snake-like moving pattern | linear | to center | | |
| 9 | `0x08` | Fade-out | Keys fade after press |  | | | |
| 10 | `0x09` | Spiral | From center to sides |  | | | |
| 11 | `0x0a` | Sinusoid | Sine wave pattern |  | | | |
| 12 | `0x0b` | Kaleidoscope | Symmetrical pattern | from center | to center | | |
| 13 | `0x0c` | Linear wave | Linear wave motion |  | | | |
| 14 | `0x0d` | User mod | WSAD + Arrows highlighted |  | | | |
| 15 | `0x0e` | Laser | Laser beam on keypress |  | | | |
| 16 | `0x0f` | Round wave | Circular wave pattern | counterclockwise | clockwise | | |
| 17 | `0x10` | Shining | Bright shining effect |  | | | |
| 18 | `0x11` | Rain | Alternative rain effect |  | | | |
| 19 | `0x12` | Horizontal wave | Random row wave |  | | | |
| 20 | `0x13` | Static fade-in | Fade in on keypress |  | | | |
| 21 | `0x14` | EDM sound reaction | Music visualization (EDM) | upright | separate | crossing | |
| 22 | `0x15` | Unknown | "Screen1" mode in original SW |  | | | |
| 23 | `0x16` | Standard sound reaction | Music visualization (Standard) |  | | | |
| 24 | `0x17` | Surf/breakers | Horizontal wave breakers |  | | | |
| 25 | `0x18` | Skew stripes | Diagonal stripe pattern |  | | | |

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


## Key Color Protocol

Setting custom color for each key.

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

| Packet | Position | Key | Keyname | Notes |
|--------|----------|-----|---------|-------|
| 0 | 0 | ESC | KEY_ESC | Row 1, Column 0 |
| 0 | 1 | Grave (`, ~) | KEY_GRAVE | Row 2, Column 0 |
| 0 | 2 | Tab | KEY_TAB | Row 3, Column 0 |
| 0 | 3 | Caps Lock | KEY_CAPSLOCK | Row 4, Column 0 |
| 0 | 4 | L-Shift | KEY_LEFTSHIFT | Row 5, Column 0 |
| 0 | 5 | L-Ctrl | KEY_LEFTCTRL | Row 6, Column 0 |
| 0 | 6 | NOT_APPLICABLE |  | Reserved |
| 0 | 7 | 1 | KEY_1 | Row 2, Column 1 |
| 0 | 8 | Q | KEY_Q | Row 3, Column 1 |
| 0 | 9 | A | KEY_A | Row 4, Column 1 |
| 0 | 10 | NOT_APPLICABLE |  | Reserved |
| 0 | 11 | NOT_APPLICABLE |  | Reserved |
| 0 | 12 | F1 | KEY_F1 | Row 1, Column 1 |
| 0 | 13 | 2 | KEY_2 | Row 2, Column 2 |
| 0 | 14 | W | KEY_W | Row 3, Column 2 |
| 0 | 15 | S | KEY_S | Row 4, Column 2 |
| 0 | 16 | Z | KEY_Z | Row 5, Column 2 |
| 0 | 17 | L-Meta (Win) | KEY_LEFTMETA | Row 6, Column 2 |
| 0 | 18 | F2 | KEY_F2 | Row 1, Column 2 |
| 0-1 | 19 | 3 | KEY_3 | Row 2, Column 3 |
| 1 | 20 | E | KEY_E | Row 3, Column 3 |
| 1 | 21 | D | KEY_D | Row 4, Column 3 |
| 1 | 22 | X | KEY_X | Row 5, Column 3 |
| 1 | 23 | L-Alt | KEY_LEFTALT | Row 6, Column 3 |
| 1 | 24 | F3 | KEY_F3 | Row 1, Column 3 |
| 1 | 25 | 4 | KEY_4 | Row 2, Column 4 |
| 1 | 26 | R | KEY_R | Row 3, Column 4 |
| 1 | 27 | F | KEY_F | Row 4, Column 4 |
| 1 | 28 | C | KEY_C | Row 5, Column 4 |
| 1 | 29 | NOT_APPLICABLE |  | Reserved |
| 1 | 30 | F4 | KEY_F4 | Row 1, Column 4 |
| 1 | 31 | 5 | KEY_5 | Row 2, Column 5 |
| 1 | 32 | T | KEY_T | Row 3, Column 5 |
| 1 | 33 | G | KEY_G | Row 4, Column 5 |
| 1 | 34 | V | KEY_V | Row 5, Column 5 |
| 1 | 35 | NOT_APPLICABLE |  | Reserved |
| 1 | 36 | F5 | KEY_F5 | Row 1, Column 5 |
| 1 | 37 | 6 | KEY_6 | Row 2, Column 6 |
| 1-2 | 38 | Y | KEY_Y | Row 3, Column 6 |
| 2 | 39 | H | KEY_H | Row 4, Column 6 |
| 2 | 40 | B | KEY_B | Row 5, Column 6 |
| 2 | 41 | Space | KEY_SPACE | Row 6, Column 6 |
| 2 | 42 | F6 | KEY_F6 | Row 1, Column 6 |
| 2 | 43 | 7 | KEY_7 | Row 2, Column 7 |
| 2 | 44 | U | KEY_U | Row 3, Column 7 |
| 2 | 45 | J | KEY_J | Row 4, Column 7 |
| 2 | 46 | N | KEY_N | Row 5, Column 7 |
| 2 | 47 | R-Alt | KEY_RIGHTALT | Row 6, Column 7 |
| 2 | 48 | F7 | KEY_F7 | Row 1, Column 7 |
| 2 | 49 | 8 | KEY_8 | Row 2, Column 8 |
| 2 | 50 | I | KEY_I | Row 3, Column 8 |
| 2 | 51 | K | KEY_K | Row 4, Column 8 |
| 2 | 52 | M | KEY_M | Row 5, Column 8 |
| 2 | 53 | Fn | KEY_FN | Row 6, Column 8 |
| 2 | 54 | F8 | KEY_F8 | Row 1, Column 8 |
| 2 | 55 | 9 | KEY_9 | Row 2, Column 9 |
| 2 | 56 | O | KEY_O | Row 3, Column 9 |
| 3 | 3 | 57 | L | KEY_L | Row 4, Column 9 |
| 3 | 58 | , | KEY_COMMA | Row 5, Column 9 |
| 3 | 59 | R-Ctrl | KEY_RIGHTCTRL | Row 6, Column 9 |
| 3 | 60 | F9 | KEY_F9 | Row 1, Column 9 |
| 3 | 61 | 0 | KEY_0 | Row 2, Column 10 |
| 3 | 62 | P | KEY_P | Row 3, Column 10 |
| 3 | 63 | ; | KEY_SEMICOLON | Row 4, Column 10 |
| 3 | 64 | . | KEY_DOT | Row 5, Column 10 |
| 3 | 65 | Left | KEY_LEFT | Row 6, Column 10 |
| 3 | 66 | F10 | KEY_F10 | Row 1, Column 10 |
| 3 | 67 | - | KEY_MINUS | Row 2, Column 11 |
| 3 | 68 | [ | KEY_LEFTBRACE | Row 3, Column 11 |
| 3 | 69 | ' | KEY_APOSTROPHE | Row 4, Column 11 |
| 3 | 70 | / | KEY_SLASH | Row 5, Column 11 |
| 3 | 71 | Down | KEY_DOWN | Row 6, Column 11 |
| 3 | 72 | F11 | KEY_F11 | Row 1, Column 11 |
| 3 | 73 | = | KEY_EQUAL | Row 2, Column 12 |
| 3 | 74 | ] | KEY_RIGHTBRACE | Row 3, Column 12 |
| 3-4 | 75 | NOT_APPLICABLE |  | Reserved |
| 4 | 76 | R-Shift | KEY_RIGHTSHIFT | Row 5, Column 12 |
| 4 | 77 | Right | KEY_RIGHT | Row 6, Column 12 |
| 4 | 78 | F12 | KEY_F12 | Row 1, Column 12 |
| 4 | 79 | Backspace | KEY_BACKSPACE | Row 2, Column 13 |
| 4 | 80 | \ | KEY_BACKSLASH | Row 3, Column 13 |
| 4 | 81 | Enter | KEY_ENTER | Row 4, Column 13 |
| 4 | 82 | Up | KEY_UP | Row 5, Column 13 |
| 4 | 83 | Ins | KEY_INSERT | Row 6, Column 13 |
| 4 | 84 | PrtSc | KEY_PRINTSCREEN | Row 1, Column 13 |
| 4 | 85 | Home | KEY_HOME | Row 2, Column 14 |
| 4 | 86 | End | KEY_END | Row 3, Column 14 |
| 4 | 87 | PgUp | KEY_PAGEUP | Row 4, Column 14 |
| 4 | 88 | PgDown | KEY_PAGE_DOWN | Row 5, Column 14 |
| 4 | 89 | Del | KEY_DELETE | Row 6, Column 14 |
| 4-7 | 90-147 | NOT_APPLICABLE |  | Reserved |

![Yenkee YKB3700 Rogue Keyboard](/images/yenkee-ykb3700-rgb-keymap-reference.png)
*Reference layout of the Yenkee YKB3700 Rogue keyboard showing key indices as used in the device’s HID RGB configuration packets.*

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

---

## Key Remapping Protocol

### Overview

This document describes the USB HID protocol for key remapping, macro assignment (not yet documented), and key disable functionality on the Yenkee 3700 Rogue keyboard. The protocol allows complete customization of the keyboard layout by reassigning scan codes and modifiers to physical key positions.

### Packet Structure

#### Basic Format
- **Total packets per configuration:** 9
- **Each packet size:** 64 bytes
- **Packet header:** `0900f801[SEQ]000000[CHECKSUM]`
- **Key data:** 14 key positions × 4 bytes each = 56 bytes

#### Packet Headers
- Packet 0: 0900f801000000fd
- Packet 1: 0900f801010000fc
- Packet 2: 0900f801020000fb
- Packet 3: 0900f801030000fa
- Packet 4: 0900f801040000f9
- Packet 5: 0900f801050000f8
- Packet 6: 0900f801060000f7
- Packet 7: 0900f801070000f6
- Packet 8: 0900f801080000f5


### Key Position Structure

Each key position uses 4 bytes in the following format:

**Common Keys (scancodes):**
```
[00] [00] [SCANCODE] [00]        # Standard scancode without modifiers
[00] [MOD1] [SCANCODE] [00]      # Standard scanocode with one modifier
[00] [MOD2] [MOD1] [SCANCODE]    # Standard scancode with two modifiers
```

**Special Function Keys:**
```
[SPEC_0] [SPEC_1] [SPEC_2] [SPEC_3]
```

### Modifier Scan Codes

| Modifier | Scan Code | Description |
|----------|-----------|-------------|
| L-Ctrl | `0xe0` | Left Control |
| L-Shift | `0xe1` | Left Shift |
| L-Alt | `0xe2` | Left Alt |
| L-Meta | `0xe3` | Left Windows/Command |
| R-Ctrl | `0xe4` | Right Control |
| R-Shift | `0xe5` | Right Shift |
| R-Alt | `0xe6` | Right Alt |
| Fn | `0x0a010000` | Function key (special function code) |

### Important Rules

1. **Modifier Order**: Modifiers must be placed immediately before the main scan code.
2. **Multiple Modifiers**: Up to 2 modifiers can be combined (order doesn't matter).
3. **Key Disable**: Use `00000000` to disable a physical key.
4. **Fn Key**: Special value `0a010000`. The FN key can be turned off or moved to another key, but it cannot be used as a modifier like Fn+Key.
5. **Reserved Positions**: Marked as DISABLED in default mapping.

### Default Key Mapping

#### Packet 0 - Positions 0-13

| Pos | Physical Key | Default Mapping | Mod2 | Mod1 | Scan Code | Reserved byte | Note |
|-----|--------------|-----------------|------|------|-----------|---------------|------|
| 0 | ESC | KEY_ESC | 0x00 | 0x00 | 0x29 | 0x00 | |
| 1 | Grave | KEY_GRAVE | 0x00 | 0x00 | 0x35 | 0x00 | |
| 2 | TAB | KEY_TAB | 0x00 | 0x00 | 0x2b | 0x00 | |
| 3 | CAPS | KEY_CAPSLOCK | 0x00 | 0x00 | 0x39 | 0x00 | |
| 4 | L-SHIFT | KEY_LEFTSHIFT | 0x00 | 0x00 | 0xe1 | 0x00 | |
| 5 | L-CTRL | KEY_LEFTCTRL | 0x00 | 0x00 | 0xe0 | 0x00 | |
| 6 |  | DISABLED | 0x00 | 0x00 | 0x00 | 0x00 | |
| 7 | 1 | KEY_1 | 0x00 | 0x00 | 0x1e | 0x00 | |
| 8 | Q | KEY_Q | 0x00 | 0x00 | 0x14 | 0x00 | |
| 9 | A | KEY_A | 0x00 | 0x00 | 0x04 | 0x00 | |
| 10 | < | KEY_102ND | 0x00 | 0x00 | 0x64 | 0x00 | this key is not physically present on the keyboard |
| 11 |  | DISABLED | 0x00 | 0x00 | 0x00 | 0x00 | Disabled position (protocol reserve for other keyboards or layouts) |
| 12 | F1 | KEY_F1 | 0x00 | 0x00 | 0x3a | 0x00 | |
| 13 | 2 | KEY_2 | 0x00 | 0x00 | 0x1f | 0x00 | |

#### Packet 1 - Positions 14-27

| Pos | Physical Key | Default Mapping | Mod2 | Mod1 | Scan Code | Reserved byte |
|-----|--------------|-----------------|------|------|-----------|---------------|
| 14 | W | KEY_W | 0x00 | 0x00 | 0x1a | 0x00 |
| 15 | S | KEY_S | 0x00 | 0x00 | 0x16 | 0x00 |
| 16 | Z | KEY_Z | 0x00 | 0x00 | 0x1d | 0x00 |
| 17 | L-META | KEY_LEFTMETA | 0x00 | 0x00 | 0xe3 | 0x00 |
| 18 | F2 | KEY_F2 | 0x00 | 0x00 | 0x3b | 0x00 |
| 19 | 3 | KEY_3 | 0x00 | 0x00 | 0x20 | 0x00 |
| 20 | E | KEY_E | 0x00 | 0x00 | 0x08 | 0x00 |
| 21 | D | KEY_D | 0x00 | 0x00 | 0x07 | 0x00 |
| 22 | X | KEY_X | 0x00 | 0x00 | 0x1b | 0x00 |
| 23 | L-ALT | KEY_LEFTALT | 0x00 | 0x00 | 0xe2 | 0x00 |
| 24 | F3 | KEY_F3 | 0x00 | 0x00 | 0x3c | 0x00 |
| 25 | 4 | KEY_4 | 0x00 | 0x00 | 0x21 | 0x00 |
| 26 | R | KEY_R | 0x00 | 0x00 | 0x15 | 0x00 |
| 27 | F | KEY_F | 0x00 | 0x00 | 0x09 | 0x00 |

#### Packet 2 - Positions 28-41
| Pos | Physical Key | Default Mapping | Mod2 | Mod1 | Scan Code | Reserved byte |
|-----|--------------|-----------------|------|------|-----------|---------------|
| 28 | C | KEY_C | 0x00 | 0x00 | 0x06 | 0x00 |
| 29 |  | DISABLED | 0x00 | 0x00 | 0x00 | 0x00 |
| 30 | F4 | KEY_F4 | 0x00 | 0x00 | 0x3d | 0x00 |
| 31 | 5 | KEY_5 | 0x00 | 0x00 | 0x22 | 0x00 |
| 32 | T | KEY_T | 0x00 | 0x00 | 0x17 | 0x00 |
| 33 | G | KEY_G | 0x00 | 0x00 | 0x0a | 0x00 |
| 34 | V | KEY_V | 0x00 | 0x00 | 0x19 | 0x00 |
| 35 |  | DISABLED | 0x00 | 0x00 | 0x00 | 0x00 |
| 36 | F5 | KEY_F5 | 0x00 | 0x00 | 0x3e | 0x00 |
| 37 | 6 | KEY_6 | 0x00 | 0x00 | 0x23 | 0x00 |
| 38 | Y | KEY_Y | 0x00 | 0x00 | 0x1c | 0x00 |
| 39 | H | KEY_H | 0x00 | 0x00 | 0x0b | 0x00 |
| 40 | B | KEY_B | 0x00 | 0x00 | 0x05 | 0x00 |
| 41 | SPACE | KEY_SPACE | 0x00 | 0x00 | 0x2c | 0x00 |

#### Packet 3 - Positions 42-55

| Pos | Physical Key | Default Mapping | Mod2 | Mod1 | Scan Code | Reserved byte |
|-----|--------------|-----------------|------|------|-----------|---------------|
| 42 | F6 | KEY_F6 | 0x00 | 0x00 | 0x3f | 0x00 |
| 43 | 7 | KEY_7 | 0x00 | 0x00 | 0x24 | 0x00 |
| 44 | U | KEY_U | 0x00 | 0x00 | 0x18 | 0x00 |
| 45 | J | KEY_J | 0x00 | 0x00 | 0x0d | 0x00 |
| 46 | N | KEY_N | 0x00 | 0x00 | 0x11 | 0x00 |
| 47 | Right | KEY_RIGHTALT | 0x00 | 0x00 | 0x4f | 0x00 |
| 48 | F7 | KEY_F7 | 0x00 | 0x00 | 0x40 | 0x00 |
| 49 | 8 | KEY_8 | 0x00 | 0x00 | 0x25 | 0x00 |
| 50 | I | KEY_I | 0x00 | 0x00 | 0x0c | 0x00 |
| 51 | K | KEY_K | 0x00 | 0x00 | 0x0e | 0x00 |
| 52 | M | KEY_M | 0x00 | 0x00 | 0x10 | 0x00 |
| 53 | Fn | KEY_FN | 0x0a | 0x01 | 0x00 | 0x00 |
| 54 | F8 | KEY_F8 | 0x00 | 0x00 | 0x41 | 0x00 |
| 55 | 9 | KEY_9 | 0x00 | 0x00 | 0x26 | 0x00 |

#### Packet 4 - Positions 56-69

| Pos | Physical Key | Default Mapping | Mod2 | Mod1 | Scan Code | Reserved byte |
|-----|--------------|-----------------|------|------|-----------|---------------|
| 56 | O | KEY_O | 0x00 | 0x00 | 0x12 | 0x00 |
| 57 | L | KEY_L | 0x00 | 0x00 | 0x0f | 0x00 |
| 58 | , | KEY_COMMA | 0x00 | 0x00 | 0x36 | 0x00 |
| 59 | R-CTRL | KEY_RIGHTCTRL | 0x00 | 0x00 | 0xe4 | 0x00 |
| 60 | F9 | KEY_F9 | 0x00 | 0x00 | 0x42 | 0x00 |
| 61 | 0 | KEY_0 | 0x00 | 0x00 | 0x27 | 0x00 |
| 62 | P | KEY_P | 0x00 | 0x00 | 0x13 | 0x00 |
| 63 | ; | KEY_SEMICOLON | 0x00 | 0x00 | 0x33 | 0x00 |
| 64 | . | KEY_DOT | 0x00 | 0x00 | 0x37 | 0x00 |
| 65 | LEFT | KEY_LEFT | 0x00 | 0x00 | 0x50 | 0x00 |
| 66 | F10 | KEY_F10 | 0x00 | 0x00 | 0x43 | 0x00 |
| 67 | - | KEY_MINUS | 0x00 | 0x00 | 0x2d | 0x00 |
| 68 | [ | KEY_LEFTBRACE | 0x00 | 0x00 | 0x2f | 0x00 |
| 69 | ' | KEY_APOSTROPHE | 0x00 | 0x00 | 0x34 | 0x00 |

#### Packet 5 - Positions 70-83

| Pos | Physical Key | Default Mapping | Mod2 | Mod1 | Scan Code | Reserved byte |
|-----|--------------|-----------------|------|------|-----------|---------------|
| 70 | / | KEY_SLASH | 0x00 | 0x00 | 0x38 | 0x00 |
| 71 | DOWN | KEY_DOWN | 0x00 | 0x00 | 0x51 | 0x00 |
| 72 | F11 | KEY_F11 | 0x00 | 0x00 | 0x44 | 0x00 |
| 73 | = | KEY_EQUAL | 0x00 | 0x00 | 0x2e | 0x00 |
| 74 | ] | KEY_RIGHTBRACE | 0x00 | 0x00 | 0x30 | 0x00 |
| 75 | #/~ | KEY_HASHTILDE | 0x00 | 0x00 | 0x32 | 0x00 |
| 76 | R-SHIFT | KEY_RIGHTSHIFT | 0x00 | 0x00 | 0xe5 | 0x00 |
| 77 | RIGHT | KEY_RIGHT | 0x00 | 0x00 | 0x4f | 0x00 |
| 78 | F12 | KEY_F12 | 0x00 | 0x00 | 0x45 | 0x00 |
| 79 | BCKSPACE | KEY_BACKSPACE | 0x00 | 0x00 | 0x2a | 0x00 |
| 80 | \ | KEY_BACKSLASH | 0x00 | 0x00 | 0x31 | 0x00 |
| 81 | ENTER | KEY_ENTER | 0x00 | 0x00 | 0x28 | 0x00 |
| 82 | UP | KEY_UP | 0x00 | 0x00 | 0x52 | 0x00 |
| 83 | INS | KEY_INSERT | 0x00 | 0x00 | 0x49 | 0x00 |

#### Packet 6 - Positions 84-97

| Pos | Physical Key | Default Mapping | Mod2 | Mod1 | Scan Code | Reserved byte |
|-----|--------------|-----------------|------|------|-----------|---------------|
| 84 | PRTSC | KEY_PRINTSCREEN | 0x00 | 0x00 | 0x46 | 0x00 |
| 85 | HOME | KEY_HOME | 0x00 | 0x00 | 0x4a | 0x00 |
| 86 | END | KEY_END | 0x00 | 0x00 | 0x4d | 0x00 |
| 87 | PGUP | KEY_PAGEUP | 0x00 | 0x00 | 0x4b | 0x00 |
| 88 | PGDOWN | KEY_PAGE_DOWN | 0x00 | 0x00 | 0x4e | 0x00 |
| 89 | DEL | KEY_DELETE | 0x00 | 0x00 | 0x4c | 0x00 |
| 90-97 |  | DISABLED | 0x00 | 0x00 | 0x00 | 0x00 |

#### Packets 7-8 - Positions 98-125

| Pos | Physical Key | Default Mapping | Mod2 | Mod1 | Scan Code | Reserved byte |
|-----|--------------|-----------------|------|------|-----------|---------------|
| 98-125 |  | DISABLED | `0x00` | `0x00` | `0x00` | `0x00` |

### Special Function Events

The keyboard supports multimedia and special functions beyond standard key remapping. These functions use extended 4-byte codes in the key position format.

#### Media Controls (`03 00 [function] 00`)

| Function | Code | XF86 Symbol |
|----------|------|-------------|
| Play/Pause | 0300cd00 | XF86AudioPlay |
| Stop | 0300b700 | XF86AudioStop |
| Previous Track | 0300b600 | XF86AudioPrev |
| Next Track | 0300b500 | XF86AudioNext |
| Volume Down | 0300ea00 | XF86AudioLowerVolume |
| Volume Up | 0300e900 | XF86AudioRaiseVolume |
| Mute | 0300e200 | XF86AudioMute |

#### Display DPMS Controls (`03 00 [function] 00`)

| Function | Code | XF86 Symbol |
|----------|------|-------------|
| Brightness Up | 03006f00 | XF86MonBrightnessUp |
| Brightness Down | 03007000 | XF86MonBrightnessDown |

#### Application Launchers (`03 00 [function] 01`)

| Function | Code | XF86 Symbol |
|----------|------|-------------|
| Media Player | 03008301 | XF86Tools |
| Calculator | 03009201 | XF86Calculator |
| Email | 03008a01 | XF86Mail |
| My Computer | 03009401 | XF86Explorer |

#### System Functions (`03 00 [function] 02`)

| Function | Code | XF86 Symbol |
|----------|------|-------------|
| Search | 03002102 | XF86Search |
| Browser (HomePage) | 03002302 | XF86HomePage |
| Reload | 03002702 | XF86Reload |

#### Zoom Functions (`00 00 e3 [data]`)

| Function | Code | Triggering |
|----------|------|-------------|
| Zoom-in | 0000e32d | `keycode 133 (keysym 0xffeb, Super_L)` + `keycode 20 (keysym 0x2d, minus)` |
| Zoom-out | 0000e32e | `keycode 133 (keysym 0xffeb, Super_L)` + `keycode 21 (keysym 0x3d, equal)` |

#### Mouse Functions (`01 00 [function] [data]`)

| Function | Code | XF86 Symbol |
|----------|------|-------------|
| Mouse Click Left | 0100f000 | - UNKNOWN - |
| Mouse Click Right | 0100f100 | - UNKNOWN - |
| Mouse Click Center | 0100f200 | - UNKNOWN - |
| Mouse Click Left-Up | 0100f400 | - UNKNOWN - |
| Mouse Click Left-Down | 0100f300 | - UNKNOWN - |
| Mouse Scroll Up | 0100f501 | - UNKNOWN - |
| Mouse Scroll Down | 0100f5ff | - UNKNOWN - |

### Special Events - Usage Examples

Remap a key to special function in key mapping packets:
```
# Remap ESC to Volume Up
0900f801000000fd [0300e900] 0000350000002b00...
# Remap ESC to Browser
0900f801000000fd [03002302] 0000350000002b00...
```

![Yenkee YKB3700 Rogue Keyboard](/images/yenkee-ykb3700-scancodes-keymap-reference.png)
*Reference map showing physical key positions as used in the USB HID packets for key remapping on the Yenkee YKB3700 Rogue.*

### Examples

#### Remap ESC to Alt+F1

Original: `00002900` → Modified: `00e23a00`

- Mod2: `0x00` (none)
- Mod1: `0xe2` (Left Alt)
- Scan Code: `0x3a` (F1)
- Null: `0x00`

#### Disable CAPS Lock

Original: `00003900` → Modified: `00000000`

#### Remap Q to Ctrl+Shift+T

Original: `00001400` → Modified: `00e0e117`

- Null: `0x00`
- Mod2: `0xe0` (Left Control)
- Mod1: `0xe1` (Left Shift) 
- Scan Code: `0x17` (T)

#### Complete Packet Example (ESC → Alt+F1) - first packet

`0900f801000000fd00e23a000000350000002b00000039000000e1000000e0000000000000001e000000140000000400000064000000000000003a0000001f00`

## Implementation Notes

- Always send all 9 packets for a complete configuration
- Maintain the exact packet order (0-8)
- Reserved positions should remain as `00000000`
- The Fn key uses special key code
- Modifiers (more than one, maximum of two) can be combined in any order (`e0e23a` = `e2e03a` = Ctrl+Alt+F1)

## Scan Code Reference

Common scan codes used in the default mapping:
- Letters: A=`0x04`, B=`0x05`, C=`0x06`, ..., Z=`0x1d`
- Numbers: 1=`0x1e`, 2=`0x1f`, ..., 0=`0x27`
- Function Keys: F1=`0x3a`, F2=`0x3b`, ..., F12=`0x45`
- Navigation: LEFT=`0x50`, RIGHT=`0x4f`, UP=`0x52`, DOWN=`0x51`
- Special: ENTER=`0x28`, SPACE=`0x2c`, TAB=`0x2b`, ESC=`0x29`

----

## Read Configuration Protocol

### Overview

This document describes the protocol for reading current configuration settings from the Yenkee 3700 Rogue keyboard. The protocol allows querying backlight settings, per-key RGB colors, and key remapping configurations via SET_REPORT/GET_REPORT requests.

### Basic Read Protocol

### Command Structure

The read protocol uses a SET_REPORT/GET_REPORT sequence:
 - SET_REPORT: Send configuration query packet
 - GET_REPORT: Receive current settings data

### USB Control Transfer Parameters
 - bmRequestType: 0xA1 (IN/Class/Interface)
 - bRequest: 0x01 (GET_REPORT)
 - wValue: 0x0300 | report_id (Feature report + Report ID)
 - wIndex: 0x0001 (Interface)
 - wLength: 64 (data size)

### Configuration Areas

#### 1. Reading Global Backlight Settings

Query Packet
```
SET_REPORT: 87000000000000
```

Response Format (64 bytes)
```
[00] [MODE] [SPEED] [BRIGHTNESS] [FLAGS] [RED] [GREEN] [BLUE] [00...00]
```

##### Response Byte Mapping
Byte | Description | Values
-----|-------------|--------
0 | Response Type | 0x87
1 | Mode | 0x00-0x18 (see Mode Reference)
2 | Speed | 0x01-0x0B (animation speed)
3 | Brightness | 0x00=Off, 0x01-0x04=Brightness levels
4 | Flags	Submode | (high nibble) + Color Flag (low nibble)
5 | Red | Red component (when custom RGB)
6 | Green | Green component (when custom RGB)
7 | Blue | Blue component (when custom RGB)
8-63 | Padding | 0x00

##### Flags Decoding
- Submode: (flags >> 4) & 0x0F
- Color Flag: flags & 0x0F

#### 2. Reading Per-Key RGB Colors

##### Query Sequence

Send 6 SET_REPORT packets sequentially:
 - 8c000000000000
 - 8c000100000000
 - 8c000200000000
 - 8c000300000000
 - 8c000400000000
 - 8c000500000000

##### Response Format

Each GET_REPORT returns 64 bytes containing RGB data for multiple keys.

##### RGB Data Structure
 - 3 bytes per key: RR GG BB
 - 148 total positions (0-147)
 - Total data: 444 bytes (148 × 3)

##### Data Organization

The RGB data is split across 6 packets:
Packet | Key Range | Data Bytes
-------|-----------|------------
0 | 0-20 | 63 bytes RGB + next bytes split
1 | 21-42 | 66 bytes RGB
2 | 43-65 | 69 bytes RGB
3 | 66-88 | 69 bytes RGB
4 | 89-111 | 69 bytes RGB
5 | 112-147 | 108 bytes RGB

##### Key Position Mapping

Same as user-mode backlight protocol (positions 0-147).

#### 3. Reading Key Remapping Settings

##### Query Sequence
Send 8 SET_REPORT packets sequentially:
- 89000000000000
- 89000100000000
- 89000200000000
- 89000300000000
- 89000400000000
- 89000500000000
- 89000600000000
- 89000700000000

##### Response Format
Each GET_REPORT returns 64 bytes containing remap data for multiple keys.

##### Remap Data Structure
 - 4 bytes per key:
   - `[00] [00] [00] [SCANCODE]` - for single key
   - or `[00] [MOD1] [SCANCODE] [00]` - for key with one modifier
   - or `[00] [MOD2] [MOD1] [SCANCODE]` - for key woth two modifiers
   - or `[SPEC_0] [SPEC_1] [SPEC_2] [SPEC_3]` - for special function code
 - 126 total positions (0-125)
 - Total data: 504 bytes (126 × 4)

##### Data Organization
The remap data is split across 8 packets:

Packet | Key Range | Data Bytes
-------|-----------|------------
0 | 0-15 | 64 bytes (16 keys)
1	| 16-31 | 64 bytes (16 keys)
2	| 32-47 | 64 bytes (16 keys)
3	| 48-63 | 64 bytes (16 keys)
4	| 64-79 | 64 bytes (16 keys)
5	| 80-95 | 64 bytes (16 keys)
6	| 96-111 | 64 bytes (16 keys)
7	| 112-125 | 56 bytes (14 keys) + 8 padding

##### Implementation Details

- Timing Considerations
- Delay between packets: 100ms recommended
- Complete sequence time: ~1-2 seconds for all configurations
