import psycopg2
import sys
import copy

#Global variables

optimisedTT = []
lowestTimeTableCost = None

# Generate the queries for each course to call.
def GetTimeTableQueries(subjectsArray):

    for subject in range(len(subjectsArray)):
        classesQuery = []

        classesQuery.append( '''select s.code, ct.name, m.day, cl.tag, m.start_time, m.end_time from courses c join terms t on (c.term_id = t.id) join subjects s on (s.id = c.subject_id) join classes cl on (cl.course_id = c.id) join classtypes ct on (ct.id = cl.type_id) join meetings m on (cl.id = m.class_id) join rooms r on (r.id = m.room_id)where t.name like '19T1' and r.code like 'K-%' and s.code like '{}'order by ct.name, m.day, m.start_time;'''.format(subjectsArray[subject])
        )
    print(len(classesQuery))
    return classesQuery


def queryClassTT(classesQuery):

    try:
        conn = psycopg2.connect("dbname='a3'")
    except Exception as e:
        print("Unable to connect to the database")
        print(e)

    cur = conn.cursor()


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

            if classtype not in currSubject:
                currSubject[classtype] = []
                currClassType = currSubject[classtype]
                currClassType.append({ 
                    'tag': tag, 'day': day, 'start': start_time, 'end': end_time
                })
            elif classtype in currSubject:
                currClassType = currSubject[classtype]
                currClassType.append({ 
                    'tag': tag, 'day': day, 'start': start_time, 'end': end_time
                })

    conn.close()
    return subjectClasses




def overLap(start1, end1, start2, end2):
    NotImplemented

def daysAtUni(days):
    NotImplemented

def hoursInDay():
    NotImplemented

def totalHoursAndDays():
    NotImplemented
def addClasses(classesDict):
    NotImplemented
def addLectures(classDict):
    NotImplemented
def generateTermTT(courseClasses):
    NotImplemented


if __name__ == "__main__":

    if len(sys.argv) > 1 and len(sys.argv) <= 4:
        subjectsArray = sys.argv[1:]
    else:
        subjectsArray = ['COMP1511', 'MATH1131']

    queries = GetTimeTableQueries(subjectsArray)
    print(queries)
    courseClasses = queryClassTT(queries)
    print(courseClasses)
    # schedule = generateTermTT(courseClasses)





