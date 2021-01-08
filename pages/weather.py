import lvgl as lv
from pages.styles import ContainerPageStyle         # type: ignore
from pages import pageBase
from lib.EventObserver import Observer, Event       # type: ignore
from math import floor, ceil    
from time import localtime
import json, gc, os, lib.urequests as req               # type: ignore

weekday_name= ["Pirmadienis", "Antradienis", "Treciadienis", "Ketvirtadienis", "Penktadienis", "Sestadienis", "Sekmadienis"]

class ui(Observer, pageBase):
    def __init__(self, app, page):
        self.delta = 946684800 - 3600*2      # (timestamp + gmt)
        Observer.__init__(self)  # DON'T FORGET THIS for event to work
        pageBase.__init__(self)
        self.observe("Reload weather", self.get_weather_data)
        with open('settings.json', 'r') as f:
            self.apikey = json.loads(f.read())["apikey"]["openweather"]

        c1 = lv.cont(page)
        c1.set_drag_parent(True)
        c1.add_style(lv.cont.PART.MAIN, ContainerPageStyle())
        c1.set_layout(lv.LAYOUT.PRETTY_TOP)
        c1.set_fit2(lv.FIT.PARENT, lv.FIT.MAX)
        c1.set_width(page.get_width())

        for i in range(7):
            day_container(c1, i)
    
    def get_weather_data(self):
        gc.collect()
        r = req.get("http://api.openweathermap.org/data/2.5/onecall?lat=54.69&lon=25.28&units=metric&exclude=minutely,hourly,alerts&appid={}".format(self.apikey))
        if r.status_code == 200:
            # try:
            resp = r.json()
            r.close()

            Event("Sensor weather", resp["current"])      # curent conditions
            for i in range(7):
                day = resp["daily"][i]
                weekday = divmod(localtime()[6]+i, 7)[1]
                tmp = {"min":floor(day["temp"]["min"]), "max":ceil(day["temp"]["max"])}
                sun = {"rise":day["sunrise"]-self.delta, "set":day["sunset"]-self.delta}   # sunrise/set
                wnd = {"dir":day["wind_deg"], "spd":round(day["wind_speed"]*10)/10}
                cnd = {"img":day["weather"][0]["icon"], "txt":day["weather"][0]["main"]}
                fal = {"rain":day.get("rain") or 0, "snow":day.get("snow") or 0}          # precipitation
                uvi = day.get("uvi") or 0
                Event("Page Weather {}".format(i), weekday, tmp, sun, wnd, cnd, fal, uvi)
                print("Page Weather {}".format(i), weekday, tmp, sun, wnd, cnd, fal, uvi)
                del tmp, sun, wnd, cnd, weekday
                gc.collect()
            # except:
            #     return
            del resp
            gc.collect()

