import libtcodpy as libtcod

Color = libtcod.Color

class Random:
    def __init__(self, stream_id):
        self.stream_id = stream_id

    def get_int(self, *args, **kwargs):
        """ rand.get_int([start,] stop) -> random integer

        Note the non-standard order of default arguments: if a single argument
        is provided, it is assumed to be the stop value, and the start (!) value
        then defaults to 0.

        You may also use keyword arguments start and stop if you prefer to be
        explicit -- this may be preferable to using the magic behaviour. Kwargs
        will override positional arguments.

        """
        if len(args) == 0 and 'stop' not in kwargs:
            raise TypeError('get_int expects either 1 positional argument or the keyword argument "stop"')

        min_value = max_value = 0
        if len(args) == 1:
            max_value = args[0]
        elif len(args) == 2:
            min_value = args[0]
            max_value = args[1]

        if 'start' in kwargs:
            min_value = kwargs['start']
        if 'stop' in kwargs:
            max_value = kwargs['stop']

        return libtcod.random_get_int(self.stream_id, min_value, max_value)

# A default Random for anyone to use
random = Random(0)

def set_custom_font(fontfile, flags=libtcod.FONT_LAYOUT_ASCII_INROW, horizontal_count=0, vertical_count=0):
    return libtcod.console_set_custom_font(fontfile, flags, horizontal_count, vertical_count)

def init_root(width, height, title, fullscreen=False, renderer=libtcod.RENDERER_SDL):
    return libtcod.console_init_root(width, height, title, fullscreen, renderer)

def wait_for_keypress(flush=False):
    return libtcod.console_wait_for_keypress(flush)

key, mouse = (libtcod.Key(), libtcod.Mouse())
def wait_for_event(mask=libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, flush=False):
    libtcod.sys_wait_for_event(mask, key, mouse, flush)
    return (key, mouse)

def check_for_event(mask=libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE):
    libtcod.sys_check_for_event(mask, key, mouse)
    return (key, mouse)

def set_fullscreen(want_fullscreen=True):
    return libtcod.console_set_fullscreen(want_fullscreen)

def is_fullscreen():
    return libtcod.console_is_fullscreen()

def is_key_pressed(key):
    return libtcod.console_is_key_pressed(key)

def is_window_closed():
    return libtcod.console_is_window_closed()

def flush():
    return libtcod.console_flush()

class Console:
    # Root console has id 0
    ROOT_ID = 0

    def __init__(self, width=0, height=0, console_id=None):
        if console_id is None:
            self.console_id = libtcod.console_new(width, height)
            self.width = width
            self.height = height
        else:
            self.console_id = console_id
            self.width = libtcod.console_get_width(console_id)
            self.height = libtcod.console_get_height(console_id)

    def __del__(self):
        if self.console_id != self.ROOT_ID: # Root console cannot be console_delete()d
            libtcod.console_delete(self.console_id)

    def __getstate__(self):
        if self.console_id == self.ROOT_ID:
            return {}
        return {'width': self.width, 'height': self.height}

    def __setstate__(self, state):
        self.__init__(state['width'], state['height'])

    def set_key_color(self, color):
        return libtcod.console_set_key_color(self.console_id, color)

    def blit(self, src_x=0, src_y=0, src_width=None, src_height=None,
             dest_console=None, dest_x=0, dest_y=0,
             alpha_fg=1.0, alpha_bg=1.0):
        if src_width is None:
            src_width = self.width
        if src_height is None:
            src_height = self.height

        dest_id = self.ROOT_ID
        if dest_console is not None:
            dest_id = dest_console.console_id

        return libtcod.console_blit(self.console_id, src_x, src_y, src_width, src_height,
                             dest_id, dest_x, dest_y, alpha_fg, alpha_bg)

    def set_default_background(self, color):
        return libtcod.console_set_default_background(self.console_id, color)

    def set_default_foreground(self, color):
        return libtcod.console_set_default_foreground(self.console_id, color)

    def set_char_background(self, x, y, color, flags=libtcod.BKGND_SET):
        return libtcod.console_set_char_background(self.console_id, x, y, color, flags)

    def put_char(self, x=0, y=0, char=' ', flags=libtcod.BKGND_NONE):
        return libtcod.console_put_char(self.console_id, x, y, char, flags)

    def print_ex(self, x=0, y=0, flags=libtcod.BKGND_NONE, align=libtcod.LEFT, text="DEFAULT_TEXT"):
        return libtcod.console_print_ex(self.console_id, x, y, flags, align, text)

    def rect(self, x, y, width, height, clear=False, effect=libtcod.BKGND_SET):
        return libtcod.console_rect(self.console_id, x, y, width, height, clear, effect)

    def clear(self):
        return libtcod.console_clear(self.console_id)

    def get_height_rect(self, x=0, y=0, width=None, height=None, text=''):
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        return libtcod.console_get_height_rect(self.console_id, x, y, width, height, text)

    def print_rect_ex(self, x=0, y=0, width=None, height=None, effect=libtcod.BKGND_NONE,
                      align=libtcod.LEFT, text=''):
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        return libtcod.console_print_rect_ex(self.console_id, x, y, width, height, effect, align, text)

