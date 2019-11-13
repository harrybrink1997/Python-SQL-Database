import psycopg2
import sys


term = sys.argv[1] if len(sys.argv) > 1 else '19T1'

def getHours(start,end):
    hours = 0
    strStart = str(start)
    strEnd = str(end)

    if (strStart[-2] == '3'):
        hours += 0.5
        start += 70
    elif (strEnd[-2] == '3'):
        hours += 0.5
        end -= 30

    hours += ((end - start) / 100)
    return hours


query1 = '''select m.start_time, m.end_time, r.id as room_id, LEFT(m.weeks_binary, 10)
from courses c join terms t on (c.term_id = t.id)
join classes cl on (cl.course_id = c.id)
join meetings m on (cl.id = m.class_id)
join rooms r on (r.id = m.room_id)
where t.name like '{}'
and r.code like 'K-%';'''.format(term)

# '''select m.start_time, m.end_time, r.id as room_id, LEFT(m.weeks_binary,10)
# from meetings m join rooms r on (r.id = m.room_id) 
# join classes cl on (cl.id = m.class_id)
# join courses c on (c.id = cl.course_id)
# join terms t on (t.id = c.term_id)
# where t.name like '{}'
# and r.code like 'K-%';'''.format(term)


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
    hours = getHours(start_time, end_time)

    print("hours is {}".format(hours))
    print("start is {}".format(start_time))
    print("end is {}".format(end_time))
    print("weeks_binary is {}".format(weeks_binary))

    for used in weeks_binary:
        if used == '1':
            weeksCount += 1
    print("weeksCount is {}".format(weeksCount))
    if room_id not in roomDictionary:
        totalRooms += 1
        roomDictionary[room_id] = hours * weeksCount
    else:
        roomDictionary[room_id] += hours * weeksCount

for room in roomDictionary:
    if roomDictionary[room] / numWeeks < 20:
        unusedRooms += 1

print("{}%".format(round((100 * unusedRooms/totalRooms), 1)))

       

conn.close()