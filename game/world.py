from __future__ import unicode_literals

import json
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
    """
    A Tile only knows how to draw itself to any position onscreen. It is not
    intended to be bound to a position in the world (the world instead contains
    ints that map via tilemap to a Tile instance).
    """
    def __init__(self, name, description, glyph, degrades_to='nothing',
                 fgcolor=color.WHITE, bgcolor=color.BLACK):
        self.name = name
        self.description = description
        self.glyph = glyph
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.degrades_to = degrades_to

    def __repr__(self):
        return '<Tile(name=%s)>' % self.name

class TileMap(object):
    def __init__(self, fp=None):
        """ fp is expected to be a readable file-like object """
        self.degrades = dict()
        self.tilemap = []

        if fp is not None:
            self.tilemap, self.degrades = json.load(fp)
        else:
            for tile in tiles.itervalues():
                self.degrades[tile.name] = tile.degrades_to
                self.tilemap.append(tile.name)

    def __getitem__(self, key):
        """ Will return a degraded Tile if the original is not available """
        return self._get_degraded(self.tilemap[key])

    def _get_degraded(self, tilename):
        if tilename in tiles:
            return tiles[tilename]
        else:
            return self._get_degraded(self.degrades[tilename])

    def save(self, fp):
        """ fp is expected to be a .write()-supporting file-like object """
        json.dump((self.tilemap, self.degrades), fp)

tiles = dict()
def _can_degrade(tile):
    """
    A tile is considered degradable if it's possible to reach the 'nothing'
    tile by walking through the tiles.degrades_to references. Note that all
    three core tiles are degradable.
    """
    degrade_chain = set()
    while tile.degrades_to in tiles:
        if tile.degrades_to == 'nothing':
            return True
        elif tile.degrades_to in degrade_chain:
            raise Exception("Circular reference: the tile '%s' degrades to '%s', which degrades to it!"
                            % (tile.name, tile.degrades_to))
        degrade_chain.add(tile.name)
        tile = tiles[tile.degrades_to]

    # if we got here, a degrades pointer referenced a nonexistent tile
    return False

def register_tile(tile):
    """
    Tiles may not be registered twice, and they must degrade to something that
    is, itself, degradable. The core tiles 'nothing', 'basic_floor', and
    'basic_wall' are always degradable.
    """
    if tile.name in tiles:
        raise KeyError("The tile '%s' has already been registered!" % tile.name)
    # 'nothing' gets a special pass, as the root of the degrade tree
    if not _can_degrade(tile) and tile.name != 'nothing':
        raise ValueError("The tile '%s' is not degradable!" % tile.name)
    tiles[tile.name] = tile

register_tile(Tile('nothing', 'Nothing', glyph=' ', bgcolor=color.BLACK))
register_tile(Tile('basic_floor', 'Floor', glyph=' ', bgcolor=color.DARK_AMBER))
register_tile(Tile('basic_wall', 'Wall', glyph='#', bgcolor=color.DARKER_ORANGE))

