import lvgl as lv  # noqa: E402
from lib.EventObserver import Event, Observer       # type: ignore
import pages.home, pages.weather                    # type: ignore
import machine, random, io, os, json, gc, micropython, network, time, ubinascii  # noqa E401
import lib.ntptime2, lib.mqtt       # type: ignore
# from pages.styles import ContainerPageStyle


gc.collect()
with open('settings.json', 'r') as f:
    global_settings = json.loads(f.read())

gc.collect()
sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print("Connecting to WiFi...")
    sta_if.active(True)
    sta_if.connect(global_settings["wifi"]["ssid"], global_settings["wifi"]["pass"])
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
print(".")
print("Connected")
print('network config:', sta_if.ifconfig())

gc.collect()

# lvgl must be initialized before any lvgl function is called or object/struct is constructed!
lv.init()

# make randomizer be random
random.seed(os.urandom(32)[0] % (1 << 32))


timer_1s = machine.Timer(0)
timer_1s.init(period=1000, mode=machine.Timer.PERIODIC, callback=lambda t: Event('tick 1 sec', None))


class Page_Empty:
    def __init__(self, app, page):
        self.app = app
        self.page = page


class tray_clock(Observer):
    def __init__(self, parent):
        bar = lv.cont(parent)
        bar.set_width(240)
        bar.set_height(20)
        bar.set_style_local_border_width(lv.cont.PART.MAIN, lv.STATE.DEFAULT, 0)
        bar.set_style_local_bg_opa(lv.cont.PART.MAIN, lv.STATE.DEFAULT, lv.OPA.COVER)
        bar.set_style_local_bg_color(lv.cont.PART.MAIN, lv.STATE.DEFAULT, lv.color_hex3(0xFFF))

        self.clock = lv.label(bar)
        self.clock.set_pos(100, 2)
        self.clock.set_text("Updating...")
        # self.clock.set_align(lv.label.ALIGN.RIGHT)

        Observer.__init__(self)  # DON'T FORGET THIS for events to work
        self.observe("tick 1 sec", self.update_clock_on_screen)

    def update_clock_on_screen(self, evt):
        rtc = machine.RTC().datetime()

        self.clock.set_text(
            "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                rtc[0],         # year
                rtc[1],         # month
                rtc[2],         # day
                rtc[4],         # hour
                rtc[5],         # minute
                rtc[6]          # second
            )
        )


class screen_main(lv.obj):

    def tabview_event(self, o, e):
        if e == lv.EVENT.VALUE_CHANGED:
            if o.get_tab_act() == 1:
                Event("Settings draw all containers")
            print(o.get_tab_act())

    def __init__(self, app, *args, **kwds):
        self.app = app
        gmt = global_settings["gmt"]
        super().__init__(*args, **kwds)

        # Observer.__init__(self)  # DON'T FORGET THIS for events to work
        # Observer.observe("Startup sequence", self.on_startup_sequence_event)
        # self.theme = AdvancedDemoTheme()

        tabview = lv.tabview(self)
        tabview.set_btns_pos(lv.tabview.TAB_POS.LEFT)
        tabview.set_anim_time(0)
        tabview.set_style_local_pad_top(lv.tabview.PART.TAB_BG, lv.STATE.DEFAULT, 20)
        tabview.set_style_local_pad_right(lv.tabview.PART.TAB_BG, lv.STATE.DEFAULT, 10)
        # _tabview.set_event_cb(self.tabview_event)
        tray_clock(self)

        pages.home.ui(self.app, tabview.add_tab(lv.SYMBOL.HOME))
        pages.weather.ui(self.app, tabview.add_tab("W"), gmt)
        # pages.home.ui(self.app, tabview.add_tab(lv.SYMBOL.HOME))


        self.mbox = lv.msgbox(lv.scr_act())
        self.mbox.set_text("Initializing...")
        self.mbox.set_text("Updating clock from NTP...")
        lib.ntptime2.settime(gmt)
        # self.mbox.align(None, lv.ALIGN.CENTER, 0, 0)
        self.on_startup_sequence_event("Drawing sensors...")
        Event("Draw sensors")
        self.on_startup_sequence_event("Loading weather data...")
        Event('Reload weather')
        self.on_startup_sequence_event("Done! All set.")
        self.mbox.start_auto_close(1500)
        print("Done! All set.")
        # Observer.forget("Startup sequence")
        del self.mbox

    def on_startup_sequence_event(self, evt_text):
        self.mbox.set_text("{} \n {}".format(self.mbox.get_text(), evt_text) )
        self.mbox.align(None, lv.ALIGN.IN_TOP_LEFT, 0, 0)

