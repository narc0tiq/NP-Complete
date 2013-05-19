""" Core functions and classes for a libtcod game. Not game-specific. """
import time

import tcod
from game import events, widgets

def slow_print(widget, text, y=1):
    label = widgets.Label(parent=widget, y=y, text=text)
    label.hcenter_in_parent()
    label.text = ""

    for char in text:
        label.text = label.text + char

        widget.render()
        tcod.flush()
        time.sleep(0.05)

def get_keys():
    """ Grab all the key events from libtcod and {events.post} them. """
    key, mouse = tcod.check_for_event(tcod.event.KEY_PRESS)
    while key.vk != tcod.key.NONE:
        events.post(events.KEY, key)
        key, mouse = tcod.check_for_event(tcod.event.KEY_PRESS)

def main_menu():
    img = tcod.ImageFile("menu_bg.png")
    img.blit_2x(tcod.root_console)
    tcod.root_console.set_default_foreground(tcod.color.WHITE)
    tcod.root_console.set_default_background(tcod.color.BLACK)

    top = widgets.Widget(width=tcod.root_console.width, height=tcod.root_console.height)
    slow_print(top, "NP-Complete")
    time.sleep(0.2)
    slow_print(top, "Survival is a Hard problem", y=2)

    m = widgets.Menu(parent=top)
    m.add_item("n", "New game")
    m.add_item("l", "Load game", disabled=True)
    quit_item = m.add_item("q", "Quit", on_activate=lambda: events.post(events.QUIT))
    m.hcenter_in_parent()
    m.vcenter_in_parent()

    quitting = False
    while not quitting:
        m.render()
        tcod.flush()

        # Get the input...
        get_keys()
        if tcod.is_window_closed():
            events.post(events.QUIT)

        # ...and handle it:
        for event in events.generator():
            if event.type == events.QUIT:
                quitting = True
            else:
                top.handle_event(event)
