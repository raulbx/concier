import firebase_admin
import datetime
from firebase_admin import credentials
from firebase_admin import firestore

class Members(object):
    def __init__(self, facebok_id, source='Blank'):
        self.fb_id = facebok_id
        self.source = source

    def find_member(self):
    	query_ref = db.collection(u'members').where(u'fb_id', u'==', self.fb_id)
    	member_obj = None
    	try:
    		members = query_ref.get()
    		for member in members:
    			member_obj = db.collection(u'members').document(member.id)
    			print ('Found Member')
    	except ValueError:
    		print(u'No such document.....!')
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
    	# Store Messages in conversation document
    	#print(" Added Conversation")
    	#Make an entry to both helpee and helper object

'''
    def __repr__(self):
        return u'City(name={}, country={}, population={}, capital={})'.format(
            self.name, self.country, self.population, self.capital)
'''

if __name__ == '__main__':
	cred = credentials.Certificate('Concier-dcb1fb05556d.json')
	firebase_admin.initialize_app(cred)
	db = firestore.client()
	fb_id='16093421424752504'
	#fb_id='16093421424752505'
	conv_id ='8BJiobazntD2bzbxPzG5'
	# Below is the helper
	#fb_id='16093421424752503' 
	message = 'This is a boiler plate Chat Message'
	#helpeeMsg = 'Thank you Ray for helping me out'
	member = Members(fb_id).find_member()
	if not member:
		# Add member
		member = Members(fb_id,'FB').add_member()[1]
		#This return type has three things. 
		#member = member_obj[1]
		#Since this is a new customer. Start a conversation with the member.
		new_conversation_ref = Members(fb_id).add_conversation(member)
		member.update({'conversations':[new_conversation_ref[1]]})
		# Return and send them message
	print(member.id)
	# Check what state they are in
	conversations_array = member.get().get('conversations') # This fetches the conversation array. For now, there should be only one conversation active.
	if len(conversations_array) > 0:
		# Look for the conversation. No need to query the DB, array has document reference and we can directly get the conversation with it. 
		#conversation_obj = db.collection(u'conversations').document(conversations_array[-1].id)
		# TODO: Need to fix below to get the right conversation
		conversation_ref = conversations_array[-1]
		# TODO: Need to fix above to get the right conversation
		conversation = conversation_ref.get()
		#We are logging the chat
		chat_seq=conversation.to_dict()['current_chat_seq']+1
		chat_log = {
		'sender':member,
		'message':message,
		'chat_seq':chat_seq,
		'timestamp':datetime.datetime.now()
		}
		conversation_ref.update({u'current_chat_seq': chat_seq})
		conversation_ref.collection(u'chats').add(chat_log)
		current_conv_state = conversation.to_dict()['conversation_state']
		#print("Found helpee {} helping out in conversation Id {}".format(conversation.to_dict()['helpee_ref'].get().id,conversations_array[-1].get().id))
		if current_conv_state < 2:
			#Member is interacting with the platform. Send the message and increment the state
			# Get the message associated with this state
			state_ref = db.collection(u'conversations').document('conversation_states')
			#try:
			print(u'Document data: {} and conv state is {}'.format(state_ref.get().to_dict().get(str(current_conv_state),''),current_conv_state))
			current_conv_state = current_conv_state+1
			conversation_ref.update({u'conversation_state': current_conv_state})
		elif current_conv_state == 2:
			#Broadcast the question to the expert community. Assign a expert, who says YES.
			print("YO")
			
		else:
			print("-------Member and expert are interacting-------")
			#Get the helper id and helpee id.
			helpee_fb_id = conversation.to_dict()['helpee_ref'].get().to_dict().get('fb_id')
			helper_fb_id = conversation.to_dict()['helper_ref'].get().to_dict().get('fb_id')
			sender_fb_id = member.get().to_dict().get('fb_id')
			print(' Helpee ID {}\n Helper ID {}\n Sender ID {}'.format(helpee_fb_id,helper_fb_id,sender_fb_id))
			#send the message to the other party.
			#Find out, who this person is this and then send the message to counter party
			if conversation.to_dict()['helper_ref'] == member:
				print ('Sender {} is the helper, send the message to helpee {}'.format(sender_fb_id,helpee_fb_id))
			elif conversation.to_dict()['helpee_ref'] == member:
				print ('Sender {} is the helpee, send the message to helper {}'.format(sender_fb_id,helper_fb_id))
			# TODO: Route messages that go to the platform

		print("State of the customer is {}".format(conversation.to_dict()['conversation_state']))
	else:
		print("No conversations. That means an expert is replying for the first time to a message")
		#Add member as helper to the conversation
		conv_ref = db.collection(u'conversations').document(conv_id)
		conv_ref.update({'helper_ref':member})
		member.update({'conversations':[conv_ref]})
		print (conv_ref.get().to_dict().get('helper_ref'))
		#conv_ref = Members(fb_id).add_conversation(member)
		# Above call returns a tuple with document reference at [1]. Access the document reference id by calling conv_id[1].id 
		#Add entry of the conversation in member object
		#member.update({'conversations':['',conv_ref[1]]})

	'''Order of things
	1) Query the member
	2) If member doesn't exist create the entry for the member
	3) Ask member what he needs help on
	4) Identify what field is this question in
	5) Find a helper, who can help the member with the question
	6) Match the helper with the member and start the conversation
	7) Orchastrate the conversation between member and helper
	'''

	#print(conversation_id)
	# Add a conversation if it doesn't exist.

	#conversation_obj = db.collection(u'conversations').document(conversation_id)
	#print(u'Document data: {}'.format(conversation_obj.get().get('active')))

	# Added Conversation
	#Members(fb_id).add_conversation(member.id,'8sTFa4P8eVFTZSQyeq2t')

	# get conversation
	#Get the conversation. Check if it is active.
	#Get the partner Profile id
	#If the partner member id is blank. Look for a partner
	#send the message to partner

		
	'''
	# query_ref = db.collection(u'members').where(u'fb_id', u'==', fb_id)
	#counter_obj = db.document(u'counters/member').get()
	#print (counter_obj.to_dict()['current_id'])
	#member_exists = False
	try:
		#print(doc_ref)
		#docs = coll_ref.get()
		members = query_ref.get()
	#	members.update({u'is_helper': True})
		for member in members:
			member_exists = member.exists
			#print(u'Document data: {}'.format(member.to_dict()))
			member_obj = db.collection(u'members').document(member.id)
			#member_obj.collection(u'conversations').add(conversation_data)
			print (member.get('expertise'))
			#print(u'Document data: {}'.format(member_obj))
			#if member_exists:
				#Check if there is an active conversation
			#	query_ref = db.collection(u'conversations').where(u'fb_id', u'==', fb_id)
			#member_obj.update({u'is_helper': True, 'token_balance':10})
	except ValueError:
		print(u'No such document.....!')
	except:
		print(u'No such document!')
'''
	'''	
	doc_ref = db.collection(u'users').document(u'alovelace')
	doc_ref.set({
		u'first': u'Ada',
		u'last': u'Lovelace',
		u'born': 1815
	})
	doc_ref = db.collection(u'users').document(u'aturing')
	doc_ref.set({
		u'first': u'Alan',
		u'middle': u'Mathison',
		u'last': u'Turing',
		u'born': 1912
	})
	users_ref = db.collection(u'users')
	docs = users_ref.get()
	for doc in docs:
		print(u'{} => {}'.format(doc.id, doc.to_dict()))
'''