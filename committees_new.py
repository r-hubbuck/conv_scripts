import pymssql, json
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
(users, committees) = getData()
print('post getData')
names, chapters, statuses, memberIds = {}, {}, {}, {}

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

com_count= {}
final = {}
placed = []
com_order = ['Constitution & Bylaws', 'Program Review', 'Rituals', 'Chapter & Association Finance', 
             'Awards', 'Convention Site', 'Petitions', 'Resolutions', 'Image & Marketing', 'Diversity Equity and Inclusion', 
             'NEST', 'Alumni Chapters', 'Advisors']
soft_cap = {'Constitution & Bylaws': 24,'Program Review': 18, 'Rituals': 18, 'Chapter & Association Finance': 24, 
             'Awards': 24, 'Convention Site': 18, 'Petitions': 18, 'Resolutions': 18, 'Image & Marketing': 15, 'Diversity Equity and Inclusion': 15, 
             'NEST': 18, 'Alumni Chapters': 24, 'Advisors': 24}
hard_cap = {'Constitution & Bylaws': 30,'Program Review': 30, 'Rituals': 30, 'Chapter & Association Finance': 30, 
             'Awards': 30, 'Convention Site': 30, 'Petitions': 30, 'Resolutions': 30, 'Image & Marketing': 30, 'Diversity Equity and Inclusion': 30, 
             'NEST': 30, 'Alumni Chapters': 50, 'Advisors': 50}
for com in com_order:
    com_count[com] = 0

# The function below is not being used yet, but once the program is finished and functioning, use the function below by passing in 
# the level and cap as paramters (cap can be soft or hard cap)
# Example: user_sort(2, soft_cap)
def com_sort(priority, cap):
    for user, coms in prefs.items():
        for com, lvl in coms.items():
            lvl = int(lvl)
            if lvl == priority and user not in placed:
                for c in com_order:
                    if com == c and com_count[c] < cap[c]:
                        com_count[c] += 1
                        placed.append(user)
                        if com in final:
                            final[com].append({"user": user, "name": names[user], "status": statuses[user], "chapter": chapters[user], "memberID": memberIds[user], "committee": com, "level": levels[prefs[user][com]]})
                        else:
                            final[com] = [{"user": user, "name": names[user], "status": statuses[user], "chapter": chapters[user], "memberID": memberIds[user], "committee": com, "level": levels[prefs[user][com]]}]
                        break

com_sort(2, soft_cap)
com_sort(1, soft_cap)
com_sort(1, hard_cap)
# for user, coms in prefs.items(): # This first loop will place prefered selections in the order of committee priority
#     for com, lvl in coms.items():
#         lvl = int(lvl)
#         if lvl == 2 and user not in placed:
#             for c in com_order:
#                 if com == c and com_count[c] < soft_cap[c]:
#                     com_count[c] += 1
#                     placed.append(user)
#                     if com in final:
#                         final[com].append({"user": user, "name": names[user], "status": statuses[user], "chapter": chapters[user], "memberID": memberIds[user], "committee": com, "level": levels[prefs[user][com]]})
#                     else:
#                         final[com] = [{"user": user, "name": names[user], "status": statuses[user], "chapter": chapters[user], "memberID": memberIds[user], "committee": com, "level": levels[prefs[user][com]]}]
#                     break
        
 
# for user, coms in prefs.items(): # This second loop will place interested selections in the order of committee priority below the soft cap
#     for com, lvl in coms.items():
#         if int(lvl) == 1 and user not in placed:
#             for c in com_order:
#                 if com == c and com_count[c] < soft_cap[c]:
#                     com_count[c] += 1
#                     placed.append(user)
#                     if com in final:
#                         final[com].append({"user": user, "name": names[user], "status": statuses[user], "chapter": chapters[user], "memberID": memberIds[user], "committee": com, "level": levels[prefs[user][com]]})
#                     else:
#                         final[com] = [{"user": user, "name": names[user], "status": statuses[user], "chapter": chapters[user], "memberID": memberIds[user], "committee": com, "level": levels[prefs[user][com]]}]
#                     break

# for user, coms in prefs.items(): # This second loop will place interested selections in the order of committee priority below the hard cap
#     for com, lvl in coms.items():
#         if int(lvl) == 1 and user not in placed:
#             for c in com_order:
#                 if com == c and com_count[c] < hard_cap[c]:
#                     com_count[c] += 1
#                     placed.append(user)
#                     if com in final:
#                         final[com].append({"user": user, "name": names[user], "status": statuses[user], "chapter": chapters[user], "memberID": memberIds[user], "committee": com, "level": levels[prefs[user][com]]})
#                     else:
#                         final[com] = [{"user": user, "name": names[user], "status": statuses[user], "chapter": chapters[user], "memberID": memberIds[user], "committee": com, "level": levels[prefs[user][com]]}]
#                     break

# Find individuals have not been placed because they didn't make a selection or chose a committee that already hit the hard cap and doesn't have alt.
for user, coms in prefs.items():
    if user not in placed:
        print(user) 

print('Program ran')
json_object = json.dumps(final, indent=4, sort_keys=True)

# Writing to file on desktop
with open("committee_results_new.json", "w") as outfile:
    outfile.write(json_object)

print(len(prefs))
print(com_count)
print(len(placed))