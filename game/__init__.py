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

    menu = widgets.Widget(width=tcod.root_console.width, height=tcod.root_console.height)
    slow_print(menu, "NP-Complete")
    time.sleep(0.2)
    slow_print(menu, "Survival is a Hard problem", y=2)

    tcod.wait_for_keypress(True)
