import utime, gc
import lvgl as lv
from lib.imagetools import get_png_info, open_png

class sensorBase():

    def __init__(self):
        self.lastUpdTime = utime.time()
        self.lastUpdCount = None

        gc.collect()
        decoder = lv.img.decoder_create()
        decoder.info_cb = get_png_info
        decoder.open_cb = open_png
        gc.collect()

    def tickClock(self, evt):
        ulocaltime = utime.localtime(utime.time() - self.lastUpdTime)
        h = ulocaltime[3]
        m = ulocaltime[4]
        s = ulocaltime[5]

        del ulocaltime

        if h > 0:
            self.updValue.set_text("{}:{:02d}:{:02d}".format(h, m, s))
        elif m > 0:
            self.updValue.set_text("{}:{:02d}".format(m, s))
        else:
            self.updValue.set_text("{}".format(s))


    def sensorUpdated(self):
        self.lastUpdTime = utime.time()

    def get_img(self, path):
        gc.collect()
        with open(path ,'rb') as f:
            png_data = f.read()
        return lv.img_dsc_t({
            'data_size': len(png_data),
            'data': png_data
        })