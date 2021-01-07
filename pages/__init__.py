import lvgl as lv
from lib.imagetools import get_png_info, open_png
import gc

class pageBase():
    def __init__(self):
        gc.collect()
        decoder = lv.img.decoder_create()
        decoder.info_cb = get_png_info
        decoder.open_cb = open_png
        gc.collect()

    def get_img(self, path):
        gc.collect()
        with open(path ,'rb') as f:
            png_data = f.read()
        return lv.img_dsc_t({
            'data_size': len(png_data),
            'data': png_data
        })
