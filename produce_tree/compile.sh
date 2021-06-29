#!/bin/bash

clear
set -e
# set -v

input="$1"
output=$(echo "$1" | cut -f 1 -d '.')

echo "output file: $output"
rm -rfv "$output"

gcc -Wall -Wextra -Wpedantic -o "$output" "$input" $(pkg-config --libs --cflags i3ipc-glib-1.0)

echo -n 'execute > ' ; read
./$output