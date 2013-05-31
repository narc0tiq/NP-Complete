""" Core functions and classes for a libtcod game. Not game-specific. """
import time

import tcod
from game import config, events, widgets, dialogs

def slow_print(widget, text, y=1):
    label = widgets.Label(parent=widget, y=y, text=text)
    label.center_in_parent(vertical=False)
    label.text = ""

    for char in text:
        label.text = label.text + char

        widget.render()
        tcod.flush() # Relying on the tcod.set_fps_limit() from earlier to limit our render rate
        key, mouse = tcod.check_for_event(tcod.event.KEY_PRESS | tcod.event.MOUSE_PRESS)
        if key.vk != tcod.key.NONE or mouse.lbutton or mouse.rbutton:
            label.text = text
            widget.render()
            return

def main_menu():
    top = widgets.Image(path="menu_bg.png", width=tcod.root_console.width, height=tcod.root_console.height)

    slow_print(top, "NP-Complete")
    time.sleep(0.2)
    slow_print(top, "Survival is a Hard problem", y=2)

    m = widgets.Menu(parent=top)
    m.add_item("n", "new game")
    m.add_item("l", "load game", disabled=True)
    m.add_item("O", "Options", on_activate=lambda w: events.post(events.LAUNCH, options_menu))
    m.add_item("M", "Mods", disabled=True)
    m.add_item("q", "quit", on_activate=lambda w: events.post(events.QUIT))
    m.center_in_parent()

    dialogs.main_loop(top)

def options_menu():
    top = widgets.Dialog(width=55, height=30)
    top.center_in_console()

    title = widgets.Label(parent=top, x=2, text="Options")

    b = widgets.Button(parent=top, y=top.rect.height-1,
                       label="Back to menu", key="Esc",
                       action=lambda: events.post(events.OK))
    b.rect.right = top.rect.width - 2

    options = widgets.List(parent=top, x=1, y=1, width=20, height=28)
    widgets.OptionsListItem(options, on_label=config.int_option_formatter("Window width", "core", "width"),
                            on_event=config.int_option_handler("core", "width", minimum=80))
    widgets.OptionsListItem(options, on_label=config.int_option_formatter("Window height", "core", "height"),
                            on_event=config.int_option_handler("core", "height", minimum=25))
    widgets.OptionsListItem(options, on_label=config.boolean_option_formatter("Fullscreen", "core", "fullscreen"),
                            on_event=config.boolean_option_handler("core", "fullscreen"))
    widgets.OptionsListItem(options, on_label=config.string_option_formatter("Activate key", "keys", "activate"),
                            on_event=config.key_option_handler("keys", "activate"))

    dialogs.main_loop(top, dialog=True)