# The root console
root_console = Console(console_id=Console.ROOT_ID)

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = libtcod.map_new(width, height)

    def __getstate__(self):
        return {'width': self.width, 'height': self.height}

    def __setstate__(self, state):
        self.__init__(state['width'], state['height'])

    def set_properties(self, x, y, see_through, pass_through):
        return libtcod.map_set_properties(self.map, x, y, see_through, pass_through)

    def compute_fov(self, x, y, radius, light_walls, algorithm):
        return libtcod.map_compute_fov(self.map, x, y, radius, light_walls, algorithm)

    def is_in_fov(self, x, y):
        return libtcod.map_is_in_fov(self.map, x, y)

class Image:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image_id = libtcod.image_new(width, height)

    def get_size(self):
        return libtcod.image_get_size(self.image_id)

    def blit_2x(self, console, dest_x=0, dest_y=0, x=0, y=0, width=None, height=None):
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        return libtcod.image_blit_2x(self.image_id, console.console_id, dest_x, dest_y, x, y, width, height)

class ImageFile(Image):
    def __init__(self, path):
        self.image_id = libtcod.image_load(path)
        self.width, self.height = self.get_size()

# Useful constants
BACKGROUND_NONE = libtcod.BKGND_NONE
BACKGROUND_SET = libtcod.BKGND_SET
BACKGROUND_MULTIPLY = libtcod.BKGND_MULTIPLY
BACKGROUND_LIGHTEN = libtcod.BKGND_LIGHTEN
BACKGROUND_DARKEN = libtcod.BKGND_DARKEN
BACKGROUND_SCREEN = libtcod.BKGND_SCREEN
BACKGROUND_COLOR_DODGE = libtcod.BKGND_COLOR_DODGE
BACKGROUND_COLOR_BURN = libtcod.BKGND_COLOR_BURN
BACKGROUND_ADD = libtcod.BKGND_ADD
BACKGROUND_ADDALPHA = libtcod.BKGND_ADDALPHA
BACKGROUND_BURN = libtcod.BKGND_BURN
BACKGROUND_OVERLAY = libtcod.BKGND_OVERLAY
BACKGROUND_ALPHA = libtcod.BKGND_ALPHA
BACKGROUND_DEFAULT = libtcod.BKGND_DEFAULT

ALIGN_LEFT = libtcod.LEFT
ALIGN_RIGHT = libtcod.RIGHT
ALIGN_CENTER = libtcod.CENTER

EVENT_KEY_PRESS = libtcod.EVENT_KEY_PRESS
EVENT_KEY_RELEASE = libtcod.EVENT_KEY_RELEASE
EVENT_KEY = libtcod.EVENT_KEY
EVENT_MOUSE_MOVE = libtcod.EVENT_MOUSE_MOVE
EVENT_MOUSE_PRESS = libtcod.EVENT_MOUSE_PRESS
EVENT_MOUSE_RELEASE = libtcod.EVENT_MOUSE_RELEASE
EVENT_MOUSE = libtcod.EVENT_MOUSE
EVENT_ANY = libtcod.EVENT_ANY

