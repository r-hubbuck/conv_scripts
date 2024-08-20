import csv
'''
Records have been sourced from t:/People/Volunteers/access db
'''

rows = []

with open("tchapters.csv", mode='r') as file:
    csvreader = csv.reader(file)
    # header = next(csvreader)
    for row in csvreader:
        if row[9] == 'FALSE':
            rows.append({'id': row[1], 'state': row[3], 'letter': row[4], 'school': row[6], 'lat': row[16], 'lon':row[17]})
print(rows[0])
print(rows[1])
print(len(rows))