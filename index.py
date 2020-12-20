import lvgl as lv  # noqa: E402
from lib.EventObserver import Event, Observer       # type: ignore
import pages.home
import machine, random, os, json, gc, micropython, network, time, ubinascii  # noqa E401
import lib.ntptime2, lib.mqtt       # type: ignore


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

gc.collect()

# lvgl must be initialized before any lvgl function is called or object/struct is constructed!
lv.init()

# make randomizer be random
random.seed(os.urandom(32)[0] % (1 << 32))


timer_1s = machine.Timer(0)
timer_1s.init(period=1000, mode=machine.Timer.PERIODIC, callback=lambda t: Event('tick 1 sec', None))


class page_controls:

    def __init__(self, app, page):
        self.app = app
        self.page = page

        CtrlBasicContainer = lv.cont(page)
        CtrlBasicContainer.set_layout(lv.LAYOUT.PRETTY_MID)
        # CtrlBasicContainer.add_style(lv.cont.PART.MAIN, ContainerStyle())
        CtrlBasicContainer.set_drag_parent(True)
        CtrlBasicContainer.align(page, lv.ALIGN.IN_TOP_LEFT, 10, 30)

        CtrlBasicContainer.set_style_local_value_str(lv.cont.PART.MAIN, lv.STATE.DEFAULT, "Basics")
        CtrlBasicContainer.set_fit2(lv.FIT.NONE, lv.FIT.TIGHT)
        CtrlBasicContainer.set_width(
            page.get_width_grid(17, 17)
        )

        btn1 = lv.btn(CtrlBasicContainer)
        btn1.set_fit2(lv.FIT.NONE, lv.FIT.TIGHT)
        lbl1 = lv.label(btn1)
        lbl1.set_text("Button1")

        btn2 = lv.btn(CtrlBasicContainer)
        btn2.toggle()
        lbl2 = lv.label(btn2)
        lbl2.set_text("Button2")

        CtrlCont1 = lv.cont(CtrlBasicContainer)
        CtrlCont1.set_width(CtrlBasicContainer.get_width_fit())
        CtrlCont1.set_layout(lv.LAYOUT.PRETTY_MID)
        # CtrlCont1.add_style(lv.cont.PART.MAIN, ContainerStyle())
        CtrlCont1.set_fit2(lv.FIT.NONE, lv.FIT.TIGHT)

        sw1 = lv.switch(CtrlCont1)  # noqa F841

        cb1 = lv.checkbox(CtrlCont1)
        cb1.set_text("Check Box 1")

        sl1 = lv.slider(CtrlBasicContainer)
        sl1.set_event_cb(self.slider_event_cb)
        sl1.set_value(40, lv.ANIM.OFF)
        sl1.set_width_margin(
            CtrlBasicContainer.get_width_fit()
        )
        sl1.set_style_local_value_ofs_x(lv.slider.PART.BG, lv.STATE.DEFAULT, 20)

        sl2 = lv.slider(CtrlBasicContainer)
        sl2.set_event_cb(self.slider_event_cb)
        sl2.set_type(lv.slider.TYPE.RANGE)
        sl2.set_value(70, lv.ANIM.OFF)
        sl2.set_left_value(30, lv.ANIM.OFF)
        if sl2.get_width() > CtrlBasicContainer.get_width_fit():
            sl2.set_width(CtrlBasicContainer.get_width_fit())

        sl2.set_width_margin(
            CtrlBasicContainer.get_width_fit()
        )

        CtrlTextContainer = lv.cont(page)
        CtrlTextContainer.set_layout(lv.LAYOUT.PRETTY_MID)
        # CtrlTextContainer.add_style(lv.cont.PART.MAIN, ContainerStyle())
        CtrlTextContainer.set_drag_parent(True)
        CtrlTextContainer.align(page, lv.ALIGN.IN_TOP_RIGHT, -1 * CtrlTextContainer.get_width() - 80, 30)

        CtrlTextContainer.set_style_local_value_str(lv.cont.PART.MAIN, lv.STATE.DEFAULT, "Text Input")
        CtrlTextContainer.set_fit2(lv.FIT.NONE, lv.FIT.TIGHT)
        CtrlTextContainer.set_width(
            page.get_width_grid(17, 17)
        )

        self.te1 = lv.textarea(CtrlTextContainer)
        self.te1.set_text("")
        self.te1.set_width(int(CtrlTextContainer.get_width() * 0.9))
        self.te1.set_placeholder_text("E-mail address")
        self.te1.set_one_line(True)
        self.te1.set_cursor_hidden(True)
        self.te1.set_event_cb(self.ta_event_cb)

        te2 = lv.textarea(CtrlTextContainer)
        te2.set_text("")
        te2.set_width(int(CtrlTextContainer.get_width() * 0.9))
        te2.set_placeholder_text("Password")
        te2.set_pwd_mode(True)
        te2.set_one_line(True)
        te2.set_cursor_hidden(True)
        te2.set_event_cb(self.ta_event_cb)

        self.te3 = lv.textarea(CtrlTextContainer)
        self.te3.set_text("")
        self.te3.set_width(int(CtrlTextContainer.get_width() * 0.9))
        self.te3.set_placeholder_text("Message")
        self.te3.set_cursor_hidden(True)
        self.te3.set_event_cb(self.ta_event_cb)

    # Slider event value
    def slider_event_cb(self, obj, evt):
        if evt == lv.EVENT.VALUE_CHANGED:
            if obj.get_type() == lv.slider.TYPE.NORMAL:
                obj.set_style_local_value_str(
                    lv.slider.PART.KNOB,
                    lv.STATE.DEFAULT,
                    str(obj.get_value())
                )
            else:
                obj.set_style_local_value_str(
                    lv.slider.PART.INDIC,
                    lv.STATE.DEFAULT,
                    "{}-{}".format(obj.get_left_value(), obj.get_value())
                )

    # Text Area event handler
    def ta_event_cb(self, obj, evt):
        def kb_event_cb(ko, ke):
            ko.def_event_cb(ke)
            if ke == lv.EVENT.CANCEL:
                ko.delete()
            if ke == lv.EVENT.APPLY:
                print("Užskaitom")

        if evt == lv.EVENT.RELEASED:
            kb = lv.keyboard(lv.scr_act())
            obj.set_cursor_hidden(False)
            kb.set_textarea(obj)
            kb.set_event_cb(kb_event_cb)

        elif evt == lv.EVENT.DEFOCUSED:
            obj.set_cursor_hidden(True)


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
        self.clock.set_pos(170, 3)
        self.clock.set_text("Updating...")

        Observer.__init__(self)  # DON'T FORGET THIS for events to work
        self.observe("tick 1 sec", self.update_clock_on_screen)

    @micropython.native
    def update_clock_on_screen(self, evt):
        rtc = machine.RTC().datetime()
        h = rtc[4]
        m = rtc[5]
        s = rtc[6]

        if h in range(0, 10):
            timeStr = "0{}:".format(h)
        else:
            timeStr = "{}:".format(h)

        if m in range(0, 10):
            timeStr = "{}0{}:".format(timeStr, m)
        else:
            timeStr = "{}{}:".format(timeStr, m)

        if s in range(0, 10):
            timeStr = "{}0{}".format(timeStr, s)
        else:
            timeStr = "{}{}".format(timeStr, s)

        self.clock.set_text(timeStr)