COLOR_BLACK = libtcod.black
COLOR_DARKEST_GREY = libtcod.darkest_grey
COLOR_DARKER_GREY = libtcod.darker_grey
COLOR_DARK_GREY = libtcod.dark_grey
COLOR_GREY = libtcod.grey
COLOR_LIGHT_GREY = libtcod.light_grey
COLOR_LIGHTER_GREY = libtcod.lighter_grey
COLOR_LIGHTEST_GREY = libtcod.lightest_grey
COLOR_DARKEST_GRAY = libtcod.darkest_gray
COLOR_DARKER_GRAY = libtcod.darker_gray
COLOR_DARK_GRAY = libtcod.dark_gray
COLOR_GRAY = libtcod.gray
COLOR_LIGHT_GRAY = libtcod.light_gray
COLOR_LIGHTER_GRAY = libtcod.lighter_gray
COLOR_LIGHTEST_GRAY = libtcod.lightest_gray
COLOR_WHITE = libtcod.white

COLOR_DARKEST_SEPIA = libtcod.darkest_sepia
COLOR_DARKER_SEPIA = libtcod.darker_sepia
COLOR_DARK_SEPIA = libtcod.dark_sepia
COLOR_SEPIA = libtcod.sepia
COLOR_LIGHT_SEPIA = libtcod.light_sepia
COLOR_LIGHTER_SEPIA = libtcod.lighter_sepia
COLOR_LIGHTEST_SEPIA = libtcod.lightest_sepia

COLOR_RED = libtcod.red
COLOR_FLAME = libtcod.flame
COLOR_ORANGE = libtcod.orange
COLOR_AMBER = libtcod.amber
COLOR_YELLOW = libtcod.yellow
COLOR_LIME = libtcod.lime
COLOR_CHARTREUSE = libtcod.chartreuse
COLOR_GREEN = libtcod.green
COLOR_SEA = libtcod.sea
COLOR_TURQUOISE = libtcod.turquoise
COLOR_CYAN = libtcod.cyan
COLOR_SKY = libtcod.sky
COLOR_AZURE = libtcod.azure
COLOR_BLUE = libtcod.blue
COLOR_HAN = libtcod.han
COLOR_VIOLET = libtcod.violet
COLOR_PURPLE = libtcod.purple
COLOR_FUCHSIA = libtcod.fuchsia
COLOR_MAGENTA = libtcod.magenta
COLOR_PINK = libtcod.pink
COLOR_CRIMSON = libtcod.crimson

COLOR_DARK_RED = libtcod.dark_red
COLOR_DARK_FLAME = libtcod.dark_flame
COLOR_DARK_ORANGE = libtcod.dark_orange
COLOR_DARK_AMBER = libtcod.dark_amber
COLOR_DARK_YELLOW = libtcod.dark_yellow
COLOR_DARK_LIME = libtcod.dark_lime
COLOR_DARK_CHARTREUSE = libtcod.dark_chartreuse
COLOR_DARK_GREEN = libtcod.dark_green
COLOR_DARK_SEA = libtcod.dark_sea
COLOR_DARK_TURQUOISE = libtcod.dark_turquoise
COLOR_DARK_CYAN = libtcod.dark_cyan
COLOR_DARK_SKY = libtcod.dark_sky
COLOR_DARK_AZURE = libtcod.dark_azure
COLOR_DARK_BLUE = libtcod.dark_blue
COLOR_DARK_HAN = libtcod.dark_han
COLOR_DARK_VIOLET = libtcod.dark_violet
COLOR_DARK_PURPLE = libtcod.dark_purple
COLOR_DARK_FUCHSIA = libtcod.dark_fuchsia
COLOR_DARK_MAGENTA = libtcod.dark_magenta
COLOR_DARK_PINK = libtcod.dark_pink
COLOR_DARK_CRIMSON = libtcod.dark_crimson

