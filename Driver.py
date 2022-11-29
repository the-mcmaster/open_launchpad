import logging as log
import time

log.basicConfig(level=log.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

#Map connecting a raw 3-byte sequence to the associated row, column, and state
#   - values are a tuple of integers 0-8 organized (r, c, s)
#        + Example: (0, 0, 0), (6, 4, 1), (6, 4, 0), (2, 4, 1)
#        Note: There is no value for (0, 8, 0) or (0, 8, 1)
#              since the button does not physically exist.
BUTTON_MAP = {
    b"\xb0h\x7f": (0, 0, 0),
    b"\xb0h\x00": (0, 0, 1),
    b"\xb0i\x7f": (0, 1, 0),
    b"\xb0i\x00": (0, 1, 1),
    b"\xb0j\x7f": (0, 2, 0),
    b"\xb0j\x00": (0, 2, 1),
    b"\xb0k\x7f": (0, 3, 0),
    b"\xb0k\x00": (0, 3, 1),
    b"\xb0l\x7f": (0, 4, 0),
    b"\xb0l\x00": (0, 4, 1),
    b"\xb0m\x7f": (0, 5, 0),
    b"\xb0m\x00": (0, 5, 1),
    b"\xb0n\x7f": (0, 6, 0),
    b"\xb0n\x00": (0, 6, 1),
    b"\xb0o\x7f": (0, 7, 0),
    b"\xb0o\x00": (0, 7, 1),
    b"\x90Q\x7f": (1, 0, 0),
    b"\x90Q\x00": (1, 0, 1),
    b"\x90R\x7f": (1, 1, 0),
    b"\x90R\x00": (1, 1, 1),
    b"\x90S\x7f": (1, 2, 0),
    b"\x90S\x00": (1, 2, 1),
    b"\x90T\x7f": (1, 3, 0),
    b"\x90T\x00": (1, 3, 1),
    b"\x90U\x7f": (1, 4, 0),
    b"\x90U\x00": (1, 4, 1),
    b"\x90V\x7f": (1, 5, 0),
    b"\x90V\x00": (1, 5, 1),
    b"\x90W\x7f": (1, 6, 0),
    b"\x90W\x00": (1, 6, 1),
    b"\x90X\x7f": (1, 7, 0),
    b"\x90X\x00": (1, 7, 1),
    b"\x90Y\x7f": (1, 8, 0),
    b"\x90Y\x00": (1, 8, 1),
    b"\x90G\x7f": (2, 0, 0),
    b"\x90G\x00": (2, 0, 1),
    b"\x90H\x7f": (2, 1, 0),
    b"\x90H\x00": (2, 1, 1),
    b"\x90I\x7f": (2, 2, 0),
    b"\x90I\x00": (2, 2, 1),
    b"\x90J\x7f": (2, 3, 0),
    b"\x90J\x00": (2, 3, 1),
    b"\x90K\x7f": (2, 4, 0),
    b"\x90K\x00": (2, 4, 1),
    b"\x90L\x7f": (2, 5, 0),
    b"\x90L\x00": (2, 5, 1),
    b"\x90M\x7f": (2, 6, 0),
    b"\x90M\x00": (2, 6, 1),
    b"\x90N\x7f": (2, 7, 0),
    b"\x90N\x00": (2, 7, 1),
    b"\x90O\x7f": (2, 8, 0),
    b"\x90O\x00": (2, 8, 1),
    b"\x90=\x7f": (3, 0, 0),
    b"\x90=\x00": (3, 0, 1),
    b"\x90>\x7f": (3, 1, 0),
    b"\x90>\x00": (3, 1, 1),
    b"\x90?\x7f": (3, 2, 0),
    b"\x90?\x00": (3, 2, 1),
    b"\x90@\x7f": (3, 3, 0),
    b"\x90@\x00": (3, 3, 1),
    b"\x90A\x7f": (3, 4, 0),
    b"\x90A\x00": (3, 4, 1),
    b"\x90B\x7f": (3, 5, 0),
    b"\x90B\x00": (3, 5, 1),
    b"\x90C\x7f": (3, 6, 0),
    b"\x90C\x00": (3, 6, 1),
    b"\x90D\x7f": (3, 7, 0),
    b"\x90D\x00": (3, 7, 1),
    b"\x90E\x7f": (3, 8, 0),
    b"\x90E\x00": (3, 8, 1),
    b"\x903\x7f": (4, 0, 0),
    b"\x903\x00": (4, 0, 1),
    b"\x904\x7f": (4, 1, 0),
    b"\x904\x00": (4, 1, 1),
    b"\x905\x7f": (4, 2, 0),
    b"\x905\x00": (4, 2, 1),
    b"\x906\x7f": (4, 3, 0),
    b"\x906\x00": (4, 3, 1),
    b"\x907\x7f": (4, 4, 0),
    b"\x907\x00": (4, 4, 1),
    b"\x908\x7f": (4, 5, 0),
    b"\x908\x00": (4, 5, 1),
    b"\x909\x7f": (4, 6, 0),
    b"\x909\x00": (4, 6, 1),
    b"\x90:\x7f": (4, 7, 0),
    b"\x90:\x00": (4, 7, 1),
    b"\x90;\x7f": (4, 8, 0),
    b"\x90;\x00": (4, 8, 1),
    b"\x90)\x7f": (5, 0, 0),
    b"\x90)\x00": (5, 0, 1),
    b"\x90*\x7f": (5, 1, 0),
    b"\x90*\x00": (5, 1, 1),
    b"\x90+\x7f": (5, 2, 0),
    b"\x90+\x00": (5, 2, 1),
    b"\x90,\x7f": (5, 3, 0),
    b"\x90,\x00": (5, 3, 1),
    b"\x90-\x7f": (5, 4, 0),
    b"\x90-\x00": (5, 4, 1),
    b"\x90.\x7f": (5, 5, 0),
    b"\x90.\x00": (5, 5, 1),
    b"\x90/\x7f": (5, 6, 0),
    b"\x90/\x00": (5, 6, 1),
    b"\x900\x7f": (5, 7, 0),
    b"\x900\x00": (5, 7, 1),
    b"\x901\x7f": (5, 8, 0),
    b"\x901\x00": (5, 8, 1),
    b"\x90\x1f\x7f": (6, 0, 0),
    b"\x90\x1f\x00": (6, 0, 1),
    b"\x90 \x7f": (6, 1, 0),
    b"\x90 \x00": (6, 1, 1),
    b"\x90!\x7f": (6, 2, 0),
    b"\x90!\x00": (6, 2, 1),
    b'\x90"\x7f': (6, 3, 0),
    b'\x90"\x00': (6, 3, 1),
    b"\x90#\x7f": (6, 4, 0),
    b"\x90#\x00": (6, 4, 1),
    b"\x90$\x7f": (6, 5, 0),
    b"\x90$\x00": (6, 5, 1),
    b"\x90%\x7f": (6, 6, 0),
    b"\x90%\x00": (6, 6, 1),
    b"\x90&\x7f": (6, 7, 0),
    b"\x90&\x00": (6, 7, 1),
    b"\x90'\x7f": (6, 8, 0),
    b"\x90'\x00": (6, 8, 1),
    b"\x90\x15\x7f": (7, 0, 0),
    b"\x90\x15\x00": (7, 0, 1),
    b"\x90\x16\x7f": (7, 1, 0),
    b"\x90\x16\x00": (7, 1, 1),
    b"\x90\x17\x7f": (7, 2, 0),
    b"\x90\x17\x00": (7, 2, 1),
    b"\x90\x18\x7f": (7, 3, 0),
    b"\x90\x18\x00": (7, 3, 1),
    b"\x90\x19\x7f": (7, 4, 0),
    b"\x90\x19\x00": (7, 4, 1),
    b"\x90\x1a\x7f": (7, 5, 0),
    b"\x90\x1a\x00": (7, 5, 1),
    b"\x90\x1b\x7f": (7, 6, 0),
    b"\x90\x1b\x00": (7, 6, 1),
    b"\x90\x1c\x7f": (7, 7, 0),
    b"\x90\x1c\x00": (7, 7, 1),
    b"\x90\x1d\x7f": (7, 8, 0),
    b"\x90\x1d\x00": (7, 8, 1),
    b"\x90\x0b\x7f": (8, 0, 0),
    b"\x90\x0b\x00": (8, 0, 1),
    b"\x90\x0c\x7f": (8, 1, 0),
    b"\x90\x0c\x00": (8, 1, 1),
    b"\x90\r\x7f": (8, 2, 0),
    b"\x90\r\x00": (8, 2, 1),
    b"\x90\x0e\x7f": (8, 3, 0),
    b"\x90\x0e\x00": (8, 3, 1),
    b"\x90\x0f\x7f": (8, 4, 0),
    b"\x90\x0f\x00": (8, 4, 1),
    b"\x90\x10\x7f": (8, 5, 0),
    b"\x90\x10\x00": (8, 5, 1),
    b"\x90\x11\x7f": (8, 6, 0),
    b"\x90\x11\x00": (8, 6, 1),
    b"\x90\x12\x7f": (8, 7, 0),
    b"\x90\x12\x00": (8, 7, 1),
    b"\x90\x13\x7f": (8, 8, 0),
    b"\x90\x13\x00": (8, 8, 1),
}

#Main driver
class Driver():
    '''Main Driver for Abelton Novation Launchpad'''
    def __init__(self):
        #continuously try to open the device file
        failing = True
        while failing:
            try:
                log.info("Attempting to connect to device")
                self.I_STREAM = open("/dev/midi5", 'rb', buffering=-1)
                failing = False
            except:
                log.warning("Could not connect to device")
                log.info("Trying again in 1 second")
                time.sleep(1)
        log.info("Successfully connected!")

        self.input_map = BUTTON_MAP

        #create default blank board
        self.graph = self._graph_init()
        self.printed = False

        log.info("Driver started successfully")

    #capture the top of the input queue in terms of state
    def input(self):
        raw_in = self.I_STREAM.read(3)
        bs = self.input_map[raw_in]
        return bs

    #build default empty button terminal graph
    def _graph_init(self):
        graph = []
        for row in range(9):
            graph.append([])
            for column in range(9):
                if row == 0 and column == 8:
                    continue
                graph[row].append("□")

        return graph

    #update the graph by button state
    def update(self, bs):
        row = bs[0]
        column = bs[1]
        state = bs[2]

        if state == 0:
            self.graph[row][column] = "▣"
        else:
            self.graph[row][column] = "□"

    #print it with the terminal
    #works well with the internal logger
    def draw(self):
        #if the map is what is currently printed,
        if self.printed:
            move = "\033[F"*10
            print(move)

            for row in self.graph:
                for column in row:
                    print(column + " ", end='')
                else:
                    print()
        else:
            log.info("LAST KNOWN STATE")
            for row in self.graph:
                for column in row:
                    print(column + " ", end='')
                else:
                    print()
            self.printed = True
