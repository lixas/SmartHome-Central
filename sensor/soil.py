import lvgl as lv
# from pages.styles import ContainerStyle
from sensor import sensorBase
# from sensor.styles import ContainerNoBorderStyle
from lib.EventObserver import Observer       # type: ignore
from micropython import const
import random, utime


class UI(Observer, sensorBase):
    def __init__(self, page, sensorMac, sensorTitle, parts, simulate=0):
        sensorBase.__init__(self)
        Observer.__init__(self)  # DON'T FORGET THIS for event to work

        self.drawSensor(page, parts, sensorTitle)
        self.observe("tick 1 sec", self.tickClock)

        if simulate:
            self.updateEach = const(random.randint(20, 40))
            self.observe("tick 1 sec", self.randomizeHumidity)
        else:
            
            self.observe("{} payload".format(sensorMac), self.processAdvPayload)

    def drawSensor(self, page, parts, sensorTitle):
        sens_c = lv.cont(page)
        sens_c.set_drag_parent(True)
        sens_c.set_layout(lv.LAYOUT.OFF)
        sens_c.set_fit2(lv.FIT.NONE, lv.FIT.TIGHT)
        sens_c.set_width(
            page.get_width_grid(parts, 1)
        )

        sens_c.set_style_local_pad_all(lv.cont.PART.MAIN, lv.STATE.DEFAULT, 1)

        title = lv.label(sens_c)
        title.set_text(sensorTitle)
        title.set_pos(10, 9)

        t = lv.label(sens_c)
        t.set_text("T")
        t.set_pos(10, 15)

        self.hum_b = lv.bar(sens_c)
        self.hum_b.set_drag_parent(True)
        self.hum_b.set_size(sens_c.get_width_grid(10, 9), 10)
        self.hum_b.set_style_local_margin_top(lv.cont.PART.MAIN, lv.STATE.DEFAULT, 5)
        self.hum_b.set_value(73, lv.ANIM.ON)
        self.hum_b.set_pos(10, 27)

        batt_s = lv.label(sens_c)
        batt_s.set_drag_parent(True)
        batt_s.set_text(lv.SYMBOL.BATTERY_3)
        batt_s.set_pos(10, 37)
        del batt_s

        self.batt_v = lv.label(sens_c)
        self.batt_v.set_drag_parent(True)
        self.batt_v.set_text("-- %")
        self.batt_v.set_pos(30, 37)

        self.rssi = lv.label(sens_c)
        self.rssi.set_drag_parent(True)
        self.rssi.set_text("{} ---".format(lv.SYMBOL.BLUETOOTH))
        self.rssi.set_pos(80, 37)

        self.updValue = lv.label(sens_c)
        self.updValue.set_text("{} ---".format(lv.SYMBOL.EYE_CLOSE))
        self.updValue.set_pos(140, 0)

        t.delete()  # created for workaround to make to move temp value to desired location
        del t

    def processAdvPayload(self, payload):
        print("Soil ", payload)
        # print('Tmp:{} Hum:{} Bat:{} @ {}mV Pck:{}'.format(
        #     int(payload[20:24], 16) / 10,
        #     int(payload[24:26], 16),
        #     int(payload[26:28], 16),
        #     int(payload[28:32], 16),
        #     int(payload[32:34], 16)
        # ))

    def randomizeHumidity(self, evt):
        if divmod(int(utime.time() - self.lastUpdTime), self.updateEach)[0] > 0:
            self.hum_b.set_value(random.randint(0, 100), lv.ANIM.ON)
            self.sensorUpdated()
