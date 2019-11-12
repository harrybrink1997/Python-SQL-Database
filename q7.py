import psycopg2
import sys


term = sys.argv[1] if len(sys.argv) > 1 else 1
if (int(term) < 1 or int(term) > 3):
    term = 1


if (term == 1): 
    term = '19T1'
elif term == 2:
    term = '19T2'
elif term == 3:
    term = '19T3'

query1 = '''select (m.end_time::float - m.start_time::float)/100 as hours, r.id as room_id, m.weeks_binary
from meetings m join rooms r on (r.id = m.room_id) 
join classes cl on (cl.id = m.class_id)
join courses c on (c.id = cl.course_id)
join terms t on (t.id = c.term_id)
where t.name like '{}'
and r.code like 'K%';'''.format(term)

try:
    conn = psycopg2.connect("dbname='a3'")
except Exception as e:
    print("Unable to connect to the database")
    print(e)

cur = conn.cursor()

try:
    cur.execute(query1)
except Exception as e:
    print("Error selecting from table2")
    print (e)

unusedRooms = 0
numWeeks = 10
roomDictionary = {}
for hours, room_id, weeks_binary in cur.fetchall():
    weeksCount = 0
    for used in weeks_binary:
        if used == '1':
            weeksCount += 1

    if room_id not in roomDictionary:
        roomDictionary[room_id] = hours * weeksCount
    else:
        roomDictionary[room_id] += hours * weeksCount

for room in roomDictionary:
    totalRooms += 1
    if roomDictionary[room] / numWeeks < 20:
        unusedRooms += 1

print("{}%".format(round((unusedRooms/totalRooms), 1)))

       

conn.close()