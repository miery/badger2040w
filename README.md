# Badger 2040W Utility Project

A collection of utilities for the **Pimoroni Badger 2040W**, including a **battery level indicator**, **Wi-Fi network manager**, and **weather display** using the Open Meteo API.

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

### 3. Weather Display
Fetches and displays current weather data, air quality, and pollen information for a specified location using the **Open Meteo API**.

#### Features
- **Current Weather**: Shows temperature, weather conditions, wind speed, and wind direction.
- **Forecast**: Displays a 2-day weather forecast with icons.
- **Sunrise/Sunset**: Shows sunrise and sunset times.
- **Air Quality**: Displays PM10, PM2.5, and UV index.
- **Pollen Levels**: Shows pollen counts for alder, birch, grass, mugwort, ragweed, and olive.
- **Automatic Theme**: Switches between day and night themes based on sunrise/sunset times.
- **Power Management**: Updates every 20 minutes when connected to USB power, and enters deep sleep mode when running on battery.

#### How It Works
- Fetches weather data from the Open Meteo API.
- Displays weather icons based on current conditions.
- Updates the display automatically or on button press.

---

## Setup

### Requirements
- **Hardware**: Pimoroni Badger 2040W
- **Firmware**: MicroPython (pre-installed on Badger 2040W)
- **Libraries**: `badger2040`, `badger_os`, `machine`, `binascii`, `urequests`, `jpegdec`
- **Icons**: Weather icons in the `/icons/` directory (e.g., `icon-sun.jpg`, `icon-rain.jpg`, etc.).

### Installation
1. Copy the provided Python scripts to your Badger 2040W.
2. Edit `wifi_networks.txt` to add your Wi-Fi networks (one per line, format: `SSID|PSK|COUNTRY`).
3. Ensure the `/icons/` directory contains the required weather icons.
4. Run the script using the Badger 2040W's built-in tools.

---

## Usage

### Battery Level Indicator
Call the `draw_battery_usage(x)` function in your main loop to display the battery level at position `x`.

### Wi-Fi Network Manager
- Navigate the list using the **Up/Down** buttons.
- Press **Button A** to scroll up a page.
- Press **Button C** to scroll down a page.
- Press **Button B** to select a network and save it to `WIFI_CONFIG.py`.

### Weather Display
- The weather display updates automatically every 20 minutes when connected to USB power.
- Press any button to wake the device from deep sleep when running on battery.

---

## File Structure
.
├── battery.py          # Battery level indicator
├── wifi_manager.py     # Wi-Fi network manager
├── weather.py          # Weather display using Open Meteo API
├── wifi_networks.txt   # List of Wi-Fi networks (SSID|PSK|COUNTRY)
├── WIFI_CONFIG.py      # Generated Wi-Fi config file (SSID, PSK, COUNTRY)
└── icons/              # Directory containing weather icons
├── icon-sun.jpg
├── icon-sun_dark.jpg
├── icon-rain.jpg
├── icon-rain_dark.jpg
└── ...

---

## Customization

### Battery Level
Adjust the `full_battery` and `empty_battery` values in the `draw_battery_usage()` function if your battery has a different voltage range.

### Wi-Fi Networks
Edit `wifi_networks.txt` to add or remove networks.

### Weather Display
- Change the latitude (`LAT`) and longitude (`LNG`) in `weather.py` to display weather data for a different location.
- Replace the icons in the `/icons/` directory to customize the visual style.

---

## License
This project is open-source and available under the [MIT License](LICENSE).

---

## Credits
- Original weather display concept inspired by [chrissyhroberts](https://github.com/chrissyhroberts).
- Weather data provided by [Open Meteo](https://open-meteo.com).
