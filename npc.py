#!/usr/bin/env python
import tcod
import game

width = game.config.parser.getint("core", "width")
height = game.config.parser.getint("core", "height")
fullscreen = game.config.parser.getboolean("core", "fullscreen")

tcod.set_custom_font('fonts/consolas12x12_gs_tc.png', tcod.font.TYPE_GREYSCALE | tcod.font.LAYOUT_TCOD)
tcod.init_root(width, height, title='NP-Complete', fullscreen=fullscreen)
tcod.set_fps_limit(25)

if __name__ == '__main__':
    game.main_menu()
