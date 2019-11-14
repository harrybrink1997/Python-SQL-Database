import psycopg2
import sys


courseName = sys.argv[1] if len(sys.argv) > 1 else "COMP1521"

query = '''select (100*g.count)::float/cl.quota as percentFull, cl.tag as class_tag, ct.name as class_type
from subjects s join courses c on (s.id = c.subject_id)
join terms t on (c.term_id = t.id)
join classes cl on (cl.course_id = c.id)
join getClassEnrolments g on (cl.id = g.class_id)
join classtypes ct on (ct.id = cl.type_id)
where s.code like '{}'
and t.name like '19T3'
order by ct.name, cl.tag, percentFull;'''.format(courseName)

view1 = '''create or replace view getClassEnrolments as
select c.class_id, count(*)
from class_enrolments c
group by class_id;'''


try:
    conn = psycopg2.connect("dbname='a3'")
except Exception as e:
    print("Unable to connect to the database")
    print(e)

cur = conn.cursor()

try:
    cur.execute(view1)
except Exception as e:
    print("Error creating view")
    print (e)

try:
    cur.execute(query)
except Exception as e:
    print("Error selecting from table")
    print (e)

classDict = {}
for percentFull, class_tag, class_type in cur.fetchall():

        if percentFull < 50:

            classDict[class_tag] = {}

            classInfo = classDict[class_tag]
            classInfo["fullPercentage"] = round(percentFull)
            classInfo["classtype"] = class_type


for bookedClass in classDict:
    classInfo = classDict[bookedClass]
    print("{} {} is {}% full".format(classInfo["classtype"], bookedClass, classInfo["fullPercentage"]))
    


conn.close()