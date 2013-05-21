""" Core functions and classes for a libtcod game. Not game-specific. """
import time

import tcod
from game import config, events, widgets

def slow_print(widget, text, y=1):
    label = widgets.Label(parent=widget, y=y, text=text)
    label.center_in_parent(vertical=False)
    label.text = ""

    for char in text:
        label.text = label.text + char

        widget.render()
        tcod.flush() # Relying on the tcod.set_fps_limit() from earlier to limit our render rate

def get_input():
    """ Grab the mouse and all the key events from libtcod and {events.post} them. """
    key, mouse = tcod.check_for_event(tcod.event.KEY_PRESS | tcod.event.MOUSE)
    events.post(events.MOUSE, mouse)
    while key.vk != tcod.key.NONE:
        events.post(events.KEY, key)
        key, mouse = tcod.check_for_event(tcod.event.KEY_PRESS)

def main_loop(top, dialog=False):
    while True:
        top.render()
        tcod.flush()

        # Get the input...
        get_input()
        if tcod.is_window_closed():
            events.post(events.QUIT)

        # ...and handle it:
        for event in events.generator():
            if event.type is events.QUIT:
                # Repost the quit event to break out of all the loops.
                events.post(events.QUIT)
                return
            elif dialog and event.type in {events.OK, events.CANCEL}:
                return
            elif event.type is events.LAUNCH:
                event.data()
            else:
                top.handle_event(event)

def main_menu():
    top = widgets.Image(path="menu_bg.png", width=tcod.root_console.width, height=tcod.root_console.height)

    slow_print(top, "NP-Complete")
    time.sleep(0.2)
    slow_print(top, "Survival is a Hard problem", y=2)

    m = widgets.Menu(parent=top)
    m.add_item("n", "new game")
    m.add_item("l", "load game", disabled=True)
    m.add_item("O", "Options", on_activate=lambda: events.post(events.LAUNCH, options_menu))
    m.add_item("M", "Mods", disabled=True)
    m.add_item("q", "quit", on_activate=lambda: events.post(events.QUIT))
    m.center_in_parent()

    main_loop(top)

def options_menu():
    top = widgets.Dialog(width=55, height=30)
    top.center_in_console()

    title = widgets.Label(parent=top, x=2, text="Options")

    b = widgets.Button(parent=top, y=top.rect.height-1,
                       label="Cancel", shortcut="{Esc}",
                       key_trigger=lambda k: k.vk==tcod.key.ESCAPE,
                       action=lambda: events.post(events.CANCEL))
    b.rect.right = top.rect.width - 2
    b2 = widgets.Button(parent=top, y=top.rect.height-1,
                        label="OK", shortcut="{Shift+Enter}",
                        key_trigger=lambda k: k.shift and k.vk==tcod.key.ENTER,
                        action=lambda: events.post(events.OK))
    b2.rect.right = b.rect.left - 1
    b3 = widgets.Button(parent=top, y=top.rect.height-1,
                        label="Apply", shortcut="{Enter}",
                        key_trigger=lambda k: k.vk==tcod.key.ENTER)
    b3.rect.right = b2.rect.left - 1

    options = widgets.List(parent=top, x=1, y=1, width=20, height=28)
    options.add_item("Window width: %d" % config.parser.getint("core", "width"))
    options.add_item("Window height: %d" % config.parser.getint("core", "height"))
    options.add_item("Fullscreen: %s" % config.parser.getboolean("core", "fullscreen"))

    main_loop(top, dialog=True)
