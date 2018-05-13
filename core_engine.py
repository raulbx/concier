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
        #cred = credentials.Certificate(ast.literal_eval(os.environ["FIREBASE_CONFIG"]))
        #firebase_admin.initialize_app(cred)
        #print("Initialization")
        #self.db = firestore.client()

    def find_member(self):
    	db = firestore.client()
    	query_ref = db.collection(u'members').where(u'fb_id', u'==', self.fb_id)
    	#member_obj = None
    	try:
    		members = query_ref.get()
    		for member in members:
    			member_obj = db.collection(u'members').document(member.id)
    			print ('Found Member')
    	except ValueError:
    		print(u'Value Error.....!')
    	except:
    		print(u'No such document!')
    	return member_obj

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
    		return db.collection(u'members').add(member_data)
    		#db.collection(u'members').document(u'member_00001').set(data)

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
    	return db.collection(u'conversations').add(conversation_data)

def checkDB():
	cred = credentials.Certificate(ast.literal_eval(os.environ["FIREBASE_CONFIG"]))
	'''
	firebase_admin_instance_exist = False
	if firebase_admin_instance_exist is False:
		firebase_admin.initialize_app(cred)
		firebase_admin_instance_exist = True
	'''
	#if firebase_admin.get_app() is None:
	#	firebase_admin.initialize_app(cred)
	#db = firestore.client()
	fb_id='16093421424752504'
	member = Members(fb_id).find_member()
	print(member.id)
	print ("Does App still exists {}".format(firebase_admin.get_app()))
	'''
	query_ref = db.collection(u'members').where(u'fb_id', u'==', fb_id)
	member_obj = None
	members = query_ref.get()
	for member in members:
		member_obj = db.collection(u'members').document(member.id)
		print ('Found Member')
	print(member_obj.id)
'''
	return 'Success'