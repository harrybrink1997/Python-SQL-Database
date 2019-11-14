import psycopg2
import sys

term = sys.argv[1] if len(sys.argv) > 1 else '19T1'



query1 = 


try:
    conn = psycopg2.connect("dbname='a3'")
except Exception as e:
    print("Unable to connect to the database")
    print(e)

cur = conn.cursor()

try:
    cur.execute(query1)
except Exception as e:
    print("Error selecting from table2")
    print (e)

for replace in cur.fetchall():


conn.close()