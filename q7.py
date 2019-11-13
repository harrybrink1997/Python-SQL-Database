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

query1 = '''select m.start_time, m.end_time, r.id as room_id, m.weeks_binary
from meetings m join rooms r on (r.id = m.room_id) 
join classes cl on (cl.id = m.class_id)
join courses c on (c.id = cl.course_id)
join terms t on (t.id = c.term_id)
where t.name like '{}'
and r.code like 'K-%';'''.format(term)


# select m.start_time, m.end_time, r.id as room_id, m.weeks_binary
# from meetings m join rooms r on (r.id = m.room_id) 
# join classes cl on (cl.id = m.class_id)
# join courses c on (c.id = cl.course_id)
# join terms t on (t.id = c.term_id)
# where t.name like '19T1'
# and r.code like 'K-%';

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
totalRooms = 0
numWeeks = 10
roomDictionary = {}
for start_time, end_time, room_id, weeks_binary in cur.fetchall():
    weeksCount = 0
    hours = float(end_time) - float(start_time) / 100
    print("hours is {}".format(hours))
    print("weeks_binary is {}".format(weeks_binary))
    for used in weeks_binary:
        if used == '1':
            weeksCount += 1
    print("weeksCount is {}".format(weeksCount))
    if room_id not in roomDictionary:
        totalRooms += 1
        roomDictionary[room_id] = hours * weeksCount
        print("roomDictionary[room_id] is {}".format(roomDictionary[room_id]))
    else:
        roomDictionary[room_id] += hours * weeksCount
        print("roomDictionary[room_id] is {}".format(roomDictionary[room_id]))

for room in roomDictionary:
    if roomDictionary[room] / numWeeks < 20:
        unusedRooms += 1

print("{}%".format(round((100 * unusedRooms/totalRooms), 1)))

       

conn.close()