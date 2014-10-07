import libtcodpy as libtcod

class Random(object):
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
    root_console.height = height
    root_console.width = width
    return libtcod.console_init_root(width, height, title, fullscreen, renderer)

def wait_for_keypress(flush=False):
    return libtcod.console_wait_for_keypress(flush)

def wait_for_event(mask=libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, flush=False):
    key, mouse = (libtcod.Key(), libtcod.Mouse())
    libtcod.sys_wait_for_event(mask, key, mouse, flush)
    return (key, mouse)

def check_for_event(mask=libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE):
    key, mouse = (libtcod.Key(), libtcod.Mouse())
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

def set_fps_limit(limit):
    return libtcod.sys_set_fps(limit)

def get_fps():
    return libtcod.sys_get_fps()

class Console(object):
    # Root console has id 0
    ROOT_ID = 0

    def __init__(self, width=20, height=10, console_id=None):
        if console_id is None:
            self.console_id = libtcod.console_new(width, height)
            self.width = width
            self.height = height
        else:
            self.console_id = console_id
            self.width = libtcod.console_get_width(console_id)
            self.height = libtcod.console_get_height(console_id)

    def close(self):
        if self.console_id != self.ROOT_ID: # Root console cannot be console_delete()d
            libtcod.console_delete(self.console_id)

    def __del__(self):
        self.close()

    def grow(self, width=None, height=None):
        """ Grow the console to at least width*height. Uses self.resize() """
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        if self.height >= height and self.width >= width:
            return # No resize needed.

        self.resize(width, height)

    def resize(self, width=None, height=None):
        """ Resize a console by destroying and recreating it """
        if self.console_id == self.ROOT_ID:
            raise AttributeError("The root console cannot be resized!")
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        if self.height == height and self.width == width:
            return # No resize needed.

        libtcod.console_delete(self.console_id)
        self.console_id = libtcod.console_new(width, height)
        self.width = width
        self.height = height

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

    def get_default_background(self):
        return libtcod.console_get_default_background(self.console_id)

    def set_default_foreground(self, color):
        return libtcod.console_set_default_foreground(self.console_id, color)

    def get_default_foreground(self):
        return libtcod.console_get_default_foreground(self.console_id)

    def set_char_background(self, x, y, color, flags=libtcod.BKGND_SET):
        return libtcod.console_set_char_background(self.console_id, x, y, color, flags)

    def put_char(self, x=0, y=0, char=' ', flags=libtcod.BKGND_NONE):
        return libtcod.console_put_char(self.console_id, x, y, char, flags)

    def print_ex(self, x=0, y=0, flags=libtcod.BKGND_NONE, align=libtcod.LEFT, text=""):
        if text is None:
            raise ValueError("Trying to console.print_ex a None!")
        return libtcod.console_print_ex(self.console_id, x, y, flags, align, text)

    def rect(self, x, y, width, height, clear=False, effect=libtcod.BKGND_SET):
        return libtcod.console_rect(self.console_id, x, y, width, height, clear, effect)

    def print_frame(self, x=0, y=0, width=None, height=None, clear=True, effect=libtcod.BKGND_SET):
        if width is None:
            width = self.width - x
        if height is None:
            height = self.height - y

        return libtcod.console_print_frame(self.console_id, x, y, width, height, clear, effect)

    def clear(self):
        return libtcod.console_clear(self.console_id)

    def get_height_rect(self, x=0, y=0, width=None, height=None, text=''):
        if text is None:
            raise ValueError("Trying to console.get_height_rect of a None!")
        if width is None:
            width = self.width - x
        if height is None:
            height = self.height - y
        return libtcod.console_get_height_rect(self.console_id, x, y, width, height, text)

    def print_rect_ex(self, x=0, y=0, width=None, height=None, effect=libtcod.BKGND_NONE,
                      align=libtcod.LEFT, text=''):
        if text is None:
            raise ValueError("Trying to console.print_rect_ex a None!")
        if width is None:
            width = self.width - x
        if height is None:
            height = self.height - y

        return libtcod.console_print_rect_ex(self.console_id, x, y, width, height, effect, align, text)

