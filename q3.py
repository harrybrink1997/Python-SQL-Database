import psycopg2
import sys


courseName = sys.argv[1] if len(sys.argv) > 1 else "ENGG"
# to be replaced for creating purposes

query = '''select s.code, b.name
from subjects s join courses c on (s.id = c.subject_id)
join terms t on (c.term_id = t.id)
join classes cl on (cl.course_id = c.id)
join meetings m on (cl.id = m.class_id)
join rooms r on (r.id = m.room_id)
join buildings b on (b.id = r.within)
where t.name like '19T2'
and s.code like '{}%'
order by b.name;'''.format(courseName)

print("{}".format(query))

try:
    conn = psycopg2.connect("dbname='a3'")
except Exception as e:
    print("Unable to connect to the database")
    print(e)

cur = conn.cursor()

try:
    cur.execute(query)
except Exception as e:
    print("Error selecting from table")
    print (e)

buildingDict = {}

for code,name in cur.fetchall():

    if name not in buildingDict:
        buildingDict[name] = [code]
    else:
        courseCodes = buildingDict[name]
        if code not in courseCodes:
            courseCodes.append(code)

for building in sorted(buildingDict):
    print("{}".format(building))
    courseCodes = sorted(buildingDict[building])

    for i in range(len(courseCodes)):
        print(" {}".format(courseCodes[i]))



conn.close()