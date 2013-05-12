""" User Interface bits and widgets """
import tcod
from game import utils

class Widget(object):
    """
    A widget is something that knows how to render itself. All things that know
    how to render themselves are widgets.

    Widgets may have child widgets; when a widget is told to render itself, it
    asks its children to render themselves. Child widgets receiving an event
    should pass that event up to the parent if they don't want to handle it.
    Widgets who are initialized knowing who their parent is will automatically
    register themselves with their parent.

    Widgets all exist in a console; on initialization, widgets not given a
    console will make a good-faith effort and assume their console is their
    parent's. At render time, a widget that still does not know what its
    console is will assume it is tcod.root_console.

    Coordinates given at init-time are parent-relative, but stored as
    console-relative (that is, widget.rect.{top,left,center,etc.} are console
    coordinates).
    """

    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0):
        self.parent = parent
        self.children = set()
        self.console = console

        if self.parent is not None:
            self.parent.register_child(self)

            if self.console is None:
                self.console = self.parent.console

            x = x + self.parent.rect.left
            y = y + self.parent.rect.top

        if self.console is None: #, even after all that,
            self.console = tcod.root_console

        self.rect = utils.Rect(x, y, width, height)

    def register_child(self, child):
        child.parent = self
        self.children.add(child)

    def render(self):
        """ The default implementation just asks children to render. """
        for child in self.children:
            child.render()

    def handle_event(self, event):
        """ The default implementation just asks the parent to handle it. """
        if self.parent is not None:
            self.parent.handle_event(event)

    def hcenter_in_parent(self):
        if self.parent is None:
            raise ValueError("Widget trying to hcenter in non-existent parent")
        self.rect.left = (self.parent.rect.left +
                          (self.parent.rect.width - self.rect.width) / 2)

    def vcenter_in_parent(self):
        if self.parent is None:
            raise ValueError("Widget trying to vcenter in non-existent parent")
        self.rect.top = (self.parent.rect.top +
                         (self. parent.rect.height - self.rect.height) / 2)

class Label(Widget):
    def __init__(self, parent=None, console=None, x=0, y=0, text="", width=0):
        super(Label, self).__init__(parent, console, x, y, width, height=0)
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
        width = self.rect.width
        if self.max_width < 1:
            width = min(len(self._text), self.console.width - self.rect.left)
        height = self.console.get_height_rect(self.rect.left, self.rect.top,
                                              width, text=self._text)
        self.rect.resize(width=width, height=height)

    def render(self):
        self.console.print_rect_ex(self.rect.left, self.rect.top,
                                   self.rect.width, self.rect.height,
                                   self.effect, self.align, self._text)
