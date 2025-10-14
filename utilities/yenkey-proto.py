#!/usr/bin/env python3
"""
Sending HID packets to Yenkee 3700 Rogue Keyboard
"""

import usb.core
import usb.util
import time
import sys
import glob
import os

IFACE=1

# Example configurations - format: ([packets], "description", "argument")
EXAMPLES = [
    (["02000000000000fd"], "Factory reset - all defaults", "factory-reset"),
    (["0702040407000000"], "Breathing - rainbow", "breathing-rainbow"),
    (["0704020427000000"], "Wave to down - rainbow", "wavedown-rainbow"), 
    (["0707020418ff456e"], "Snake - custom color", "snake-pink"),
    (["0701040408ff0000"], "Static - red", "static-red"),
    (["070104040800ff00"], "Static - green", "static-green"),
    (["07010404080000ff"], "Static - blue", "static-blue"),
    (["0709040407000000"], "Disco - rainbow", "disco-rainbow"),
    (["0700040007000000"], "Turn off LEDs", "off"),
    (["070402040800ff00"], "Wave - green", "wave-green"),
    (["070b020407ff456e"], "Kaleidoscope - rainbow", "kaleidoscope-rainbow"),
    # Key remapping examples (would need all 9 packets for complete remap)
    (
      [
        "0900f801000000fd000029000000350000002b00000039000000e1000000e0000000000000001e000000140000000400000064000000000000003a0000001f00",
        "0900f801010000fc00001a000000160000001d000000e30000003b0000002000000008000000070000001b000000e20000003c00000021000000150000000900",
        "0900f801020000fb000006000000000000003d00000022000000170000000a00000019000000000000003e000000230000001c0000000b000000050000002c00",
        "0900f801030000fa00003f00000024000000180000000d00000011000000e600000040000000250000000c0000000e00000010000a0100000000410000002600",
        "0900f801040000f90000120000000f00000036000000e4000000420000002700000013000000330000003700000050000000430000002d0000002f0000003400",
        "0900f801050000f800003800000051000000440000002e0000003000000032000000e50000004f000000450000002a0000003100000028000000520000004900",
        "0900f801060000f70000460000004a0000004d0000004b0000004e0000004c000000000000000000000000000000000000000000000000000000000000000000",
        "0900f801070000f60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "0900f801080000f50000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
      ], "Reset keymap to the default", "resetkeymap"
    ),
    (
      [
        "0900f801000000fd000029000000350000002b00000000000000e1000000e0000000000000001e000000140000000400000064000000000000003a0000001f00",
        "0900f801010000fc00001a000000160000001d000000e30000003b0000002000000008000000070000001b000000e20000003c00000021000000150000000900",
        "0900f801020000fb000006000000000000003d00000022000000170000000a00000019000000000000003e000000230000001c0000000b000000050000002c00",
        "0900f801030000fa00003f00000024000000180000000d00000011000000e600000040000000250000000c0000000e00000010000a0100000000410000002600",
        "0900f801040000f90000120000000f00000036000000e4000000420000002700000013000000330000003700000050000000430000002d0000002f0000003400",
        "0900f801050000f800003800000051000000440000002e0000003000000032000000e50000004f000000450000002a0000003100000028000000520000004900",
        "0900f801060000f70000460000004a0000004d0000004b0000004e0000004c000000000000000000000000000000000000000000000000000000000000000000",
        "0900f801070000f60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "0900f801080000f50000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
      ], "Disable CapsLock", "disablecaps"
    ),
    (
      [
        "0900f801000000fd00e23a000000350000002b00000039000000e1000000e0000000000000001e000000140000000400000064000000000000003a0000001f00",
        "0900f801010000fc00001a000000160000001d000000e30000003b0000002000000008000000070000001b000000e20000003c00000021000000150000000900",
        "0900f801020000fb000006000000000000003d00000022000000170000000a00000019000000000000003e000000230000001c0000000b000000050000002c00",
        "0900f801030000fa00003f00000024000000180000000d00000011000000e600000040000000250000000c0000000e00000010000a0100000000410000002600",
        "0900f801040000f90000120000000f00000036000000e4000000420000002700000013000000330000003700000050000000430000002d0000002f0000003400",
        "0900f801050000f800003800000051000000440000002e0000003000000032000000e50000004f000000450000002a0000003100000028000000520000004900",
        "0900f801060000f70000460000004a0000004d0000004b0000004e0000004c000000000000000000000000000000000000000000000000000000000000000000",
        "0900f801070000f60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "0900f801080000f50000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
      ], "Map ESC to Alt+F1", "esctoaltf1"
    ),
]

