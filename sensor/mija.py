import lvgl as lv
from sensor import sensorBase
from lib.EventObserver import Observer       # type: ignore
from random import randint
from micropython import const
import utime, gc

class UI(Observer, sensorBase):
    def __init__(self, page, sensorMac, sensorTitle, parts, simulate=0):
        gc.collect()
        sensorBase.__init__(self)
        Observer.__init__(self)  # DON'T FORGET THIS for event to work
        self.drawSensor(page, parts, sensorTitle)
        self.observe("tick 1 sec", self.tickClock)

        # self.tbl = None
        if simulate:
            self.updateEach = const(randint(20, 40))
            self.observe("tick 1 sec", self.randomizeTemperature)
        else:
            self.observe("{} payload".format(sensorMac), self.processAdvPayload)
        #     gc.collect()
        #     import lib.mdb as mdb
        #     if not mdb.Database.exist("history"):
        #         db = mdb.Database.create("history", 100)
        #     else:
        #         db = mdb.Database.open("history")

        #     self.last_t = None
        #     self.last_h = None
        #     if not str(sensorMac) in db.list_tables():
        #         self.tbl = db.create_table(
        #             str(sensorMac),
        #             ["ts", "t", "h", "b"]
        #         )
        #     else:
        #         self.tbl = db.open_table(str(sensorMac))


    def drawSensor(self, page, parts, sensorTitle):
        self.sensCont = lv.cont(page)
        self.sensCont.set_drag_parent(True)
        self.sensCont.set_layout(lv.LAYOUT.OFF)
        self.sensCont.set_fit2(lv.FIT.NONE, lv.FIT.TIGHT)
        self.sensCont.set_width(
            page.get_width_grid(parts, 1)
        )

        self.sensCont.set_style_local_pad_all(lv.cont.PART.MAIN, lv.STATE.DEFAULT, 1)

        title = lv.label(self.sensCont)
        title.set_text(sensorTitle)
        title.set_pos(13, 9)
        del title

        t = lv.label(self.sensCont)
        t.set_text("T")
        t.set_pos(10, 22)

        temp_s = lv.img(self.sensCont)
        temp_s.set_drag_parent(True)
        temp_s.set_pos(5, 20)
        temp_s.set_src(
            self.get_img("images/sensor/thermo.png")
        )
        del temp_s

        self.temp_v = lv.label(self.sensCont)
        self.temp_v.set_drag_parent(True)
        self.temp_v.set_text("--.-")
        self.temp_v.set_pos(20, 24)

        hum_s = lv.img(self.sensCont)
        hum_s.set_drag_parent(True)
        hum_s.set_pos(83, 16)
        hum_s.set_src(
            self.get_img("images/sensor/hum.png")
        )
        del hum_s

        self.hum_v = lv.label(self.sensCont)
        self.hum_v.set_drag_parent(True)
        self.hum_v.set_text("--%")
        self.hum_v.set_pos(100, 16)

        batt_s = lv.label(self.sensCont)
        batt_s.set_drag_parent(True)
        batt_s.set_text(lv.SYMBOL.BATTERY_3)
        batt_s.set_pos(80, 33)
        del batt_s

        self.batt_v = lv.label(self.sensCont)
        self.batt_v.set_drag_parent(True)
        self.batt_v.set_text("--%")
        self.batt_v.set_pos(100, 33)

        self.rssi = lv.label(self.sensCont)
        self.rssi.set_drag_parent(True)
        self.rssi.set_text("{} ---".format(lv.SYMBOL.BLUETOOTH))
        self.rssi.set_pos(140, 16)

        self.updValue = lv.label(self.sensCont)
        self.updValue.set_drag_parent(True)
        self.updValue.set_text("{} ---".format(lv.SYMBOL.EYE_CLOSE))
        self.updValue.set_pos(140, 0)

        t.delete()  # created for workaround to make to move temp value to desired location
        del t

    def processAdvPayload(self, payload, rssi):
        self.rssi.set_text("{} {}".format(lv.SYMBOL.BLUETOOTH, rssi))
        self.sensorUpdated()
        if self.lastUpdCount != int(payload[32:34], 16):    # counter from payload

            self.temp_v.set_text(
                "{}{}".format(int(payload[20:24],16)/10, u"\u00B0")
            )        # temp °

            self.hum_v.set_text("{}%".format(int(payload[24:26],16)))
            self.batt_v.set_text("{}%".format(int(payload[26:28],16)))
            self.lastUpdCount = int(payload[32:34], 16)


    def randomizeTemperature(self, evt):
        if divmod(int(utime.time() - self.lastUpdTime), self.updateEach)[0] > 0:
            self.temp_v.set_text(str(
                randint(150, 350) / 10
            ))
            self.sensorUpdated()
