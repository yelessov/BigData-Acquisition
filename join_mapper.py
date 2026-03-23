#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line or "movieId" in line: 
        continue
    
    parts = line.split(',')
    
    if len(parts) == 4 and parts[0].isdigit() and parts[1].isdigit():
        movie_id = parts[1]
        rating = parts[2]
        print("{}\tB_rating\t{}".format(movie_id, rating))
        
    elif len(parts) >= 3:
        movie_id = parts[0]
        title = ",".join(parts[1:-1])
        print("{}\tA_movie\t{}".format(movie_id, title))