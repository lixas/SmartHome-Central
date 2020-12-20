import lvgl as lv
from sensor import sensorBase
from lib.EventObserver import Observer          # type: ignore
import lib.urequests as req, gc, json, os       # type: ignore
from math import floor, ceil

gc.collect()


class UI(Observer, sensorBase):
    def __init__(self, page, sensorMac, sensorTitle, parts, simulate=0):
        gc.collect()
        sensorBase.__init__(self)
        Observer.__init__(self)  # DON'T FORGET THIS for event to work
        # self.sensorTitle = sensorTitle
        with open('settings.json', 'r') as f:
            self.apikey = json.loads(f.read())["apikey"]["openweather"]

        self.drawSensor(page, parts, sensorTitle)
        self.observe("tick 1 sec", self.tickClock)
        self.observe("Reload current weather", self.reloadData)

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

        self.cond_s = lv.img(sensCont)
        self.cond_s.set_drag_parent(True)
        self.cond_s.set_pos(55, 10)

        self.cond_t = lv.label(sensCont)
        self.cond_t.set_drag_parent(True)
        self.cond_t.set_text("Condition")
        self.cond_t.set_pos(15, 35)

        wind_s = lv.img(sensCont)
        wind_s.set_drag_parent(True)
        wind_s.set_pos(93, 5)
        wind_s.set_src(
            self.get_img("images/sensor/wind.png")
        )
        del wind_s

        self.wind_v = lv.label(sensCont)
        self.wind_v.set_drag_parent(True)
        self.wind_v.set_text("--")
        self.wind_v.set_pos(110, 4)

        self.today_v = lv.label(sensCont)
        self.today_v.set_drag_parent(True)
        self.today_v.set_text("--- / --")
        self.today_v.set_pos(140, 4)

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

        self.uv_v = lv.label(sensCont)
        self.uv_v.set_drag_parent(True)
        self.uv_v.set_text("---")
        self.uv_v.set_pos(157, 21)

        self.updValue = lv.label(sensCont)
        self.updValue.set_text("{} ---".format(lv.SYMBOL.EYE_CLOSE))
        self.updValue.set_pos(137, 38)

        t.delete()  # created for workaround to make to move temp value to desired location
        del t

    def reloadData(self):
        gc.collect()
        r = req.get("http://api.openweathermap.org/data/2.5/onecall?lat=54.69&lon=25.28&units=metric&exclude=minutely,hourly,alerts&appid={}".format(self.apikey))
        if r.status_code == 200:
            try:
                weather = r.json()
            except:
                self.cond_t.set_text("Err: json parse")
                return

            r.close()
            del r
            gc.collect()

            self.temp_v.set_text(
                "{}{}".format(round(weather.get("current").get("temp")*10)/10, u"\u00B0")
            )
            self.wind_v.set_text(str(round(weather["daily"][0]["wind_speed"]*10)/10))
            self.uv_v.set_text(str(round(weather["daily"][0]["uvi"]*10)/10))
            self.cond_t.set_text(str(weather["current"]["weather"][0]["main"]))
            self.today_v.set_text(
                "{}{} / {}{}".format(floor(weather["daily"][0]["temp"]["min"]), u"\u00B0", ceil(weather["daily"][0]["temp"]["max"]),u"\u00B0")
            )

            cond_img = "{}.png".format(weather["current"]["weather"][0]["icon"])
            if cond_img in os.listdir("images/condition/") :  # only known icons
                self.cond_s.set_src(
                    self.get_img("images/condition/{}".format(cond_img))
                )
            else:
                print("Unknown condition file ", cond_img)
                self.cond_t.set_text(cond_img)
                self.cond_s.set_src(
                    self.get_img("images/condition/empty.png")
                )
            del cond_img

            # rain = weather["daily"][0]["rain"] if "rain" in weather["daily"][0] else 0
            rain = weather.get("daily")[0].get("rain") or 0
            # snow = weather["daily"][0]["snow"] if "snow" in weather["daily"][0] else 0
            snow = weather.get("daily")[0].get("snow") or 0
            if( rain>0 or snow>0):
                self.rain_v.set_text(str(round((rain+snow)*10)/10))
            else:
                self.rain_v.set_text("0")

            self.sensorUpdated()
            gc.collect()
        else:
            self.cond_t.set_text("Err: HTTP {}".format(r.status_code))
            r.close()
            del r
            gc.collect()


