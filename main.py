import curses
import os

def main(stdscr, path: str) -> list:
    '''
    Keys:
        UP(j) / DOWN(k) - Navigation
        *               - Selecting all options
        ^               - Unselecting all options
        e               - Inverse select
        o               - Open the directory
        ENTER           - Select the directory
        q               - Return the selected options and exit
        Q               - Do not return anything and exit
        r               - Refresh
    '''
    SELECTED = list()
    # Turn off cursor blinking
    curses.curs_set(0)

    # Disable automatic echoing of keys and line buffering
    curses.noecho()
    curses.cbreak()

    # Tell curses not to worry about cursor position when refreshing
    stdscr.leaveok(True)

    # Get screen dimensions
    sh, sw = stdscr.getmaxyx()

    # Initialize colors
    curses.start_color()
    # Overwrite default colors
    curses.init_color(curses.COLOR_RED, 1000, 333, 333)  # Red
    curses.init_color(curses.COLOR_GREEN, 313, 980, 482)  # Green
    curses.init_color(curses.COLOR_YELLOW, 945, 980, 550)  # Yellow
    curses.init_color(curses.COLOR_BLUE, 738, 574, 972)  # Blue
    curses.init_color(curses.COLOR_MAGENTA, 1000, 474, 776)  # Magenta
    curses.init_color(curses.COLOR_CYAN, 545, 913, 992)  # Cyan
    curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)  # White
    curses.init_color(curses.COLOR_BLACK, 100, 100, 100)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    
    #A method for returning the directories
    abspath = os.path.abspath
    dir     = abspath(path)
    def manage_menu_items(dir):
        dirs = ['..'] + sorted(os.listdir(dir))
        items = list()
        for i in dirs:
            info = [i]
            if os.path.isdir(dir+ '/' +i):
                info += [curses.color_pair(3), 0,  True]
            elif os.access(dir+ '/' +i, os.X_OK):
                info += [curses.color_pair(2), 0, False]
            else:
                info += [curses.color_pair(0), 0, False]
            items.append(info)
        return items

    # Create a window for the menu
    menu_win = curses.newwin(sh - 2, sw, 0, 0)  # Adjust height by 1 less than screen height

    # Enable keypad input for the menu window
    menu_win.keypad(True)

    # Define menu items with colors
    menu_items = manage_menu_items(dir)

    # Highlight the first item by default
    selected_item = 0

    # Define variables for scrolling
    start_row = 0
    visible_rows = min(sh - 2, len(menu_items))  # Adjust for screen height

    # List to store selected options
    selected_options = []
    bar = curses.newwin(2, sw, sh - 2, 0)

    # Main loop
    while True:
        # Clear the menu window
        percent = (selected_item+1) * 100 // len(menu_items)
        menu_win.clear()
        menu_win.refresh()
        bar.clear()
        lendir = len(dir)
        bar.addstr(0,0, " [{}] selected".format(len(SELECTED)),curses.color_pair(6))
        bar.addstr(1, 0, ' '+dir[lendir -sw + 6: ] if sw-6 < lendir else dir, curses.color_pair(5))
        bar.addstr(1, sw-5, "{}%".format("0"+str(percent) if percent < 10 else percent), curses.color_pair(4))
        bar.refresh()

        # Display the visible menu items with colors
        for i in range(start_row, min(start_row + visible_rows, len(menu_items))):
            option_text, option_color, option_highlight, Type= menu_items[i]
            option_text = option_text[:sw-13] + '...' + option_text[-7:] if len(option_text) > sw -2 else option_text
            if i == selected_item:
                menu_win.addstr(i - start_row, 0,"> " + option_text, option_color | option_highlight)
            else:
                menu_win.addstr(i - start_row, 2, option_text, option_color | option_highlight)

        # Refresh the menu window
        menu_win.refresh()

        # Get user input
        key = menu_win.getch()

        # Handle user input
        if key == curses.KEY_UP or key == ord('j'):
            selected_item = max(0, selected_item - 1)
            if selected_item < start_row:
                start_row = max(0, start_row - 1)  # Ensure start_row doesn't go negative
        elif key == curses.KEY_DOWN or key == ord('k'):
            selected_item = min(len(menu_items) - 1, selected_item + 1)
            if selected_item >= start_row + visible_rows:
                start_row = min(len(menu_items) - visible_rows, start_row + 1)  # Ensure start_row doesn't exceed max
        elif key == ord('q'):
            # If 'q' is pressed, create a new window at the last line and exit
            break
        # ENTER for selected a option
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_item == 0:
                continue
            menu_items[selected_item][2] = 0 if menu_items[selected_item][2] !=0 else curses.A_UNDERLINE
            if selected_item not in selected_options:
                selected_options.append(selected_item)  # Add selected option to list
            else:
                selected_options.remove(selected_item)  # Remove if already selected
            if dir + '/' + menu_items[selected_item][0] in SELECTED:
                SELECTED.remove(dir + '/' + menu_items[selected_item][0])
            elif dir + '/' + menu_items[selected_item][0] not in SELECTED:
                SELECTED.append(dir + '/' + menu_items[selected_item][0])
        # HOME for goto first option
        elif key == curses.KEY_HOME:
            selected_item = 0
        # END for goto last option
        elif key == curses.KEY_END:
            selected_item = len(menu_items)-1
        # o for open a directory
        elif key == ord('o'):
            if menu_items[selected_item][3] == True:
                pre_dir = dir
                dir = abspath(dir + '/' + menu_items[selected_item][0])
                try:
                    menu_items = manage_menu_items(dir)
                except PermissionError:
                    dir = pre_dir
                    menu_items = manage_menu_items(dir)
                selected_item= 0
                selected_options = []
                for i, j in enumerate(menu_items):
                    if dir + '/' + j[0] in SELECTED:
                        selected_options.append(i)
                        menu_items[i][2] = curses.A_UNDERLINE
        # * for selecting all
        elif key == ord('*'):
            selected_options = [x for x in range(1, len(menu_items))]
            for i in range(1, len(menu_items)):
                menu_items[i][2] = curses.A_UNDERLINE
                if dir + '/' + menu_items[i][0] in SELECTED:
                    pass
                elif dir + '/' + menu_items[i][0] not in SELECTED:
                    SELECTED.append(dir + '/' + menu_items[i][0])
        # ^ for unselecting all
        elif key == ord('^'):
            selected_options = []
            for i in range(len(menu_items)):
                menu_items[i][2] = 0
                if dir + '/' + menu_items[i][0] in SELECTED:
                    SELECTED.remove(dir + '/' + menu_items[i][0])
        # e for inverse selection
        elif key == ord('e'):
            inverse = [x for x in range(1, len(menu_items))]
            for i in range(1, len(menu_items)):
                if i in selected_options:
                    inverse.remove(i)
                menu_items[i][2] = 0 if menu_items[i][2] != 0 else curses.A_UNDERLINE
                if dir + '/' + menu_items[i][0] in SELECTED:
                    SELECTED.remove(dir + '/' + menu_items[i][0])
                elif dir + '/' + menu_items[i][0] not in SELECTED:
                    SELECTED.append(dir + '/' + menu_items[i][0])
        # Refresh the window
        elif key == ord('r'):
            menu_win.refresh()
        # Q for quiting without returning any values
        elif key == ord('Q'):
            return []
        # Recalculate visible rows based on current screen height and menu items list size
        visible_rows = min(sh - 2, len(menu_items))
    while True:
        ...
    # Clean up
    curses.endwin()
    return SELECTED

if __name__ == "__main__":
    result = curses.wrapper(main, '')

