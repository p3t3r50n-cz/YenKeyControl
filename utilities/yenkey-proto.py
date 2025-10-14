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
                # Looking for line like: PRODUCT=3151/4002/201
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
            
            print(self.dev)
            print("device bus:", self.dev.bus)
            print("device address:", self.dev.address)
            print("device port:", self.dev.port_number)
            print("device speed:", self.dev.speed)
            print(f">>> PATH: {self.sysfs_path}")
            
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
        
        print(">>> _setup_communication PRE:")
        self.showActive()
        
        try:
            # Disconnect kernel driver for interface IFACE
            if self.dev.is_kernel_driver_active(0):
                self.dev.detach_kernel_driver(0)
                print("Kernel driver disconnected for interface 0")

            if self.dev.is_kernel_driver_active(1):
                self.dev.detach_kernel_driver(1)
                print("Kernel driver disconnected for interface 1")

            print("Communication setup on Interface 0")
            
            print(">>> _setup_communication POST:")
            self.showActive()
            
            return True

        except Exception as e:
            
            print(f"Communication setup error: {e}")
            
            print(">>> _setup_communication POST:")
            self.showActive()
            
            return False

    def send_packet(self, hex_string, description="Command"):
        """Send packet to Interface 0 - this preserves Fn functions!"""
        if not self.dev:
            print("Device not connected")
            return False

        try:
            print(f"Sending: {description}")
            print(f"  Raw: {hex_string}")

            # Prepare data for SET_REPORT
            hex_clean = hex_string.replace(" ", "")
            main_data = bytes.fromhex(hex_clean)

            if len(main_data) > 64:
                print(f"  Warning: Data longer than 64 bytes, truncating")
                main_data = main_data[:64]

            if len(main_data) < 64:
                checksum = bytes([(0x100 - ((sum(main_data) + 1) & 0xFF)) & 0xFF])
                main_data += checksum

            main_data += b"\x00" * (64 - len(main_data))

            print(f"  Data: {main_data.hex()}")
            print(f"  Length: {len(main_data)} bytes")

            # KEY: Send SET_REPORT to Interface 0 (wIndex=0)
            self.dev.ctrl_transfer(0x21, 0x09, 0x0300, IFACE, main_data)

            print("  Command sent successfully (Fn functions should remain active)\n")
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
            time.sleep(0.1)  # Short pause

        print(f"Total successful: {success_count}/{len(packets)}")
        return success_count == len(packets)

    def disconnect(self):
        """End communication"""
        if self.dev:
            try:
                self.dev.attach_kernel_driver(1)
                self.dev.attach_kernel_driver(0)
                print("Kernel driver attached for interface")
            except:
                print("Kernel driver for interface was NOT attached!")
                pass
            
            # 1. Dispose resources before unbind
            if self.dev:
                usb.util.dispose_resources(self.dev)
                self.dev = None
            
            #self.usb_path = "2-1"
            
            # 2. Unbind
            print(f"  Disconnecting {self.sysfs_path}...")
            with open("/sys/bus/usb/drivers/usb/unbind", "w") as f:
                f.write(self.sysfs_path)
            
            # 3. Bind
            print(f"  Connecting {self.sysfs_path}...")
            with open("/sys/bus/usb/drivers/usb/bind", "w") as f:
                f.write(self.sysfs_path)
            
            #time.sleep(1)
            
            #print(">>> disconnect POST:")
            #self.showActive()
            
            print("Device disconnected")

def main():
    preset_packets = [
        ("07 01 04 04 00", "Static - red"),
        ("07 02 04 04 00", "Breathing - red"),
        ("07 04 04 04 02", "Wave - blue"),
        ("07 09 04 04 07", "Disco - rainbow"),
        ("07 00 04 00 07", "Turn off LED"),
    ]
    
    if len(sys.argv) > 1:
        custom_packets = []
        for i, arg in enumerate(sys.argv[1:], 1):
            hex_clean = arg.replace(" ", "")
            if len(hex_clean) > 128:
                hex_clean = hex_clean[:128]
                print(f"Warning: Packet {i} is too long, truncating to 64 bytes")
            custom_packets.append((hex_clean, f"Custom command {i}"))
        packets_to_send = custom_packets
    else:
        packets_to_send = preset_packets

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
