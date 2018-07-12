import core_engine

payload = {}

class Exchange(object):

	def __init__(self, member_identifier, source):
		self.member_identifier = member_identifier
		self.source = source

	def get_action(self, conversation_ref):
		print("Member Identifier is {} and conversation_ref is {}".format(self.member_identifier,conversation_ref.get().id))
		sender_msg = "This is new"
		return form_payload('plain_message',sender_msg,self.member_identifier,"conversation_id")

	def start_conversation(self):
		print("Starting Conversation")

def form_payload(response_type,text_message,recipient_id,conversation_id):
	payload['recipient'] = {
	'id': recipient_id
	}
	if response_type =='plain_message':
		payload['notification_type'] = 'REGULAR'
		payload['message'] = {
		'text' : text_message
		}
	elif response_type =='welcome_buttons':
		payload['message'] = {
		}

	return payload