from collections import namedtuple
from numpy import zeros, int16
from tcod import color

CHUNK_WIDTH = CHUNK_HEIGHT = 256
CHUNK_DEPTH = 16

class World(object):
    def __init__(self):
        self.chunk_provider = ChunkProvider()

class Chunk(object):
    def __init__(self, west, north, bottom):
        self.west = west
        self.bottom = bottom
        self.north = north
        self.east = self.west + CHUNK_WIDTH
        self.south = self.north + CHUNK_HEIGHT
        self.top = self.bottom + CHUNK_DEPTH

        self.tiles = zeros( (CHUNK_DEPTH, CHUNK_WIDTH, CHUNK_HEIGHT), dtype=int16)

    def contains(self, x, y, z):
        return (x >= self.west and x < self.east and
                y >= self.north and y < self.south and
                z >= self.bottom and z < self.top)

    def __repr__(self):
        return 'Chunk(west=%d, north=%d, bottom=%d)' % (self.west, self.north, self.bottom)

class ChunkProvider(dict):
    def __getitem__(self, key):
        new_key = coords_to_chunk(*key[0:3])
        return super(ChunkProvider, self).__getitem__(new_key)

    def __missing__(self, key):
        return Chunk(*key[0:3])

def coords_to_chunk(x, y, z):
    return (x - (x % CHUNK_WIDTH),
            y - (y % CHUNK_HEIGHT),
            z - (z % CHUNK_DEPTH))


class Tile(object):
    def __init__(self, name, glyph, fgcolor=color.WHITE, bgcolor=color.BLACK):
        self.name = name
        self.glyph = glyph
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor

tile_dict = dict()
tile_dict['nothing'] = Tile('Nothing', glyph=' ', bgcolor=color.BLACK)
tile_dict['floor'] = Tile('Floor', glyph=' ', bgcolor=color.DARK_AMBER)
tile_dict['wall'] = Tile('Wall', glyph='#', bgcolor=color.DARKER_ORANGE)

