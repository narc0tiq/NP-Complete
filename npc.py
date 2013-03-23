#!/usr/bin/env python

import tcod, game

tcod.set_custom_font('fonts/consolas12x12_gs_tc.png', tcod.font.TYPE_GREYSCALE | tcod.font.LAYOUT_TCOD)
tcod.init_root(80, 25, title='NP-Complete', fullscreen=False)
tcod.set_fps_limit(20)

if __name__ == '__main__':
    game.main_menu()

