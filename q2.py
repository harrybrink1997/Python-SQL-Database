import psycopg2


create or replace view splitCodes as
select substring(s.code from 1 for 3) as letters, substring(s.code from 5 for 7) as numbers
from subjects s;

create or replace view countCodes as
select s.numbers, count(*)
from splitCodes s
group by s.numbers;

select *
from countCodes c join splitCodes s on (s.numbers = c.numbers)
where c.count = 8
order by c.numbers asc;





try:
    conn = psycopg2.connect("dbname='a3'")
except Exception as e:
    print("Unable to connect to the database")
    print(e)

cur = conn.cursor()

numCourses = 8
try:
    cur.execute("")
except Exception as e:
    print("Error selecting from table")
    print (e)

for numbers, count, letters in cur.fetchall():
    checker = 1
    courses = []
    if (checker % numCourses == 1)
        if (checker != 1)
            
            print(courses)
        
        courses = [numbers]

    courses.append(letters)

    

conn.close()