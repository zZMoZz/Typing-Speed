import curses
from keyboard import is_pressed
from time import sleep, time
from curses import wrapper
from random import choice
from shutil import get_terminal_size


def get_clip():
    try:
        with open('clips.txt', mode='r') as file:
            return choice([clip for clip in file.readlines()]).strip()

    except FileNotFoundError:
        print('There are missing files, please reinstall the test again to continue')
        exit()


def welcome_message(screen):
    buffer = 'Welcome TO Typing Speed Test ...'
    screen.clear()
    screen.move(curses.LINES // 2 -1, curses.COLS // 2 - len(buffer) // 2)
    for char in buffer:
        sleep(0.05)
        screen.addstr(char)
        screen.refresh() # without this line, flush effect will be disable.
    
    sleep(0.8)


def start_window(screen):
    screen.clear()

    while True:
        buffer = 'Mode 1: Without Timer'
        screen.addstr(curses.LINES // 2 -1, curses.COLS // 2 - len(buffer) // 2, buffer)

        buffer = 'Mode 2: Specify Timer'
        screen.addstr(curses.LINES // 2, curses.COLS // 2 - len(buffer) // 2, buffer)

        screen.addstr(curses.LINES // 2 +1, curses.COLS // 2 - len(buffer) // 2, '-'*len(buffer))
        screen.addstr(curses.LINES // 2 +2, curses.COLS // 2 - len(buffer) // 2, 'Mode Number >>')

        # check choosed mode
        mode = screen.getkey()

        if mode in ('1', '2'): 
            return mode
        
        elif mode == '\x1b': 
            exit()

        else:
            buffer = 'Invalid Input, Please Try again'
            screen.clear()
            screen.addstr(curses.LINES // 2 -1, curses.COLS // 2 - len(buffer) // 2, buffer)
            screen.refresh()
            sleep(1.4)
            screen.clear()


def display_text(screen, input_text, target_text): 
    row, column = 0, 0

    screen.clear() # important
    screen.addstr(0, 0, target_text)
    screen.move(0, 0)

    for i in range(len(input_text)):
        if input_text[i] == target_text[i]:
            color = curses.color_pair(1) 
        else:
            color = curses.color_pair(2)

        if column == screen.getmaxyx()[1]:
            column = 0
            row +=1
            
        screen.addstr(row, column, target_text[i], color)
        column+=1


def handle_input(screen, input_text): 
        input_char = screen.getkey()

        if input_char == 'SHF_PADENTER':
            input_char = "'"

        if input_char in ("KEY_BACKSPACE", '\b', "\x7f"): # to run with different operating systems
            if(len(input_text) > 0): 
                input_text.pop()
        
        elif input_char == '\x1b':
            exit()

        else:
            input_text.append(input_char)


def test(screen, mode): 
    full_input_text = []
    full_target_text = []

    if mode == '1':
        time = Mode1(screen, full_target_text, full_input_text)
    else:
        time = Mode2(screen, full_target_text, full_input_text)

    # Calculate mistakes number
    mistakes, length = 0, 0
    for a, b in zip(full_target_text, full_input_text):
        length+=len(b)
        for i, y in zip(a, b):
            if i != y: mistakes+=1 

    screen.clear()
    return time, mistakes, length


def Mode1(screen, full_target_text, full_input_text):
    input_text = []
    target_text = get_clip()

    start_time = time()
    while len(target_text) > len(input_text):
        display_text(screen, input_text, target_text)
        handle_input(screen, input_text)
    end_time = time()

    full_target_text.append(target_text)
    full_input_text.append(input_text)

    return end_time-start_time


def Mode2(screen, full_target_text, full_input_text):
    # get timer
    while True:
        buffer = 'Timer [from 1 to 60 min] >>'
        screen.clear()
        screen.addstr(curses.LINES // 2 -1, curses.COLS // 2 - len(buffer) // 2, buffer)

        try:
            curses.echo()
            if (timer:= int(screen.getstr(2))) in range(1, 61): break
            else: raise ValueError

        except:
            buffer = 'Invalid Input, Please Try again'
            screen.addstr(curses.LINES // 2 -1, curses.COLS // 2 - len(buffer) // 2, buffer)
            screen.refresh()
            sleep(1.4)

    input_text = []
    target_text = get_clip()

    start = time()
    while (time()-start)/60 < timer:
        if len(target_text) == len(input_text):
            full_input_text.append(input_text)
            full_target_text.append(target_text)
            input_text.clear()
            target_text = get_clip()

        display_text(screen, input_text, target_text)
        handle_input(screen, input_text)

    if input_text != []:
        full_input_text.append(input_text)
        full_target_text.append(target_text[:len(input_text)])

    return timer*60


def print_result(screen, time, mistakes, length): 
    screen.clear()
    buffer = f'| Speed: {round((length/5) / (time/60))} WPM | Accurcy: {round((length-mistakes)*100/length)}% | Mistakes: {mistakes} | Time: {round(time/60, 1)}M |'
    screen.addstr(curses.LINES // 2 -2, curses.COLS // 2 - len(buffer) // 2, buffer)


def main(screen):
   # constants
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    welcome_message(screen)

    while True:
        mode = start_window(screen) 
        time, mistakes, length = test(screen, mode)
        print_result(screen, time, mistakes, length)

        buffer = 'To Leave Enter [E] ,, To Repeat The Test Enter Another Key:'
        screen.addstr(curses.LINES // 2, curses.COLS // 2 - len(buffer) // 2, buffer)
        
        curses.echo()
        if buffer:= screen.getstr().lower() == b'e':
            exit()

    
wrapper(main)