import psycopg2
import sys
import os

user_state = {
	'recipient_id':'',
	'fbseq':0,
	'active_question':1,
	'responder_id':''
}
responses = ['This is your Concier. How can I help you?','Let me find someone, who can help you with it.',' is happy to help you with this purchase. Do you want to connect with him?','Great. I am going to connect you to ']
def matchhelper():
	
	'''Get active helpers
	find the one that can help this users and is currently available
	send the reciepient id
	If the conversation is already in progress. Just send the existing helper id.
	something new
	'''
	DATABASE_URL = os.environ['DATABASE_URL']
	con = None
	conn = psycopg2.connect(DATABASE_URL, sslmode='require')

	try:
		#con = psycopg2.connect("host='localhost' dbname='testdb' user='pythonspot' password='password'") 
		con = psycopg2.connect(DATABASE_URL, sslmode='require')
		cur = con.cursor()
		cur.execute("CREATE TABLE Products(Id INTEGER PRIMARY KEY, Name VARCHAR(20), Price INT)")
		cur.execute("INSERT INTO Products VALUES(1,'Milk',5)")
		cur.execute("INSERT INTO Products VALUES(2,'Sugar',7)")
		cur.execute("INSERT INTO Products VALUES(3,'Coffee',3)")
		cur.execute("INSERT INTO Products VALUES(4,'Bread',5)")
		cur.execute("INSERT INTO Products VALUES(5,'Oranges',3)")
		cur.execute("SELECT * FROM Products")
		while True:
			row = cur.fetchone()
			if row == None:
				break
			print("Product: " + row[1] + "\t\tPrice: " + str(row[2]))
		con.commit()
	except psycopg2.DatabaseError, e:
		if con:
			con.rollback()
			print 'Error %s' % e
			sys.exit(1)
	finally:
		if con:
			con.close()


def fbrespond(recipient_id,sequence):
	response_message = 'This is empty'
	if user_state['recipient_id']== recipient_id :
		print("User interaction is in progress")
		if sequence > user_state['fbseq'] :
			#This is new message. Advance to the next question
			print (user_state)
			user_state['fbseq'] = sequence
			if user_state['active_question'] < 3 :
				user_state['active_question'] = user_state['active_question'] + 1
			else :
				user_state['active_question'] = 1
			nextQID = user_state['active_question']
			print (user_state)
			response_message=responses[nextQID]
		else :
			print ('Message came twice')
	# they are already in conversation
	else :
		print ('First interaction')
		user_state['recipient_id'] = recipient_id
		response_message = responses[1]
	return response_message