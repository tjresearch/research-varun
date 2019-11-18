import curses
from curses import wrapper


stdcsr = curses.initscr()
curses.noecho()
stdcsr.keypad(True)

def exit():
    curses.nocbreak()
    stdcsr.keypad(False)
    curses.echo()
    curses.endwin()

def main(stdcsr):
    stdcsr.clear()
    pad = curses.newpad(100,100)
    for y in range(0, 99):
        for x in range(0, 99):
            pad.addch(y, x, ord('a') + (x * x + y * y) % 26)

    #pad.refresh(0, 0, 5, 5, 20, 75)

wrapper(main)


