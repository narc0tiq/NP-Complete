""" User Interface bits and widgets """
import collections

import tcod
from game import events, utils

class Widget(object):
    """
    A widget is something that knows how to render itself. All things that know
    how to render themselves are widgets.

    Widgets may have child widgets; when a widget is told to render itself, it
    asks its children to render themselves. Widgets may receive events; if an
    event is handled by a widget, it should return True. Otherwise, the event
    should be pased along to children, returning True if one of the children
    handled it, or False otherwise.

    Widgets who are initialized knowing who their parent is will automatically
    register themselves with their parent.

    Widgets all exist in a console; on initialization, widgets not given a
    console will make a good-faith effort and assume their console is their
    parent's. At render time, a widget that still does not know what its
    console is will assume it is tcod.root_console.

    Coordinates (in self.rect) are parent-relative (unless there's no parent,
    in which case, they are console-relative).
    """

    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0, color_set=None):
        self.parent = parent
        self.child_dict = collections.OrderedDict()
        self.children = self.child_dict.viewkeys()
        self.console = console
        self.fgcolor = tcod.color.WHITE
        self.bgcolor = tcod.color.BLACK
        self.color_set = color_set

        if self.parent is not None:
            if self.console is None:
                self.console = self.parent.console
            self.parent.register_child(self)

        if self.console is None: #, even after all that,
            self.console = tcod.root_console

        self.rect = utils.Rect(x, y, width, height)

    def register_child(self, child):
        child.parent = self
        self.child_dict[child] = None

    def point_to_screen(self, point):
        """ Translates a Point(x,y) inside this widget into screen coordinates """
        x = point.x + self.rect.left
        y = point.y + self.rect.top

        if self.parent:
            return self.parent.point_to_screen(utils.Point(x,y))
        else:
            return utils.Point(x,y)

    def screen_to_point(self, point):
        """
        Translates a Point(x,y) in screen coordinates into a point inside this
        widget. Inverse of self.point_to_screen().
        """
        x = point.x - self.rect.left
        y = point.y - self.rect.top

        if self.parent:
            return self.parent.screen_to_point(utils.Point(x,y))
        else:
            return utils.Point(x,y)

    def render(self):
        """ The default implementation just asks children to render. """
        for child in self.children:
            child.render()

    def handle_event(self, ev):
        """
        The default implementation just asks children if they want it. If they
        return True, they did.
        """
        for child in self.children:
            if child.handle_event(ev):
                return True

        return False

    def center_in_parent(self, horizontal=True, vertical=True):
        if self.parent is None:
            raise ValueError("Widget trying to center in non-existent parent")
        if horizontal:
            self.rect.left = (self.parent.rect.width - self.rect.width) / 2
        if vertical:
            self.rect.top = (self. parent.rect.height - self.rect.height) / 2

    def center_in_console(self, horizontal=True, vertical=True):
        if horizontal:
            self.rect.left = (self.console.width - self.rect.width) / 2
        if vertical:
            self.rect.top = (self.console.height - self.rect.height) / 2

class Image(Widget):
    def __init__(self, path, parent=None, console=None, x=0, y=0, width=0, height=0):
        super(Image, self).__init__(parent, console, x, y, width, height)
        self.image = tcod.ImageFile(path)

    def render(self):
        self.image.blit_2x(self.console)
        super(Image, self).render()

class Label(Widget):
    def __init__(self, parent=None, console=None, x=0, y=0, text="", width=0, color_set=None):
        super(Label, self).__init__(parent, console, x, y, width, height=0, color_set=color_set)
        self.max_width = width
        self._text = text
        self.align = tcod.align.LEFT
        self.effect = tcod.background.SET

        self.calc_size()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.calc_size()

    def calc_size(self):
        text = self._text
        if self.color_set is not None:
            text = self.color_set.strip(self._text)

        width = self.rect.width
        if self.max_width < 1:
            width = min(len(text), self.console.width - self.rect.left)
        height = self.console.get_height_rect(self.rect.left, self.rect.top,
                                              width, text=self._text)
        self.rect.resize(width=width, height=height)

    def render(self):
        if self.color_set is not None:
            self.color_set.set_colors(0, self.fgcolor, self.bgcolor)
            self.color_set.apply()

        x,y = self.point_to_screen(utils.origin)

        self.console.set_default_foreground(self.fgcolor)
        self.console.set_default_background(self.bgcolor)
        self.console.print_rect_ex(x, y, self.rect.width, self.rect.height,
                                   self.effect, self.align, self._text)

        super(Label, self).render()

