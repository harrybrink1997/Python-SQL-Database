import psycopg2
import sys


courseName = sys.argv[1] if len(sys.argv) > 1 else "ENGG"

query = '''select t.name, s.code, g.count
from subjects s join courses c on (s.id = c.subject_id)
join terms t on (c.term_id = t.id)
join getCourseEnrolments g on (c.id = g.course_id)
join classes cl on (cl.course_id = c.id)
where s.code like '{}%';'''.format(courseName)


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

termDict = {}
for name,code,count in cur.fetchall():

    if name not in termDict:
        termDict[name] = {}
        codeCounts = termDict[name]
        codeCounts[code] = count

    else:
        codeCounts = termDict[name]
        if code not in codeCounts:
            codeCounts[code] = count


for term in sorted(termDict):
    print("{}".format(term))

    codeCounts = termDict[term]

    for course in sorted(codeCounts):
       print(" {}({})".format(course, codeCounts[course]))



conn.close()