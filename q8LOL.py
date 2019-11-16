# COMP3311 19T3 Assignment 3

import cs3311
import sys
import copy

# yeet should probs use OO but cbf so here's a global variable haha
lowestCost = None
optimalTimetables = []

'''
Generates a dict of timetables for each course
    dict = {course : timetables} 
'''
def getTimetables(courses, cur):
    allTimetables = {}
    for course in courses:
        tt = getTimetableForCourse(cur, course)
        allTimetables[course] = tt
    return allTimetables

'''
Generates a dict of timetables for a course
    dict = {classtype: {classID : [meeting times]}}
'''
def getTimetableForCourse(cur, course):
    query = '''select * from q8('{}')'''.format(course)
    cur.execute(query)
    classTimetables = {}
    for tup in cur.fetchall():
        classid, classType, day, start, end = tup
        if (classType == 'Web stream'):
            classTimetables[classType] = []
        elif (classTimetables.get(classType) is None):
            classTimetables[classType] = {classid : [(day, start, end)]}
        elif (classTimetables[classType].get(classid) is None):
            classTimetables[classType][classid] = [(day, start, end)]
        else:
            classTimetables[classType][classid].append((day, start, end))
    return classTimetables

'''
    Attempts to generate a timetable
'''
def scheduleMeUp(timetables):
    optimalSchedule = {}
    # choose lecture streams for courses first of all 
    # if it has a web stream lecture - it doesn't show up 
    courseLecs = []
    for course, courseSched in timetables.items():
        numStreams = 0
        if (courseSched.get('Web Stream') is not None) :
            courseSched.pop('Web Stream')
            numStreams = 0
        elif (courseSched.get('Lecture') is not None):
            numStreams = len(courseSched.get('Lecture').keys())

        courseLecs.append((course, numStreams))
    courseLecs.sort(key= lambda x : x[1])
    # select lectures 
    selectLectures(courseLecs, optimalSchedule, timetables)

    global lowestCost
    global optimalTimetables
    #print(lowestCost)
    #print(optimalTimetables)
    for tt in optimalTimetables:
        outputResult(tt, calculateCost(tt))


def outputResult(optimalSchedule, cost):
    print('Total hours: {:.1f}'.format(cost))
    results = []
    for day, times in optimalSchedule.items():
        if (not times):
            continue
        
        classTimes = []
        for times, course in times.items():
            classTimes.append((times, course))

        classTimes.sort()
        results.append((day, classTimes))

    results.sort(key=lambda x : _sortByWeekDays1(x))

    for day, times in results:
        print('  {}'.format(day))
        for time in times:
            print('    {}{}-{}'.format(time[1], time[0][0], time[0][1]))

