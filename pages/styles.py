import lvgl as lv


class ContainerStyle(lv.style_t):
    def __init__(self):
        super().__init__()
        self.set_value_align(lv.STATE.DEFAULT, lv.ALIGN.OUT_TOP_LEFT)
        self.set_value_ofs_y(lv.STATE.DEFAULT, -lv.dpx(0))
        self.set_margin_all(lv.STATE.DEFAULT, 0)
        self.set_margin_top(lv.STATE.DEFAULT, lv.dpx(10))


class ContainerNoBorderStyle(lv.style_t):
    def __init__(self):
        super().__init__()
        # self.set_border_color(lv.STATE.DEFAULT, None)
        self.set_bg_opa(lv.STATE.DEFAULT, lv.OPA.TRANSP)
        self.set_border_width(lv.STATE.DEFAULT, 0)
        self.set_pad_all(lv.STATE.DEFAULT, 0)
        self.set_margin_all(lv.STATE.DEFAULT, 0)


class ContainerPageStyle(ContainerNoBorderStyle):
    def __init__(self):
        super().__init__()
        self.set_margin_all(lv.STATE.DEFAULT, 0)
        self.set_pad_all(lv.STATE.DEFAULT, 0)
        self.set_pad_top(lv.STATE.DEFAULT, 8)


class ContainerTitleBarStyle(ContainerNoBorderStyle):
    def __init__(self):
        super().__init__()
        self.set_bg_opa(lv.STATE.DEFAULT, lv.OPA.COVER)
        self.set_bg_color(lv.STATE.DEFAULT, lv.color_hex3(0xFFF))


class ColorStyle(lv.style_t):
    def __init__(self, color):
        super().__init__()
        self.set_bg_opa(lv.STATE.DEFAULT, lv.OPA.COVER)
        self.set_bg_color(lv.STATE.DEFAULT, lv.color_hex3(color))
        self.set_bg_grad_color(lv.STATE.DEFAULT, lv.color_hex3(0xFFF))
        self.set_bg_grad_dir(lv.STATE.DEFAULT, lv.GRAD_DIR.VER)
        # self.set_bg_main_stop(lv.STATE.DEFAULT, 0);
        # self.set_bg_grad_stop(lv.STATE.DEFAULT, 128);


class ChartPaddingStyle(lv.style_t):
    def __init__(self):
        super().__init__()
        self.set_pad_left(lv.STATE.DEFAULT, 10)
        self.set_pad_right(lv.STATE.DEFAULT, 10)
        self.set_pad_bottom(lv.STATE.DEFAULT, 10)
        self.set_pad_top(lv.STATE.DEFAULT, 10)


class ShadowStyle(lv.style_t):
    def __init__(self):
        super().__init__()
        self.set_shadow_opa(lv.STATE.DEFAULT, lv.OPA.COVER)
        self.set_shadow_width(lv.STATE.DEFAULT, 3)
        self.set_shadow_color(lv.STATE.DEFAULT, lv.color_hex3(0xAAA))
        self.set_shadow_ofs_x(lv.STATE.DEFAULT, 5)
        self.set_shadow_ofs_y(lv.STATE.DEFAULT, 3)
        self.set_shadow_spread(lv.STATE.DEFAULT, 0)


class ModalBackground(lv.style_t):
    def __init__(self):
        super().__init__()
        self.set_bg_opa(lv.STATE.DEFAULT, lv.OPA._30)
        self.set_bg_color(lv.STATE.DEFAULT, lv.color_hex3(0x000))


# A square button with a shadow when not pressed
class ButtonStyle(lv.style_t):
    def __init__(self):
        super().__init__()
        self.set_radius(lv.STATE.DEFAULT, lv.dpx(8))
        self.set_shadow_opa(lv.STATE.DEFAULT, lv.OPA.COVER)
        self.set_shadow_width(lv.STATE.DEFAULT, lv.dpx(10))
        self.set_shadow_color(lv.STATE.DEFAULT, lv.color_hex3(0xAAA))
        self.set_shadow_ofs_x(lv.STATE.DEFAULT, lv.dpx(10))
        self.set_shadow_ofs_y(lv.STATE.DEFAULT, lv.dpx(10))
        self.set_shadow_spread(lv.STATE.DEFAULT, 0)

        self.set_shadow_ofs_x(lv.STATE.PRESSED, lv.dpx(0))
        self.set_shadow_ofs_y(lv.STATE.PRESSED, lv.dpx(0))


##############################################################################
# Themes
class AdvancedDemoTheme(lv.theme_t):

    def __init__(self):
        super().__init__()
        self.button_style = ButtonStyle()

        # This theme is based on active theme (material)
        base_theme = lv.theme_get_act()
        self.copy(base_theme)

        # This theme will be applied only after base theme is applied
        self.set_base(base_theme)

        # Set the "apply" callback of this theme to our custom callback
        self.set_apply_cb(self.apply)

        # Activate this theme
        self.set_act()

    def apply(self, theme, obj, name):
        if name == lv.THEME.BTN:
            obj.add_style(obj.PART.MAIN, self.button_style)
##############################################################################
