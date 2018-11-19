import os
import sys
import csv

# Path to the temp.csv which consists of midi file on csv format
path = os.path.join(os.path.dirname(__file__), "temp.csv")
# File (csv) re-written to be converted to midi file
output_file = open(os.path.join(os.path.dirname(__file__), "output.csv"), 'wb')
writer = csv.writer(output_file)

try:
    num_tracks = sys.argv[1]
except IndexError:
    print("Tracks to remove has not been given !")
    num_tracks = -1

if num_tracks != -1:
	with open(path, 'rb') as csvfile:
	    datas = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
	    for row in datas:
	        if row[0] != num_tracks:
	            writer.writerow(row)
else:
	raise(IndexError)
