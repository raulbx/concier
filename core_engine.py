import psycopg2
import sys
import os
import firebase_admin
import datetime
import ast
from firebase_admin import credentials
from firebase_admin import firestore

class Members(object):
	cred = credentials.Certificate(ast.literal_eval(os.environ["FIREBASE_CONFIG"]))
	firebase_admin.initialize_app(cred)

	def __init__(self, facebok_id, source='Blank'):
		self.fb_id = facebok_id
		self.source = source

	def get_member(self):
		db = firestore.client()
		query_refs = db.collection(u'members').where(u'fb_id', u'==', self.fb_id).get()
		member_ref = None
		try:
			#member_refs = query_ref.get()
			for member in query_refs:
				member_ref = db.collection(u'members').document(member.id)
			if member_ref is None:
				print("Member doesn't exist. Adding Member")
				member_ref = Members(self.fb_id,'FB').add_member()[1]
		except ValueError:
			print(u'Value Error.....!')
		except:
			print(u'This is an Exception situation')
		return member_ref

	def add_member(self):
    	#if not member_exists:
		member_data = {
		'fb_id': self.fb_id,
		'source': self.source,
		'is_helper':False,
		'is_helpee':True,
		'token_balance':0,
		'conversations':[], # Good idea is to store references in this array
		'expertise':['electronics','health'],
		'signupdate':datetime.datetime.now(),
		'lastactivedate':datetime.datetime.now()
		}
		print("Added Member")
		db = firestore.client()
		return db.collection(u'members').add(member_data)
	
	def add_conversation(self,helpee_ref):
		conversation_data = {
    	'helpee_ref':helpee_ref, # this is reference to the helper obj
    	#'helpee_id':helpee_id,
    	'active':True,
    	'conversation_state':0,
    	'current_chat_seq':0,
    	'startdate':datetime.datetime.now(),
    	'lastactivedate':datetime.datetime.now()
    	}
		db = firestore.client()
		return db.collection(u'conversations').add(conversation_data)

	def get_active_conversation(self,member):
		# Get the latest conversation. If no convers
		conversations_array = member.get().get('conversations')
		#active_conv = len(conversations_array)
		conversation_ref = conversations_array[0]
		# TODO: Need to fix above to get the right conversation
		conversation = conversation_ref.get()
		return conversation