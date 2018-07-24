import core_engine
import message_payloads
import response_payload
from string import Template


class Exchange(object):

    def __init__(self, member_identifier, source_platform,core_engine_obj,user_response):
        self.user_id_on_platform = member_identifier
        self.source_platform = source_platform
        self.core_engine_obj=core_engine_obj
        self.user_response = user_response

    def get_action(self, conversation_ref,conversation_state):
        print("Member Identifier is {} and conversation_ref is {} and conversation_state is {}".format(self.user_id_on_platform,conversation_ref.get().id, conversation_state))
        payload =response_payload.fb_payload(conversation_state,'...',self.user_id_on_platform,conversation_ref.get().id)
        if 'platform' in payload:
            platform_action = payload['platform'].get('action')
            payload = getattr(self, platform_action)(payload,conversation_ref)
            del payload['platform']
        if payload is None:
            payload =response_payload.fb_payload('default_state','...',self.user_id_on_platform,conversation_ref.get().id)
        print(payload)
        print('-------Above is the raw payload -----')
        return payload
        '''
        flow_state_ref = self.core_engine_obj.get_conv_flow_state(flow_state)
        response_payload = flow_state_ref.get().to_dict().get('response_payload')
        platformResponse = flow_state_ref.get().to_dict().get('response')
        platformAction = flow_state_ref.get().to_dict().get('platform_action')
        if platformAction:
            platformResponse = getattr(self, platformAction)(platformResponse,conversation_ref)
        print("Contnuing a conversation. Flow state is {}".format(flow_state))

        if flow_state_ref.get().to_dict().get('recipient')== 'sender':
            recipient = self.user_id_on_platform
        else:
            recipient = None
        return message_payloads.fb_payload(response_payload,platformResponse,recipient,conversation_ref.get().id)
        '''

    def start_conversation(self,member_ref):
        conversation_ref = member_ref.add_conversation(member_ref.get_member())
        return response_payload.fb_payload('welcome_user','',self.user_id_on_platform,conversation_ref.get().id)

        '''
        conversation_ref = member_ref.add_conversation(member_ref.get_member())
        flow_state_ref = self.core_engine_obj.get_conv_flow_state("start_here")
        response_payload = flow_state_ref.get().to_dict().get('response_payload')
        platformResponse = flow_state_ref.get().to_dict().get('response')
        recipient = None
        print("Starting new conversation")
        if flow_state_ref.get().to_dict().get('recipient')== 'sender':recipient = self.user_id_on_platform 
        return message_payloads.fb_payload(response_payload,platformResponse,recipient,conversation_ref.get().id)
        '''

    def substitute_argument(self, payload, conversation_ref):
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        return payload

    def set_future_state(self,payload,conversation_ref):
        conversation_ref.update({'conversation_state':payload['platform'].get('future_state')})
        #payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        return payload

    def record_category_set_future_state(self,payload,conversation_ref):
        conversation_ref.update({'product_category':self.user_response})
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        payload = set_future_state(self,payload,conversation_ref)
        return payload

    def record_need(self,payload,conversation_ref):
        conversation_ref.update({'user_need':self.user_response})
        print("Saving users need-question")
        return payload

    def record_time_frame(self,payload,conversation_ref):
        conversation_ref.update({'time_frame':self.user_response})
        print("Setting time frame")
        return payload

    def record_price_and_broadcast_request(self,payload,conversation_ref):
        conversation_ref.update({'active':True,'max_price':self.user_response,'is_helpee':True, 'helper_ref':None,'conversation_state':payload['platform'].get('future_state')})
        print("Broadcasting message")
        print(self.core_engine_obj.get_experts(conversation_ref.get().to_dict().get('product_category')))
        return payload

    def add_expertise(self,payload,conversation_ref):
        self.core_engine_obj.add_expert(self.core_engine_obj.get_member(),self.user_response,payload['message'].get('text'))
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        return payload