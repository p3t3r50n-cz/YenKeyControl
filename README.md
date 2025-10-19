# Yenkee YKB3700 Rogue Keyboard Protocol Documentation and Command-line Utilities

![Yenkee YKB3700 Rogue Keyboard](./images/YKB3700.png)

## Reverse Engineering Project

This comprehensive documentation and command-line utilites are the result of meticulous reverse engineering of the Yenkee YKB3700 Rogue (and probably others based on a similar ROYUAN chipset) keyboard protocol. Unlike many manufacturers who provide open APIs or cross-platform support, the vendor only offers proprietary Windows software, effectively locking out Linux, macOS, and other operating system users from customizing their RGB lighting experience.

**Our mission:** To liberate this excellent mechanical keyboard from its Windows-only shackles and empower the open-source community with complete control over its RGB lighting capabilities.

## Repository structure

### Documentation
- **[Communication Protocol](/docs/communication-protocol.md)**  
  Complete protocol documentation with uncovered commands, capabilities, and packet structures.

### Source Code
- **[YenKey Proto](/src/yenkey-proto.py)**  
  Simple prototyping script for functionality verification and packet debugging.  
  *Documentation: [yenkey-proto](/docs/yenkey-proto.md)*

- **[YenKey CLI](/src/yenkey-cli.py)**  
  Complete command-line utility for backlight effects, key colors, and key remapping.  
  *Documentation: [yenkey-cli](/docs/yenkey-cli.md)*

### Communication Protocol Documentation Structure

This documentation is divided into three main sections:

1. [**Lighting Effects Protocol**](/docs/communication-protocol.md#lighting-effects-protocol) - Control global effects, colors, brightness, and animation speeds
2. [**Per-Key RGB Control**](/docs/communication-protocol.md#user-mode-backlight-protocol---setting-custom-color-for-each-key) - Individual key color programming (see separate documentation)
3. [**Per-Key remapping**](/docs/communication-protocol.md#yenkee-3700-rogue-keyboard-key-remapping-protocol) - Describes the options for reassigning individual keys to different functions (e.g., sending different scancodes)

### What We've Uncovered

Through careful analysis, we've successfully decoded:
- Complete packet structure for all lighting effects
- 25 different lighting modes with submode variations
- Custom RGB color implementation for individual keys
- Key remapping implementation
- Speed and brightness control parameters
- Checksum calculation algorithm
- Proper packet sequencing and timing

### Why This Matters

This project enables:
- **Cross-platform support** - Linux, macOS, BSD, etc.
- **Custom software** - Create your own lighting controllers
- **Scripting integration** - Programmatic control for workflows
- **Open source projects** - Community-driven improvements
- **Long-term compatibility** - No reliance on vendor software updates

### Device informations

 - **USB VID:** 3151
 - **USB PID:** 4002

**Output from `lsusb`**
```
lsusb -v -d 3151:4002

Bus 002 Device 115: ID 3151:4002  FK2102T-C
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               2.00
  bDeviceClass            0
  bDeviceSubClass         0
  bDeviceProtocol         0
  bMaxPacketSize0        64
  idVendor           0x3151
  idProduct          0x4002
  bcdDevice            2.01
  iManufacturer           0
  iProduct                2 FK2102T-C
  iSerial                 0
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength       0x003b
    bNumInterfaces          2
    bConfigurationValue     1
    iConfiguration          0
    bmAttributes         0xa0
      (Bus Powered)
      Remote Wakeup
    MaxPower              100mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      1 Boot Interface Subclass
      bInterfaceProtocol      1 Keyboard
      iInterface              0
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength      89
         Report Descriptors:
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81  EP 1 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0008  1x 8 bytes
        bInterval               1
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        1
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      0
      bInterfaceProtocol      0
      iInterface              0
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength     158
         Report Descriptors:
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x82  EP 2 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0010  1x 16 bytes
        bInterval               1
Device Status:     0x0000
  (Bus Powered)
```

### ⚠️ Legal Notice

This project was created through clean-room reverse engineering for interoperability purposes. All trademarks remain property of their respective owners. This project aims to enhance user experience, not circumvent legitimate copyright protections.

*Join us in celebrating the spirit of open hardware and software freedom! **Feel free to modify or fork** :-)*
