import psycopg2
import sys, traceback
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
		#'expertise':['electronics','health'], # This is now stored in a different collection
		'signupdate':datetime.datetime.now(),
		'lastactivedate':datetime.datetime.now()
		}
		print("Added Member")
		db = firestore.client()
		return db.collection(u'members').add(member_data)
	
	def add_conversation(self,member_ref):
		conversation_data = {
    	'helpee_ref':member_ref, # this is reference to the member obj
    	#'helpee_id':helpee_id,
    	'active':False,
    	'conversation_state':'identify_timeframe',
    	'current_chat_seq':0,
    	'startdate':datetime.datetime.now(),
    	'lastactivedate':datetime.datetime.now()
    	}
		db = firestore.client()
		conversation_ref=db.collection(u'conversations').add(conversation_data)[1]
		member_ref.update({'conversations':[conversation_ref]})
		return conversation_ref

	def get_active_conversation(self,member):
		# Get the latest conversation. If no convers
		conversations_array = member.get().get('conversations')
		#active_conv = len(conversations_array)
		if len(conversations_array) > 0:
			# TODO: Need to fix this to get the right conversation
			conversation_ref = conversations_array[-1]
			conversation = conversation_ref.get()
		else:
			conversation = None
		return conversation

	def get_active_conversation_ref(self,member):
		# Get the latest conversation. If no convers
		conversations_array = member.get().get('conversations')
		#active_conv = len(conversations_array)
		if len(conversations_array) > 0:
			# TODO: Need to fix this to get the right conversation
			conversation_ref = conversations_array[-1]
			print(conversation_ref.get().id)
			#conversation = conversation_ref.get()
		else:
			conversation_ref = None
		# THERE IS SOME BUG IN PYTHON. This print statement doesn't return values from the call
		print("This is the call to conversation".format(conversation_ref.get()))
		return conversation_ref

	def get_active_conversation_ref_byID(self,conversation_id):
		db = firestore.client()
		conversation_ref = db.collection("conversations").document(conversation_id)
		return conversation_ref

	def log_message(self,member,conversation_ref,message):
		#conversations_array = member.get().get('conversations')
		#conversation_ref = conversations_array[-1]
		conversation = conversation_ref.get()
		chat_seq=conversation.to_dict()['current_chat_seq']+1
		chat_log = {
		'sender':member,
		'message':message,
		'chat_seq':chat_seq,
		'timestamp':datetime.datetime.now()
		}
		conversation_ref.update({u'current_chat_seq': chat_seq})
		conversation_ref.collection(u'chats').add(chat_log)
		return

	def get_experts(self,expertise):
		db = firestore.client()
		return db.collection("expertise").where("expertise_category", "==", expertise)

	def add_expert(self,member,member_expertise):
		expertise_data = {
		'expertise_category':member_expertise,
		'member':[member]
		}
		expertise_ref = None
		db = firestore.client()
		expertise_query_ref=db.collection("expertise").where("expertise_category", "==", member_expertise).get()
		try:
			for expertise in expertise_query_ref:
				expertise_ref = db.collection(u'expertise').document(expertise.id)
			if expertise_ref is None:
				print("Expertise doesn't exist. Adding Member")
				expertise_ref = db.collection(u'expertise').add(expertise_data)
			else :
				print("Expertise exists. Adding Member to existing expertise")
				member_array = expertise_ref.get().to_dict().get('member')
				member_array.append(member)
				expertise_ref.update({'member':member_array}, firestore.CreateIfMissingOption(True))
		except ValueError:
			print(u'Value Error.....!')
		except:
			print(u'This is an exception situation')
			traceback.print_stack()
		return expertise_ref