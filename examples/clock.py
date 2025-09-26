import time
import machine
import badger2040

display = badger2040.Badger2040()
display.set_update_speed(2)
display.set_thickness(4)
WIDTH, HEIGHT = display.get_bounds()

if badger2040.is_wireless():
    import ntptime
    try:
        display.connect()
        if display.isconnected():
            ntptime.settime()
            badger2040.pico_rtc_to_pcf()
    except (RuntimeError, OSError) as e:
        print(f"Wireless Error: {e}")

try:
    badger2040.pcf_to_pico_rtc()
except RuntimeError:
    pass

rtc = machine.RTC()
display.set_font("sans")

cursors = ["year", "month", "day", "hour", "minute"]
set_clock = False
toggle_set_clock = False
cursor = 0
last = 0

button_a = badger2040.BUTTONS[badger2040.BUTTON_A]
button_b = badger2040.BUTTONS[badger2040.BUTTON_B]
button_c = badger2040.BUTTONS[badger2040.BUTTON_C]
button_up = badger2040.BUTTONS[badger2040.BUTTON_UP]
button_down = badger2040.BUTTONS[badger2040.BUTTON_DOWN]

def is_dst(year, month, day, hour, wd):
    # Reguły dla strefy Europa/Warszawa (CET/CEST)
    # Ostatnia niedziela marca -> początek czasu letniego (2:00 -> 3:00)
    # Ostatnia niedziela października -> koniec czasu letniego (3:00 -> 2:00)
    if month > 3 and month < 10:
        return True
    if month == 3:
        # Ostatnia niedziela marca
        last_sunday_march = 31 - (rtc.datetime()[3] + 31 - 1) % 7
        if day >= last_sunday_march and (day > last_sunday_march or hour >= 2):
            return True
    if month == 10:
        # Ostatnia niedziela października
        last_sunday_october = 31 - (rtc.datetime()[3] + 31 - 1) % 7
        if day < last_sunday_october or (day == last_sunday_october and hour < 2):
            return True
    return False

def get_timezone_offset(year, month, day, hour, wd):
    return 2 if is_dst(year, month, day, hour, wd) else 1

def button(pin):
    global last, set_clock, toggle_set_clock, cursor, year, month, day, hour, minute
    time.sleep(0.01)
    if not pin.value():
        return
    if button_a.value() and button_c.value():
        machine.reset()
    adjust = 0
    if pin == button_b:
        toggle_set_clock = True
        if set_clock:
            rtc.datetime((year, month, day, 0, hour, minute, 0, 0))
            if badger2040.is_wireless():
                badger2040.pico_rtc_to_pcf()
        return
    if set_clock:
        if pin == button_c:
            cursor += 1
            cursor %= len(cursors)
        if pin == button_a:
            cursor -= 1
            cursor %= len(cursors)
        if pin == button_up:
            adjust = 1
        if pin == button_down:
            adjust = -1
        if cursors[cursor] == "year":
            year += adjust
            year = max(year, 2022)
            day = min(day, days_in_month(month, year))
        if cursors[cursor] == "month":
            month += adjust
            month = min(max(month, 1), 12)
            day = min(day, days_in_month(month, year))
        if cursors[cursor] == "day":
            day += adjust
            day = min(max(day, 1), days_in_month(month, year))
        if cursors[cursor] == "hour":
            hour += adjust
            hour %= 24
        if cursors[cursor] == "minute":
            minute += adjust
            minute %= 60
        draw_clock()

def days_in_month(month, year):
    if month == 2 and ((year % 4 == 0 and year % 100 != 0) or year % 400 == 0):
        return 29
    return (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[month - 1]

def draw_clock():
    hms = "{:02}:{:02}".format(hour, minute)
    ymd = "{:02}/{:02}/{:04}".format(day, month, year)
    hms_width = display.measure_text(hms, 1.8)
    hms_offset = int((badger2040.WIDTH / 2) - (hms_width / 2))
    h_width = display.measure_text(hms[0:2], 1.8)
    mi_width = display.measure_text(hms[3:5], 1.8)
    mi_offset = display.measure_text(hms[0:3], 1.8)
    ymd_width = display.measure_text(ymd, 1.0)
    ymd_offset = int((badger2040.WIDTH / 2) - (ymd_width / 2))
    y_width = display.measure_text(ymd[0:4], 1.0)
    m_width = display.measure_text(ymd[5:7], 1.0)
    m_offset = display.measure_text(ymd[0:5], 1.0)
    d_width = display.measure_text(ymd[8:10], 1.0)
    d_offset = display.measure_text(ymd[0:8], 1.0)

    display.set_pen(15)
    display.clear()
    display.set_pen(0)
    display.text(hms, hms_offset, 40, 0, 1.8)
    display.text(ymd, ymd_offset, 100, 0, 1.0)

    if set_clock:
        display.set_pen(0)
        if cursors[cursor] == "year":
            display.line(ymd_offset, 120, ymd_offset + y_width, 120, 4)
        if cursors[cursor] == "month":
            display.line(ymd_offset + m_offset, 120, ymd_offset + m_offset + m_width, 120, 4)
        if cursors[cursor] == "day":
            display.line(ymd_offset + d_offset, 120, ymd_offset + d_offset + d_width, 120, 4)
        if cursors[cursor] == "hour":
            display.line(hms_offset, 70, hms_offset + h_width, 70, 4)
        if cursors[cursor] == "minute":
            display.line(hms_offset + mi_offset, 70, hms_offset + mi_offset + mi_width, 70, 4)

    display.update()

for b in badger2040.BUTTONS.values():
    b.irq(trigger=machine.Pin.IRQ_RISING, handler=button)

year, month, day, wd, hour, minute, second, _ = rtc.datetime()
if (year, month, day) == (2021, 1, 1):
    rtc.datetime((2022, 2, 28, 0, 12, 0, 0, 0))

last_minute = minute
draw_clock()

while True:
    if not set_clock:
        year, month, day, wd, hour, minute, second, _ = rtc.datetime()
        tz_offset = get_timezone_offset(year, month, day, hour, wd)
        hour += tz_offset
        hour %= 24

        if minute != last_minute:
            draw_clock()
            last_minute = minute

    if toggle_set_clock:
        set_clock = not set_clock
        print(f"Set clock changed to: {set_clock}")
        toggle_set_clock = False
        draw_clock()

    time.sleep(10)
