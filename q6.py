import psycopg2

query = '''select id, weeks
from meetings;'''

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

for id, weeks in cur.fetchall():
    binaryString = [0] * 11
    stringTainted = False
    for c in weeks:
        if c == '<' or c == 'N':
            stringTainted = True

    if stringTainted != True:
        separatedWeeks = weeks.split(',')

        for segments in separatedWeeks:
            weeksRange = segments.split('-')
            if len(weeksRange) > 1:
                for i in range(int(weeksRange[0]), int(weeksRange[1]) + 1):
                    binaryString[i - 1] = 1
            else:
                binaryString[int(weeksRange[0]) - 1] = 1
    
    insertionBinary = ''
    for digit in binaryString:
        insertionBinary += str(digit)

    insertionQuery = '''update meetings 
    set weeks_binary = {} 
    where id = {}'''.format(insertionBinary, id)

    print("{}".format(insertionQuery))

    try:
        cur.execute(insertionQuery)
    except Exception as e:
        print("Error updating the weeks table")
        print(e)

conn.commit()
conn.close()