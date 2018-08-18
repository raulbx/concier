import core_engine
import message_payloads
import response_payload
import copy
from firebase_admin import firestore
from datetime import datetime, timezone
from string import Template


class Exchange(object):

    def __init__(self, member_identifier, source_platform,core_engine_obj,user_response):
        self.user_id_on_platform = member_identifier
        self.source_platform = source_platform
        self.core_engine_obj=core_engine_obj
        self.user_response = user_response

    def get_action(self, conversation_ref,conversation_state):
        payloads = []
        try:
            conversation_duration_hours = abs(datetime.now(timezone.utc)-conversation_ref.get().to_dict().get('lastactivedate')).days * 24

            print("Member Identifier: {}\nconversation_ref: {} \nConversation_state: {} \nConversation Duration: {}".format(self.user_id_on_platform,conversation_ref.get().id, conversation_state,conversation_duration_hours))

            if conversation_duration_hours > 24:
                print('this conversation has been active for more than 24 hours')
                conversation_state = 'conversation_ended_request_review'

            payload = {} # Flush the payload
            payload = response_payload.fb_payload(conversation_state,'...',self.user_id_on_platform,conversation_ref.get().id,payload)    

            print("----------------------------Pay------------------------ \n{}\n----------------Load-----------------\n".format(payload))
            if 'platform' in payload:
                platform_action = payload['platform'].get('action')
                payload = getattr(self, platform_action)(payload,conversation_ref)
            if payload is None:
                payload =response_payload.fb_payload('default_state','...',self.user_id_on_platform,conversation_ref.get().id,payload)
            #print(payload)
            #print('-------Above is the raw payload -----')
            if isinstance(payload,(list,)):
                #this takes care of broadcast messages
                payloads = payload
            else:
                payloads.append(payload)
        except Exception as e:
            print('Exception Occured. {}'.format(str(e)))
            payload = response_payload.fb_payload('default_state','...',self.user_id_on_platform,'',payload)

        return payloads

    def start_conversation(self,core_engine_obj,user_details):
        payloads = []
        core_engine_obj.update_member_details(core_engine_obj.get_member(),user_details)
        payload = {}
        conversation_ref = core_engine_obj.add_conversation(core_engine_obj.get_member())
        payload = response_payload.fb_payload('welcome_user',user_details['first_name'],self.user_id_on_platform,conversation_ref.get().id,payload)
        payloads.append(payload)
        return payloads

    def remove_helper_ref_from_current_conversation(self, payload, conversation_ref):
        conversation_ref.update({'helper_ref':firestore.DELETE_FIELD})
        conversation_ref.update({'helper_state':firestore.DELETE_FIELD})
        return payload

    def remove_helpee_ref_from_current_conversation(self, payload, conversation_ref):
        conversation_ref.update({'helpee_ref':firestore.DELETE_FIELD})
        conversation_ref.update({'helpee_state':firestore.DELETE_FIELD})
        return payload

    def substitute_argument(self, payload, conversation_ref):
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        return payload

    def set_future_state(self,payload,conversation_ref):
        ####conversation_ref.update({'conversation_state':payload['platform'].get('future_state')})
        if payload['platform'].get('helper_next_state'):
            conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
        if payload['platform'].get('helpee_next_state'):
            conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})

        #payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        del payload['platform']
        return payload

    def record_value_set_future_state(self,payload,conversation_ref):
        #run validation first
        if payload['platform'].get('validate'):
            if payload['platform'].get('validate')=='input_length_more_than_20' and len(self.user_response)<20:
                payload = response_payload.fb_payload('validation_failure_response',payload['platform'].get('validation__failure_message'),self.user_id_on_platform,conversation_ref.get().id,payload)
        else:
            conversation_ref.update({payload['platform'].get('field'):self.user_response})

            #setting the states for helper and helpee
            if payload['platform'].get('helper_next_state'):
                conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
            if payload['platform'].get('helpee_next_state'):
                conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})

            conversation_ref.update({'lastactivedate':datetime.now()})
            payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        del payload['platform']
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
        ####conversation_ref.update({'active':True,'max_price':self.user_response,'helper_ref':None,'conversation_state':payload['platform'].get('future_state')})
        if payload['platform'].get('helper_next_state'):
            conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
        if payload['platform'].get('helpee_next_state'):
            conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})
        
        #print("Broadcasting message")
        #print (payload)
        product_category = conversation_ref.get().to_dict().get('product_category')
        #print(product_category)
        experts_list = self.core_engine_obj.get_experts(product_category)
        #print()
        #Need to refine this code
        #payloads.append(payload) #This creates the response payload for the person needing help
        #print(payloads)
        response_template = 'Buyer is interested in making a decision on below purchase.  Can you help? \nNeed: $arg1\nProduct Category: $arg2\nSpecific Product: $arg3\nPrice Range: $arg4\nTimeline: $arg5'
        response = Template(response_template).safe_substitute(arg1=conversation_ref.get().to_dict().get('user_need'),arg2=product_category,arg3=conversation_ref.get().to_dict().get('specific_product'),arg4=conversation_ref.get().to_dict().get('max_price'),arg5=conversation_ref.get().to_dict().get('time_frame'))
        print('\nPayload before assignement\n')
        for expert in experts_list:
            expertPayload = {}
            expertPayload = response_payload.fb_payload('broadcast_message',response,expert.get().to_dict().get('fb_id'),conversation_ref.get().id,expertPayload)
            #payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=product_category,arg2=conversation_ref.get().to_dict().get('max_price'),arg3=conversation_ref.get().to_dict().get('user_need'))
            payloads.append(expertPayload)
        del payload['platform']
        payloads.append(payload)
        print('Number of experts is {}'.format(len(experts_list)))

        #print(payloads)
        return payloads

    def assign_helper(self,payload,conversation_ref):
        #Assign this conversation to this expert.
        member_ref = self.core_engine_obj.get_member()
        self.core_engine_obj.append_conversation_ref(member_ref,conversation_ref)
        helpee_Name = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('first_name')
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=helpee_Name)
        #####conversation_ref.update({'helper_ref':member_ref,'conversation_state':payload['platform'].get('future_state')})
        if payload['platform'].get('helper_next_state'):
            conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
        if payload['platform'].get('helpee_next_state'):
            conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})
        del payload['platform']
        return payload

    def connect_expert_to_user(self,payload,conversation_ref):
        payloads = []
        ''' Get the correct conversation ref. 
        Send two messages. One to the expert and the other to the helpee
        '''
        member_ref = self.core_engine_obj.get_member()
        helpee_Name = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('first_name')
        helper_Name = member_ref.get().to_dict().get('first_name')
        #helpeePayload = response_payload.fb_payload('agree_to_help','...',conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id'),conversation_ref.get().id)

        print('Helper is {} and Helpee is {}'.format(helper_Name,helpee_Name))
        helpeePayload = copy.deepcopy(payload)

        #payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=helpee_Name)
        payload['message']['text'] = Template('Thanks. Next messages will be from $arg1').safe_substitute(arg1=helpee_Name)
        payloads.append(payload)
        
        helpeePayload['message']['text'] = helper_Name+' will help you with this product. Next message will be from '+helper_Name+'\n'+helper_Name+': '+self.user_response
        helpeePayload['recipient']['id'] = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')
        payloads.append(helpeePayload)
        print('Helpee message is {}'.format(helpeePayload['message']['text']))
        self.core_engine_obj.append_conversation_ref(member_ref,conversation_ref)
        
        #######conversation_ref.update({'helper_ref':member_ref,'conversation_state':payload['platform'].get('future_state')})
        if payload['platform'].get('helper_next_state'):
            conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
        if payload['platform'].get('helpee_next_state'):
            conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})
        
        return payloads

    def exchange_conversations(self,payload,conversation_ref):
        # set the recipient ID for the counter party
        helpee_id = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')
        helper_id = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('fb_id')
        
        #Deternine if this helper or helpee
        if self.user_id_on_platform == helper_id:
            recipient_id = helpee_id
            partyName = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('first_name')#This should be the first_name of the sender so it will be the counter party first_name
            #send message to helpee
        else:
            recipient_id = helper_id
            partyName = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('first_name') # this should be the first_name of the sender
            #send message to helper
        #response =partyName+': '+message['message'].get('text')
        print("Party first_name is {} and response is {}".format(partyName, self.user_response))
        if self.user_response and partyName:
            payload['message']['text'] = partyName+': '+self.user_response
        else:
            payload['message']['text'] = '...'
        payload['recipient']['id'] = recipient_id
        print(payload)

        return payload

    def request_review_from_both_parties(self,payload,conversation_ref):

        payloads = []
        helpee_id = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')
        helper_id = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('fb_id')

        payload['recipient']['id'] = helpee_id
        payloads.append(payload)
        helpeePayload = {}
        helpeePayload = copy.deepcopy(payload)
        helpeePayload['recipient']['id'] = helper_id
        payloads.append(helpeePayload)
        
        ####conversation_ref.update({'conversation_state':payload['platform'].get('future_state')})

        return payloads

    def record_review(self,payload,conversation_ref):
        helpee_id = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')
        helper_id = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('fb_id')
        review = ''
        #Deternine if this helper or helpee
        if self.user_id_on_platform == helper_id:
            # This is helper save the review for helper
            review = conversation_ref.get().to_dict().get('helper_review')
            review +=self.user_response
            conversation_ref.update({'helper_review':review})
            conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
        else:
            review = conversation_ref.get().to_dict().get('helpee_review')
            review +=self.user_response
            conversation_ref.update({'helpee_review':review})
            conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})

        ########conversation_ref.update({'conversation_state':payload['platform'].get('future_state')})
                
        return payload

    def start_new_conversation(self,payload,conversation_ref):
        new_conversation_ref = self.core_engine_obj.add_conversation(self.core_engine_obj.get_member())
        #do this to get the right conversation id in the conversation
        payload = {}
        payload = response_payload.fb_payload('conversation_closed','...',self.user_id_on_platform,new_conversation_ref.get().id,payload)
        return payload

    def add_expertise(self,payload,conversation_ref):
        self.core_engine_obj.add_expert(self.core_engine_obj.get_member(),self.user_response,payload['message'].get('text'))
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        del payload['platform']
        return payload

def message_active_conversation(conversation_refs):
    payloads = []
    for conversation_ref in conversation_refs:
        payload=response_payload.fb_payload('message_if_conversation_active','...',conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('fb_id'),conversation_ref.get().id)
        payloads.append(payload)
    return payloads