COLOR_DARKER_RED = libtcod.darker_red
COLOR_DARKER_FLAME = libtcod.darker_flame
COLOR_DARKER_ORANGE = libtcod.darker_orange
COLOR_DARKER_AMBER = libtcod.darker_amber
COLOR_DARKER_YELLOW = libtcod.darker_yellow
COLOR_DARKER_LIME = libtcod.darker_lime
COLOR_DARKER_CHARTREUSE = libtcod.darker_chartreuse
COLOR_DARKER_GREEN = libtcod.darker_green
COLOR_DARKER_SEA = libtcod.darker_sea
COLOR_DARKER_TURQUOISE = libtcod.darker_turquoise
COLOR_DARKER_CYAN = libtcod.darker_cyan
COLOR_DARKER_SKY = libtcod.darker_sky
COLOR_DARKER_AZURE = libtcod.darker_azure
COLOR_DARKER_BLUE = libtcod.darker_blue
COLOR_DARKER_HAN = libtcod.darker_han
COLOR_DARKER_VIOLET = libtcod.darker_violet
COLOR_DARKER_PURPLE = libtcod.darker_purple
COLOR_DARKER_FUCHSIA = libtcod.darker_fuchsia
COLOR_DARKER_MAGENTA = libtcod.darker_magenta
COLOR_DARKER_PINK = libtcod.darker_pink
COLOR_DARKER_CRIMSON = libtcod.darker_crimson

COLOR_DARKEST_RED = libtcod.darkest_red
COLOR_DARKEST_FLAME = libtcod.darkest_flame
COLOR_DARKEST_ORANGE = libtcod.darkest_orange
COLOR_DARKEST_AMBER = libtcod.darkest_amber
COLOR_DARKEST_YELLOW = libtcod.darkest_yellow
COLOR_DARKEST_LIME = libtcod.darkest_lime
COLOR_DARKEST_CHARTREUSE = libtcod.darkest_chartreuse
COLOR_DARKEST_GREEN = libtcod.darkest_green
COLOR_DARKEST_SEA = libtcod.darkest_sea
COLOR_DARKEST_TURQUOISE = libtcod.darkest_turquoise
COLOR_DARKEST_CYAN = libtcod.darkest_cyan
COLOR_DARKEST_SKY = libtcod.darkest_sky
COLOR_DARKEST_AZURE = libtcod.darkest_azure
COLOR_DARKEST_BLUE = libtcod.darkest_blue
COLOR_DARKEST_HAN = libtcod.darkest_han
COLOR_DARKEST_VIOLET = libtcod.darkest_violet
COLOR_DARKEST_PURPLE = libtcod.darkest_purple
COLOR_DARKEST_FUCHSIA = libtcod.darkest_fuchsia
COLOR_DARKEST_MAGENTA = libtcod.darkest_magenta
COLOR_DARKEST_PINK = libtcod.darkest_pink
COLOR_DARKEST_CRIMSON = libtcod.darkest_crimson

COLOR_LIGHT_RED = libtcod.light_red
COLOR_LIGHT_FLAME = libtcod.light_flame
COLOR_LIGHT_ORANGE = libtcod.light_orange
COLOR_LIGHT_AMBER = libtcod.light_amber
COLOR_LIGHT_YELLOW = libtcod.light_yellow
COLOR_LIGHT_LIME = libtcod.light_lime
COLOR_LIGHT_CHARTREUSE = libtcod.light_chartreuse
COLOR_LIGHT_GREEN = libtcod.light_green
COLOR_LIGHT_SEA = libtcod.light_sea
COLOR_LIGHT_TURQUOISE = libtcod.light_turquoise
COLOR_LIGHT_CYAN = libtcod.light_cyan
COLOR_LIGHT_SKY = libtcod.light_sky
COLOR_LIGHT_AZURE = libtcod.light_azure
COLOR_LIGHT_BLUE = libtcod.light_blue
COLOR_LIGHT_HAN = libtcod.light_han
COLOR_LIGHT_VIOLET = libtcod.light_violet
COLOR_LIGHT_PURPLE = libtcod.light_purple
COLOR_LIGHT_FUCHSIA = libtcod.light_fuchsia
COLOR_LIGHT_MAGENTA = libtcod.light_magenta
COLOR_LIGHT_PINK = libtcod.light_pink
COLOR_LIGHT_CRIMSON = libtcod.light_crimson

