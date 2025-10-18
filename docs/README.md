# Yenkee YKB3700 Rogue Keyboard Protocol Documentation

![Yenkee YKB3700 Rogue Keyboard](/images/YKB3700.png)

## Reverse Engineering Project

This comprehensive documentation is the result of meticulous reverse engineering of the Yenkee YKB3700 Rogue (OEM ROYUAN) keyboard protocol. Unlike many manufacturers who provide open APIs or cross-platform support, the vendor only offers proprietary Windows software, effectively locking out Linux, macOS, and other operating system users from customizing their RGB lighting experience.

**Our mission:** To liberate this excellent mechanical keyboard from its Windows-only shackles and empower the open-source community with complete control over its RGB lighting capabilities.

### Methodology

The protocol was reverse engineered using:
- **USBPcap** - For capturing raw USB traffic between the keyboard and official Windows software
- **Wireshark** - For detailed analysis of captured USB packets and protocol patterns
- **Systematic testing** - Methodical testing of each parameter to understand its function
- **Community collaboration** - Sharing findings and validating results across multiple keyboard units

### Documentation Structure

This documentation is divided into main sections:

1. [**Lighting Effects Protocol**](./communication-protocol.md#lighting-effects-protocol) - Control global effects, colors, brightness, and animation speeds
2. [**Per-Key RGB Control**](./communication-protocol.md#user-mode-backlight-protocol---setting-custom-color-for-each-key) - Individual key color programming (see separate documentation)
3. [**Per-Key remapping**](./communication-protocol.md#yenkee-3700-rogue-keyboard-key-remapping-protocol) - Describes the options for reassigning individual keys to different functions (e.g., sending different scancodes)

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

*Join us in celebrating the spirit of open hardware and software freedom! Feel free to modify or fork :-)*

*[Continue reading to explore the complete protocol...](./communication-protocol.md)*
