import pymssql, os, datetime, sys, json
import networkx as nx
from collections import OrderedDict

'''
This file should be executed from the terminal/powershell within 10.10.1.3 with the password passed in following the command as seen below:
$ python committee.py <password>
This will connect to the Convention database and print json data to the console and to an external .json file on the 10.10.1.3 desktop.
* If you get a database error you can check the database error log within program files.
Use tbp-bdickson as the user to connect to (admin) and ensure all credentials are up-to-date and accurate. 
Reverting to tds_version 7.0 resolved the issue of freezing during connection
'''

capacities = {}
def getData():
    committees = {}
    print('About to connect...')
    conn = pymssql.connect(
        host=r'10.10.1.3',
        tds_version=r'7.0',
        user=r'tbp\bdickson',
        # password=sys.argv[1],
        password='KPwbi89@STMarys',
        database='Convention'
    )
    print('Connected...')
    cursor = conn.cursor(as_dict=True)
    # Get all project information for this project and store it in dictionaries for users and committees
    cursor.execute('''SELECT *, FirstName + ' ' + LastName as FullName
                   from Conv_Users where CommitteeWilling in ('Y', 'M')''')
    users = cursor.fetchall()
    cursor.execute('''SELECT Code, Committee from Conv_Committee order by Committee''')
    coms = cursor.fetchall()
    for com in coms:
        committees[com['Code']] = com['Committee']
        capacities[com['Committee']] = len(users) // 12 + 1 # capacity is the same for each com: total users / number of coms
    return (users, committees)

'''
0 = no interest
1 = interested
2 = prefered
'''
levels = {"0": "No Interest", "1": "Interested", "2": "Prefered"}
prefs = {}
print('pre getData')
(users, committees) = getData()
print('post getData')
names = {}
chapters = {}
statuses = {}
memberIds = {}
for user in users:
    name = user['UserID']
    names[name] = user['FullName']
    chapters[name] = user['ChapterCode']
    statuses[name] = user['status_code']
    memberIds[name] = user['MemberID']
    prefs[name] = {}
    user_prefs = user['CommitteePrefered']
    for p in user_prefs.split(','):
        (lvl, code) = p.split('|')
        prefs[name][committees[code]] = lvl

G = nx.DiGraph()
num_persons = len(prefs)
G.add_node('dest', demand=num_persons)
A=[]
test = []
for user, coms in prefs.items():
    G.add_node(user, demand=-1)
    for com, lvl in coms.items():
        print(user, com, lvl)
        lvl = int(lvl)
        if lvl == 2:
            cost = -100
        elif lvl == 1:
            cost = -60
        elif lvl == 0:
            cost = -10
        G.add_edge(user, com, capacity=1, weight=cost)

for com, c in capacities.items():
    G.add_edge(com, 'dest', capacity=c, weight=0)

def get_key(val):
    for key, value in committees.items():
            if val == value:
                return key
    return "key doesn't exist"

res = {}
flowdict = nx.min_cost_flow(G)
for user in prefs:
    for com, flow in flowdict[user].items():
        if flow:
            committeeCode = get_key(com)
            if com in res:
                res[com].append({"user": user, "name": names[user], "status": statuses[user], "chapter": chapters[user], "memberID": memberIds[user], "committee": com, "committeeCode": committeeCode, "level": levels[prefs[user][com]]})
            else:
                res[com] = [{"user": user, "name": names[user], "status": statuses[user], "chapter": chapters[user], "memberID": memberIds[user], "committee": com, "committeeCode": committeeCode, "level": levels[prefs[user][com]]}]
           
print('Program ran')
print(len(users))
'''
sort_order = ['level', 'user']
res2 = {}
for key, val in res.items():
    ordered = [OrderedDict(sorted(item.items(), key=lambda item: sort_order.index(item[0])))
                for item in val]
    res2[key] = ordered
'''
#  Print the json data to terminal and create an object to print. Once printed, copy/paste over into your local machine and format the data as preferred.
print(json.dumps(res, sort_keys=True))
json_object = json.dumps(res, indent=4, sort_keys=True)

# Writing to file on desktop
with open("committee_results.json", "w") as outfile:
    outfile.write(json_object)
