""" Core functions and classes for a libtcod game. Not game-specific. """

import time
import tcod

con = tcod.Console(80, 25)

def main_menu():
    con.set_default_foreground(tcod.color.WHITE)
    con.print_rect_ex(text="Hello, world!")

    con.blit()
    tcod.flush()

    time.sleep(1)
