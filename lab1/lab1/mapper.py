#!/usr/bin/env python3
import sys

# Read each line from standard input (Hadoop feeds the data here)
for line in sys.stdin:
    line = line.strip()
    # Skip the header row
    if "movieId" in line:
        continue
    
    # Split the CSV line into columns
    columns = line.split(',')
    
    # Check if we have enough columns to avoid errors
    if len(columns) >= 3:
        # The genres are in the last column
        genres_string = columns[-1]
        
        # Split the genres by the pipe character '|'
        genres = genres_string.split('|')
        
        # Print out each genre and a 1, separated by a tab
        for genre in genres:
            print(f"{genre.strip()}\t1")