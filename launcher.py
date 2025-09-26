import gc
import os
import time
import math
import badger2040
import badger_os
import pngdec
import jpegdec
import network
from machine import ADC, Pin

APP_DIR = "/examples"
FONT_SIZE = 2

changed = False
exited_to_launcher = False
woken_by_button = badger2040.woken_by_button()  # Must be done before we clear_pressed_to_wake

if badger2040.pressed_to_wake(badger2040.BUTTON_A) and badger2040.pressed_to_wake(badger2040.BUTTON_C):
    # Pressing A and C together at start quits app
    exited_to_launcher = badger_os.state_clear_running()
    badger2040.reset_pressed_to_wake()
else:
    # Otherwise restore previously running app
    badger_os.state_launch()


display = badger2040.Badger2040()
display.set_font("bitmap8")
display.led(128)

png = pngdec.PNG(display.display)
jpeg = jpegdec.JPEG(display.display)

state = {
    "page": 0,
    "running": "launcher"
}

badger_os.state_load("launcher", state)

examples = [x[:-3] for x in os.listdir("/examples") if x.endswith(".py")]

# Approximate center lines for buttons A, B and C
centers = (41, 147, 253)
MAX_PAGE = math.ceil(len(examples) / 3)
WIDTH = 296

en_pin = Pin(25, Pin.OUT)

def draw_battery_usage(x):
    full_battery = 4.2 
    empty_battery = 2.8
    usb_detect = Pin('WL_GPIO2', Pin.IN)
    if usb_detect.value() == 1:
        plug_icon = bytearray((
            0b00111100, 0b01100110, 0b01000010, 0b01000010,
            0b01111110, 0b01000010, 0b01000010, 0b00111100
        ))
        display.set_pen(15)
        display.image(plug_icon, 8, 8, x + 85, 4)
        display.text("USB", x + 95, 4, WIDTH, 1.0)
    else:
        # 2. Pomiar napięcia baterii
        en_pin.value(1)
        time.sleep(0.1)
        adc = ADC(29)
        _ = adc.read_u16()  # Odrzuć pierwszą próbkę
        total = 0
        for _ in range(10):
            total += adc.read_u16()
            time.sleep(0.01)
        avg_raw = total / 10
        vsys_div = (avg_raw / 323.2) * 0.045
        battery_voltage = vsys_div * (full_battery / 0.045)

        # 3. Obliczanie poziomu baterii
        b_level = 100.0 * (battery_voltage - empty_battery) / (full_battery - empty_battery)
        b_level = max(0, min(100, b_level))  # Ograniczenie do 0-100%
        b_level_rounded = 5 * round(b_level / 5)  # Zaokrąglanie do 5%

        # 4. Rysowanie ikony baterii
        battery_icon = bytearray((
            0b110011, 0b001100, 0b011110, 0b011110,
            0b010010, 0b010010, 0b010010, 0b011110, 0b000001
        ))
        display.set_pen(15)
        display.image(battery_icon, 6, 9, x, 3)

        # 5. Rysowanie paska i poziomu
        display.rectangle(x + 8, 3, 80, 10)
        display.set_pen(0)
        display.rectangle(x + 9, 4, 78, 8)
        display.set_pen(15)
        display.rectangle(x + 10, 5, int(76.0 * (b_level / 100.0)), 6)
        display.text("{:.0f}%".format(b_level_rounded), x + 91, 4, WIDTH, 1.0)
        
def draw_disk_usage(x):
    _, f_used, _ = badger_os.get_disk_usage()
    display.set_pen(15)
    display.image(
        bytearray(
            (
                0b00000000,
                0b00111100,
                0b00111100,
                0b00111100,
                0b00111000,
                0b00000000,
                0b00000000,
                0b00000001,
            )
        ),
        8,
        8,
        x,
        4,
    )
    display.rectangle(x + 10, 3, 80, 10)
    display.set_pen(0)
    display.rectangle(x + 11, 4, 78, 8)
    display.set_pen(15)
    display.rectangle(x + 12, 5, int(76 / 100.0 * f_used), 6)
    display.text("{:.2f}%".format(f_used), x + 91, 4, WIDTH, 1.0)
    
def render():
    display.set_pen(15)
    display.clear()
    display.set_pen(0)

    max_icons = min(3, len(examples[(state["page"] * 3):]))

    for i in range(max_icons):
        x = centers[i]
        label = examples[i + (state["page"] * 3)]
        icon_label = label.replace("_", "-")
        icon = f"{APP_DIR}/icon-{icon_label}"
        label = label.replace("_", " ")
        for lib, ext in [(png, "png"), (jpeg, "jpg")]:
            try:
                lib.open_file(f"{icon}.{ext}")
                lib.decode(x - 26, 30)
                break
            except (OSError, RuntimeError):
                continue
        display.set_pen(0)
        w = display.measure_text(label, FONT_SIZE)
        display.text(label, int(x - (w / 2)), 16 + 80, WIDTH, FONT_SIZE)

    for i in range(MAX_PAGE):
        x = 286
        y = int((128 / 2) - (MAX_PAGE * 10 / 2) + (i * 10))
        display.set_pen(0)
        display.rectangle(x, y, 8, 8)
        if state["page"] != i:
            display.set_pen(15)
            display.rectangle(x + 1, y + 1, 6, 6)

    display.set_pen(0)
    display.rectangle(0, 0, WIDTH, 16)
    draw_disk_usage(50) 
    draw_battery_usage(175) # call the battery bar
    display.set_pen(15)
    display.text("p00fOS", 4, 4, WIDTH, 1.0)

    display.update()



def wait_for_user_to_release_buttons():
    while display.pressed_any():
        time.sleep(0.01)


def launch_example(index):
    wait_for_user_to_release_buttons()

    file = examples[(state["page"] * 3) + index]
    file = f"{APP_DIR}/{file}"

    for k in locals().keys():
        if k not in ("gc", "file", "badger_os"):
            del locals()[k]

    gc.collect()

    badger_os.launch(file)


def button(pin):
    global changed
    changed = True

    if pin == badger2040.BUTTON_A:
        launch_example(0)
    if pin == badger2040.BUTTON_B:
        launch_example(1)
    if pin == badger2040.BUTTON_C:
        launch_example(2)
    if pin == badger2040.BUTTON_UP:
        state["page"] = (state["page"] - 1) % MAX_PAGE
        render()
    if pin == badger2040.BUTTON_DOWN:
        state["page"] = (state["page"] + 1) % MAX_PAGE
        render()


if exited_to_launcher or not woken_by_button:
    wait_for_user_to_release_buttons()
    display.set_update_speed(badger2040.UPDATE_MEDIUM)
    render()

display.set_update_speed(badger2040.UPDATE_FAST)

while True:
    # Sometimes a button press or hold will keep the system
    # powered *through* HALT, so latch the power back on.
    display.keepalive()

    if display.pressed(badger2040.BUTTON_A):
        button(badger2040.BUTTON_A)
    if display.pressed(badger2040.BUTTON_B):
        button(badger2040.BUTTON_B)
    if display.pressed(badger2040.BUTTON_C):
        button(badger2040.BUTTON_C)

    if display.pressed(badger2040.BUTTON_UP):
        button(badger2040.BUTTON_UP)
    if display.pressed(badger2040.BUTTON_DOWN):
        button(badger2040.BUTTON_DOWN)

    if changed:
        badger_os.state_save("launcher", state)
        changed = False

    display.halt()