import csv
import sys

f = open("washingtonToChina.data", 'w')
counter = 1
for columns in csv.reader(open("washingtonToChina.txt", 'r'), delimiter=","):
    st = str(counter) + " " + columns[2] + "\n"
    f.write(st)
    counter = counter + 1
f.close()
