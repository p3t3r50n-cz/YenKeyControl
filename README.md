# Yankee 3700 Rogue Keyboard - Communication protocols

## User backlight mode - setting custom color for each key

### Overview

The Yankee 3700 Rogue keyboard (OEM ROGYUAN) uses a proprietary USB HID protocol for RGB lighting control of each key. The protocol is optimized for 64-byte HID packets and employs advanced RGB data packing with overflow between packets.

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
