import csv
'''
Records have been sources from https://data.humdata.org/dataset/ourairports-usa?
This file reads in the file that was downloaded from above to filter and write only medium
and large sized airports that have IATA codes. The file created should be used in travel_estimate.py
'''

rows, rows2, final = [], [], []

with open("average_fare.csv", mode='r') as file:
    csvreader = csv.reader(file)
    # header = next(csvreader)
    for row in csvreader:
        if row[5]:
            if float(row[5]) > 250.00: 
                rows.append(row)
            # rows.append({'id': row[0], 'code': row[16], 
            #             'lat': float(row[4]), 'lon': float(row[5])})
print(rows[0])
print(len(rows))

with open("airports-alt.csv", mode='r') as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    for row in csvreader:
        rows2.append(row)

print(rows2[0])
print(len(rows2))

for i in rows:
    for j in rows2:
        if i[1] == j[1]:
            # print(i)
            final.append({'code': i[1], 'name': i[2], 'lat': j[2], 'lon': j[3], 'fare': i[5]})
            
for f in final:
    print(f)

try:
    with open('airports.csv', mode='w', newline='') as csvfile:
        fieldnames = final[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in final:
            writer.writerow(row)    
except IOError:
    print("I/O error")