import psycopg2


view1 = '''create or replace view splitCodes as
select substring(s.code from 1 for 3) as letters, substring(s.code from 5 for 7) as numbers
from subjects s;'''

view2 = '''create or replace view countCodes as
select s.numbers, count(*)
from splitCodes s
group by s.numbers;'''

query = '''select *
from countCodes c join splitCodes s on (s.numbers = c.numbers)
where c.count = 8
order by c.numbers asc;'''





try:
    conn = psycopg2.connect("dbname='a3'")
except Exception as e:
    print("Unable to connect to the database")
    print(e)

cur = conn.cursor()

numCourses = 8
try:
    cur.execute(view1)
except Exception as e:
    print("Error creating view")
    print (e)

try:
    cur.execute(view2)
except Exception as e:
    print("Error creating view")
    print (e)

try:
    cur.execute(query)
except Exception as e:
    print("Error selecting from table")
    print (e)


checker = 1
courses = []
for numbers, count, letters, _ignore in cur.fetchall():

    if (checker % numCourses == 1):
        if (checker != 1):
            
            print('{}'.format(courses))
            courses = []
        
        courses.append(numbers)

    courses.append(letters)
    checker += 1

    

conn.close()