button_cs = tcod.ColorSet()
button_cs.set_colors(1, fgcolor=tcod.color.LIME)

class Button(Widget):
    def __init__(self, shortcut, label, parent=None, console=None, x=0, y=0, width=0,
                 key_trigger=None, action=None, color_set=None):
        super(Button, self).__init__(parent, console, x, y, width, height=1, color_set=color_set)
        self.key_trigger = key_trigger
        self.action = action
        if self.color_set is None:
            self.color_set = button_cs

        label_text = self.color_set.sprintf("%(1)c" + shortcut + "%(0)c " + label)
        self.label = Label(parent=self, x=1, text=label_text)
        if self.rect.width < 1:
            self.rect.resize(width=self.label.rect.width)
        elif self.rect.width < self.label.rect.width:
            raise ValueError("Button's assigned width is insufficient!")
        else:
            self.label.center_in_parent()

    def render(self):
        self.color_set.apply()

        self.console.set_default_background(self.bgcolor)
        origin = self.point_to_screen(utils.origin)
        self.console.rect(origin.x, origin.y, width=self.rect.width, height=1)

        super(Button, self).render()

        self.console.set_default_foreground(self.fgcolor)
        self.console.put_char(origin.x, origin.y, '[')
        self.console.put_char(origin.x + self.rect.width - 1, origin.y, ']')

    def handle_event(self, ev):
        if(self.action is not None and ev.type is events.KEY and
           self.key_trigger is not None and self.key_trigger(ev.data)):
            self.action()
            return True

        super(Button, self).handle_event(ev)

class ListItem(Label):
    def __init__(self, parent, label, disabled=False, on_activate=None):
        self.disabled = disabled
        self.on_activate = on_activate

        pos = parent.next_item_pos()
        width = parent.max_width
        super(ListItem, self).__init__(parent, parent.sub_console,
                                       x=pos.x, y=pos.y, width=width,
                                       text=label, color_set=parent.color_set)


    def point_to_screen(self, point):
        x = point.x + self.rect.left
        y = point.y + self.rect.top

        return utils.Point(x,y)

    def calc_size(self):
        super(ListItem, self).calc_size()
        self.parent.notify_resize(self)

    def handle_event(self, ev):
        if ev.type == events.KEY and ev.data.vk == tcod.key.ENTER:
            if self.on_activate:
                self.on_activate(self)
            return True

        return super(ListItem, self).handle_event(ev)

    def render(self):
        self.console.set_default_background(self.bgcolor)
        self.console.rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height, clear=True)
        super(ListItem, self).render()

options_cs = tcod.ColorSet()
options_cs.set_colors(1, fgcolor=tcod.color.LIME)

class OptionsListItem(ListItem):
    def __init__(self, parent, on_label, on_event):
        super(OptionsListItem, self).__init__(parent, label=on_label())
        self.on_label = on_label
        self.on_event = on_event
        if self.color_set is None:
            self.color_set = options_cs

    def handle_event(self, ev):
        if self.on_event(ev):
            self.text = self.on_label()
            return True

        return super(OptionsListItem, self).handle_event(ev)

