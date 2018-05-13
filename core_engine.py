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

	def find_member(self):
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

def checkDB():
	#cred = credentials.Certificate(ast.literal_eval(os.environ["FIREBASE_CONFIG"]))
	fb_id='16093421424752504'
	db = firestore.client()
	member = Members(fb_id).find_member()
	return 'Success'