import core_engine

payload = {}

class Exchange(object):

	def __init__(self, member_identifier, source_platform,member_core_engine_ref):
		self.user_id_on_platform = member_identifier
		self.source_platform = source_platform
		self.member_core_engine_ref=member_core_engine_ref

	def get_action(self, conversation_ref,flow_state):
		print("Member Identifier is {} and conversation_ref is {}".format(self.user_id_on_platform,conversation_ref.get().id))
		flow_state_ref = self.member_core_engine_ref.get_conv_flow_state(flow_state)
		response_type = flow_state_ref.get().to_dict().get('response_type')
		response = flow_state_ref.get().to_dict().get('response')
		recipient = None
		print("Starting new conversation")
		if flow_state_ref.get().to_dict().get('recipient')== 'sender':
			recipient = self.user_id_on_platform 
		return form_payload(response_type,response,recipient,conversation_ref.get().id)

	def start_conversation(self,member_ref):
		conversation_ref = member_ref.add_conversation(member_ref.get_member())
		flow_state_ref = self.member_core_engine_ref.get_conv_flow_state("start_here")
		response_type = flow_state_ref.get().to_dict().get('response_type')
		response = flow_state_ref.get().to_dict().get('response')
		recipient = None
		print("Starting new conversation")
		if flow_state_ref.get().to_dict().get('recipient')== 'sender':
			recipient = self.user_id_on_platform 
		return form_payload(response_type,response,recipient,conversation_ref.get().id)

def form_payload(response_type,response,recipient_id,conversation_id):
	payload['recipient'] = {
	'id': recipient_id
	}
	if response_type =='plain_message':
		payload['notification_type'] = 'REGULAR'
		payload['message'] = {
		'text' : response
		}
	elif response_type =='welcome_user':
		payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":response,
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Get shopping advice?",
                    "payload":"seekingAdvice:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Other?",
                    "payload":"other:"+conversation_id
                    }
                    ]
                }
            }
        }

	return payload