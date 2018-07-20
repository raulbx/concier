import core_engine
import message_payloads



class Exchange(object):

	def __init__(self, member_identifier, source_platform,core_engine_obj,user_response):
		self.user_id_on_platform = member_identifier
		self.source_platform = source_platform
		self.core_engine_obj=core_engine_obj
		self.user_response = user_response

	def get_action(self, conversation_ref,flow_state):
		print("Member Identifier is {} and conversation_ref is {} and flow_state is {}".format(self.user_id_on_platform,conversation_ref.get().id, flow_state))
		flow_state_ref = self.core_engine_obj.get_conv_flow_state(flow_state)
		response_payload = flow_state_ref.get().to_dict().get('response_payload')
		platformResponse = flow_state_ref.get().to_dict().get('response')
		platformAction = flow_state_ref.get().to_dict().get('platformAction')
		if platformAction:
			platformResponse = getattr(self, platformAction)(platformResponse)
		print("Contnuing a conversation. Flow state is {}".format(flow_state))

		if flow_state_ref.get().to_dict().get('recipient')== 'sender':
			recipient = self.user_id_on_platform
		else:
			recipient = None
		return message_payloads.fb_payload(response_payload,platformResponse,recipient,conversation_ref.get().id)

	def start_conversation(self,member_ref):
		conversation_ref = member_ref.add_conversation(member_ref.get_member())
		flow_state_ref = self.core_engine_obj.get_conv_flow_state("start_here")
		response_payload = flow_state_ref.get().to_dict().get('response_payload')
		platformResponse = flow_state_ref.get().to_dict().get('response')
		recipient = None
		print("Starting new conversation")
		if flow_state_ref.get().to_dict().get('recipient')== 'sender':recipient = self.user_id_on_platform 
		return message_payloads.fb_payload(response_payload,platformResponse,recipient,conversation_ref.get().id)

	def add_expertise(self,platform_response):
		return self.core_engine_obj.add_expert(self.core_engine_obj.get_member(),self.user_response,platform_response)

	def set_product_category(self,platform_response):
		print("Setting product category")

	def set_time_frame(self,platform_response):
		print("Setting time frame")

	def set_max_price(self,platform_response):
		print ("Setting product price")

	def broadcast_help_needed_request(self,platform_response):
		print("Broadcasting message")
		self.core_engine_obj.get_experts(conversation.to_dict().get('product_category'))


