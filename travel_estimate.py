from math import cos, asin, sqrt
import csv
import geocoder
'''
Records have been sources from https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FHK&QO_fu146_anzr=b4vtv0%20n0q%20Qr56v0n6v10%20f748rB
This data can be updated every quarter. Only include ORIGIN_AIRPORT_ID, ORIGIN, DEST_AIRPORT_ID, DEST, & MARKET_FARE in the download.
'''
airports, chapters, chapters_flying, chapters_attending = [], [], [], []
num_driving, num_flying, driving_cost, flying_cost, total_driving_dist = 0, 0, 0, 0, 0 

# Constants
REIMBURSEMENT = 0.30    # USD/mile
DRIVING_RADIUS = 356    # km - Equal to 240 miles (4 hrs at 60 mph) minus 30km because driving in a straight line isn't possible

# Use geocoder with Bing API to find the coordinates of the user specified host city
host_city = 'detroit'
g = geocoder.bing(host_city, key='AnvgeuA4C4-2kzZXHMpgQKlYd52nPaG3yc3PnjKqXPE3zd1Y5f32pXebbcvyW9V3')
results = g.json
print(results['lat'], results['lng'])
v = {'lat':results['lat'], 'lon':results['lng']}

# Open the airport csv and read in data
with open("airports.csv", 'r') as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    for row in csvreader:
        airports.append({'code': row[0], 'name': row[1],
                        'lat': float(row[2]), 'lon': float(row[3]),
                        'fare': float(row[4])})
        
# Open the airport csv and read in data
with open("chapters.csv", 'r') as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    for row in csvreader:
        chapters.append({'id': row[0], 'state': row[1],
                        'letter': row[2], 'code': row[1] + " " + row[2], 'school': row[3],
                        'lat': float(row[4]), 'lon': float(row[5])})
        
# Open the chapter attendance csv for the given year and read in data
with open("ChapterAttendanceColumbus.csv", 'r') as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    for row in csvreader:
        if row:
            chapters_attending.append(row[0].strip())

final_chapters = [x for x in chapters if x['code'] in chapters_attending]

print(len(final_chapters))  

# Haversine formula to find the shortest distance between a given gps location and the gps location of each airport and return the airport dict. of the closest airport for a given gps location
def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    hav = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(hav))

def closest(data, v): # 
    return min(data, key=lambda p: distance(v['lat'],v['lon'],p['lat'],p['lon']))

convention_airport = closest(airports, v)
print('Example Convention Location: ', convention_airport)

# given a convention location (v), print the closest airport and iterate through each chapter and determine if they will fly or drive
# use 'in chapters' if there is no data on which chapters attended, otherwise use 'final_chapters'
for s in final_chapters: 
    chapter_airport = closest(airports, s)
    if distance(s['lat'], s['lon'], convention_airport['lat'], convention_airport['lon']) < DRIVING_RADIUS:
        num_driving += 1
        driving_distance = distance(s['lat'], s['lon'], convention_airport['lat'], convention_airport['lon'])
        driving_cost += ((driving_distance * REIMBURSEMENT) * 2)
        total_driving_dist += (driving_distance * 0.621371)
    else:
        num_flying += 1
        flying_cost += (chapter_airport['fare'] + convention_airport['fare'])
        
driving_cost = driving_cost * 1.2
total_cost = driving_cost + flying_cost

print('***********************************************')
print(num_driving, 'chapters driving ------', num_flying, 'chapters flying')
print('$', round(flying_cost, 2), '- cost of flying 1 member from', num_flying, 'chapters two ways')
print('$', round(driving_cost, 2), '- cost of driving 1 member from', num_driving, 'chapters two ways a total of', round(total_driving_dist, 2), 'miles')
print('$', round(total_cost, 2), '- total cost')
print('***********************************************')
