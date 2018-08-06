import core_engine
import message_payloads
import response_payload
import copy
from string import Template


class Exchange(object):

    def __init__(self, member_identifier, source_platform,core_engine_obj,user_response):
        self.user_id_on_platform = member_identifier
        self.source_platform = source_platform
        self.core_engine_obj=core_engine_obj
        self.user_response = user_response

    def get_action(self, conversation_ref,conversation_state):
        payloads = []
        print("Member Identifier is {} and conversation_ref is {} and conversation_state is {}".format(self.user_id_on_platform,conversation_ref.get().id, conversation_state))
        payload = response_payload.fb_payload(conversation_state,'...',self.user_id_on_platform,conversation_ref.get().id)
        print(payload)
        if 'platform' in payload:
            platform_action = payload['platform'].get('action')
            payload = getattr(self, platform_action)(payload,conversation_ref)
        if payload is None:
            payload =response_payload.fb_payload('default_state','...',self.user_id_on_platform,conversation_ref.get().id)
        #print(payload)
        #print('-------Above is the raw payload -----')
        if isinstance(payload,(list,)):
            #this takes care of broadcast messages
            payloads = payload
        else:
            payloads.append(payload)
        print(payloads)
        return payloads

    def start_conversation(self,member_ref):
        payloads = []
        conversation_ref = member_ref.add_conversation(member_ref.get_member())
        payload = response_payload.fb_payload('welcome_user','',self.user_id_on_platform,conversation_ref.get().id)
        payloads.append(payload)
        return payloads

    def substitute_argument(self, payload, conversation_ref):
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        return payload

    def set_future_state(self,payload,conversation_ref):
        conversation_ref.update({'conversation_state':payload['platform'].get('future_state')})
        #payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        del payload['platform']
        return payload

    def record_category_set_future_state(self,payload,conversation_ref):
        conversation_ref.update({'product_category':self.user_response})
        conversation_ref.update({'conversation_state':payload['platform'].get('future_state')})
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        del payload['platform']
       # payload = set_future_state(self,payload,conversation_ref)
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
        payloads = []
        conversation_ref.update({'active':True,'max_price':self.user_response,'helper_ref':None,'conversation_state':payload['platform'].get('future_state')})
        print("Broadcasting message")
        #del payload['platform']
        product_category = conversation_ref.get().to_dict().get('product_category')
        print(product_category)
        experts_list = self.core_engine_obj.get_experts(product_category)
        #print()
        #Need to refine this code
        payloads.append(payload) #This creates the response payload for the person needing help
        response_template = 'We have a member, who is looking for an $arg1 item within price $arg2. Members question is : --$arg3--. Do you want to help?'
        response = Template(response_template).safe_substitute(arg1=product_category,arg2=conversation_ref.get().to_dict().get('max_price'),arg3=conversation_ref.get().to_dict().get('user_need'))
        for expert in experts_list:
            #expert_id=expert_member.get().to_dict().get('fb_id')
            payload = response_payload.fb_payload('broadcast_message',response,expert.get().to_dict().get('fb_id'),conversation_ref.get().id)
            #payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=product_category,arg2=conversation_ref.get().to_dict().get('max_price'),arg3=conversation_ref.get().to_dict().get('user_need'))
            payloads.append(payload)
        print('Number of experts is {}'.format(len(experts_list)))
        return payloads

    def connect_expert_to_user(self,payload,conversation_ref):
        payloads = []
        ''' Get the correct conversation ref. 
        Send two messages. One to the expert and the other to the helpee
        '''
        #TODO: Add the conversation reference in Experts Profile.
        member_ref = self.core_engine_obj.get_member()
        helpee_Name = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('Name')
        helper_Name = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('Name')
        #helpeePayload = response_payload.fb_payload('agree_to_help','...',conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id'),conversation_ref.get().id)

        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=helpee_Name)
        payloads.append(payload)

        helpeePayload = copy.deepcopy(payload)
        helpeePayload['message']['text'] = Template(helpeePayload['message'].get('text')).safe_substitute(arg1=helper_Name)
        helpeePayload['recipient']['id'] = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')
        payloads.append(helpeePayload)

        self.core_engine_obj.append_conversation_ref(member_ref,conversation_ref)
        conversation_ref.update({'helper_ref':member_ref,'conversation_state':payload['platform'].get('future_state')})
        
        return payloads

    def exchange_conversations(self,payload,conversation_ref):
        # set the recipient ID for the counter party
        helpee_id = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')
        helper_id = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('fb_id')
        
        #Deternine if this helper or helpee
        if self.user_id_on_platform == helper_id:
            recipient_id = helpee_id
            partyName = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('Name')#This should be the name of the sender so it will be the counter party name
            #send message to helpee
        else:
            recipient_id = helper_id
            partyName = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('Name') # this should be the name of the sender
            #send message to helper
        #response =partyName+': '+message['message'].get('text')
        print("Party Name is {} and response is {}".format(partyName, self.user_response))
        if self.user_response and partyName:
            payload['message']['text'] = partyName+': '+self.user_response
        else:
            payload['message']['text'] = '...'
        payload['recipient']['id'] = recipient_id
        print(payload)
        return payload

    def add_expertise(self,payload,conversation_ref):
        self.core_engine_obj.add_expert(self.core_engine_obj.get_member(),self.user_response,payload['message'].get('text'))
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        return payload