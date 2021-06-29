// scan the raw json character-by-character

// each type of character is meaningful: brackets, commas, quotes. 

// use a case statement to perform a known action based on each of those types of characters

// there are a known number of states that my code will encounter, based on where in the json file it is:
// - new depth achieved
// - reduced depth

// - field name identified
// - identifying field name

// for each state, there are deterministic actions to be taken with the available information. 


// this program, so far, just draws & updates the GUI.
// when the user interacts, the while loop is paused until the interaction is solved.

// just write a function that can parse and act on the json it's given.


// CODE TODO

// - calculate depth correctly, keep a running count
// - print list of monitors
// - print list of workspaces, per monitor
// - print list of windows, per workspace
// - print hierarchy of windows (containers, etc)

// - draw the window tree in the GUI
//   - box in correct place
//   - rectangles per-window
//   - indented correctly

// how are gui updates timed?
// - periodic
//      if nothing's happened for a while, redraw the gui (1, 5, or 30 seconds?)
//      if the trigger works reliably, periodic updates aren't needed
// - triggered
//      https://i3wm.org/docs/ipc.html#_subscribing_to_events
//      Just watch for changes to 'window' and update the gui as-needed? 
//      write a function 'draw-gui' that refreshes the interface based on a new copy of the window tree
// - calculated & manually adjusted
//      include a button to recalculate the gui

// - click on a window to focus it
//      if you want to focus a particular window, you can do it like so: i3.focus(title="window title")
// - middle click on a window to close it
// - drag & drop a window to move it & reparent it (and its children)

#include <stdio.h>
#include <stdlib.h>

int main()
{
    FILE *fp;
    char  ch;
    int depth = 0;

    fp = fopen("tree.simplified.json", "r");

    if (fp == NULL) { printf("File is not available \n"); exit(1); }


    while ((ch = fgetc(fp)) != EOF)
    {

        // calculate depth
        switch(ch) {

            case '{' :

                depth++;
                printf("depth increased: d = %d\n", depth);
                break;

            case '}' :

                depth--;
                printf("depth decreased: d = %d\n", depth);
                break;

        }

        

    }

    fclose(fp);

    return 0;
}
