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