class day_container(Observer, pageBase):
    def __init__(self, parent, num):
        Observer.__init__(self)  # DON'T FORGET THIS for event to work
        self.observe("Page Weather {}".format(num), self.update)
        self.num=num
        self.draw_day(parent)
    
    def update(self, weekday, tmp, sun, wnd, cnd, fal, uvi):
        self.title.set_text(weekday_name[weekday])
        self.tmp.set_text("{}{} / {}{}".format(tmp.get("min"), u"\u00B0", tmp.get("max"), u"\u00B0"))
        
        self.wind_dir.set_angle( wnd.get("dir")*10)
        self.wind_spd.set_text("{} m/s".format(wnd.get("spd")))

        self.cond_t.set_text("{}".format(cnd.get("txt")))
        cond_img = "{}.png".format(cnd.get("img"))
        if cond_img in os.listdir("images/condition/") :  # only known icons
            self.cond_i.set_src(
                self.get_img("images/condition/{}".format(cond_img))
            )
        else:
            print("Unknown condition file ", cond_img)
            self.cond_t.set_text(cond_img)
            self.cond_i.set_src(
                self.get_img("images/condition/unknown.png")
            )
        del cond_img
        gc.collect()

        self.uv.set_text("{}".format(round(uvi*10)/10))

        if( fal.get("rain")>0 or fal.get("snow")>0):
            self.rain.set_text("{}".format(round((fal.get("rain")+fal.get("snow"))*10)/10))
        else:
            self.rain.set_text("0")

        if self.num == 0:
            sun_rise_time = localtime(sun.get("rise"))
            self.sun_rise.set_text("{}:{:02d}".format(sun_rise_time[3], sun_rise_time[4]))

            sun_set_time = localtime(sun.get("set"))
            self.sun_set.set_text("{}:{:02d}".format(sun_set_time[3], sun_set_time[4]))

            sun_time = divmod(sun.get("set")-sun.get("rise"), 3600)
            self.sun_len.set_text("{}:{:02d}".format(sun_time[0], round(sun_time[1]/3600*60)))

    def draw_day(self, parent):
        sensCont = lv.cont(parent)
        sensCont.set_drag_parent(True)
        sensCont.set_layout(lv.LAYOUT.OFF)
        sensCont.set_fit2(lv.FIT.NONE, lv.FIT.TIGHT)
        sensCont.set_width(
            parent.get_width_grid(1, 1)
        )
        sensCont.set_style_local_pad_all(lv.cont.PART.MAIN, lv.STATE.DEFAULT, 0)

        self.title = lv.label(sensCont)
        self.title.set_text("week day #")
        self.title.set_pos(13, 3)

        tmp_i = lv.img(sensCont)
        tmp_i.set_drag_parent(True)
        tmp_i.set_pos(8, 18)
        tmp_i.set_src(
            self.get_img("images/sensor/thermo2.png")
        )
        del tmp_i

        self.tmp = lv.label(sensCont)
        self.tmp.set_text("Temperature")
        self.tmp.set_pos(23, 18)

        self.wind_dir = lv.img(sensCont)
        self.wind_dir.set_drag_parent(True)
        self.wind_dir.set_pos(5, 38)
        self.wind_dir.set_src(
            self.get_img("images/sensor/direction.png")
        )
        self.wind_dir.set_pivot(7, 7)
        

        self.wind_spd = lv.label(sensCont)
        self.wind_spd.set_text("spd m/s")
        self.wind_spd.set_pos(23, 38)

        self.cond_i = lv.img(sensCont)
        self.cond_i.set_drag_parent(True)
        self.cond_i.set_pos(100, 13)
        self.cond_i.set_src(
            self.get_img("images/condition/unknown.png")
        )

        self.cond_t = lv.label(sensCont)
        self.cond_t.set_text("Conditions")
        self.cond_t.set_pos(95, 41)

        
        rain_i = lv.img(sensCont)
        rain_i.set_drag_parent(True)
        rain_i.set_pos(143, 9)
        rain_i.set_src(
            self.get_img("images/sensor/rain.png")
        )
        del rain_i

        self.rain = lv.label(sensCont)
        self.rain.set_drag_parent(True)
        self.rain.set_text("---")
        self.rain.set_pos(160, 9)

        uv_i = lv.img(sensCont)
        uv_i.set_drag_parent(True)
        uv_i.set_pos(143, 29)
        uv_i.set_src(
            self.get_img("images/sensor/uv.png")
        )
        del uv_i

        self.uv = lv.label(sensCont)
        self.uv.set_drag_parent(True)
        self.uv.set_text("---")
        self.uv.set_pos(160, 29)

        if self.num==0:
            sun_rise_i = lv.img(sensCont)
            sun_rise_i.set_drag_parent(True)
            sun_rise_i.set_pos(4, 57)
            sun_rise_i.set_src(
                self.get_img("images/sensor/sunrise.png")
            )
            del sun_rise_i
            gc.collect()

            self.sun_rise = lv.label(sensCont)
            self.sun_rise.set_text("sunrise")
            self.sun_rise.set_pos(27, 58)


            sun_set_i = lv.img(sensCont)
            sun_set_i.set_drag_parent(True)
            sun_set_i.set_pos(67, 57)
            sun_set_i.set_src(
                self.get_img("images/sensor/sunset.png")
            )
            del sun_set_i
            gc.collect()

            self.sun_set = lv.label(sensCont)
            self.sun_set.set_text("sunset")
            self.sun_set.set_pos(92, 58)

            sun_len_i = lv.img(sensCont)
            sun_len_i.set_drag_parent(True)
            sun_len_i.set_pos(134, 59)
            sun_len_i.set_src(
                self.get_img("images/sensor/sunlen.png")
            )
            del sun_len_i
            gc.collect()

            self.sun_len = lv.label(sensCont)
            self.sun_len.set_text("day")
            self.sun_len.set_pos(152, 60)
            gc.collect()