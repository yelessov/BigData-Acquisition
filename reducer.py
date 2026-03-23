#!/usr/bin/env python3
import sys

current_genre = None
current_count = 0

# Read the sorted input from the mapper
for line in sys.stdin:
    line = line.strip()
    
    # Split the line into the genre and the count (1)
    genre, count = line.split('\t', 1)
    
    try:
        count = int(count)
    except ValueError:
        continue # If count isn't a number, skip this line

    # If we are still looking at the same genre, keep adding
    if current_genre == genre:
        current_count += count
    else:
        # If the genre changes, print the total for the previous genre!
        if current_genre:
            print(f"{current_genre}\t{current_count}")
        # Reset the tracker for the new genre
        current_genre = genre
        current_count = count

# Don't forget to print the very last genre after the loop finishes!
if current_genre == genre:
    print(f"{current_genre}\t{current_count}")