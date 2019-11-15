import psycopg2
import sys
import copy
import operator

# Global variables

optimisedTT = []
lowestTimeTableCost = None

# Generate the queries for each course to call.


def GetTimeTableQueries(subjectsArray):
    classesQuery = []
    for subject in range(len(subjectsArray)):
        classesQuery.append(
            '''select s.code, ct.name, m.day, cl.tag, m.start_time, m.end_time from courses c join terms t on (c.term_id = t.id) join subjects s on (s.id = c.subject_id) join classes cl on (cl.course_id = c.id) join classtypes ct on (ct.id = cl.type_id) join meetings m on (cl.id = m.class_id) join rooms r on (r.id = m.room_id)where t.name like '19T1' and r.code like 'K-%' and s.code like '{}'order by ct.name, m.day, m.start_time;'''.format(subjectsArray[subject]))

    return classesQuery


def printTimeTable(optimisedTT, lowestTimeTableCost):
    print("")
    print("Printing formatted timetable")

    print("Total hours: {}".format(round(lowestTimeTableCost, 1)))

    for day in optimisedTT:
        dayToPrint = convertDaysToString(day)
        dayClasses = optimisedTT[day]

        print("  {}".format(dayToPrint))

        for subjects in dayClasses:
            course = subjects.get('course')
            classtype = subjects.get('classtype')
            startTime = subjects.get('start')
            endTime = subjects.get('end')
            print("    {} {}: {}-{}".format(course, classtype, startTime, endTime))

    print("")
    print("default printing")
    print("")
    print(lowestTimeTableCost)
    print(optimisedTT)


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
            print(e)

        subjectClasses[subjectsArray[i]] = {}
        currSubject = subjectClasses[subjectsArray[i]]

        for code, classtype, day, tag, start_time, end_time in cur.fetchall():
            day = getDayofWeek(day)  # Converts days into number for sorting.
            if classtype not in currSubject:

                if classtype == 'Web Stream':
                    currSubject[classtype] = []
                else:
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


def daysAtUni(OSched):
    totalDays = 0

    for days in OSched:
        totalDays += 1

    return totalDays


def hoursInDay(coursesInDay):
    minTime = None
    maxTime = None

    for subject in coursesInDay:
        if minTime == None and maxTime == None:
            minTime = subject.get('start')
            maxTime = subject.get('end')
        else:
            if subject.get('start') < minTime:
                minTime = subject.get('start')

            if subject.get('end') > maxTime:
                maxTime = subject.get('end')

    totalTime = 0
    strMinTime = str(minTime)
    strMaxTime = str(maxTime)
    if (strMinTime[-2] == '3'):
        totalTime += 0.5
        strMinTime[-2] = '0'

    if (strMaxTime[-2] == '3'):
        totalTime -= 0.5
        strMaxTime[-2] = '0'

    minTime = int(strMinTime)
    maxTime = int(strMaxTime)

    totalTime += (maxTime - minTime) / 100

    return totalTime


def overLappingEvents(event1, event2):
    if event1.get('start') < event2.get('end') and event2.get('start') < event1.get('end'):
        return True
# only takes single dictionary objects not arrays.


def addToTT(type, classes, OSched, course):
    print("input into addtt function: {}".format(classes))
    print("")
    day = classes.get('day')

    if day in OSched:
        targetDay = OSched[day]
        for event in targetDay:
            if overLappingEvents(classes, event) == True:
                return False
            else:
                continue

    # for meeting in classes:
    #     print(meeting)
    #     day = meeting.get('day')

    #     if day not in OSched:
    #         continue
    #     else:
    #         targetDay = OSched[day]
    #         for event in targetDay:
    #             if overLappingEvents(targetDay, event) == True:
    #                 return False
    #             else:
    #                 continue

    classes['classtype'] = type
    classes['course'] = course
    if day not in OSched:
        OSched[day] = []
        day = OSched[day]
        day.append(classes)
    else:
        day = OSched[day]
        day.append(classes)

    return True


def totalHoursDaysTravel(OSched):

    totalDays = daysAtUni(OSched)
    travelTime = totalDays * 2
    timeSpentAtUni = 0

    for daysPresent in OSched:
        timeSpentAtUni += hoursInDay(OSched.get(daysPresent))

    return (timeSpentAtUni + travelTime)


def determineIfOptimised(OSched):
    global lowestTimeTableCost
    global optimisedTT

    currCost = totalHoursDaysTravel(OSched)

    if (lowestTimeTableCost is None):
        lowestTimeTableCost = currCost
        optimisedTT.append(OSched)
    elif currCost < lowestTimeTableCost:
        lowestTimeTableCost = currCost
        optimisedTT = [OSched]
    elif currCost == lowestTimeTableCost:
        optimisedTT.append(OSched)

    return


def addClasses(courseClasses, OSched, remaining):

    courseClassTypes = []

    if (len(remaining) > 1):
        targetCourse = courseClasses.get(remaining[-1])
        for classtypes in targetCourse:
            if (classtypes != 'Lecture'):
                courseClassTypes.append(classtypes)

    if (len(remaining) == 0 or (len(remaining) == 1 and len(courseClassTypes) == 0)):
        determineIfOptimised(OSched)
        return

    remaining = copy.deepcopy(remaining)
    targetCourse = remaining.pop()
    CTSelection = []
    targetCourseObj = courseClasses.get(targetCourse)
    for classtypes in targetCourseObj:
        if (classtypes != 'Lecture'):
            CTSelection.append(classtypes)
    selectCourseClasses(courseClasses, OSched,
                        targetCourse, CTSelection, remaining)


