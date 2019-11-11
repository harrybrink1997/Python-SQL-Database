import psycopg2

try:
    conn = psycopg2.connect("dbname='a3'")
except Exception as e:
    print("Unable to connect to the database")
    print(e)

cur = conn.cursor()

view1 = '''create or replace view getCourseEnrolments as
select c.course_id, count(*)
from course_enrolments c
group by course_id;'''

query = '''select s.code, c.quota, g.count
from subjects s join courses c on (s.id = c.subject_id)
join terms t on (c.term_id = t.id)
join getCourseEnrolments g on (c.id = g.course_id)
where t.name like '19T3'
and c.quota > 50
and g.count > c.quota
order by s.code;'''

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

rows = cur.fetchall()

for tochange in rows:


conn.close()



