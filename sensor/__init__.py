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

    @micropython.native  # type: ignore
    def tickClock(self, evt):
        delta = utime.time() - self.lastUpdTime
        ulocaltime = utime.localtime(delta)
        h = ulocaltime[3]
        m = ulocaltime[4]
        s = ulocaltime[5]

        del delta, ulocaltime

        t = "{} ".format(lv.SYMBOL.EYE_OPEN)
        if h > 0:
            # timeStr += str(h) + ":"
            t = "{}{}:".format(t, h)
            if m in range(1, 10):
                # timeStr += "0" + str(m) + ":"
                t = "{}0{}:".format(t, m)
            else:
                # timeStr += str(m) + ":"
                t = "{}{}:".format(t, m)
        elif m > 0:
            # timeStr += str(m) + ":"
            t = "{}{}:".format(t, m)

        if m > 0 and s in range(0, 10):
            # timeStr += "0" + str(s)
            t = "{}0{}".format(t, s)
        else:
            # timeStr += str(s)
            t = "{}{}".format(t, s)

        self.updValue.set_text(t)

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