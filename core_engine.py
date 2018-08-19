import psycopg2
import sys, traceback
import os
import firebase_admin
import datetime
import ast
from string import Template
from firebase_admin import credentials
from firebase_admin import firestore
import google.cloud.exceptions

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
		'is_helpee':False,
		'reward_balance':0,
		'conversations':[], # Good idea is to store references in this array
		#'expertise':['electronics','health'], # This is now stored in a different collection
		'signupdate':datetime.datetime.now(),
		'lastactivedate':datetime.datetime.now()
		}
		print("Added Member")
		db = firestore.client()
		return db.collection(u'members').add(member_data)

	def update_member_details(self,member_ref,user_details):
		member_ref.update({'first_name':user_details['first_name'],'last_name':user_details['last_name']})
		return True
	
	def add_conversation(self,member_ref):
		conversation_data = {
    	'helpee_ref':member_ref, # this is reference to the member obj
    	'helper_ref':member_ref,
    	#'helpee_id':helpee_id,
    	'active':False,
    	'helper_state':'welcome_user',
    	'helpee_state':'welcome_user',
    	'current_chat_seq':0,
    	'startdate':datetime.datetime.now(),
    	'lastactivedate':datetime.datetime.now()
    	}
		db = firestore.client()
		conversation_ref=db.collection(u'conversations').add(conversation_data)[1]
		self.append_conversation_ref(member_ref,conversation_ref)
		#member_ref.update({'conversations':[conversation_ref]})
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

	def get_active_conversation_ref(self,member_ref):
		# Get the latest conversation. If no convers
		conversations_array = member_ref.get().get('conversations')
		#active_conv = len(conversations_array)
		if len(conversations_array) > 0:
			# TODO: Need to fix this to get the right conversation
			conversation_ref = conversations_array[-1]
			#print(conversation_ref.get().id)
			print('Conversation ID is above: ')
			#conversation = conversation_ref.get()
		else:
			conversation_ref = None
		# THERE IS SOME BUG IN PYTHON. This print statement doesn't return values from the call 
		print ('We are  getting conversation ref associated with this user----Donot remove. Added because of python bug.')
		return conversation_ref

	def get_active_conversation_ref_byID(self,conversation_id):
		db = firestore.client()
		conversation_ref = db.collection("conversations").document(conversation_id)
		return conversation_ref

	def append_conversation_ref(self,member_ref,conversation_ref):
		conversations_array = member_ref.get().get('conversations')
		if conversation_ref in conversations_array:
			#Don't do anything.Member is already added to the conversation
			print('Member already added to the conversation')
		else:
			conversations_array.append(conversation_ref)
			member_ref.update({'conversations':conversations_array,'lastactivedate':datetime.datetime.now()}, firestore.CreateIfMissingOption(True))
			print('Assigned expert to the conversation')
		return True

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

	def get_conv_flow_state(self,flow_state):
		db = firestore.client()
		flow_state_ref = db.collection("conversation_flow_states").document(flow_state)
		return flow_state_ref

	def get_experts(self,expertise):
		db = firestore.client()
		#return db.collection("expertise").where("expertise_category", "==", expertise)
		expertise_ref = db.collection("expertise").document(expertise)
		print('Getting the expertise ref: '.format(expertise_ref))
		if expertise_ref:
			expert_list = expertise_ref.get().to_dict().get('member')
			print('Experts found')
		else:
			expert_list = []
			print('No Experts found')
		return expert_list

	def add_expert(self,member_ref,member_expertise,platform_response):
		expertise_data = {
		'member':[member_ref]
		}
		expertise_ref = None
		db = firestore.client()
		#expertise_query_ref=db.collection("expertise").where("expertise_category", "==", member_expertise).get()
		expertise_ref=db.collection("expertise").document(member_expertise)
		try:
			expertise_obj = expertise_ref.get() #This will throw error if the expertise doesn't exist.
			member_array = expertise_obj.to_dict().get('member')
			if member_ref in member_array:
				#Member is already registered as an expert for expertise
				platform_response = "You are already registered as an expert for {}".format(member_expertise)
			else: 
				member_array.append(member_ref)
				expertise_ref.update({'member':member_array}, firestore.CreateIfMissingOption(True))	
				
		except google.cloud.exceptions.NotFound:
			#Don't hate me. Apparently this is the EAFP way in Python - https://docs.python.org/3.6/glossary.html#term-eafp 
			expertise_ref = db.collection(u'expertise').document(member_expertise).set(expertise_data)
		member_ref.update({'is_helper':True})
		platform_response = Template(platform_response).safe_substitute(arg1=member_expertise)
		return platform_response

class Platform(object):
	#cred = credentials.Certificate(ast.literal_eval(os.environ["FIREBASE_CONFIG"]))
	#firebase_admin.initialize_app(cred)

	def __init__(self):
		print('Initializing Platform')

	def get_all_active_conversations(self):
		db = firestore.client()
		query_refs = db.collection("conversations").where(u'active', u'==', True).get()
		conversation_refs = []
		try:
			for conversation_snapshot in query_refs:
				#print (conversation_snapshot.id)
				#print (conversation_snapshot.reference)
				conversation_refs.append(conversation_snapshot.reference)
		except ValueError:
			print(u'Value Error.....!')
		except Exception as e:
			print(str(e))
		return conversation_refs
