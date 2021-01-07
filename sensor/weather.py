import lvgl as lv
from sensor import sensorBase
from lib.EventObserver import Observer          # type: ignore
import gc, os       # type: ignore
from math import floor, ceil

gc.collect()


class UI(Observer, sensorBase):
    def __init__(self, page, sensorMac, sensorTitle, parts, simulate=0):
        gc.collect()
        sensorBase.__init__(self)
        Observer.__init__(self)  # DON'T FORGET THIS for event to work

        self.drawSensor(page, parts, sensorTitle)
        self.observe("tick 1 sec", self.tickClock)
        self.observe("Sensor weather", self.loadData)

        self.angle = 0

    def drawSensor(self, page, parts, sensorTitle):
        sensCont = lv.cont(page)
        sensCont.set_drag_parent(True)
        sensCont.set_layout(lv.LAYOUT.OFF)
        sensCont.set_fit2(lv.FIT.NONE, lv.FIT.TIGHT)
        sensCont.set_width(
            page.get_width_grid(parts, 1)
        )
        sensCont.set_style_local_pad_all(lv.cont.PART.MAIN, lv.STATE.DEFAULT, 0)

        title = lv.label(sensCont)
        title.set_text(sensorTitle)
        title.set_pos(13, 9)

        t = lv.label(sensCont)
        t.set_text("T")
        t.set_pos(10, 22)

        temp_s = lv.img(sensCont)
        temp_s.set_drag_parent(True)
        temp_s.set_pos(5, 14)
        temp_s.set_src(
            self.get_img("images/sensor/thermo.png")
        )
        del temp_s

        self.temp_v = lv.label(sensCont)
        self.temp_v.set_drag_parent(True)
        self.temp_v.set_text("--.-")
        self.temp_v.set_pos(20, 18)

        self.cond_i = lv.img(sensCont)
        self.cond_i.set_drag_parent(True)
        self.cond_i.set_pos(55, 10)

        self.cond = lv.label(sensCont)
        self.cond.set_drag_parent(True)
        self.cond.set_text("Condition")
        self.cond.set_pos(15, 35)

        wind_s = lv.img(sensCont)
        wind_s.set_drag_parent(True)
        wind_s.set_pos(93, 38)
        wind_s.set_src(
            self.get_img("images/sensor/wind.png")
        )
        del wind_s

        self.wind_v = lv.label(sensCont)
        self.wind_v.set_drag_parent(True)
        self.wind_v.set_text("-- m/s")
        self.wind_v.set_pos(110, 37)

        self.wind_dir = lv.img(sensCont)
        self.wind_dir.set_drag_parent(True)
        self.wind_dir.set_pos(165, 38)
        self.wind_dir.set_src(
            self.get_img("images/sensor/direction.png")
        )
        self.wind_dir.set_pivot(7, 7)

        # self.today_v = lv.label(sensCont)
        # self.today_v.set_drag_parent(True)
        # self.today_v.set_text("--- / --")
        # self.today_v.set_pos(93, 37)

        rain_s = lv.img(sensCont)
        rain_s.set_drag_parent(True)
        rain_s.set_pos(93, 21)
        rain_s.set_src(
            self.get_img("images/sensor/rain.png")
        )
        del rain_s

        self.rain_v = lv.label(sensCont)
        self.rain_v.set_drag_parent(True)
        self.rain_v.set_text("--")
        self.rain_v.set_pos(110, 21)

        uv_s = lv.img(sensCont)
        uv_s.set_drag_parent(True)
        uv_s.set_pos(140, 21)
        uv_s.set_src(
            self.get_img("images/sensor/uv.png")
        )
        del uv_s

        self.uv = lv.label(sensCont)
        self.uv.set_drag_parent(True)
        self.uv.set_text("---")
        self.uv.set_pos(157, 21)

        self.updValue = lv.label(sensCont)
        self.updValue.set_text("00:00")
        self.updValue.set_pos(140, 1)
        self.updValue.set_width(20)
        self.updValue.set_align(lv.label.ALIGN.RIGHT)

        t.delete()  # created for workaround to make to move temp value to desired location
        del t

    def loadData(self, current):
        self.temp_v.set_text(
            "{:.1f}{}".format(current.get("temp"), u"\u00B0")
        )
        self.wind_v.set_text("{:.1f} m/s".format(current.get("wind_speed")))
        self.wind_dir.set_angle( -self.angle + current.get("wind_deg")*10)
        self.angle = current.get("wind_deg")*10
        self.uv.set_text("{:.1f}".format(current.get("uvi")))
        self.cond.set_text("{}".format(current["weather"][0]["main"]))
        # self.today_v.set_text(
        #     "{}{} / {}{}".format(floor(today["temp"]["min"]), u"\u00B0", ceil(today["temp"]["max"]),u"\u00B0")
        # )

        cond_img = "{}.png".format(current["weather"][0]["icon"])
        if cond_img in os.listdir("images/condition/") :  # only known icons
            self.cond_i.set_src(
                self.get_img("images/condition/{}".format(cond_img))
            )
        else:
            print("Unknown condition file ", cond_img)
            self.cond.set_text(cond_img)
            self.cond_i.set_src(
                self.get_img("images/condition/unknown.png")
            )
        del cond_img

        rain = current.get("rain").get("1h") if "rain" in current else 0
        snow = current.get("snow").get("1h") if "snow" in current else 0
        if( rain>0 or snow>0):
            self.rain_v.set_text("{:.1f}".format(rain+snow))
        else:
            self.rain_v.set_text("0")

        self.sensorUpdated()
        gc.collect()