COLOR_LIGHTER_RED = libtcod.lighter_red
COLOR_LIGHTER_FLAME = libtcod.lighter_flame
COLOR_LIGHTER_ORANGE = libtcod.lighter_orange
COLOR_LIGHTER_AMBER = libtcod.lighter_amber
COLOR_LIGHTER_YELLOW = libtcod.lighter_yellow
COLOR_LIGHTER_LIME = libtcod.lighter_lime
COLOR_LIGHTER_CHARTREUSE = libtcod.lighter_chartreuse
COLOR_LIGHTER_GREEN = libtcod.lighter_green
COLOR_LIGHTER_SEA = libtcod.lighter_sea
COLOR_LIGHTER_TURQUOISE = libtcod.lighter_turquoise
COLOR_LIGHTER_CYAN = libtcod.lighter_cyan
COLOR_LIGHTER_SKY = libtcod.lighter_sky
COLOR_LIGHTER_AZURE = libtcod.lighter_azure
COLOR_LIGHTER_BLUE = libtcod.lighter_blue
COLOR_LIGHTER_HAN = libtcod.lighter_han
COLOR_LIGHTER_VIOLET = libtcod.lighter_violet
COLOR_LIGHTER_PURPLE = libtcod.lighter_purple
COLOR_LIGHTER_FUCHSIA = libtcod.lighter_fuchsia
COLOR_LIGHTER_MAGENTA = libtcod.lighter_magenta
COLOR_LIGHTER_PINK = libtcod.lighter_pink
COLOR_LIGHTER_CRIMSON = libtcod.lighter_crimson

COLOR_LIGHTEST_RED = libtcod.lightest_red
COLOR_LIGHTEST_FLAME = libtcod.lightest_flame
COLOR_LIGHTEST_ORANGE = libtcod.lightest_orange
COLOR_LIGHTEST_AMBER = libtcod.lightest_amber
COLOR_LIGHTEST_YELLOW = libtcod.lightest_yellow
COLOR_LIGHTEST_LIME = libtcod.lightest_lime
COLOR_LIGHTEST_CHARTREUSE = libtcod.lightest_chartreuse
COLOR_LIGHTEST_GREEN = libtcod.lightest_green
COLOR_LIGHTEST_SEA = libtcod.lightest_sea
COLOR_LIGHTEST_TURQUOISE = libtcod.lightest_turquoise
COLOR_LIGHTEST_CYAN = libtcod.lightest_cyan
COLOR_LIGHTEST_SKY = libtcod.lightest_sky
COLOR_LIGHTEST_AZURE = libtcod.lightest_azure
COLOR_LIGHTEST_BLUE = libtcod.lightest_blue
COLOR_LIGHTEST_HAN = libtcod.lightest_han
COLOR_LIGHTEST_VIOLET = libtcod.lightest_violet
COLOR_LIGHTEST_PURPLE = libtcod.lightest_purple
COLOR_LIGHTEST_FUCHSIA = libtcod.lightest_fuchsia
COLOR_LIGHTEST_MAGENTA = libtcod.lightest_magenta
COLOR_LIGHTEST_PINK = libtcod.lightest_pink
COLOR_LIGHTEST_CRIMSON = libtcod.lightest_crimson

COLOR_DESATURATED_RED = libtcod.desaturated_red
COLOR_DESATURATED_FLAME = libtcod.desaturated_flame
COLOR_DESATURATED_ORANGE = libtcod.desaturated_orange
COLOR_DESATURATED_AMBER = libtcod.desaturated_amber
COLOR_DESATURATED_YELLOW = libtcod.desaturated_yellow
COLOR_DESATURATED_LIME = libtcod.desaturated_lime
COLOR_DESATURATED_CHARTREUSE = libtcod.desaturated_chartreuse
COLOR_DESATURATED_GREEN = libtcod.desaturated_green
COLOR_DESATURATED_SEA = libtcod.desaturated_sea
COLOR_DESATURATED_TURQUOISE = libtcod.desaturated_turquoise
COLOR_DESATURATED_CYAN = libtcod.desaturated_cyan
COLOR_DESATURATED_SKY = libtcod.desaturated_sky
COLOR_DESATURATED_AZURE = libtcod.desaturated_azure
COLOR_DESATURATED_BLUE = libtcod.desaturated_blue
COLOR_DESATURATED_HAN = libtcod.desaturated_han
COLOR_DESATURATED_VIOLET = libtcod.desaturated_violet
COLOR_DESATURATED_PURPLE = libtcod.desaturated_purple
COLOR_DESATURATED_FUCHSIA = libtcod.desaturated_fuchsia
COLOR_DESATURATED_MAGENTA = libtcod.desaturated_magenta
COLOR_DESATURATED_PINK = libtcod.desaturated_pink
COLOR_DESATURATED_CRIMSON = libtcod.desaturated_crimson