# The root console
root_console = Console(console_id=Console.ROOT_ID)

class Map(object):
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

class Image(object):
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

class ColorSet(object):
    """
    Defines five color pairs to be used to change colors in mid-string -- see
    http://doryen.eptalys.net/data/libtcod/doc/1.5.1/html2/console_print.html?py=true#9
    for the underlying mechanism.

    Usage involves:
        >>> cs = tcod.ColorSet()
        >>> cs.set_colors(1, fgcolor=tcod.color.RED)
        >>> cs.set_colors(2, bgcolor=tcod.color.AZURE)
        >>> s = "Text with a %(1)cred%(0)c word and an %(2)cazure-background%(0) word."
        >>> fmt_s = cs.sprintf(s)
        >>> cs.apply()

    The resulting fmt_s can now be used in a Console.print*(); note that
    cs.apply() is required for defining the color set in the console -- it is
    not a bad idea to save it until just before printing the string. Note also
    that len(fmt_s) is four characters longer than the printed string -- use
    with caution.
    """
    def __init__(self):
        self.fgcolor = libtcod.white
        self.bgcolor = libtcod.black
        self.chars = {'0': libtcod.COLCTRL_STOP, '1': libtcod.COLCTRL_1, '2': libtcod.COLCTRL_2,
                      '3': libtcod.COLCTRL_3, '4': libtcod.COLCTRL_4, '5': libtcod.COLCTRL_5}
        self.colors = {libtcod.COLCTRL_1: (None, None),
                       libtcod.COLCTRL_2: (None, None),
                       libtcod.COLCTRL_3: (None, None),
                       libtcod.COLCTRL_4: (None, None),
                       libtcod.COLCTRL_5: (None, None)}

    def set_colors(self, pair_id, fgcolor=None, bgcolor=None):
        """
        Sets the color pair pair_id (0-5) to the desired colors. Note that an
        invalid pair_id will be treated as pair_id 1. pair_id 0 sets the default
        colors, which will be used to fill in {None}s in other color pairs when
        self.apply() is called.
        """
        if pair_id == 0:
            self.fgcolor = fgcolor
            self.bgcolor = bgcolor
            return

        if not(1 <= pair_id <= 5):
            pair_id = 1
        pair = self.chars[str(pair_id)]

        self.colors[pair] = (fgcolor, bgcolor)

    def sprintf(self, string):
        """
        Pass in a string using %(1)c to %(5)c for the five color pairs. Use
        %(0)c to reset to console default colors.
        """
        return string % self.chars

    def strip(self, string):
        """ Gives you string with the color control characters removed. """
        return string.translate(None, ''.join([chr(x) for x in self.chars.values()]))

    def apply(self, console=None):
        """
        Call this before rendering a string that wants to use the color pairs
        defined in this ColorSet. If you provide a console, the console's fore-
        and background will be set to the default colors.
        """
        if console:
            console.set_default_foreground(self.fgcolor)
            console.set_default_background(self.bgcolor)

        for color_code, colors in self.colors.iteritems():
            fgcolor, bgcolor = colors
            if fgcolor is None:
                fgcolor = self.fgcolor
            if bgcolor is None:
                bgcolor = self.bgcolor
            libtcod.console_set_color_control(color_code, fgcolor, bgcolor)

color_set_empty = ColorSet()

# Useful constants
class background(object):
    NONE = libtcod.BKGND_NONE
    SET = libtcod.BKGND_SET
    MULTIPLY = libtcod.BKGND_MULTIPLY
    LIGHTEN = libtcod.BKGND_LIGHTEN
    DARKEN = libtcod.BKGND_DARKEN
    SCREEN = libtcod.BKGND_SCREEN
    COLOR_DODGE = libtcod.BKGND_COLOR_DODGE
    COLOR_BURN = libtcod.BKGND_COLOR_BURN
    ADD = libtcod.BKGND_ADD
    ADDALPHA = libtcod.BKGND_ADDALPHA
    BURN = libtcod.BKGND_BURN
    OVERLAY = libtcod.BKGND_OVERLAY
    ALPHA = libtcod.BKGND_ALPHA
    DEFAULT = libtcod.BKGND_DEFAULT