class YenkeeKeyboard:
    def __init__(self, vid=0x3151, pid=0x4002):
        self.vid = vid
        self.pid = pid
        self.dev = None
        self.sysfs_path = None

    def get_sysfs_path(self, vid, pid):
        """Find sysfs path for USB device by idVendor and idProduct"""
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
        """Connect to keyboard"""
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

    def showActive(self):
        if self.dev.is_kernel_driver_active(0):
            print(" CON: IFACE0 active")
        else:
            print(" CON: IFACE0 NOT active")
        if self.dev.is_kernel_driver_active(1):
            print(" CON: IFACE1 active")
        else:
            print(" CON: IFACE1 NOT active")

    def _setup_communication(self):
        """Setup communication on Interface 0"""
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
        """Send packet to Interface 0 - this preserves Fn functions!"""
        if not self.dev:
            print("Device not connected")
            return False

        try:
            print(f"Sending: {description}")
            hex_clean = hex_string.replace(" ", "")
            main_data = bytes.fromhex(hex_clean)

            if len(main_data) > 64:
                print(f"  Warning: Data longer than 64 bytes, truncating")
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
        """Send multiple packets sequentially"""
        success_count = 0
        for i, (hex_string, description) in enumerate(packets, 1):
            print(f"Packet {i}/{len(packets)}:")
            if self.send_packet(hex_string, description):
                success_count += 1
            time.sleep(0.1)
        print(f"Total successful: {success_count}/{len(packets)}")
        return success_count == len(packets)

    def disconnect(self):
        """End communication"""
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

def show_usage():
    """Show usage information"""
    print("Yenkee 3700 Rogue Keyboard Controller")
    print("=" * 50)
    print("Usage:")
    print("  ./yenkey-proto.py <example_name>          # Run predefined example")
    print("  ./yenkey-proto.py <hex_packet> ...        # Send custom HID packets")
    print()
    print("Available examples:")
    for packets, description, arg_name in EXAMPLES:
        print(f"  {arg_name:<20} {description}")
    print()
    print("Custom usage:")
    print("  ./yenkey-proto.py 0701040408ff0000        # Send single hex packet")
    print("  ./yenkey-proto.py 0701040408ff0000 070204040800ff00  # Multiple packets")
    print()
    print("Examples:")
    print("  ./yenkey-proto.py breathing-rainbow")
    print("  ./yenkey-proto.py wavedown-rainbow")
    print("  ./yenkey-proto.py static-red")
    print("  ./yenkey-proto.py 0701040408ff0000")

def get_example_by_name(name):
    """Find example by argument name"""
    for packets, description, arg_name in EXAMPLES:
        if arg_name == name:
            return (packets, description)
    return None

def main():
    if len(sys.argv) == 1:
        # No arguments - show help and exit
        show_usage()
        sys.exit(0)
    
    # Process command line arguments
    packets_to_send = []
    
    for arg in sys.argv[1:]:
        # Check if it's a predefined example
        example = get_example_by_name(arg)
        if example:
            packets, description = example
            print(f"Setting-up: {description}")
            for i, packet in enumerate(packets, 1):
                packets_to_send.append((packet, f"{description} [{i}/{len(packets)}]"))
        else:
            # Custom hex packet
            hex_clean = arg.replace(" ", "")
            if all(c in '0123456789abcdefABCDEF' for c in hex_clean):
                if len(hex_clean) > 128:
                    hex_clean = hex_clean[:128]
                    print(f"Warning: Packet too long, truncating to 64 bytes")
                packets_to_send.append((hex_clean, f"Custom: {arg}"))
            else:
                print(f"Error: '{arg}' is not a valid example or hex packet")
                print("Available examples: " + ", ".join([ex[2] for ex in EXAMPLES]))
                sys.exit(1)

    keyboard = YenkeeKeyboard()

    try:
        if keyboard.connect():
            keyboard.send_multiple_packets(packets_to_send)
        else:
            print("Cannot connect to keyboard")
            sys.exit(1)

    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        keyboard.disconnect()

if __name__ == "__main__":
    main()