class page_settings(Observer):
    def __init__(self, app, page):
        self.app = app
        self.page = page

        self.c1 = lv.cont(self.page)
        self.c1.set_drag_parent(True)
        # self.c1.add_style(lv.cont.PART.MAIN, ContainerPageStyle())
        self.c1.set_layout(lv.LAYOUT.PRETTY_TOP)
        self.c1.set_fit2(lv.FIT.PARENT, lv.FIT.MAX)

        Observer.__init__(self)  # DON'T FORGET THIS for events to work
        self.observe("Settings draw all containers", self.draw_all_containers)

    def draw_all_containers(self):
        self.draw_display_container()
        self.forget("Settings draw all containers")

    def draw_display_container(self):
        global global_settings
        dispCont = lv.cont(self.c1)
        dispCont.set_drag_parent(True)
        dispCont.set_layout(lv.LAYOUT.PRETTY_TOP)
        dispCont.set_fit2(lv.FIT.NONE, lv.FIT.TIGHT)
        dispCont.set_width(self.c1.get_width_grid(1, 1))
        dispCont.set_style_local_pad_all(lv.cont.PART.MAIN, lv.STATE.DEFAULT, 1)

        lv.label(dispCont).set_text("Display Brightness")

        screen_brightnes_slider = lv.slider(dispCont)
        screen_brightnes_slider.set_range(1, 512)
        screen_brightnes_slider.set_anim_time(0)
        screen_brightnes_slider.set_value(global_settings["screen_brightness"], lv.ANIM.OFF)
        screen_brightnes_slider.set_event_cb(self.on_screen_brightnes_slider)
        screen_brightnes_slider.set_width(dispCont.get_width_grid(20, 19))
        del screen_brightnes_slider

        lv.label(dispCont).set_text("Turn screen off after")

        screen_timeout_roler_map = {
            1: [15, "15 sec"],
            2: [30, "30 sec"],
            3: [60, "1 min"],
            4: [120, "2 min"],
            5: [300, "5 min"],
            6: [600, "10 min"],
            10: [-1, "Never"]
        }

        tmp_map = []
        value_to_find = global_settings["light_time_out"]
        value_index = None
        a = 0

        for k in sorted(screen_timeout_roler_map):
            if value_to_find == screen_timeout_roler_map[k][0] and value_index is None:
                value_index = a
            tmp_map.append(screen_timeout_roler_map[k][1])
            a += 1

        screen_timeout_roler = lv.roller(dispCont)
        screen_timeout_roler.set_anim_time(0)
        screen_timeout_roler.set_options("\n".join(map(str, tmp_map)), lv.roller.MODE.NORMAL)
        screen_timeout_roler.set_visible_row_count(3)
        if value_index:
            screen_timeout_roler.set_selected(value_index, lv.ANIM.OFF)
        screen_timeout_roler.set_event_cb(self.on_screen_timeout_roler)

        del tmp_map, value_index, value_to_find, a, dispCont

    def on_screen_brightnes_slider(self, o, e):
        if e == lv.EVENT.VALUE_CHANGED:
            # pwm2.duty(o.get_value())
            pass
        elif e == lv.EVENT.RELEASED:
            global_settings["screen_brightness"] = o.get_value()

    def on_screen_timeout_roler(self, o, e):
        if e == lv.EVENT.RELEASED:
            print("selected", o.get_selected())

