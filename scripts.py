import threading, webbrowser
from time import sleep
from functools import partial
import lp_events, lp_colors, keyboard, parse, sound

COLOR_ACTIVE = lp_colors.GREEN
COLOR_PRIMED = lp_colors.RED
COLOR_DEFAULT = lp_colors.BLUE_THIRD

threads = [[None for y in range(9)] for x in range(9)]
running = False
to_run = []
text = [["" for y in range(9)] for x in range(9)]

def run_in_bg(func, x, y):
    global threads
    global to_run
    if not running:
        threads[x][y] = threading.Thread(None, func)
        threads[x][y].start()
    else:
        to_run.append((func, x, y))

def run_funcs(funcs_in):
    global running
    global to_run
    running = True
    for f in funcs_in:
        f()
    running = False
    if len(to_run) > 0:
        tup = to_run.pop(0)
        func = tup[0]
        x = tup[1]
        y = tup[2]
        run_in_bg(func, x, y)
    threading.Timer(0.01, lp_colors.update, ()).start()

def run_script(script_str, x=-1, y=-1):
    script_lines = script_str.split('\n')
    funcs_to_run = []
    print("[scripts] NOW PARSING SCRIPT...")
    for line in script_lines:
        split_line = line.split(' ')
        if split_line[0] == "STRING":
            type_string = " ".join(split_line[1:])
            funcs_to_run.append(partial(keyboard.controller.type, type_string))

            print_string = type_string
            print("[scripts] TYPE STRING " + print_string)
        elif split_line[0] == "DELAY":
            funcs_to_run.append(partial(sleep, float(split_line[1])))
            print("[scripts] DELAY " + split_line[1] + " SECONDS")
        elif split_line[0] == "TAP":
            if len(split_line) < 3:
                funcs_to_run.append(partial(keyboard.tap, split_line[1]))
                print("[scripts] TAP " + split_line[1])
            else:
                funcs_to_run.append(partial(keyboard.tap, split_line[1], float(split_line[2])))
                print("[scripts] TAP " + split_line[1] + " FOR " + str(split_line[2]) + " SECONDS")
        elif split_line[0] == "PRESS":
            funcs_to_run.append(partial(keyboard.controller.press, split_line[1]))
            print("[scripts] PRESS " + split_line[1])
        elif split_line[0] == "RELEASE":
            funcs_to_run.append(partial(keyboard.controller.release, split_line[1]))
            print("[scripts] RELEASE " + split_line[1])
        elif split_line[0] == "SP_TAP":
            if keyboard.sp(split_line[1]) != None:
                if len(split_line) < 3:
                    funcs_to_run.append(partial(keyboard.tap, keyboard.sp(split_line[1])))
                    print("[scripts] SPECIAL TAP " + split_line[1])
                else:
                    funcs_to_run.append(partial(keyboard.tap, keyboard.sp(split_line[1]), split_line[2]))
                    print("[scripts] SPECIAL TAP " + split_line[1] + " FOR " + str(split_line[2]) + " SECONDS")
            else:
                print("[scripts] TAP INVALID SPECIAL CHARACTER: " + split_line[1] + ", SKIPPING...")
        elif split_line[0] == "SP_PRESS":
            if keyboard.sp(split_line[1]) != None:
                funcs_to_run.append(partial(keyboard.controller.press, keyboard.sp(split_line[1])))
                print("[scripts] SPECIAL PRESS " + split_line[1])
            else:
                print("[scripts] PRESS INVALID SPECIAL CHARACTER: " + split_line[1])
                print("[scripts] SKIPPING...")
        elif split_line[0] == "SP_RELEASE":
            if keyboard.sp(split_line[1]) != None:
                funcs_to_run.append(partial(keyboard.controller.release, keyboard.sp(split_line[1])))
                print("[scripts] SPECIAL RELEASE " + split_line[1])
            else:
                print("[scripts] RELEASE INVALID SPECIAL CHARACTER: " + split_line[1] + ", SKIPPING...")
        elif split_line[0] == "WEB":
            link = split_line[1]
            if "http" not in link:
                link = "http://" + link
            funcs_to_run.append(partial(webbrowser.open, link))
            print("[scripts] OPEN WEBSITE " + link)
        elif split_line[0] == "WEB_NEW":
            link = split_line[1]
            if "http" not in link:
                link = "http://" + link
            funcs_to_run.append(partial(webbrowser.open_new, link))
            print("[scripts] OPEN WEBSITE (TRY NEW WINDOW) " + link)
        elif split_line[0] == "SOUND":
            sound.play(split_line[1])
            print("[scripts] PLAY SOUND " + split_line[1])
        else:
            print("[scripts] INVALID COMMAND: " + split_line[0] + ", SKIPPING...")
    script_func = partial(run_funcs, funcs_to_run)
    if (x >= 0) and (y >= 0):
        print("[scripts] SCRIPT PARSED. RUNNING IN BACKGROUND...")
        run_in_bg(script_func, x, y)
    else:
        print("[scripts] SCRIPT PARSED. RUNNING...")
        script_func()

def bind(x, y, script_down, off_color=COLOR_DEFAULT):
    script_down_bindable = lambda a, b : run_script(script_down, x, y)
    lp_events.bind_func_with_colors(x, y, script_down_bindable, off_color, COLOR_ACTIVE)
    text[x][y] = script_down

def unbind(x, y):
    lp_events.unbind(x, y)
    threads[x][y] = None
    text[x][y] = ""

def unbind_all():
    global threads
    global text
    global to_run
    lp_events.unbind_all()
    threads = [[None for y in range(9)] for x in range(9)]
    text = [["" for y in range(9)] for x in range(9)]
    to_run = []

