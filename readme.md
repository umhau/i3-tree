# i3tree



## notes

You'll quickly discover that window titles are newly significant. In particular,
terminals are going to be...opaque. Here's something to help: 

    https://stackoverflow.com/a/7110386

    trap 'echo -ne "\033]2;$(history 1 | sed "s/^[ ]*[0-9]*[ ]*//g")\007"' DEBUG

Put the above line in your .bashrc and your terminals will get proper titles.