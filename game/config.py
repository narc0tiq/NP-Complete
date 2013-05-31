import ConfigParser, os, atexit
from datetime import datetime as dt

import tcod
from game import events, dialogs

parser = ConfigParser.SafeConfigParser()
with open("data/defaults.cfg") as f:
    parser.readfp(f)
parser.read(["data/config.cfg", os.path.expanduser("~/.NP-Complete/data/config.cfg")])

def int_option_formatter(label, section, option):
    def formatter():
        value = parser.getint(section, option)
        s = '%s: %%(1)c%d%%(0)c' % (label, value)
        return tcod.color_set_empty.sprintf(s)
    return formatter

def boolean_option_formatter(label, section, option):
    def formatter():
        value = parser.getboolean(section, option)
        s = '%s: %%(1)c%s%%(0)c' % (label, "Enabled" if value else "Disabled")
        return tcod.color_set_empty.sprintf(s)
    return formatter

def string_option_formatter(label, section, option):
    def formatter():
        try:
            value = parser.get(section, option)
        except:
            s = '%s: %%(3)cUnset%%(0)c' % label
        else:
            s = '%s: %%(1)c%s%%(0)c' % (label, value)
        return tcod.color_set_empty.sprintf(s)
    return formatter

def int_option_handler(section, option, minimum=None, maximum=None):
    def handler(event):
        if event.type is events.KEY and event.data.vk in (tcod.key.LEFT, tcod.key.RIGHT):
            value = parser.getint(section, option)
            if event.data.vk == tcod.key.LEFT and (minimum is None or value > minimum):
                value -= 1
            elif event.data.vk == tcod.key.RIGHT and (maximum is None or value < maximum):
                value += 1
            parser.set(section, option, str(value))
            return True
        return False
    return handler

def boolean_option_handler(section, option):
    def handler(event):
        if event.type is events.KEY and event.data.vk in (tcod.key.ENTER, tcod.key.LEFT, tcod.key.RIGHT):
            value = True
            if event.data.vk == tcod.key.ENTER:
                value = not parser.getboolean(section, option)
            elif event.data.vk == tcod.key.LEFT:
                value = False
            parser.set(section, option, "yes" if value else "no")
            return True
        return False
    return handler

def key_option_handler(section, option):
    def handler(event):
        if event.type is events.KEY:
            if event.data.vk in (tcod.key.BACKSPACE, tcod.key.LEFT):
                parser.set(section, option, 'None')
            elif event.data.vk in (tcod.key.ENTER, tcod.key.RIGHT):
                value = dialogs.keybind_dialog()
                if value:
                    parser.set(section, option, value)
            return True
        return False
    return handler

@atexit.register
def save():
    try:
        with open("data/config.cfg", "w") as f:
            f.write("# Generated %s\n\n" % dt.now().ctime())
            parser.write(f)
    except IOError:
        with open("~/.NP-Complete/data/config.cfg", "w") as f:
            parser.write(f)