COLOR_BRASS = libtcod.brass
COLOR_COPPER = libtcod.copper
COLOR_GOLD = libtcod.gold
COLOR_SILVER = libtcod.silver

COLOR_CELADON = libtcod.celadon
COLOR_PEACH = libtcod.peach

KEY_NONE = libtcod.KEY_NONE
KEY_ESCAPE = libtcod.KEY_ESCAPE
KEY_BACKSPACE = libtcod.KEY_BACKSPACE
KEY_TAB = libtcod.KEY_TAB
KEY_ENTER = libtcod.KEY_ENTER
KEY_SHIFT = libtcod.KEY_SHIFT
KEY_CONTROL = libtcod.KEY_CONTROL
KEY_ALT = libtcod.KEY_ALT
KEY_PAUSE = libtcod.KEY_PAUSE
KEY_CAPSLOCK = libtcod.KEY_CAPSLOCK
KEY_PAGEUP = libtcod.KEY_PAGEUP
KEY_PAGEDOWN = libtcod.KEY_PAGEDOWN
KEY_END = libtcod.KEY_END
KEY_HOME = libtcod.KEY_HOME
KEY_UP = libtcod.KEY_UP
KEY_LEFT = libtcod.KEY_LEFT
KEY_RIGHT = libtcod.KEY_RIGHT
KEY_DOWN = libtcod.KEY_DOWN
KEY_PRINTSCREEN = libtcod.KEY_PRINTSCREEN
KEY_INSERT = libtcod.KEY_INSERT
KEY_DELETE = libtcod.KEY_DELETE
KEY_LWIN = libtcod.KEY_LWIN
KEY_RWIN = libtcod.KEY_RWIN
KEY_APPS = libtcod.KEY_APPS
KEY_0 = libtcod.KEY_0
KEY_1 = libtcod.KEY_1
KEY_2 = libtcod.KEY_2
KEY_3 = libtcod.KEY_3
KEY_4 = libtcod.KEY_4
KEY_5 = libtcod.KEY_5
KEY_6 = libtcod.KEY_6
KEY_7 = libtcod.KEY_7
KEY_8 = libtcod.KEY_8
KEY_9 = libtcod.KEY_9
KEY_KP0 = libtcod.KEY_KP0
KEY_KP1 = libtcod.KEY_KP1
KEY_KP2 = libtcod.KEY_KP2
KEY_KP3 = libtcod.KEY_KP3
KEY_KP4 = libtcod.KEY_KP4
KEY_KP5 = libtcod.KEY_KP5
KEY_KP6 = libtcod.KEY_KP6
KEY_KP7 = libtcod.KEY_KP7
KEY_KP8 = libtcod.KEY_KP8
KEY_KP9 = libtcod.KEY_KP9
KEY_KPADD = libtcod.KEY_KPADD
KEY_KPSUB = libtcod.KEY_KPSUB
KEY_KPDIV = libtcod.KEY_KPDIV
KEY_KPMUL = libtcod.KEY_KPMUL
KEY_KPDEC = libtcod.KEY_KPDEC
KEY_KPENTER = libtcod.KEY_KPENTER
KEY_F1 = libtcod.KEY_F1
KEY_F2 = libtcod.KEY_F2
KEY_F3 = libtcod.KEY_F3
KEY_F4 = libtcod.KEY_F4
KEY_F5 = libtcod.KEY_F5
KEY_F6 = libtcod.KEY_F6
KEY_F7 = libtcod.KEY_F7
KEY_F8 = libtcod.KEY_F8
KEY_F9 = libtcod.KEY_F9
KEY_F10 = libtcod.KEY_F10
KEY_F11 = libtcod.KEY_F11
KEY_F12 = libtcod.KEY_F12
KEY_NUMLOCK = libtcod.KEY_NUMLOCK
KEY_SCROLLLOCK = libtcod.KEY_SCROLLLOCK
KEY_SPACE = libtcod.KEY_SPACE
KEY_CHAR = libtcod.KEY_CHAR
