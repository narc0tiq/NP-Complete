To actually run the application, you will need to provide the appropriate
libTCOD DLLs or SOs for your system -- they must be in the directory you launch
npc.py from (usually, right here where npc.py is).

These instructions are correct for libTCOD v1.5.1:

On Windows, you will want libtcod-mingw.dll, SDL.dll, and zlib1.dll.
Alternately, you may use libtcod-VS.dll in place of the mingw version -- either
should work just as well.

On Linux, you will want libtcod.so and possibly SDLlib.so (however, the latter
should be provided by your package manager if at all possible -- on
Debian/Ubuntu, try ``sudo apt-get install libsdl1.2debian``).