class page_weather:
    def __init__(self, app, page):
        # self.app = app
        # self.page = page

        # c1 = lv.cont(page)
        # c1.set_drag_parent(True)
        # c1.add_style(lv.cont.PART.MAIN, ContainerPageStyle())
        # c1.set_layout(lv.LAYOUT.PRETTY_TOP)
        # c1.set_fit2(lv.FIT.PARENT, lv.FIT.MAX)
        # c1.set_width(page.get_width())

        self.forecast(page)
    
    def forecast(self, c1):
        parts = 1
        sensCont = lv.cont(c1)
        sensCont.set_drag_parent(True)
        # sensCont.add_style(lv.cont.PART.MAIN, ContainerPageStyle())
        sensCont.set_layout(lv.LAYOUT.OFF)
        sensCont.set_fit2(lv.FIT.NONE, lv.FIT.TIGHT)
        sensCont.set_width(
            c1.get_width_grid(parts, 1)
        )
        sensCont.set_style_local_pad_all(lv.cont.PART.MAIN, lv.STATE.DEFAULT, 1)

        title = lv.label(sensCont)
        title.set_text("Prognoze")
        title.set_pos(13, 9)



class screen_main(lv.obj):

    def tabview_event(self, o, e):
        if e == lv.EVENT.VALUE_CHANGED:
            if o.get_tab_act() == 1:
                Event("Settings draw all containers")
            print(o.get_tab_act())

    def __init__(self, app, *args, **kwds):
        self.app = app
        super().__init__(*args, **kwds)
        # self.theme = AdvancedDemoTheme()

        _tabview = lv.tabview(self)
        _tabview.set_btns_pos(lv.tabview.TAB_POS.LEFT)
        # _tabview.set_anim_time(0)
        _tabview.set_style_local_pad_top(lv.tabview.PART.TAB_BG, lv.STATE.DEFAULT, 20)
        _tabview.set_style_local_pad_right(lv.tabview.PART.TAB_BG, lv.STATE.DEFAULT, 10)
        _tabview.set_event_cb(self.tabview_event)

        tray_clock(self)

        pages.home.ui(self.app, _tabview.add_tab(lv.SYMBOL.HOME))
        # page_weather(self.app, _tabview.add_tab("W"))
        # page_settings(self.app, _tabview.add_tab(lv.SYMBOL.SETTINGS))


        self.mbox = lv.msgbox(lv.scr_act())
        self.mbox.set_text("Initializing...")
        self.mbox.set_text("Updating clock from NTP")
        lib.ntptime2.settime(global_settings["gmt"])
        # self.mbox.align(None, lv.ALIGN.CENTER, 0, 0)
        self.first_sequence_event("Drawing sensors...")
        Event("Draw sensors")
        self.first_sequence_event("Loading weather...")
        Event("Reload current weather")
        self.first_sequence_event("Done! All set.")
        self.mbox.start_auto_close(500)
        print("Done! All set.")
        del self.mbox

    def first_sequence_event(self, evt_text):
        self.mbox.set_text("{} \n {}".format(self.mbox.get_text(), evt_text) )
        self.mbox.align(None, lv.ALIGN.IN_TOP_LEFT, 0, 0)

