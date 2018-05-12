import psycopg2
import sys
import os
import firebase_admin
import datetime
import ast
from firebase_admin import credentials
from firebase_admin import firestore


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

def checkDB():
	firebase_config = ast.literal_eval(os.environ["FIREBASE_CONFIG"])
	cred = credentials.Certificate(firebase_config)
	firebase_admin.initialize_app(cred)
	db = firestore.client()
	fb_id='16093421424752504'
	query_ref = db.collection(u'members').where(u'fb_id', u'==', self.fb_id)
	member_obj = None
	members = query_ref.get()
	for member in members:
		member_obj = db.collection(u'members').document(member.id)
		print ('Found Member')
	print(member_obj.id)
	return 'Success'