class List(Widget):
    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0, color_set=None):
        super(List, self).__init__(parent, console, x, y, 0, 0, color_set=color_set)
        self.max_width = max(0, width-1) # leave 1 character of width for the scrollbar, if fixed-width
        self.max_height = height
        self.selected_item = None
        self.sub_console = tcod.Console(max(self.max_width, 20), max(self.max_height, 10))
        self.scroll_top = 0
        self.selected_bgcolor = tcod.color.AZURE
        self.disabled_fgcolor = tcod.color.DARK_GREY
        self.last_child = None

    def register_child(self, child):
        self.last_child = child

        try:
            if self.selected_item is None and not child.disabled:
                self.selected_item = child
        except AttributeError:
            pass

        super(List, self).register_child(child)

    def add_item(self, label, disabled=False, on_activate=None):
        li = ListItem(parent=self, label=label, disabled=disabled, on_activate=on_activate)

        return li

    def next_item_pos(self):
        if self.last_child is None:
            return utils.origin
        else:
            return utils.Point(0, self.last_child.rect.bottom)

    def notify_resize(self, child):
        for other in (x for x in self.children if x.rect.top > child.rect.top):
            other.rect.top = child.rect.bottom
            child = other

        self.recalc_size()

    def recalc_size(self):
        width = max([x.rect.width for x in self.children])
        height = self.last_child.rect.bottom if self.last_child is not None else 0
        self.rect.resize(width, height)

    def scroll_by(self, amount):
        self.scroll_top += amount

    def scroll_to(self, top, bottom=None):
        if self.max_height < 1:
            return # Nothing to do for variable height lists.

        scroll_bottom = self.scroll_top + self.max_height
        if top < self.scroll_top: # scroll up
            self.scroll_by(top - self.scroll_top)
        elif bottom is not None and bottom > scroll_bottom: # scroll down
            self.scroll_by(bottom - scroll_bottom)

    def render(self):
        if self.rect.width < 1 or self.rect.height < 1:
            self.recalc_size()

        self.sub_console.grow(self.rect.width, self.rect.height)

        draw_width = self.max_width+1 if self.max_width > 0 else self.rect.width
        draw_height = self.max_height if self.max_height > 0 else self.rect.height

        if self.color_set is not None:
            self.color_set.apply()

        origin = self.point_to_screen(utils.origin)
        self.console.rect(origin.x, origin.y, draw_width, draw_height, clear=True)

        self.sub_console.set_default_background(self.bgcolor)
        self.sub_console.clear()
        for child in self.children:
            child.bgcolor = self.bgcolor
            if self.selected_item is child:
                child.bgcolor = self.selected_bgcolor
                self.scroll_to(child.rect.top, child.rect.bottom)

            if child.disabled:
                child.fgcolor = self.disabled_fgcolor
            else:
                child.fgcolor = self.fgcolor

            child.render()

        self.sub_console.blit(0, self.scroll_top,
                              draw_width, draw_height,
                              self.console, origin.x, origin.y)

    def handle_event(self, ev):
        if self.selected_item is not None:
            if ev.type == events.KEY and ev.data.vk in (tcod.key.DOWN, tcod.key.UP):
                children = list(self.children)
                selected_index = children.index(self.selected_item)
                if ev.data.vk == tcod.key.DOWN and (selected_index+1) < len(self.children):
                    self.selected_item = children[selected_index + 1]
                elif ev.data.vk == tcod.key.UP and selected_index > 0:
                    self.selected_item = children[selected_index - 1]
                return True
            else:
                return self.selected_item.handle_event(ev)

        return super(List, self).handle_event(ev)

class Dialog(Widget):
    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0):
        super(Dialog, self).__init__(parent, console, x, y, width, height)

    def render(self):
        self.console.set_default_foreground(self.fgcolor)
        self.console.set_default_background(self.bgcolor)
        self.console.print_frame(self.rect.left, self.rect.top, self.rect.width, self.rect.height)
        super(Dialog, self).render()

menu_cs = tcod.ColorSet()
menu_cs.set_colors(1, fgcolor=tcod.color.LIME)
menu_cs.set_colors(2, fgcolor=tcod.color.LIGHT_GREY)

class Menu(Dialog):
    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0, color_set=None):
        super(Menu, self).__init__(parent, console, x, y, width, height)
        self.max_width = width
        self.max_height = height
        self.list = List(parent=self, x=x+1, y=y+1, width=max(0, width-2), height=max(0, height-2))
        self.keys = {}
        self.color_set = color_set
        if self.color_set is None:
            self.color_set = menu_cs
        self.list.color_set = self.color_set

    def add_item(self, key, label, disabled=False, on_activate=None):
        parts = label.partition(key)
        if parts[1] == '':
            parts = (label + ' (', key, ')')

        color_part = '%(1)c'
        if disabled:
            color_part = '%(2)c'

        label_text = self.color_set.sprintf(''.join((parts[0], color_part, parts[1], '%(0)c', parts[2])))

        item = self.list.add_item(label_text, disabled, on_activate)
        self.calc_size()
        self.keys[key] = item
        return item

    @property
    def selected_item(self):
        return self.list.selected_item

    def calc_size(self):
        self.list.recalc_size()
        if self.max_width < 1:
            self.rect.width = self.list.rect.width + 2
        if self.max_height < 1:
            self.rect.height = self.list.rect.height + 2

    def render(self):
        self.color_set.apply()
        super(Menu, self).render()

    def handle_event(self, ev):
        if ev.type == events.KEY and chr(ev.data.c) in self.keys:
            self.list.selected_item = self.keys[chr(ev.data.c)]
            return True

        return super(Menu, self).handle_event(ev)
