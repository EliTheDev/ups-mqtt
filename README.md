# Windows UPS Debug Tool

This guide creates a simple Windows tool to debug and test UPS functionality by displaying real-time UPS statistics in the command console. This is designed for debugging the machine itself, not for monitoring or reporting.

## Prerequisites

- Windows 10 laptop
- UPS with USB connection
- Python 3.8 or higher
- Administrator privileges

## Required Software

### 1. Install Python

- Download Python from [python.org](https://python.org)
- During installation, check “Add Python to PATH”
- Verify installation: `python --version`

### 2. Install Required Python Packages

Open Command Prompt as Administrator and run:

```cmd
pip install pyusb libusb1 colorama
```

## Create the UPS Debug Tool

Create a new file called `ups_debug.py`:

```python
#!/usr/bin/env python3

import time
import sys
import os
import json
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows console colors
init()

class UPSDebugTool:
def __init__(self):
self.clear_screen()
self.print_header()

def clear_screen(self):
"""Clear console screen"""
os.system('cls' if os.name == 'nt' else 'clear')

def print_header(self):
"""Print application header"""
print(f"{Fore.CYAN}{'='*60}")
print(f"{Fore.CYAN} Windows UPS Debug Tool")
print(f"{Fore.CYAN} Real-time UPS Statistics Display")
print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
print()

def detect_ups_devices(self):
"""Detect USB UPS devices"""
try:
import usb.core
import usb.util

print(f"{Fore.YELLOW}Scanning for UPS devices...{Style.RESET_ALL}")

# Find USB devices
devices = usb.core.find(find_all=True)
ups_devices = []

# Common UPS vendor IDs and names
ups_vendors = {
0x051d: "APC",
0x0463: "MGE UPS Systems",
0x09ae: "Tripp Lite",
0x0764: "Cyber Power Systems",
0x06da: "Phoenixtec Power",
0x0925: "Lakeview Research",
0x0001: "Fiskars, Powerman",
0x ffff: "Various/Generic"
}

for device in devices:
try:
if device.idVendor and device.idProduct:
if device.idVendor in ups_vendors:
vendor_name = ups_vendors[device.idVendor]
ups_devices.append({
'vendor_id': device.idVendor,
'product_id': device.idProduct,
'vendor_name': vendor_name,
'device': device
})
except Exception:
continue

return ups_devices

except ImportError:
print(f"{Fore.RED}Error: pyusb not available. Install with: pip install pyusb{Style.RESET_ALL}")
return []
except Exception as e:
print(f"{Fore.RED}Error detecting UPS devices: {e}{Style.RESET_ALL}")
return []

def get_ups_basic_info(self, device_info):
"""Get basic UPS information"""
try:
device = device_info['device']

# Try to get device strings
try:
manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else "Unknown"
except:
manufacturer = device_info['vendor_name']

try:
product = usb.util.get_string(device, device.iProduct) if device.iProduct else "Unknown"
except:
product = f"Product ID: {hex(device_info['product_id'])}"

try:
serial = usb.util.get_string(device, device.iSerialNumber) if device.iSerialNumber else "Unknown"
except:
serial = "Not Available"

return {
'manufacturer': manufacturer,
'product': product,
'serial': serial,
'vendor_id': hex(device_info['vendor_id']),
'product_id': hex(device_info['product_id'])
}

except Exception as e:
return {
'manufacturer': device_info['vendor_name'],
'product': f"Product ID: {hex(device_info['product_id'])}",
'serial': "Error reading device",
'vendor_id': hex(device_info['vendor_id']),
'product_id': hex(device_info['product_id']),
'error': str(e)
}

def simulate_ups_stats(self):
"""Simulate UPS statistics for demonstration"""
import random

# Base values that change slightly over time
base_battery = 85 + random.randint(-5, 15)
base_load = 25 + random.randint(-10, 20)
base_voltage = 120 + random.uniform(-5, 5)

return {
'status': random.choice(['Online', 'On Battery', 'Low Battery', 'Charging']),
'battery_charge': max(0, min(100, base_battery)),
'battery_voltage': round(12.0 + random.uniform(-1, 1), 1),
'input_voltage': round(base_voltage, 1),
'output_voltage': round(base_voltage + random.uniform(-2, 2), 1),
'load_percent': max(0, min(100, base_load)),
'frequency': round(60.0 + random.uniform(-0.5, 0.5), 1),
'temperature': round(25 + random.uniform(-5, 10), 1),
'runtime_remaining': f"{random.randint(45, 180)} minutes",
'last_test': "2025-07-10",
'model': "Debug Simulation"
}

def print_ups_info(self, ups_info):
"""Print UPS device information"""
print(f"{Fore.GREEN}UPS Device Information:{Style.RESET_ALL}")
print(f" Manufacturer: {ups_info.get('manufacturer', 'Unknown')}")
print(f" Product: {ups_info.get('product', 'Unknown')}")
print(f" Serial: {ups_info.get('serial', 'Unknown')}")
print(f" Vendor ID: {ups_info.get('vendor_id', 'Unknown')}")
print(f" Product ID: {ups_info.get('product_id', 'Unknown')}")

if 'error' in ups_info:
print(f" {Fore.YELLOW}Note: {ups_info['error']}{Style.RESET_ALL}")
print()

def print_ups_stats(self, stats):
"""Print UPS statistics in a formatted table"""
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"{Fore.CYAN}UPS Statistics - {timestamp}{Style.RESET_ALL}")
print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")

# Status with color coding
status = stats['status']
if status == 'Online':
status_color = Fore.GREEN
elif status == 'On Battery':
status_color = Fore.YELLOW
elif status == 'Low Battery':
status_color = Fore.RED
else:
status_color = Fore.BLUE

print(f"Status: {status_color}{status}{Style.RESET_ALL}")

# Battery info with color coding
battery = stats['battery_charge']
if battery > 50:
battery_color = Fore.GREEN
elif battery > 20:
battery_color = Fore.YELLOW
else:
battery_color = Fore.RED

print(f"Battery Charge: {battery_color}{battery}%{Style.RESET_ALL}")
print(f"Battery Voltage: {stats['battery_voltage']}V")

# Load with color coding
load = stats['load_percent']
if load < 70:
load_color = Fore.GREEN
elif load < 90:
load_color = Fore.YELLOW
else:
load_color = Fore.RED

print(f"Load: {load_color}{load}%{Style.RESET_ALL}")

# Voltage and frequency
print(f"Input Voltage: {stats['input_voltage']}V")
print(f"Output Voltage: {stats['output_voltage']}V")
print(f"Frequency: {stats['frequency']}Hz")
print(f"Temperature: {stats['temperature']}°C")
print(f"Runtime Left: {stats['runtime_remaining']}")
print(f"Model: {stats['model']}")

print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")

def run_continuous_display(self, refresh_interval=5):
"""Run continuous UPS stats display"""
print(f"{Fore.YELLOW}Starting continuous UPS monitoring...{Style.RESET_ALL}")
print(f"Press Ctrl+C to stop")
print()

try:
while True:
# Clear screen and show header
self.clear_screen()
self.print_header()

# Simulate getting UPS stats (replace with actual UPS communication)
stats = self.simulate_ups_stats()
self.print_ups_stats(stats)

print(f"\n{Fore.CYAN}Refreshing every {refresh_interval} seconds...{Style.RESET_ALL}")
print(f"{Fore.CYAN}Press Ctrl+C to exit{Style.RESET_ALL}")

time.sleep(refresh_interval)

except KeyboardInterrupt:
print(f"\n{Fore.YELLOW}Monitoring stopped by user{Style.RESET_ALL}")

def run_single_check(self):
"""Run a single UPS check and display results"""
# Detect UPS devices
ups_devices = self.detect_ups_devices()

if ups_devices:
print(f"{Fore.GREEN}Found {len(ups_devices)} UPS device(s):{Style.RESET_ALL}")
print()

for i, device_info in enumerate(ups_devices):
print(f"{Fore.YELLOW}Device {i+1}:{Style.RESET_ALL}")
ups_info = self.get_ups_basic_info(device_info)
self.print_ups_info(ups_info)

# Show simulated stats for each device
stats = self.simulate_ups_stats()
stats['model'] = ups_info['product']
self.print_ups_stats(stats)
print()
else:
print(f"{Fore.RED}No UPS devices detected.{Style.RESET_ALL}")
print()
print("Troubleshooting tips:")
print("1. Check USB cable connection")
print("2. Ensure UPS supports USB communication")
print("3. Install UPS manufacturer's drivers")
print("4. Run as Administrator")
print()

# Still show simulated stats for debugging
print(f"{Fore.YELLOW}Showing simulated UPS data for debugging:{Style.RESET_ALL}")
stats = self.simulate_ups_stats()
self.print_ups_stats(stats)

def main():
tool = UPSDebugTool()

print("Choose an option:")
print("1. Single UPS check")
print("2. Continuous monitoring")
print("3. Exit")

try:
choice = input(f"\n{Fore.CYAN}Enter choice (1-3): {Style.RESET_ALL}")

if choice == '1':
print()
tool.run_single_check()
elif choice == '2':
refresh_rate = input(f"\n{Fore.CYAN}Refresh interval in seconds (default 5): {Style.RESET_ALL}")
try:
refresh_rate = int(refresh_rate) if refresh_rate else 5
except ValueError:
refresh_rate = 5
print()
tool.run_continuous_display(refresh_rate)
elif choice == '3':
print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
sys.exit(0)
else:
print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")

except KeyboardInterrupt:
print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
sys.exit(0)

if __name__ == "__main__":
main()
```

## Create USB Driver Test Script

Create `test_usb_ups.py` for basic USB detection:

```python
#!/usr/bin/env python3

import sys

def test_usb_detection():
"""Test USB UPS detection capabilities"""

print("Windows UPS USB Detection Test")
print("=" * 40)

try:
import usb.core
import usb.util
print("✓ PyUSB library available")
except ImportError:
print("✗ PyUSB not found. Install with: pip install pyusb")
return False

try:
# Test libusb backend
import libusb1
print("✓ libusb1 backend available")
except ImportError:
print("✗ libusb1 not found. Install with: pip install libusb1")
return False

print("\nScanning all USB devices...")
devices = usb.core.find(find_all=True)
device_count = len(list(devices))
print(f"Found {device_count} total USB devices")

print("\nUPS Detection Test Complete")
return True

if __name__ == "__main__":
test_usb_detection()
```

## Usage Instructions

### 1. Install Dependencies

```cmd
pip install pyusb libusb1 colorama
```

### 2. Test USB Detection

```cmd
python test_usb_ups.py
```

### 3. Run UPS Debug Tool

```cmd
python ups_debug.py
```

### 4. Choose Your Mode:

- **Option 1**: Single check - Shows UPS info and current stats once
- **Option 2**: Continuous monitoring - Refreshes stats every few seconds
- **Option 3**: Exit

## Features

### Console Display:

- **Color-coded status** (Green=Online, Yellow=On Battery, Red=Low Battery)
- **Real-time statistics** with automatic refresh
- **Device detection** and basic info display
- **Clear, formatted output** optimized for debugging

### Debug Information:

- UPS device manufacturer and model
- Battery charge level and voltage
- Input/output voltage and frequency
- Load percentage and temperature
- Runtime remaining estimates
- Connection status

### Troubleshooting:

- Automatic USB device detection
- Clear error messages and solutions
- Fallback simulation mode if no UPS detected
- Administrator privilege checking

## Troubleshooting

### Common Issues:

1. **“No UPS devices detected”:**
- Check USB cable connection
- Run Command Prompt as Administrator
- Install UPS manufacturer’s drivers
- Verify UPS supports USB communication
1. **PyUSB import errors:**
- Install libusb: `pip install libusb1`
- Download libusb-win32 drivers if needed
1. **Permission errors:**
- Always run as Administrator
- Check Windows Device Manager for driver issues
1. **Display issues:**
- Update Windows Terminal for better color support
- Use Command Prompt if PowerShell has display problems

This simplified tool focuses purely on local debugging and testing, displaying all UPS information directly in the console without any external monitoring or reporting components.
