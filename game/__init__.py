""" Core functions and classes for a libtcod game. Not game-specific. """
import time, types

import tcod
from game import config, events, widgets, dialogs


def slow_print(widget, text, y=1):
    label = widgets.Label(parent=widget, y=y, text=text)
    label.center(vertical=False)
    label.text = ""

    for char in text:
        label.text = label.text + char

        widget.render()
        tcod.flush()  # Relying on the tcod.set_fps_limit() from earlier to limit our render rate
        key, mouse = tcod.check_for_event(tcod.event.KEY_PRESS | tcod.event.MOUSE_PRESS)
        if key.vk != tcod.key.NONE or mouse.lbutton or mouse.rbutton:
            label.text = text
            widget.render()
            return


def main_menu():
    print tcod.root_console.width, tcod.root_console.height
    top = widgets.Image(path="menu_bg.png",
                        width=tcod.root_console.width, height=tcod.root_console.height)

    slow_print(top, "NP-Complete")
    time.sleep(0.2)
    slow_print(top, "Survival is a Hard problem", y=2)

    m = widgets.List(parent=top)
    widgets.Label(parent=m, text="This is a test")
    widgets.Label(parent=m, text="Hello.")
    m.selected_child = m.children.last
    widgets.Label(parent=m, text="Another long thing.")
#    m.add_item("n", "new game")
#    m.add_item("l", "load game", disabled=True)
#    m.add_item("O", "Options", on_activate=lambda w: events.post(events.LAUNCH, options_menu))
#    m.add_item("M", "Mods", disabled=True)
#    m.add_item("q", "quit", on_activate=lambda w: events.post(events.QUIT))
    m.center()

    dialogs.main_loop(top)


def options_menu():
    top = widgets.Dialog(width=55, height=tcod.root_console.height - 6)
    top.center_in_console()

    widgets.Label(parent=top, x=2, text="Options")

    b = widgets.Button(parent=top, y=top.rect.height - 1,
                       label="Back to menu", key="Esc",
                       action=lambda: events.post(events.OK))
    b.rect.right = top.rect.width - 2

    cs = tcod.ColorSet()
    cs.set_colors(1, fgcolor=tcod.color.LIME)
    cs.set_colors(2, fgcolor=tcod.color.AMBER)

    options = widgets.List(parent=top, x=1, y=1, width=23, height=top.rect.height - 2)
    widgets.OptionsListItem(options, on_label=config.int_option_formatter("Window width", "core", "width"),
                            on_event=config.int_option_handler("core", "width", minimum=80),
                            description=cs.sprintf("The width of the window, if fullscreen is disabled.\n"
                                                   "%(2)cThe game must be restarted for this change to take effect!%(0)c\n"
                                                   "Minimum: %(1)c80%(0)c"))
    widgets.OptionsListItem(options, on_label=config.int_option_formatter("Window height", "core", "height"),
                            on_event=config.int_option_handler("core", "height", minimum=25),
                            description=cs.sprintf("The height of the window, if fullscreen is disabled.\n"
                                                   "%(2)cThe game must be restarted for this change to take effect!%(0)c\n"
                                                   "Minimum: %(1)c25%(0)c"))
    widgets.OptionsListItem(options, on_label=config.boolean_option_formatter("Fullscreen", "core", "fullscreen"),
                            on_event=config.boolean_option_handler("core", "fullscreen"),
                            description=cs.sprintf("Run the game in full-screen mode.\n"
                                                   "%(2)cThe game must be restarted for this change to take effect!%(0)c"))
    widgets.OptionsListItem(options, on_label=config.string_option_formatter("Activate key", "keys", "activate"),
                            on_event=config.key_option_handler("keys", "activate"),
                            description=cs.sprintf("The key used to activate various items (e.g. selecting an item from a list of items).\n"
                                                   "Default: %(1)cNumEnter%(0)c"))

    l = widgets.Label(parent=top, x=25, y=1, width=29, color_set=cs,
                      text=cs.sprintf("%(1)cUp%(0)c/%(1)cDown%(0)c to select an option,\n%(1)cLeft%(0)c/%(1)cRight%(0)c or %(1)cEnter%(0)c to adjust.\n\n"
                                      "Options take effect immediately, unless otherwise noted."))
    description = widgets.Label(parent=top, x=25, width=28, color_set=cs)
    description.rect.top = l.rect.bottom + 1

    def option_event(self, event):
        result = widgets.List.handle_event(self, event)
        description.text = self.selected_item.description
        return result
    options.handle_event = types.MethodType(option_event, options, widgets.List)

    dialogs.main_loop(top, dialog=True)
