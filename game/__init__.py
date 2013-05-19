""" Core functions and classes for a libtcod game. Not game-specific. """
import time

import tcod
from game import widgets

def slow_print(widget, text, y=1):
    label = widgets.Label(parent=widget, y=y, text=text)
    label.hcenter_in_parent()
    label.text = ""

    for char in text:
        label.text = label.text + char

        widget.render()
        tcod.flush()
        time.sleep(0.05)

def main_menu():
    img = tcod.ImageFile("menu_bg.png")
    img.blit_2x(tcod.root_console)
    tcod.root_console.set_default_foreground(tcod.color.WHITE)
    tcod.root_console.set_default_background(tcod.color.BLACK)

    top = widgets.Widget(width=tcod.root_console.width, height=tcod.root_console.height)
    slow_print(top, "NP-Complete")
    time.sleep(0.2)
    slow_print(top, "Survival is a Hard problem", y=2)

    l = widgets.List(parent=top)
    l.add_item("New game")
    l.add_item("Load game", disabled=True)
    quit_item = l.add_item("Quit")
    l.hcenter_in_parent()
    l.vcenter_in_parent()

    quitting = False
    while not quitting:
        l.render()
        tcod.flush()

        key, mouse = tcod.wait_for_event(tcod.event.KEY_PRESS)
        if tcod.is_window_closed():
            quitting = True
        elif key.vk == tcod.key.ENTER:
            if l.selected_item is quit_item:
                quitting = True
        else:
            l.handle_event(widgets.event.KEY, key)