'''
    Calculates hours spent on campus
'''
def calculateCost(optimalSchedule):
    totalHours = 0
    for day, times in optimalSchedule.items():
        totalHours+=2
        campushours = list(times.keys())
        campushours.sort()
        start = campushours[0][0]
        end = campushours[-1][-1]
        endAsMin = 60*(end // 100) + (end % 100)
        startAsMin = 60*(start // 100) + (start % 100)
        hrdiff = (endAsMin - startAsMin)/60
        totalHours += hrdiff
    return totalHours


'''
    Given a list of remaining courses, selects classes for that course
'''
def selectClasses(timetables, optimalSchedule, coursesRemaining):
    # duplicate code bcos we want to find out the class types first

    # if no courses remaining add to timetables
    # if courses remaining, but selected course has no classes, then pop and continue
    # if 1 course remaining and selected course has no classes, then add to timetables
    tmpClassTypes = []
    if (len(coursesRemaining) >= 1):
        tmpClassTypes = [x for x in timetables[coursesRemaining[-1]].keys() if x != 'Lecture']

    
    # have finished our selections or no classes to select
    if (len(coursesRemaining) == 0 or (len(coursesRemaining) == 1 and len(tmpClassTypes) == 0)):
        global lowestCost
        global optimalTimetables
        cost = calculateCost(optimalSchedule)
        if (lowestCost is None):
            lowestCost = cost
            optimalTimetables.append(optimalSchedule)
        elif (cost == lowestCost):
            optimalTimetables.append(optimalSchedule)
        elif (cost < lowestCost):
            lowestCost = cost
            optimalTimetables = [optimalSchedule]
        return

    coursesRemaining = copy.deepcopy(coursesRemaining)
    courseToSelectFor = coursesRemaining.pop()
    classTypes = [x for x in timetables[courseToSelectFor].keys() if x != 'Lecture']
    selectRecurse(timetables, optimalSchedule, courseToSelectFor, classTypes, coursesRemaining)

'''
    Selects classes for a course and then selects more classes for other courses 
'''
def selectRecurse(timetables, optimalSchedule, course, classTypes, coursesRemaining):
    if (len(classTypes) == 0):
        selectClasses(timetables, optimalSchedule, coursesRemaining)
        return

    classTypes = copy.deepcopy(classTypes)
    classType = classTypes.pop()
    # generate all meetings
    # List1. Meetings that occur on days we have class, ordered by time
    # List2. Meetings that occur on days we don't have class, ordered by earliness
    allMeetings = [x for x in timetables[course][classType].values()]
    priorityMeetings = []
    lowPriMeetings = []

    for meeting in allMeetings:
        days = [x[0] for x in meeting]
        if any(day in optimalSchedule.keys() for day in days):
            if meeting not in priorityMeetings:
                priorityMeetings.append(meeting)
        elif meeting not in lowPriMeetings:
            lowPriMeetings.append(meeting)
            
    priorityMeetings.sort(key=lambda x: _sortByWeekDays(x))
    lowPriMeetings.sort(key=lambda x: _sortByWeekDays(x))
    allMeetings = priorityMeetings + lowPriMeetings

    # recursively enrol in other classes
    # choose class for given class type then recurse
    for potential in allMeetings:
        # add to schedule, otherwise continue - spawn more copies of schedule
        schedule = copy.deepcopy(optimalSchedule)
        if (addToTimetable(potential, course, classType, schedule)):
            
            currentCost = calculateCost(schedule)
            global lowestCost
            # if current cost is already greater than current minimum then this 
            # time table is useless so discard and move on
            if (lowestCost is not None and currentCost > lowestCost):
                continue
        
            # we've successfuly selected all classes so now choose other courses
            if (len(classTypes) == 0):
                selectClasses(timetables, schedule, coursesRemaining)
            # otherwise choose remaining class types 
            else:
                selectRecurse(timetables, schedule, course, classTypes, coursesRemaining)



def selectLectures(lectureTimes, optimalSchedule, timetables):
    # lecture times selected, now select courses
    if (len(lectureTimes) == 0):
        selectClasses(timetables, optimalSchedule, list(timetables.keys()))
        return

    lectureTimes = copy.deepcopy(lectureTimes)
    course, numStreams = lectureTimes.pop(0)
    if (numStreams == 0):
        selectLectures(lectureTimes, optimalSchedule, timetables)
    elif (numStreams == 1):
        for k,v in timetables[course]['Lecture'].items():
            addToTimetable(v, course, 'Lecture', optimalSchedule)
        selectLectures(lectureTimes, optimalSchedule, timetables)
    else:
        lectures = [x for x in timetables[course]['Lecture'].values()]
        lectures.sort(key= lambda x: _sortByWeekDays(x))
        print(lectures)
        print("")
        for meeting in lectures:
            schedule = copy.deepcopy(optimalSchedule)
            # attempt to add lecture and gauge optimal cost
            if (addToTimetable(meeting, course, 'Lecture', schedule)):
                global lowestCost
                if (lowestCost is not None and calculateCost(schedule) > lowestCost):
                    continue
                else:
                    # select remaining lectures
                    selectLectures(lectureTimes, schedule, timetables)
            # if lecture can't be added then continue
            else:
                continue

def removefromTimetable(meetings, optimalSchedule):
    for meeting in meetings:
        day, start, end = meeting
        if (optimalSchedule.get(day) is None):
            print("ruhroh")
        else:
            optimalSchedule[day].pop((day, start, end))

def addToTimetable(meetings, courseName, classType, optimalSchedule):
    if (classType == 'Lecture'):
        print(meetings)
    # check if each meeting can be added
    for meeting in meetings:
        day, start, end = meeting
        # dont need to worry about conflicts if no classes on day
        if (optimalSchedule.get(day) is None):
            continue
        # check if overlap
        else:
            for existStart,existEnd in optimalSchedule[day].keys():
                if (start < existEnd and existStart < end):
                    return False 

    # if we haven't returned, then there are no overlaps so we can add
    for meeting in meetings:
        day, start, end = meeting
        if (optimalSchedule.get(day) is None):
            optimalSchedule[day] = {}

        optimalSchedule[day][(start,end)] = courseName + " " + classType + ": "
                        
    return True

def _sortByWeekDays(x):
    x = x[0]
    switch = {
        "Mon" : 1,
        "Tue" : 2,
        "Wed" : 3,
        "Thu" : 4,
        "Fri" : 5
    }

    return (switch.get(x[0], 6), x[1], x[2])

def _sortByWeekDays1(x):
    switch = {
        "Mon" : 1,
        "Tue" : 2,
        "Wed" : 3,
        "Thu" : 4,
        "Fri" : 5
    }

    return switch.get(x[0], 6)

if __name__ == "__main__":
    if (len(sys.argv) > 1 and len(sys.argv) <= 4):
        courses = sys.argv[1:]
    else: 
        courses = ['COMP1511', 'MATH1131']

    conn = cs3311.connect()
    cur = conn.cursor()

    timetables = getTimetables(courses, cur)
    optimalSchedule = scheduleMeUp(timetables)

    cur.close()
    conn.close()