def altDayClasses(OSched, classArray):
    classesOutput = []

    for day in OSched:
        for classes in classArray:
            if classes.get('day') != day:
                classesOutput.append(classes)

    return sorted(classesOutput, key=lambda i: (i['day'], i['start']))


def sameDayClasses(OSched, classArray):
    classesOutput = []

    for day in OSched:
        for classes in classArray:
            if classes.get('day') == day:
                classesOutput.append(classes)

    return sorted(classesOutput, key=lambda i: (i['day'], i['start']))


def selectCourseClasses(courseClasses, OSched, course, types, remaining):
    if (len(remaining) == 0):
        addClasses(courseClasses, OSched, remaining)
        return

    types = copy.deepcopy(types)
    targetCT = types.pop()

    courseObject = courseClasses.get(course)
    CTArray = courseObject.get(targetCT)

    SDClasses = sameDayClasses(OSched, CTArray)
    ADClasses = altDayClasses(OSched, CTArray)
    availCourseClasses = SDClasses + ADClasses

    for classes in availCourseClasses:
        currOptSched = copy.deepcopy(OSched)

        if (addToTT(targetCT, classes, OSched, course) == True):
            currCost = totalHoursDaysTravel(currOptSched)
            global lowestTimeTableCost

            if (lowestTimeTableCost is not None and currCost > lowestTimeTableCost):
                continue

            if (len(types) == 0):
                addClasses(courseClasses, OSched, remaining)
            else:
                selectCourseClasses(courseClasses, OSched,
                                    course, types, remaining)


def lectureEntriesIdentical(lec1, lec2):
    if lec1.get('start') == lec2.get('start') and lec1.get('end') == lec2.get('end') and lec1.get('day') == lec2.get('day') and lec1.get('tag') == lec2.get('tag'):
        return True

    return False


def lectureSelected(lec, courseLectures):
    if len(courseLectures) == 0:
        return False
    else:
        for lecture in courseLectures:
            if lectureEntriesIdentical(lec, lecture):
                return True

    return False


def findLectures(course, courseClasses):
    courseLectures = courseClasses.get(course).get('Lecture')
    lectureSlots = []

    for lecture in courseLectures:
        if lectureSelected(lecture, lectureSlots) == False:
            lectureSlots.append(lecture)

    return lectureSlots


def addLectures(lecStreamAsc, OSched, courseClasses):
    if (len(lecStreamAsc) == 0):
        addClasses(courseClasses, OSched, list(courseClasses.keys()))
        return

    # Run thourgh all the lecture slots.
    lecStreamAsc = copy.deepcopy(lecStreamAsc)
    courseObject = lecStreamAsc.pop(0)
    numStreams = courseObject.get('numStreams')
    course = courseObject.get('course')

    if (numStreams == 0):
        addLectures(lecStreamAsc, OSched, courseClasses)
    elif (numStreams == 1):
        lectureToAdd = findLectures(course, courseClasses)
        addToTT('Lecture', lectureToAdd, OSched, course)
        addLectures(lecStreamAsc, OSched, courseClasses)
    else:

        lecturesToAdd = findLectures(course, courseClasses)
        # not working bringing out everything. TODO
        print("lectures to add: {}".format(lecturesToAdd))
        print("")
        lecturesToAdd.sort(key=operator.itemgetter('day'))
        for lecture in lecturesToAdd:
            opitmalSched = copy.deepcopy(OSched)
            if addToTT('Lecture', lecture, OSched, course) == True:
                global lowestTimeTableCost
                if (lowestTimeTableCost is not None and totalHoursDaysTravel(opitmalSched) > lowestTimeTableCost):
                    continue
                else:
                    addLectures(lecStreamAsc, OSched, courseClasses)
            else:
                continue


def convertDaysToString(num):
    days = {
        "1": "Monday",
        "2": "Tuesday"
        "3": "Wednesday"
        "4": "Thursday"
        "5": "Friday"
    }


def getDayofWeek(day):
    days = {
        "Mon": 1,
        "Tue": 2,
        "Wed": 3,
        "Thu": 4,
        "Fri": 5
    }

    return days[day]


def numLectureStreams(lectureArray):
    # TODO this is wrong! i think...
    streams = []
    for i in lectureArray:
        if i.get('tag') not in streams:
            streams.append(i.get('tag'))

    return len(streams)


def generateTermTT(courseClasses):
    OSched = {}
    lectures = []
    for subject in courseClasses:
        lectureStreams = 0

        if 'Web Stream' in courseClasses.get(subject):
            lectureStreams = 0
            courseClasses.get(subject).pop('Web Stream')
        else:
            lectureStreams = numLectureStreams(
                courseClasses.get(subject).get('Lecture'))

        lectures.append({
            "course": subject,
            "numStreams": lectureStreams
        })

    # lecStreamAsc = lectures.sort(key=operator.itemgetter('numStreams'), reverse=False)
    lecStreamAsc = sorted(lectures, key=lambda i: (i['numStreams']))
    print(lecStreamAsc)
    print("")

    addLectures(lecStreamAsc, OSched, courseClasses)

    global optimisedTT
    global lowestTimeTableCost
    for timetable in optimisedTT:
        printTimeTable(timetable, lowestTimeTableCost)


if __name__ == "__main__":

    if len(sys.argv) > 1 and len(sys.argv) <= 4:
        subjectsArray = sys.argv[1:]
    else:
        subjectsArray = ['COMP1511', 'MATH1131']

    queries = GetTimeTableQueries(subjectsArray)
    courseClasses = queryClassTT(queries)
    generateTermTT(courseClasses)
