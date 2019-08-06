import psycopg2
import sys
import os

if __name__ == '__main__':
	#main()
	if len(sys.argv) == 3:
		if 'create' == sys.argv[1]:
			print ("This is CREATE Data Management Operations (DMO) %s",sys.argv[2])
			con = None
			try:
				con = psycopg2.connect("dbname='d20coon3i1dijk' user='tpazwgfztkhlis' host='ec2-23-21-166-148.compute-1.amazonaws.com' password='ffcd560d22ce459a070dac72704648bf1c1f6bed78ee8643b9ee9ceebb6738b8'", sslmode='require')
			except Exception as e:
				print ("I am unable to connect to the database")
			cur = con.cursor()
			cur.execute("CREATE TABLE MEMBERS(Id INTEGER PRIMARY KEY, FB_ID INT, ISHELPER BOOLEAN,ISHELPEE BOOLEAN, SIGNUP_DATE DATE, LAST_ACTIVE DATE, TOKEN_BALANCE REAL)")
			con.close()
		elif 'add' == sys.argv[1]:
			print ("This is ADD Data Management Operations (DMO)")
		elif 'other' == sys.argv[1]:
			print ("Nothing")
