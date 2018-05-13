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

def checkDB():
	#cred = credentials.Certificate(ast.literal_eval(os.environ["FIREBASE_CONFIG"]))
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