class align(object):
    LEFT = libtcod.LEFT
    RIGHT = libtcod.RIGHT
    CENTER = libtcod.CENTER

class event(object):
    KEY_PRESS = libtcod.EVENT_KEY_PRESS
    KEY_RELEASE = libtcod.EVENT_KEY_RELEASE
    KEY = libtcod.EVENT_KEY
    MOUSE_MOVE = libtcod.EVENT_MOUSE_MOVE
    MOUSE_PRESS = libtcod.EVENT_MOUSE_PRESS
    MOUSE_RELEASE = libtcod.EVENT_MOUSE_RELEASE
    MOUSE = libtcod.EVENT_MOUSE
    ANY = libtcod.EVENT_ANY

Color = libtcod.Color
class color(object):
    BLACK = libtcod.black
    DARKEST_GREY = libtcod.darkest_grey
    DARKER_GREY = libtcod.darker_grey
    DARK_GREY = libtcod.dark_grey
    GREY = libtcod.grey
    LIGHT_GREY = libtcod.light_grey
    LIGHTER_GREY = libtcod.lighter_grey
    LIGHTEST_GREY = libtcod.lightest_grey
    DARKEST_GRAY = libtcod.darkest_gray
    DARKER_GRAY = libtcod.darker_gray
    DARK_GRAY = libtcod.dark_gray
    GRAY = libtcod.gray
    LIGHT_GRAY = libtcod.light_gray
    LIGHTER_GRAY = libtcod.lighter_gray
    LIGHTEST_GRAY = libtcod.lightest_gray
    WHITE = libtcod.white

    DARKEST_SEPIA = libtcod.darkest_sepia
    DARKER_SEPIA = libtcod.darker_sepia
    DARK_SEPIA = libtcod.dark_sepia
    SEPIA = libtcod.sepia
    LIGHT_SEPIA = libtcod.light_sepia
    LIGHTER_SEPIA = libtcod.lighter_sepia
    LIGHTEST_SEPIA = libtcod.lightest_sepia

    RED = libtcod.red
    FLAME = libtcod.flame
    ORANGE = libtcod.orange
    AMBER = libtcod.amber
    YELLOW = libtcod.yellow
    LIME = libtcod.lime
    CHARTREUSE = libtcod.chartreuse
    GREEN = libtcod.green
    SEA = libtcod.sea
    TURQUOISE = libtcod.turquoise
    CYAN = libtcod.cyan
    SKY = libtcod.sky
    AZURE = libtcod.azure
    BLUE = libtcod.blue
    HAN = libtcod.han
    VIOLET = libtcod.violet
    PURPLE = libtcod.purple
    FUCHSIA = libtcod.fuchsia
    MAGENTA = libtcod.magenta
    PINK = libtcod.pink
    CRIMSON = libtcod.crimson

    DARK_RED = libtcod.dark_red
    DARK_FLAME = libtcod.dark_flame
    DARK_ORANGE = libtcod.dark_orange
    DARK_AMBER = libtcod.dark_amber
    DARK_YELLOW = libtcod.dark_yellow
    DARK_LIME = libtcod.dark_lime
    DARK_CHARTREUSE = libtcod.dark_chartreuse
    DARK_GREEN = libtcod.dark_green
    DARK_SEA = libtcod.dark_sea
    DARK_TURQUOISE = libtcod.dark_turquoise
    DARK_CYAN = libtcod.dark_cyan
    DARK_SKY = libtcod.dark_sky
    DARK_AZURE = libtcod.dark_azure
    DARK_BLUE = libtcod.dark_blue
    DARK_HAN = libtcod.dark_han
    DARK_VIOLET = libtcod.dark_violet
    DARK_PURPLE = libtcod.dark_purple
    DARK_FUCHSIA = libtcod.dark_fuchsia
    DARK_MAGENTA = libtcod.dark_magenta
    DARK_PINK = libtcod.dark_pink
    DARK_CRIMSON = libtcod.dark_crimson

    DARKER_RED = libtcod.darker_red
    DARKER_FLAME = libtcod.darker_flame
    DARKER_ORANGE = libtcod.darker_orange
    DARKER_AMBER = libtcod.darker_amber
    DARKER_YELLOW = libtcod.darker_yellow
    DARKER_LIME = libtcod.darker_lime
    DARKER_CHARTREUSE = libtcod.darker_chartreuse
    DARKER_GREEN = libtcod.darker_green
    DARKER_SEA = libtcod.darker_sea
    DARKER_TURQUOISE = libtcod.darker_turquoise
    DARKER_CYAN = libtcod.darker_cyan
    DARKER_SKY = libtcod.darker_sky
    DARKER_AZURE = libtcod.darker_azure
    DARKER_BLUE = libtcod.darker_blue
    DARKER_HAN = libtcod.darker_han
    DARKER_VIOLET = libtcod.darker_violet
    DARKER_PURPLE = libtcod.darker_purple
    DARKER_FUCHSIA = libtcod.darker_fuchsia
    DARKER_MAGENTA = libtcod.darker_magenta
    DARKER_PINK = libtcod.darker_pink
    DARKER_CRIMSON = libtcod.darker_crimson

    DARKEST_RED = libtcod.darkest_red
    DARKEST_FLAME = libtcod.darkest_flame
    DARKEST_ORANGE = libtcod.darkest_orange
    DARKEST_AMBER = libtcod.darkest_amber
    DARKEST_YELLOW = libtcod.darkest_yellow
    DARKEST_LIME = libtcod.darkest_lime
    DARKEST_CHARTREUSE = libtcod.darkest_chartreuse
    DARKEST_GREEN = libtcod.darkest_green
    DARKEST_SEA = libtcod.darkest_sea
    DARKEST_TURQUOISE = libtcod.darkest_turquoise
    DARKEST_CYAN = libtcod.darkest_cyan
    DARKEST_SKY = libtcod.darkest_sky
    DARKEST_AZURE = libtcod.darkest_azure
    DARKEST_BLUE = libtcod.darkest_blue
    DARKEST_HAN = libtcod.darkest_han
    DARKEST_VIOLET = libtcod.darkest_violet
    DARKEST_PURPLE = libtcod.darkest_purple
    DARKEST_FUCHSIA = libtcod.darkest_fuchsia
    DARKEST_MAGENTA = libtcod.darkest_magenta
    DARKEST_PINK = libtcod.darkest_pink
    DARKEST_CRIMSON = libtcod.darkest_crimson

    LIGHT_RED = libtcod.light_red
    LIGHT_FLAME = libtcod.light_flame
    LIGHT_ORANGE = libtcod.light_orange
    LIGHT_AMBER = libtcod.light_amber
    LIGHT_YELLOW = libtcod.light_yellow
    LIGHT_LIME = libtcod.light_lime
    LIGHT_CHARTREUSE = libtcod.light_chartreuse
    LIGHT_GREEN = libtcod.light_green
    LIGHT_SEA = libtcod.light_sea
    LIGHT_TURQUOISE = libtcod.light_turquoise
    LIGHT_CYAN = libtcod.light_cyan
    LIGHT_SKY = libtcod.light_sky
    LIGHT_AZURE = libtcod.light_azure
    LIGHT_BLUE = libtcod.light_blue
    LIGHT_HAN = libtcod.light_han
    LIGHT_VIOLET = libtcod.light_violet
    LIGHT_PURPLE = libtcod.light_purple
    LIGHT_FUCHSIA = libtcod.light_fuchsia
    LIGHT_MAGENTA = libtcod.light_magenta
    LIGHT_PINK = libtcod.light_pink
    LIGHT_CRIMSON = libtcod.light_crimson

    LIGHTER_RED = libtcod.lighter_red
    LIGHTER_FLAME = libtcod.lighter_flame
    LIGHTER_ORANGE = libtcod.lighter_orange
    LIGHTER_AMBER = libtcod.lighter_amber
    LIGHTER_YELLOW = libtcod.lighter_yellow
    LIGHTER_LIME = libtcod.lighter_lime
    LIGHTER_CHARTREUSE = libtcod.lighter_chartreuse
    LIGHTER_GREEN = libtcod.lighter_green
    LIGHTER_SEA = libtcod.lighter_sea
    LIGHTER_TURQUOISE = libtcod.lighter_turquoise
    LIGHTER_CYAN = libtcod.lighter_cyan
    LIGHTER_SKY = libtcod.lighter_sky
    LIGHTER_AZURE = libtcod.lighter_azure
    LIGHTER_BLUE = libtcod.lighter_blue
    LIGHTER_HAN = libtcod.lighter_han
    LIGHTER_VIOLET = libtcod.lighter_violet
    LIGHTER_PURPLE = libtcod.lighter_purple
    LIGHTER_FUCHSIA = libtcod.lighter_fuchsia
    LIGHTER_MAGENTA = libtcod.lighter_magenta
    LIGHTER_PINK = libtcod.lighter_pink
    LIGHTER_CRIMSON = libtcod.lighter_crimson

    LIGHTEST_RED = libtcod.lightest_red
    LIGHTEST_FLAME = libtcod.lightest_flame
    LIGHTEST_ORANGE = libtcod.lightest_orange
    LIGHTEST_AMBER = libtcod.lightest_amber
    LIGHTEST_YELLOW = libtcod.lightest_yellow
    LIGHTEST_LIME = libtcod.lightest_lime
    LIGHTEST_CHARTREUSE = libtcod.lightest_chartreuse
    LIGHTEST_GREEN = libtcod.lightest_green
    LIGHTEST_SEA = libtcod.lightest_sea
    LIGHTEST_TURQUOISE = libtcod.lightest_turquoise
    LIGHTEST_CYAN = libtcod.lightest_cyan
    LIGHTEST_SKY = libtcod.lightest_sky
    LIGHTEST_AZURE = libtcod.lightest_azure
    LIGHTEST_BLUE = libtcod.lightest_blue
    LIGHTEST_HAN = libtcod.lightest_han
    LIGHTEST_VIOLET = libtcod.lightest_violet
    LIGHTEST_PURPLE = libtcod.lightest_purple
    LIGHTEST_FUCHSIA = libtcod.lightest_fuchsia
    LIGHTEST_MAGENTA = libtcod.lightest_magenta
    LIGHTEST_PINK = libtcod.lightest_pink
    LIGHTEST_CRIMSON = libtcod.lightest_crimson

    DESATURATED_RED = libtcod.desaturated_red
    DESATURATED_FLAME = libtcod.desaturated_flame
    DESATURATED_ORANGE = libtcod.desaturated_orange
    DESATURATED_AMBER = libtcod.desaturated_amber
    DESATURATED_YELLOW = libtcod.desaturated_yellow
    DESATURATED_LIME = libtcod.desaturated_lime
    DESATURATED_CHARTREUSE = libtcod.desaturated_chartreuse
    DESATURATED_GREEN = libtcod.desaturated_green
    DESATURATED_SEA = libtcod.desaturated_sea
    DESATURATED_TURQUOISE = libtcod.desaturated_turquoise
    DESATURATED_CYAN = libtcod.desaturated_cyan
    DESATURATED_SKY = libtcod.desaturated_sky
    DESATURATED_AZURE = libtcod.desaturated_azure
    DESATURATED_BLUE = libtcod.desaturated_blue
    DESATURATED_HAN = libtcod.desaturated_han
    DESATURATED_VIOLET = libtcod.desaturated_violet
    DESATURATED_PURPLE = libtcod.desaturated_purple
    DESATURATED_FUCHSIA = libtcod.desaturated_fuchsia
    DESATURATED_MAGENTA = libtcod.desaturated_magenta
    DESATURATED_PINK = libtcod.desaturated_pink
    DESATURATED_CRIMSON = libtcod.desaturated_crimson

    BRASS = libtcod.brass
    COPPER = libtcod.copper
    GOLD = libtcod.gold
    SILVER = libtcod.silver

    CELADON = libtcod.celadon
    PEACH = libtcod.peach

    def from_string(self, name):
        if not name:
            return self.WHITE
        if name.upper() in self.__dict__:
            return self.__dict__[name.upper()]
        return self.WHITE

