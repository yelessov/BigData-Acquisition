#!/usr/bin/env python3
import sys

current_movie_id = None
current_title = None
rating_sum = 0.0
rating_count = 0

for line in sys.stdin:
    line = line.strip()
    parts = line.split('\t')
    
    if len(parts) != 3: 
        continue
        
    movie_id, record_type, value = parts
    
    if current_movie_id != movie_id:
        if current_movie_id is not None and current_title is not None and rating_count > 0:
            avg_rating = rating_sum / rating_count
            print("{}\t{:.2f}".format(current_title, avg_rating))
        
        current_movie_id = movie_id
        current_title = None
        rating_sum = 0.0
        rating_count = 0
    
    if record_type == "A_movie":
        current_title = value
    elif record_type == "B_rating":
        try:
            rating_sum += float(value)
            rating_count += 1
        except ValueError:
            pass

if current_movie_id is not None and current_title is not None and rating_count > 0:
    avg_rating = rating_sum / rating_count
    print("{}\t{:.2f}".format(current_title, avg_rating))