import ConfigParser, os, atexit
from datetime import datetime as dt

parser = ConfigParser.SafeConfigParser()
with open("data/defaults.cfg") as f:
    parser.readfp(f)
parser.read(["data/config.cfg", os.path.expanduser("~/.NP-Complete/data/config.cfg")])

@atexit.register
def save():
    try:
        with open("data/config.cfg", "w") as f:
            f.write("# Generated %s\n\n" % dt.now().ctime())
            parser.write(f)
    except IOError:
        with open("~/.NP-Complete/data/config.cfg", "w") as f:
            parser.write(f)
