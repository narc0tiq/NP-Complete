from collections import namedtuple
from numpy import zeros, int16

CHUNK_WIDTH = CHUNK_HEIGHT = 256
CHUNK_DEPTH = 16

def coords_to_chunk(x, y, z):
    return (x - (x % CHUNK_WIDTH),
            y - (y % CHUNK_HEIGHT),
            z - (z % CHUNK_DEPTH))

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