class Hardware(Observer):
    def __init__(self):
        Observer.__init__(self)  # DON'T FORGET THIS for events to work
        self.observe("TouchEvent", self.touchevt)
        self.observe("tick 1 sec", self.turn_screen_off)
        self.lcd = 1
        self.lcd_time = time.time() + global_settings["screen"]["time"]

    def init_gui_esp32(self):
        # Initialize ILI9341 display
        from lib.drivers.ili9XXX import ili9341, ROTATE_180     # type: ignore

        self.disp = ili9341(
            miso=19, mosi=23, clk=18, cs=26, dc=27, rst=33, backlight=-1, power=-1, power_on=-1,
            mhz=40, factor=16, hybrid=True, double_buffer=False, spihost=1, rot=ROTATE_180
        )

        '''
        SCLK_1 (GPIO14) <-->	CLK
        CS_1 (GPIO15)   <-->	CS
        MOSI_1 (GPIO13) <-->	DIN
        MISO_1 (GPIO12) <-->	DO
        GPIO33      	<-->	IRQ
        '''
        # Register xpt2046 touch driver
        from lib.drivers.xpt2046 import xpt2046     # type: ignore
        self.touch = xpt2046(spihost=2, miso=12, mosi=13, clk=14, cs=15, mhz=2, transpose=True, invert_x=False, invert_y=True)      # 180
        # self.touch = xpt2046(spihost=2, miso=12, mosi=13, clk=14, cs=15, mhz=2, transpose=True, invert_x=True, invert_y=False)      # 0

    def init_gui(self):
        self.init_gui_esp32()
        # Create the main screen and load it.
        self.screen_main = screen_main(self)
        lv.scr_load(self.screen_main)

    def touchevt(self):
        brightness.duty(global_settings["screen"]["bright"])
        self.lcd = 1
        self.lcd_time = time.time() + global_settings["screen"]["time"]

    def turn_screen_off(self, timer):
        if self.lcd:
            if time.time() > self.lcd_time:
                brightness.duty(global_settings["screen"]["dim"])
                self.lcd = 0

gc.collect()
brightness = machine.PWM(machine.Pin(global_settings["screen"]["pin"]), freq=20000, duty=global_settings["screen"]["bright"])  # create and configure in one go

Hardware().init_gui()


def mqtt_checker(data=None):
    try:
        mqtt.check_msg()
    except:
        machine.reset()

def mqtt_evt(topic, msg):
    try:
        msg = json.loads(msg)
        Event(
            "{} payload".format(topic.decode("utf-8").split("/")[-1]),
            msg["payload"],
            msg["rssi"]
        )
    except:
        pass

mqtt = lib.mqtt.MQTTClient("Central-".format(str(ubinascii.hexlify(machine.unique_id()))), global_settings["mqtt"]["broker"])
mqtt.set_callback(mqtt_evt)
mqtt.connect()
mqtt.subscribe("{}#".format(global_settings["mqtt"]["base"]))


lv.task_enable(
    lv.task_create(mqtt_checker, 300, lv.TASK_PRIO.HIGH, None)      # 0.3s
)

lv.task_enable(
    lv.task_create(lambda t: Event('Reload weather'), 1000*60*15, lv.TASK_PRIO.HIGHEST, None)      # 15m
)

lv.task_enable(
    lv.task_create(lambda t: lib.ntptime2.settime(global_settings["gmt"]), 1000*60*60*24, lv.TASK_PRIO.HIGHEST, None)      # 24h
)

class logToFile(io.IOBase):
    def __init__(self):
        pass

    def write(self, data):
        with open("logfile", mode="a") as f:
            f.write(data)
        return len(data)
# os.dupterm(logToFile())