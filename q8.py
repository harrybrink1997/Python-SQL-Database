import psycopg2
import sys

subjects = []  

term = sys.argv[1] if len(sys.argv) > 1 else '19T1'

term = '19T1'
subjectsArray = ['COMP1511']

classesQuery = []

for subject in range(len(subjectsArray)):
    classesQuery.append(
        '''select s.code, ct.name, m.day, cl.tag, m.start_time, m.end_time
        from courses c join terms t on (c.term_id = t.id)
        join subjects s on (s.id = c.subject_id)
        join classes cl on (cl.course_id = c.id)
        join classtypes ct on (ct.id = cl.type_id)
        join meetings m on (cl.id = m.class_id)
        join rooms r on (r.id = m.room_id)
        where t.name like '{}'
        and r.code like 'K-%'
        and s.code like '{}'
        order by ct.name, m.day, m.start_time;'''.format(term,subjectsArray[subject])
    ) 



# select s.code, ct.name as classtype, m.day, cl.tag, m.start_time, m.end_time
# from courses c join terms t on (c.term_id = t.id)
# join subjects s on (s.id = c.subject_id)
# join classes cl on (cl.course_id = c.id)
# join classtypes ct on (ct.id = cl.type_id)
# join meetings m on (cl.id = m.class_id)
# join rooms r on (r.id = m.room_id)
# where t.name like '19T1'
# and r.code like 'K-%'
# and s.code like 'COMP1511'
# order by ct.name, m.day, m.start_time;

try:
    conn = psycopg2.connect("dbname='a3'")
except Exception as e:
    print("Unable to connect to the database")
    print(e)

cur = conn.cursor()

# Gets all the classes for each course. 
subjectClasses = {}
for i in range(len(classesQuery)):
    try:
        cur.execute(classesQuery[i])
    except Exception as e:
        print("Error selecting from table2")
        print (e)

    subjectClasses[subjectsArray[i]] = {}
    currSubject = subjectClasses[subjectsArray[i]]

    for code, classtype, day, tag, start_time, end_time in cur.fetchall():
        
        if (classtype == 'Lecture'):
            print(tag)

        if classtype not in currSubject:
            currSubject[classtype] = {}
            currClassType = currSubject[classtype]
            currClassType[tag] = { 
                'day': day, 'start': start_time, 'end': end_time
            }
        else:
            currClassType = currSubject[classtype]
            currClassType[tag] = { 
                'day': day, 'start': start_time, 'end': end_time
            }

print(subjectClasses.get('COMP1511').get('Lecture'))



conn.close()

def overLap(start1, end1, start2, end2):
    return False

def daysAtUni(days):
    return 2

def hoursInDay():
    return 3

def addClasses(classesDict):
    print(classesDict)

# timeTables = {}
# for courses in subjectClasses:
#     addClasses(subjectClasses.get(courses).get('Lectures'))