class Application(Observer):
    def __init__(self):
        Observer.__init__(self)  # DON'T FORGET THIS for events to work
        self.observe("TouchEvent", self.touchevt)
        self.observe("tick 1 sec", self.turn_screen_off)
        self.lcd = 1
        self.lcd_time = time.time() + global_settings["screen"]["time"]

    def init_gui_esp32(self):
        # Initialize ILI9341 display
        from lib.drivers.ili9XXX import ili9341, ROTATE_180     # type: ignore

        # self.disp = ili9341(
        #     miso=19, mosi=23, clk=18, cs=26, dc=27, rst=33, backlight=32, power=-1, power_on=-1, backlight_on=1,
        #     mhz=40, factor=16, hybrid=True, double_buffer=False, spihost=1,
        #     rot=ROTATE_180
        # )

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
                brightness.duty(global_settings["screen"]["down"])
                self.lcd = 0

gc.collect()
brightness = machine.PWM(machine.Pin(32), freq=20000, duty=global_settings["screen"]["bright"])  # create and configure in one go

Application().init_gui()


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
    lv.task_create(mqtt_checker, 200, lv.TASK_PRIO.HIGH, None)
)

lv.task_enable(
    lv.task_create(lambda t: Event('Reload current weather'), 1000*60*10, lv.TASK_PRIO.HIGH, None)
)

lv.task_enable(
    lv.task_create(lambda t: lib.ntptime2.settime(global_settings["gmt"]), 1000*60*60*24, lv.TASK_PRIO.HIGH, None)
)