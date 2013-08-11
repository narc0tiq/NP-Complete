import types

import tcod
from game import events, widgets, utils

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
                return event.data
            elif event.type is events.LAUNCH:
                event.data()
            else:
                top.dispatch(event)

def keybind_dialog():
    top = widgets.Dialog(width=40, height=3)
    top.center_in_console()

    title = widgets.Label(parent=top, x=2, text="Keybind Capture")

    l = widgets.Label(parent=top, x=1, y=1, text="Press a key (Esc to cancel)...", width=38)
    def on_key(ev):
        if utils.key_check("Esc")(ev.data):
            events.post(events.CANCEL)
        else:
            name = utils.name_key(ev.data)
            if name is not None:
                events.post(events.OK, name)
        return True
    l.handlers[events.KEY] = on_key

    return main_loop(top, dialog=True)