class key(object):
    NONE = libtcod.KEY_NONE
    ESCAPE = libtcod.KEY_ESCAPE
    BACKSPACE = libtcod.KEY_BACKSPACE
    TAB = libtcod.KEY_TAB
    ENTER = libtcod.KEY_ENTER
    SHIFT = libtcod.KEY_SHIFT
    CONTROL = libtcod.KEY_CONTROL
    ALT = libtcod.KEY_ALT
    PAUSE = libtcod.KEY_PAUSE
    CAPSLOCK = libtcod.KEY_CAPSLOCK
    PAGEUP = libtcod.KEY_PAGEUP
    PAGEDOWN = libtcod.KEY_PAGEDOWN
    END = libtcod.KEY_END
    HOME = libtcod.KEY_HOME
    UP = libtcod.KEY_UP
    LEFT = libtcod.KEY_LEFT
    RIGHT = libtcod.KEY_RIGHT
    DOWN = libtcod.KEY_DOWN
    PRINTSCREEN = libtcod.KEY_PRINTSCREEN
    INSERT = libtcod.KEY_INSERT
    DELETE = libtcod.KEY_DELETE
    LWIN = libtcod.KEY_LWIN
    RWIN = libtcod.KEY_RWIN
    APPS = libtcod.KEY_APPS
    K0 = libtcod.KEY_0
    K1 = libtcod.KEY_1
    K2 = libtcod.KEY_2
    K3 = libtcod.KEY_3
    K4 = libtcod.KEY_4
    K5 = libtcod.KEY_5
    K6 = libtcod.KEY_6
    K7 = libtcod.KEY_7
    K8 = libtcod.KEY_8
    K9 = libtcod.KEY_9
    KP0 = libtcod.KEY_KP0
    KP1 = libtcod.KEY_KP1
    KP2 = libtcod.KEY_KP2
    KP3 = libtcod.KEY_KP3
    KP4 = libtcod.KEY_KP4
    KP5 = libtcod.KEY_KP5
    KP6 = libtcod.KEY_KP6
    KP7 = libtcod.KEY_KP7
    KP8 = libtcod.KEY_KP8
    KP9 = libtcod.KEY_KP9
    KPADD = libtcod.KEY_KPADD
    KPSUB = libtcod.KEY_KPSUB
    KPDIV = libtcod.KEY_KPDIV
    KPMUL = libtcod.KEY_KPMUL
    KPDEC = libtcod.KEY_KPDEC
    KPENTER = libtcod.KEY_KPENTER
    F1 = libtcod.KEY_F1
    F2 = libtcod.KEY_F2
    F3 = libtcod.KEY_F3
    F4 = libtcod.KEY_F4
    F5 = libtcod.KEY_F5
    F6 = libtcod.KEY_F6
    F7 = libtcod.KEY_F7
    F8 = libtcod.KEY_F8
    F9 = libtcod.KEY_F9
    F10 = libtcod.KEY_F10
    F11 = libtcod.KEY_F11
    F12 = libtcod.KEY_F12
    NUMLOCK = libtcod.KEY_NUMLOCK
    SCROLLLOCK = libtcod.KEY_SCROLLLOCK
    SPACE = libtcod.KEY_SPACE
    CHAR = libtcod.KEY_CHAR

class font(object):
    LAYOUT_ASCII_INCOL = libtcod.FONT_LAYOUT_ASCII_INCOL
    LAYOUT_ASCII_INROW = libtcod.FONT_LAYOUT_ASCII_INROW
    TYPE_GREYSCALE = libtcod.FONT_TYPE_GREYSCALE
    TYPE_GRAYSCALE = libtcod.FONT_TYPE_GRAYSCALE
    LAYOUT_TCOD = libtcod.FONT_LAYOUT_TCOD
