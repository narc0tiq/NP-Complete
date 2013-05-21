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
        self.children = []
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
        self.children.append(child)

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
            self.color_set.apply()

        x,y = self.point_to_screen(utils.origin)

        self.console.set_default_foreground(self.fgcolor)
        self.console.set_default_background(self.bgcolor)
        self.console.print_rect_ex(x, y, self.rect.width, self.rect.height,
                                   self.effect, self.align, self._text)

        super(Label, self).render()

class Button(Widget):
    def __init__(self, label, parent=None, console=None, x=0, y=0, width=0,
                 key_trigger=None, action=None, color_set=None):
        super(Button, self).__init__(parent, console, x, y, width, height=1, color_set=color_set)
        self.key_trigger = key_trigger
        self.action = action
        self.shortcut_fgcolor = tcod.color.LIME

        self.label = Label(parent=self, x=1, text=label)
        if self.rect.width < 1:
            self.rect.resize(width=self.label.rect.width)
        elif self.rect.width < self.label.rect.width:
            raise ValueError("Button's assigned width is insufficient!")
        else:
            self.label.center_in_parent()

    def render(self):
        if self.color_set is not None:
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

ListItem = collections.namedtuple("ListItem", ["label", "disabled", "on_activate"])

class List(Widget):
    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0, color_set=None):
        super(List, self).__init__(parent, console, x, y, 0, 0, color_set=color_set)
        self.init_width = max(0, width-1) # leave 1 character of width for the scrollbar, if fixed-width
        self.init_height = height
        self.items = []
        self.selected_item = None
        self.sub_console = None
        self.scroll_y = 0
        self.render_item_override = None
        self.selected_bgcolor = tcod.color.AZURE
        self.disabled_fgcolor = tcod.color.DARK_GREY

    def add_item(self, label, disabled=False, on_activate=None):
        """
        Warning: Trying to add_item() after the list has been rendered is
        currently unsupported.
        """
        if self.sub_console is not None:
            raise AttributeError("Trying to add items to a list after offscreen surface created.")

        li = ListItem(label, disabled, on_activate)

        self.items.append(li)
        if self.selected_item is None and not li.disabled:
            self.selected_item = li

        self._calc_size(li)
        return li

    def _calc_size(self, item):
        """
        Recalculates the size of the offscreen surface to include the size of
        the given item. self.add_item() will automatically call this, as will
        self.recalc_size().
        """
        self.rect.height += self.console.get_height_rect(self.rect.left, self.rect.top,
                                                         self.init_width,
                                                         text=item.label)

        label_text = item.label
        if self.color_set is not None:
            label_text = self.color_set.strip(item.label)

        if self.init_width > 0:
            self.rect.width = self.init_width
        elif len(label_text) > self.rect.width:
            self.rect.width = len(label_text)

    def recalc_size(self):
        """ Call this if you edited self.items without using self.add_item() """
        if self.sub_console is not None:
            raise AttributeError("Trying to resize list after offscreen surface created.")

        self.rect.resize(0, 0)
        for item in self.items:
            self._calc_size(item)


    def scroll_by(self, amount):
        self.scroll_y += amount

    def scroll_to(self, y, height=1):
        if self.init_height < 1:
            return # Nothing to do for variable height lists.

        scroll_bottom = self.scroll_y + self.init_height
        if y < self.scroll_y: # scroll up
            self.scroll_by(y - self.scroll_y)
        elif y+height > scroll_bottom: # scroll down
            self.scroll_by(y+height - scroll_bottom)

    def render(self):
        """
        Note that the first render creates an offscreen surface, which is never
        re-created; self.add_item() and self.recalc_size() will refuse to
        operate.
        """
        if self.color_set is not None:
            self.color_set.apply()

        if self.sub_console is None:
            self.sub_console = tcod.Console(self.rect.width, self.rect.height)

        draw_width = self.init_width+1 if self.init_width > 0 else self.rect.width
        draw_height = self.init_height if self.init_height > 0 else self.rect.height

        origin = self.point_to_screen(utils.origin)
        self.console.rect(origin.x, origin.y, draw_width, draw_height, clear=True)

        y = 0
        for i in self.items:
            height = self.sub_console.get_height_rect(0, y, text=i.label)

            bgcolor = self.bgcolor
            if self.selected_item is i:
                bgcolor = self.selected_bgcolor
                self.scroll_to(y, height)
            self.sub_console.set_default_background(bgcolor)
            self.sub_console.rect(0, y, self.rect.width, height, clear=True)
            self.sub_console.set_default_background(self.bgcolor)

            if i.disabled:
                self.sub_console.set_default_foreground(self.disabled_fgcolor)
            else:
                self.sub_console.set_default_foreground(self.fgcolor)

            self.sub_console.print_rect_ex(0, y, text=i.label)
            if self.render_item_override:
                self.render_item_override(self.sub_console, i, 0, y, self.rect.width, height)
            y += height

        self.sub_console.blit(0, self.scroll_y,
                              draw_width, draw_height,
                              self.console, origin.x, origin.y)

    def handle_event(self, ev):
        if ev.type == events.KEY:
            selected_index = self.items.index(self.selected_item)
            if ev.data.vk == tcod.key.DOWN and (selected_index+1) < len(self.items):
                self.selected_item = self.items[selected_index + 1]
                return True
            elif ev.data.vk == tcod.key.UP and selected_index > 0:
                self.selected_item = self.items[selected_index - 1]
                return True
            elif ev.data.vk == tcod.key.ENTER and self.selected_item.on_activate:
                self.selected_item.on_activate()
                return True

        return super(List, self).handle_event(ev)

class Dialog(Widget):
    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0):
        super(Dialog, self).__init__(parent, console, x, y, width, height)

    def render(self):
        self.console.set_default_foreground(self.fgcolor)
        self.console.set_default_background(self.bgcolor)
        self.console.print_frame(self.rect.left, self.rect.top, self.rect.width, self.rect.height)
        super(Dialog, self).render()

class Menu(Dialog):
    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0):
        super(Menu, self).__init__(parent, console, x, y, width, height)
        self.init_width = width
        self.init_height = height
        self.list = List(parent=self, x=x+1, y=y+1, width=max(0, width-2), height=max(0, height-2))
        self.list.render_item_override = self.render_item
        self.keys = {}
        self.shortcut_fgcolor = tcod.color.LIME
        self.disabled_shortcut_fgcolor = tcod.color.LIGHT_GREY

    def add_item(self, key, label, disabled=False, on_activate=None):
        label = key + " " + label
        item = self.list.add_item(label, disabled, on_activate)
        self.calc_size()
        self.keys[key] = item
        return item

    @property
    def selected_item(self):
        return self.list.selected_item

    def calc_size(self):
        if self.init_width < 1:
            self.rect.width = self.list.rect.width + 2
        if self.init_height < 1:
            self.rect.height = self.list.rect.height + 2

    def render(self):
        if self.color_set is not None:
            self.color_set.apply()
        super(Menu, self).render()

    def render_item(self, console, item, x, y, width, height):
        console.set_default_foreground(self.shortcut_fgcolor)
        if item.disabled:
            console.set_default_foreground(self.disabled_shortcut_fgcolor)
        console.put_char(x, y, item.label[0])
        console.set_default_foreground(self.fgcolor)

    def handle_event(self, ev):
        if ev.type == events.KEY and chr(ev.data.c) in self.keys:
            self.list.selected_item = self.keys[chr(ev.data.c)]
            return True

        return super(Menu, self).handle_event(ev)
