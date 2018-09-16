import core_engine
import message_payloads
import response_payload
import traceback

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
        payload = {}

        try:
            conversation_duration_hours = abs(datetime.now(timezone.utc)-conversation_ref.get().to_dict().get('lastactivedate')).days * 24

            print("Member Identifier: {}\nconversation_ref: {} \nConversation_state: {} \nConversation Duration: {}".format(self.user_id_on_platform,conversation_ref.get().id, conversation_state,conversation_duration_hours))

            if conversation_duration_hours > 24:
                print('this conversation has been active for more than 24 hours')
                conversation_state = 'conversation_ended_request_review'

            # Flush the payload
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
        except Exception as err:
            print('Exception Occured. {}'.format(str(err)))
            traceback.print_tb(err.__traceback__)
            payload = response_payload.fb_payload('default_state','Houston, we have a problem.',self.user_id_on_platform,'',payload)
            payloads.append(payload)
        return payloads

    def start_conversation(self,core_engine_obj):
        
        #core_engine_obj.update_member_details(core_engine_obj.get_member(),user_details)
        payload = {}
        conversation_ref = core_engine_obj.add_conversation(core_engine_obj.get_member())
        first_name = self.core_engine_obj.get_member().get().to_dict().get('first_name')
        print('First Name from DB is {}'.format(first_name))
        payload = response_payload.fb_payload('welcome_user','...',self.user_id_on_platform,conversation_ref.get().id,payload)
        payload['message']['attachment']['payload']['text'] = Template(payload['message']['attachment']['payload'].get('text')).safe_substitute(arg1=first_name)
        print(payload)
        return payload

    def append_member_name(self, payload, conversation_ref):
        first_name = self.core_engine_obj.get_member().get().to_dict().get('first_name')
        payload['message']['attachment']['payload']['text'] = Template(payload['message']['attachment']['payload'].get('text')).safe_substitute(arg1=first_name)

        return payload

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
        
        if payload['platform'].get('helper_next_state'):
            conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
        if payload['platform'].get('helpee_next_state'):
            conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})

        #payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        del payload['platform']
        return payload

    def record_value_set_future_state(self,payload,conversation_ref):
        #run validation first
        validation_passed = True
        if payload['platform'].get('validate'):
            if payload['platform'].get('validate')=='input_length_more_than_20' and len(self.user_response)<20:
                payload = response_payload.fb_payload('validation_failure_response',payload['platform'].get('validation__failure_message'),self.user_id_on_platform,conversation_ref.get().id,payload)
                validation_passed=False

        if validation_passed:
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

    def get_specific_products(self,payload,conversation_ref):
        product_list=self.core_engine_obj.get_specific_products(self.user_response)
        print(product_list)
        #payload['message']['quick_replies']
        if len(product_list)>0:
            payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
            payload['message']['quick_replies']=[]
            for product in product_list:
                option ={
                "content_type":"text",
                "title":product,
                "payload":payload['platform']['current_conversation_state']+':'+conversation_ref.get().id
                }
                payload['message']['quick_replies'].append(option)
        else:
            if payload['platform'].get('helper_next_state'):
                next_state = 'helper_next_state'
                self.add_expertise(payload,conversation_ref)
            elif payload['platform'].get('helpee_next_state'):
                next_state = 'helpee_next_state'
            payload = response_payload.fb_payload(payload['platform'][next_state],'...',self.user_id_on_platform,conversation_ref.get().id,payload)
            payload = self.record_value_set_future_state(payload, conversation_ref)
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
        payloads.append(payload)

        

        '''
        if payload['platform'].get('helper_next_state'):
            conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
        if payload['platform'].get('helpee_next_state'):
            conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})
        '''

        specific_product = conversation_ref.get().to_dict().get('specific_product')
        experts_list = self.core_engine_obj.get_experts(specific_product)
       
        response_template = 'A community member wants to talk to you about a product you purchased. Can you help? \nProduct: $arg1\nNeed: $arg2\nPrice Range: $arg3\nTimeline: $arg4'
        response = Template(response_template).safe_substitute(arg1=specific_product,arg2=conversation_ref.get().to_dict().get('user_need'),arg3=conversation_ref.get().to_dict().get('max_price'),arg4=conversation_ref.get().to_dict().get('time_frame'))
        print('\nPayload before assignement\n')
        helpee_state =''
        if len(experts_list)>0:
            for expert in experts_list:
                if expert.get().id != self.user_id_on_platform:
                    expertPayload = {}
                    expertPayload = response_payload.fb_payload('broadcast_message',response,expert.get().to_dict().get('fb_id'),conversation_ref.get().id,expertPayload)
                    helpee_state = payload['platform'].get('helpee_next_state')
                    #payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=product_category,arg2=conversation_ref.get().to_dict().get('max_price'),arg3=conversation_ref.get().to_dict().get('user_need'))
                    payloads.append(expertPayload)
        else:
            # we didn't find any expert. Let the helpee know that we don't have a expert. We will be in touch once we find one.
            payload['message']['text'] = 'We don\'t have a member, who knows about {}. We regularly on board new members. We will get in touch once we have a member, who knows about {}'.format(specific_product,specific_product)
            helpee_state='conversation_closed'
        conversation_ref.update({'active':True,'max_price':self.user_response,'helper_ref':None,'helpee_state':helpee_state})

        del payload['platform']
        
        print('Number of experts is {}'.format(len(experts_list)))

        #print(payloads)
        return payloads

    def decline_to_help(self,payload,conversation_ref):
        payloads = []
        payloads.append(payload)
        new_conversation_payload = self.start_new_conversation(payload,conversation_ref)
        payloads.append(new_conversation_payload)
        
        return payloads

    def assign_helper(self,payload,conversation_ref):
        #Assign this conversation to this expert.
        member_ref = self.core_engine_obj.get_member()
        self.core_engine_obj.append_conversation_ref(member_ref,conversation_ref)
        conversation_ref.update({'helper_ref':member_ref})
        product_Name = conversation_ref.get().to_dict().get('specific_product')
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=product_Name)
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
        conversation_ref.update({'expert_why_product_bought':self.user_response})
        member_ref = self.core_engine_obj.get_member()
        helpee_Name = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('first_name')
        helper_Name = member_ref.get().to_dict().get('first_name')

        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=helpee_Name)
        payloads.append(payload)

        product_bought = conversation_ref.get().to_dict().get('expert_what_product_bought')
        products_in_the_market = conversation_ref.get().to_dict().get('expert_key_products_in_the_market')
        product_price_ranges = conversation_ref.get().to_dict().get('expert_product_price_ranges')
        product_differences = conversation_ref.get().to_dict().get('expert_product_differences')
        why_bought_product = conversation_ref.get().to_dict().get('expert_why_product_bought')

        helpeePayload= {}
        helpeeResponse = '{} made a similar purchase recently. Below is some information about {}\'s purchase.\n\nProduct bought: {}\nProduct looked at:{}\nPrice range:{}\nDifference in product:{}\nWhy member bought {}:{}\n\nCommunity member will have 12 hours to interact with you before you are released back to the community. At any time, if you want to end the conversation, type #end and enter.\nWe will now connect you to {}. Please say hi!'.format(helper_Name,helper_Name,product_bought,products_in_the_market,product_price_ranges,product_differences,product_bought,why_bought_product,helper_Name)
        helpeePayload = response_payload.fb_payload('default_state',helpeeResponse,conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id'),conversation_ref.get().id,helpeePayload)
        payloads.append(helpeePayload)
        print('Helper is {} and Helpee is {}'.format(helper_Name,helpee_Name))
        if payload['platform'].get('helper_next_state'):
            conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
        if payload['platform'].get('helpee_next_state'):
            conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})

        return payloads

    def exchange_conversations(self,payload,conversation_ref):
        payloads =[]
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

        print("Party first_name is {} and response is {}".format(partyName, self.user_response))
        if self.user_response and partyName:
            payload['message']['text'] = partyName+': '+self.user_response
        else:
            payload['message']['text'] = '...'
        
        payload['recipient']['id'] = recipient_id

        #If one of the party ends the conversation, it will go here.

        if '#end' in self.user_response.lower():
            print('User has asked to end the conversation:')
            payload = response_payload.fb_payload('conversation_ended_request_review','...',self.user_id_on_platform,conversation_ref.get().id,payload)
            payload = self.request_review(payload,conversation_ref)
            counterPartyPayload= {}
            counterPartyPayload = response_payload.fb_payload('conversation_ended_request_review','...',recipient_id,conversation_ref.get().id,counterPartyPayload)
            counterPartyPayload['message']['attachment']['payload']['text']='The other user has decided to end the conversation. Was this experience helpful?'
            payloads.append(counterPartyPayload)

        payloads.append(payload)

        return payloads

    def request_review(self,payload,conversation_ref):
        helpee_id = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')
        helper_id = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('fb_id')

        if self.user_id_on_platform == helper_id:
            conversation_ref.update({'helper_state':payload['platform'].get('next_state')})
        else:
            conversation_ref.update({'helpee_state':payload['platform'].get('next_state')})
        conversation_ref.update({'lastactivedate':datetime.now()})
        return payload

    def record_review(self,payload,conversation_ref):
        payloads = []
        helpee_id = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')
        helper_id = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('fb_id')
        #Deternine if this helper or helpee
        if self.user_id_on_platform == helper_id:
            # This is helper save the review for helper
            #print('Before Update: Helpee Review Stored in the DB is: {} and user response is {}'.format(review, self.user_response))
            review = conversation_ref.get().to_dict().get('helper_review')
            if review:
                review += self.user_response
            else:
                review = self.user_response
            conversation_ref.update({'helper_review':review})
            print('After Update: Helper Review Stored in the DB is: {} and user response is {}'.format(review, self.user_response))
            conversation_ref.update({'helper_state':payload['platform'].get('next_state')})
        else:
            #print('Before Update: Helpee Review Stored in the DB is: {} and user response is {}'.format(review, self.user_response))
            review = conversation_ref.get().to_dict().get('helpee_review')
            if review:
                review += self.user_response
            else:
                review = self.user_response
            conversation_ref.update({'helpee_review':review})
            print('After Update: Helpee Review Stored in the DB is: {} and user response is {}'.format(review, self.user_response))
            conversation_ref.update({'helpee_state':payload['platform'].get('next_state')})
        
        conversation_ref.update({'lastactivedate':datetime.now()})
        payloads.append(payload)

        if payload['platform'].get('next_state')=='conversation_closed':
            new_conversation_payload = self.start_new_conversation(payload,conversation_ref)
            payloads.append(new_conversation_payload)

        return payloads

    def start_new_conversation(self,payload,conversation_ref):
        new_conversation_ref = self.core_engine_obj.add_conversation(self.core_engine_obj.get_member())
        #do this to get the right conversation id in the conversation
        payload = {}
        #This call is again made to populate the conversation ref in the payload.
        first_name = self.core_engine_obj.get_member().get().to_dict().get('first_name')
        print('Starting new conversation. First Name is {}'.format(first_name))
        payload = response_payload.fb_payload('welcome_user','...',self.user_id_on_platform ,new_conversation_ref.get().id,payload)
        payload['message']['attachment']['payload']['text'] = Template(payload['message']['attachment']['payload'].get('text')).safe_substitute(arg1=first_name)
        return payload

    def add_expertise(self,payload,conversation_ref):
        self.core_engine_obj.add_expertise(self.core_engine_obj.get_member(),self.user_response,payload['message'].get('text'))
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=self.user_response)
        #del payload['platform']
        return payload

def message_active_conversation(conversation_refs):
    payloads = []
    for conversation_ref in conversation_refs:
        payload=response_payload.fb_payload('message_if_conversation_active','...',conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('fb_id'),conversation_ref.get().id)
        payloads.append(payload)
    return payloads