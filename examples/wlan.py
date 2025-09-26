import binascii
import badger2040
import badger_os
import machine

# *** List Title ***
list_title = "Wi-Fi Network Selection"
list_file = "wifi_networks.txt"

# Global Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT
ARROW_THICKNESS = 3
ARROW_WIDTH = 18
ARROW_HEIGHT = 14
ARROW_PADDING = 2
MAX_ITEM_CHARS = 26
TITLE_TEXT_SIZE = 0.7
ITEM_TEXT_SIZE = 0.6
ITEM_SPACING = 20
LIST_START = 40
LIST_PADDING = 2
LIST_WIDTH = WIDTH - LIST_PADDING - LIST_PADDING - ARROW_WIDTH
LIST_HEIGHT = HEIGHT - LIST_START - LIST_PADDING - ARROW_HEIGHT

# Default networks - can be edited in wifi_networks.txt
# Format: "SSID|PSK|COUNTRY"
list_items = [
    "2.4G-WLAN|62a08f6646f43b8cdc188b00955ef18668b0a1fc7e9f33228064bc3ee4e34740|PL",
    "katedra_chemfiz|3540af3409191b5bce7b7aa3e51c36ec1a545784c3e22d2475203668dca6bbe1|PL"
]

save_list = False
try:
    with open(list_file, "r") as f:
        raw_list_items = f.read().strip()
    if raw_list_items:
        list_items = raw_list_items.split("\n")
    else:
        save_list = True
except OSError:
    save_list = True

if save_list:
    with open(list_file, "w") as f:
        for item in list_items:
            f.write(item + "\n")

# ------------------------------
#      Drawing functions
# ------------------------------

