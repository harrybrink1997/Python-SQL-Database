import psycopg2
import sys


#numCourses = sys.argv[1] if len(sys.argv) > 1 else 2
#if (int(numCourses) < 2 or int(numCourses) > 10):
#    numCourses = 2


view1 = '''create or replace view splitCodes as
select substring(s.code from 1 for 4) as letters, substring(s.code from 5 for 7) as numbers
from subjects s;'''

view2 = '''create or replace view countCodes as
select s.numbers, count(*)
from splitCodes s
group by s.numbers;'''

query = '''select *
from countCodes c join splitCodes s on (s.numbers = c.numbers)
where c.count = 8
order by c.numbers asc;'''#.format(int(numCourses))





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
    cur.execute(view2)
except Exception as e:
    print("Error creating view")
    print (e)

try:
    cur.execute(query)
except Exception as e:
    print("Error selecting from table")
    print (e)

numCourses = 8
checker = 1
courses = []
for numbers, count, letters, _ignore in cur.fetchall():

    if checker == numCourses:
        courses.append(letters)

        courseNumbers = courses[0]
        courses.pop(0)
        sortedCourses = sorted(courses)
        
        print('{}: '.format(courseNumbers), end = ""),

        for i in range(len(sortedCourses)):
            print('{} '.format(sortedCourses[i]), end = "" ),

        print("")
        courses = []
        checker = 1

    elif checker == 1:
        courses.append(numbers)
        courses.append(letters)
        checker += 1
    else:
        courses.append(letters)
        checker += 1

    
conn.close()