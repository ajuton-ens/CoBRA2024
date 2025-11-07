#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

def main(stdscr):
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_YELLOW)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    BLUE_AND_YELLOW = curses.color_pair(1)
    GREEN_AND_BLACK = curses.color_pair(2)
    RED_AND_WHITE = curses.color_pair(3)
    
    win = curses.newwin(18,3,2,2)
    rectangle(stdscr, 2, 2, 5, 20)
    stdscr.refresh()
    stdscr.getch()

    #stdscr.clear()
    #stdscr.addstr(10, 15, "hello worldaa")
    #stdscr.addstr(10, 12, "uullo world")
    #stdscr.addstr(15, 25, "truc !!")
    #stdscr.refresh()
    #stdscr.getch()

wrapper(main)