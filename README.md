# Badger 2040W Utility Project

A collection of utilities for the **Pimoroni Badger 2040W**, including a **battery level indicator** and **Wi-Fi network manager**.

---

## Features

### 1. Battery Level Indicator
Displays the current battery level as a percentage and a visual bar. Automatically detects USB power and shows a plug icon when connected.

#### How It Works
- Measures the battery voltage using the ADC (Analog-to-Digital Converter).
- Calculates the battery level as a percentage based on the voltage range (4.2V = 100%, 2.8V = 0%).
- Renders a battery icon, a progress bar, and the percentage value.
- Detects USB power and displays a plug icon if the device is charging.

---

### 2. Wi-Fi Network Manager
Allows users to select and save Wi-Fi networks from a list. Networks are stored in a text file (`wifi_networks.txt`) and can be edited manually.

#### Features
- Displays a scrollable list of Wi-Fi networks.
- Supports navigation using the Badger 2040W buttons (A, B, C, Up, Down).
- Saves the selected network to `WIFI_CONFIG.py` for use in other applications.
- Persists the selected item and scroll position between reboots.

#### How It Works
- Loads networks from `wifi_networks.txt` (format: `SSID|PSK|COUNTRY`).
- Renders a list with scrollable items and interactive buttons.
- Updates the configuration file when a network is selected.

---

## Setup

### Requirements
- **Hardware**: Pimoroni Badger 2040W
- **Firmware**: MicroPython (pre-installed on Badger 2040W)
- **Libraries**: `badger2040`, `badger_os`, `machine`, `binascii`

### Installation
1. Copy the provided Python scripts to your Badger 2040W.
2. Edit `wifi_networks.txt` to add your Wi-Fi networks (one per line, format: `SSID|PSK|COUNTRY`).
3. Run the script using the Badger 2040W's built-in tools.

---

## Usage

### Battery Level Indicator
Call `draw_battery_usage(x)` in your main loop to display the battery level at position `x`.

### Wi-Fi Network Manager
- Navigate the list using **Up/Down** buttons.
- Press **Button A** to scroll up a page.
- Press **Button C** to scroll down a page.
- Press **Button B** to select a network and save it to `WIFI_CONFIG.py`.

---

## Customization
- **Battery Level**: Adjust `full_battery` and `empty_battery` values in `draw_battery_usage()` if your battery has a different voltage range.
- **Wi-Fi Networks**: Edit `wifi_networks.txt` to add or remove networks.

---

## License
This project is open-source and available under the [MIT License](LICENSE).