def draw_list(items, start_item, highlighted_item, x, y, width, height, item_height, columns):
    item_x = 0
    item_y = 0
    current_col = 0
    for i in range(start_item, len(items)):
        ssid, _, _ = items[i].split("|")
        if i == highlighted_item:
            display.set_pen(12)
            display.rectangle(item_x, item_y + y - (item_height // 2), width // columns, item_height)
        display.set_pen(0)
        display.text(ssid, item_x + x + item_height, item_y + y, WIDTH, ITEM_TEXT_SIZE)
        item_y += item_height
        if item_y >= height - (item_height // 2):
            item_x += width // columns
            item_y = 0
            current_col += 1
            if current_col >= columns:
                return

def draw_up(x, y, width, height, thickness, padding):
    border = (thickness // 4) + padding
    display.line(x + border, y + height - border, x + (width // 2), y + border)
    display.line(x + (width // 2), y + border, x + width - border, y + height - border)

def draw_down(x, y, width, height, thickness, padding):
    border = (thickness // 2) + padding
    display.line(x + border, y + border, x + (width // 2), y + height - border)
    display.line(x + (width // 2), y + height - border, x + width - border, y + border)

def draw_left(x, y, width, height, thickness, padding):
    border = (thickness // 2) + padding
    display.line(x + width - border, y + border, x + border, y + (height // 2))
    display.line(x + border, y + (height // 2), x + width - border, y + height - border)

def draw_right(x, y, width, height, thickness, padding):
    border = (thickness // 2) + padding
    display.line(x + border, y + border, x + width - border, y + (height // 2))
    display.line(x + width - border, y + (height // 2), x + border, y + height - border)

def draw_tick(x, y, width, height, thickness, padding):
    border = (thickness // 2) + padding
    display.line(x + border, y + ((height * 2) // 3), x + (width // 2), y + height - border)
    display.line(x + (width // 2), y + height - border, x + width - border, y + border)

def update_wifi_config(selected_item):
    ssid, psk, country = selected_item.split("|")
    with open("WIFI_CONFIG.py", "w") as f:
        f.write(f'SSID = "{ssid}"\n')
        f.write(f'PSK = "{psk}"\n')
        f.write(f'COUNTRY = "{country}"\n')

# ------------------------------
#        Program setup
# ------------------------------

changed = True
state = {"current_item": 0}
badger_os.state_load("wifi_list", state)
items_hash = binascii.crc32("\n".join(list_items))
if "items_hash" not in state or state["items_hash"] != items_hash:
    state["current_item"] = 0
    state["items_hash"] = items_hash
    changed = True

# Global variables
items_per_page = 0
display = badger2040.Badger2040()
display.led(128)
display.set_font("sans")
display.set_thickness(2)

if changed:
    display.set_update_speed(badger2040.UPDATE_FAST)
else:
    display.set_update_speed(badger2040.UPDATE_TURBO)

# Find out what the longest item is
longest_item = 0
for i in range(len(list_items)):
    ssid, _, _ = list_items[i].split("|")
    while True:
        item_length = display.measure_text(ssid, ITEM_TEXT_SIZE)
        if item_length > 0 and item_length > LIST_WIDTH - ITEM_SPACING:
            list_items[i] = ssid[:-1] + "|" + list_items[i].split("|")[1] + "|" + list_items[i].split("|")[2]
            ssid = ssid[:-1]
        else:
            break
    longest_item = max(longest_item, display.measure_text(ssid, ITEM_TEXT_SIZE))

# Calculate the number of columns and items per page
list_columns = 1
while longest_item + ITEM_SPACING < (LIST_WIDTH // (list_columns + 1)):
    list_columns += 1
items_per_page = ((LIST_HEIGHT // ITEM_SPACING) + 1) * list_columns

# ------------------------------
#       Main program loop
# ------------------------------

while True:
    display.keepalive()
    if len(list_items) > 0:
        if display.pressed(badger2040.BUTTON_A):
            if state["current_item"] > 0:
                page = state["current_item"] // items_per_page
                state["current_item"] = max(state["current_item"] - (items_per_page) // list_columns, 0)
                if page != state["current_item"] // items_per_page:
                    display.update_speed(badger2040.UPDATE_FAST)
                changed = True
        if display.pressed(badger2040.BUTTON_B):
            selected_item = list_items[state["current_item"]]
            update_wifi_config(selected_item)
            display.set_pen(15)
            display.clear()
            display.set_pen(0)
            display.text("Saved!", 30, HEIGHT // 2, WIDTH, 1.0)
            display.update()
            # display.halt(2000)
        if display.pressed(badger2040.BUTTON_C):
            if state["current_item"] < len(list_items) - 1:
                page = state["current_item"] // items_per_page
                state["current_item"] = min(state["current_item"] + (items_per_page) // list_columns, len(list_items) - 1)
                if page != state["current_item"] // items_per_page:
                    display.update_speed(badger2040.UPDATE_FAST)
                changed = True
        if display.pressed(badger2040.BUTTON_UP):
            if state["current_item"] > 0:
                state["current_item"] -= 1
                changed = True
        if display.pressed(badger2040.BUTTON_DOWN):
            if state["current_item"] < len(list_items) - 1:
                state["current_item"] += 1
                changed = True

    if changed:
        badger_os.state_save("wifi_list", state)
        display.set_pen(15)
        display.clear()
        display.set_pen(12)
        display.rectangle(WIDTH - ARROW_WIDTH, 0, ARROW_WIDTH, HEIGHT)
        display.rectangle(0, HEIGHT - ARROW_HEIGHT, WIDTH, ARROW_HEIGHT)
        y = LIST_PADDING + 12
        display.set_pen(0)
        display.text(list_title, LIST_PADDING, y, WIDTH, TITLE_TEXT_SIZE)
        y += 12
        display.set_pen(0)
        display.line(LIST_PADDING, y, WIDTH - LIST_PADDING - ARROW_WIDTH, y)
        if len(list_items) > 0:
            page_item = 0
            if items_per_page > 0:
                page_item = (state["current_item"] // items_per_page) * items_per_page
            draw_list(list_items, page_item, state["current_item"], LIST_PADDING, LIST_START, LIST_WIDTH, LIST_HEIGHT, ITEM_SPACING, list_columns)
            # Draw the interaction button icons
            display.set_pen(0)
            if state["current_item"] > 0:
                draw_up(WIDTH - ARROW_WIDTH, (HEIGHT // 4) - (ARROW_HEIGHT // 2), ARROW_WIDTH, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)
            if state["current_item"] < (len(list_items) - 1):
                draw_down(WIDTH - ARROW_WIDTH, ((HEIGHT * 3) // 4) - (ARROW_HEIGHT // 2), ARROW_WIDTH, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)
            if state["current_item"] > 0:
                draw_left((WIDTH // 7) - (ARROW_WIDTH // 2), HEIGHT - ARROW_HEIGHT, ARROW_WIDTH, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)
            if state["current_item"] < (len(list_items) - 1):
                draw_right(((WIDTH * 6) // 7) - (ARROW_WIDTH // 2), HEIGHT - ARROW_HEIGHT, ARROW_WIDTH, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)
            draw_tick((WIDTH // 2) - (ARROW_WIDTH // 2), HEIGHT - ARROW_HEIGHT, ARROW_HEIGHT, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)
        else:
            empty_text = "No networks"
            text_length = display.measure_text(empty_text, ITEM_TEXT_SIZE)
            display.text(empty_text, ((LIST_PADDING + LIST_WIDTH) - text_length) // 2, (LIST_HEIGHT // 2) + LIST_START - (ITEM_SPACING // 4), WIDTH, ITEM_TEXT_SIZE)
        display.update()
        display.set_update_speed(badger2040.UPDATE_TURBO)
        changed = False
    display.halt()
