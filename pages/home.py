import lvgl as lv
from lib.EventObserver import Observer
from sensor import mija, soil, weather
from pages.styles import ContainerPageStyle
import gc, json


class ui(Observer):
    def __init__(self, app, page):
        # self.app = app
        # self.page = page

        self.c1 = lv.cont(page)
        self.c1.set_drag_parent(True)
        self.c1.add_style(lv.cont.PART.MAIN, ContainerPageStyle())
        self.c1.set_layout(lv.LAYOUT.PRETTY_TOP)
        self.c1.set_fit2(lv.FIT.PARENT, lv.FIT.MAX)
        self.c1.set_width(page.get_width())

        Observer.__init__(self)  # DON'T FORGET THIS for events to work
        self.observe("Draw sensors", self.draw_sensors)


    def draw_sensors(self):
        gc.collect()
        with open('settings.json', 'r') as f:
            global_settings = json.loads(f.read())

        for sensor in sorted(global_settings["sensors"], key=lambda k: int(k.get('order', 0)), reverse=False):
            # if sensor["mac"] not in self.sensors.keys():
            if sensor["type"] == 'mija':
                # self.sensors[str(sensor["mac"])] = 
                mija.UI(
                    page=self.c1,
                    sensorMac=sensor["mac"],
                    sensorTitle=sensor["title"],
                    parts=1,
                    simulate=sensor["simulate"]
                )
            elif sensor["type"] == 'soil':
                # self.sensors[str(sensor["mac"])] = 
                soil.UI(
                    page=self.c1,
                    sensorMac=sensor["mac"],
                    sensorTitle=sensor["title"],
                    parts=1,
                    simulate=sensor["simulate"]
                )
            elif sensor["type"] == 'weather':
                # self.sensors[str(sensor["mac"])] = 
                weather.UI(
                    page=self.c1,
                    sensorMac=sensor["mac"],
                    sensorTitle=sensor["title"],
                    parts=1,
                    simulate=sensor["simulate"]
                )
            gc.collect()
        self.forget("Draw sensors")
        gc.collect()
