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

            '''
            if conversation_duration_hours > 24:
                print('this conversation has been active for more than 24 hours')
                conversation_state = 'conversation_ended_request_review'
            '''

            # Flush the payload
            if '#end' in self.user_response.lower() and conversation_state !='helper_helpee_matched':
                payload = response_payload.fb_payload('conversation_ended_request_review','...',self.user_id_on_platform,conversation_ref.get().id,payload)
            else:
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
            payload = response_payload.fb_payload('default_state','Houston, we have a problem. Error happened.',self.user_id_on_platform,'',payload)
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
        payloads = []
        infoPayload = {}
        first_name = self.core_engine_obj.get_member().get().to_dict().get('first_name')
        payload['message']['attachment']['payload']['text'] = Template(payload['message']['attachment']['payload'].get('text')).safe_substitute(arg1=first_name)
        payloads.append(payload)
        
        infoPayload = response_payload.fb_payload('end_conversation_info','...',self.user_id_on_platform,conversation_ref.get().id,infoPayload)
        payloads.append(infoPayload)

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
            if payload['platform'].get('validate')=='input_length_more_than_10' and len(self.user_response)<10:
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

    def record_need_and_broadcast_request(self,payload,conversation_ref):
        payloads = []
        payloads.append(payload)
        product = conversation_ref.get().to_dict().get('product')
        user_need = self.user_response
        
        print("User need is {}".format(user_need))

        experts_list = self.core_engine_obj.get_super_experts()# Super experts will get messages for everything. They can choose to decline or accept the request.

        response_template = 'A user is researching for the Product: $arg1.\nUser need: $arg2.\nDo you want to help?'
        response = Template(response_template).safe_substitute(arg1=product,arg2=user_need)
        print('\nSending message to super experts\n')
        
        helpee_state =payload['platform'].get('helpee_next_state')
        if len(experts_list)>0:
            for expert in experts_list:
                if expert.get().to_dict().get('fb_id') != self.user_id_on_platform:
                    expertPayload = {}
                    expertPayload = response_payload.fb_payload('broadcast_request_to_super_experts',response,expert.get().to_dict().get('fb_id'),conversation_ref.get().id,expertPayload)
                    payloads.append(expertPayload)
                    print('Expert is {} and request came from {}'.format(expert.get().to_dict().get('fb_id'),self.user_id_on_platform))
        else:
            # we didn't find any expert. Let the helpee know that we don't have a expert. We will be in touch once we find one.
            payload['message']['text'] = 'Currently, we don\'t have a member who has bought a product you have specified. We will get back to you, when a member who can you help you joins.'
            helpee_state='conversation_closed'
        
        conversation_ref.update({'active':True,'user_need':user_need,'helper_ref':None,'helpee_state':helpee_state})

        del payload['platform']
        return payloads

    def record_price_and_broadcast_request(self,payload,conversation_ref):
        payloads = []
        payloads.append(payload)

        

        '''
        if payload['platform'].get('helper_next_state'):
            conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
        if payload['platform'].get('helpee_next_state'):
            conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})
        '''

        product = conversation_ref.get().to_dict().get('product')
        specific_product = conversation_ref.get().to_dict().get('specific_product')
        experts_list = self.core_engine_obj.get_experts(product)
       
        response_template = 'A community member wants to talk to you about a product you purchased. Can you help? \nProduct: $arg1\nNeed: $arg2\nPrice Range: $arg3\nTimeline: $arg4'
        response = Template(response_template).safe_substitute(arg1=product,arg2=conversation_ref.get().to_dict().get('user_need'),arg3=conversation_ref.get().to_dict().get('max_price'),arg4=conversation_ref.get().to_dict().get('time_frame'))
        print('\nPayload before assignement\n')
        helpee_state =''
        if len(experts_list)>0:
            for expert in experts_list:
                if expert.get().to_dict().get('fb_id') != self.user_id_on_platform:
                    expertPayload = {}
                    expertPayload = response_payload.fb_payload('broadcast_request_to_super_experts',response,expert.get().to_dict().get('fb_id'),conversation_ref.get().id,expertPayload)
                    helpee_state = payload['platform'].get('helpee_next_state')
                    #payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=product_category,arg2=conversation_ref.get().to_dict().get('max_price'),arg3=conversation_ref.get().to_dict().get('user_need'))
                    payloads.append(expertPayload)
                    print('Expert is {} and request came from {}'.format(expert.get().to_dict().get('fb_id'),self.user_id_on_platform))
        else:
            # we didn't find any expert. Let the helpee know that we don't have a expert. We will be in touch once we find one.
            payload['message']['text'] = 'Currently, we don\'t have a member who has bought a product you have specified. We will get back to you, when a member who can you help you joins.'
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
        #self.core_engine_obj.append_conversation_ref(member_ref,conversation_ref)
        ### Add to active conversation partner Map
        conversations_array = member_ref.get().get('conversations')
        member_short_id = ''
        if conversation_ref in conversations_array:
            #Don't do anything.Member is already added to the conversation
            print('Member already added to the conversation')
        else:
            conversations_array.append(conversation_ref)
            active_helpees_map = member_ref.get().get('active_conv_partners')
            print("Active Helpees Map",active_helpees_map)
            member_short_id = (conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('first_name')+conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('last_name')[0]+''+str(len(active_helpees_map)+1)).lower()
            #dict_key = member_short_id 
            active_helpees_map[member_short_id]=conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')
            member_ref.update({'conversations':conversations_array,'active_conv_partners':active_helpees_map,'lastactivedate':datetime.now()}, firestore.CreateIfMissingOption(True))
        ####
        conversation_ref.update({'helper_ref':member_ref})
        product_Name = conversation_ref.get().to_dict().get('product')
        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(arg1=product_Name)
        if payload['platform'].get('helper_next_state'):
            conversation_ref.update({'helper_state':payload['platform'].get('helper_next_state')})
        if payload['platform'].get('helpee_next_state'):
            conversation_ref.update({'helpee_state':payload['platform'].get('helpee_next_state')})
        #del payload['platform']
        return member_short_id

    def connect_expert_to_user(self,payload,conversation_ref):
        payloads = []
        ''' Get the correct conversation ref. 
        Send two messages. One to the expert and the other to the helpee
        '''

        conversation_ref.update({'expert_why_product_bought':self.user_response})
        member_ref = self.core_engine_obj.get_member()
        helpee_Name = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('first_name')
        helper_Name = member_ref.get().to_dict().get('first_name')

        member_short_id = self.assign_helper(payload,conversation_ref)

        payload['message']['text'] = Template(payload['message'].get('text')).safe_substitute(helpee_arg1=helpee_Name+' ('+member_short_id+')')
        payloads.append(payload)

        product_bought = conversation_ref.get().to_dict().get('expert_what_product_bought')
        products_in_the_market = conversation_ref.get().to_dict().get('expert_key_products_in_the_market')
        product_price_ranges = conversation_ref.get().to_dict().get('expert_product_price_ranges')
        product_differences = conversation_ref.get().to_dict().get('expert_product_differences')
        why_bought_product = conversation_ref.get().to_dict().get('expert_why_product_bought')
        product = conversation_ref.get().to_dict().get('product')

        helpeePayload= {}
        #This response is commented to accomodate Super Experts. If both kind of experts are present, tweak the helpee response below.
        #helpeeResponse = '{} made a similar purchase recently. Below is some information about {}\'s purchase.\n\nProduct bought: {}\nProduct looked at:{}\nPrice range:{}\nDifference in product:{}\nWhy member bought {}:{}\n\nYou have 12 hours to talk to community member before you release member to talk to other members. At any time, if you want to end the conversation, type #end and enter.\nWe will now connect you to {}. Please say hi!'.format(helper_Name,helper_Name,product_bought,products_in_the_market,product_price_ranges,product_differences,product_bought,why_bought_product,helper_Name)
        helpeeResponse = '{} is an expert in {}. You have 12 hours chat to with {}. At any time, if you want to end the conversation, type #end.\nWe will now connect you to {}. Please say hi!'.format(helper_Name, product, helper_Name, helper_Name)
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
        msg_frm_other_party = self.user_response
        member_needs_help = False
        member_id_based_on_aka = 0
        hash_tag_cmd = '' 

        end_conversation = False

        for platform_cmd in self.user_response.split():
            if platform_cmd.startswith('#'):#find every character that starts with #
                #this is the place to identify platform commands.
                if platform_cmd == '#end':
                    end_conversation = True
                    break
                elif platform_cmd =='#help':
                    member_needs_help = True
                    break
                    #respond back to the person, who sent this message. Don't alter the payload['recipient']['id'] 
                    #Create two payloads. Send one to the admins and other to the sender.
                elif self.user_id_on_platform == helper_id:
                    #All the other hash tag commands for helpers
                    if platform_cmd =='#helpees':
                        #Show the List of people, I am helping
                        active_conv_partners = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('active_conv_partners')
                        member_id_based_on_aka = 1
                        print("List of helpees",active_conv_partners)
                    else:
                        member_id_based_on_aka = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('active_conv_partners').get(platform_cmd.replace("#","").lower(),-1)
                        hash_tag_cmd = platform_cmd
                        #msg_frm_other_party= platform_cmd.replace("#","")
                        print('Member Id is',member_id_based_on_aka)
                        break
        
        if self.user_id_on_platform == helper_id:
            if member_id_based_on_aka ==-1:
                #Let the helper know that the user with this #tag doesn't exist. Don't alter the payload['recipient']['id'] 
                payload['message']['text']='Unable to deliver the last message.\n\nYou are not in conversation with '+hash_tag_cmd.replace("#","")+'.'
                payload['recipient']['id'] = helper_id
                print("State not equal to -1")
            elif member_id_based_on_aka ==0:
                payload['message']['text'] = 'Unable to deliver the last message.\n\n Please include a #<Helpee Name>'
                payload['recipient']['id'] = helper_id
                print("State 0")
                # this is Helper. Helper needs to define a #tag username. Ask helper to send the #tag username.
            elif member_id_based_on_aka ==1:
                payload['message']['text'] = 'You are in conversation with:\n'+"\n".join(active_conv_partners.keys())
                payload['recipient']['id'] = helper_id
                print("State 0")
                # this is Helper. Helper needs to define a #tag username. Ask helper to send the #tag username.
            else:
                # Helper has sent a #tag command and we have found the user. Send this message to the person with the id
                payload['recipient']['id']  = member_id_based_on_aka
                payload['message']['text'] = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('first_name')+':'+self.user_response.replace(hash_tag_cmd,"")
                print("Sending it to right person")
        else:
            payload['recipient']['id'] = helper_id
            #Helper needs to know, who is sending the message.
            active_conv_partners_dict= conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('active_conv_partners')
            member_short_id = list(active_conv_partners_dict.keys())[list(active_conv_partners_dict.values()).index(self.user_id_on_platform)]
            print(member_short_id)
            payload['message']['text'] = member_short_id+':'+self.user_response
                    # this is helpee. Send the message to helper, with helpee's name

        
        '''
        #Deternine if this is helper or helpee
        if self.user_id_on_platform == helper_id:
            #send message to helpee
            if member_id_based_on_aka != -1:
                recipient_id = helpee_id
                partyName = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('first_name')#This should be the first_name of the sender so it will be the counter party first_name
            else:
                #Helper has typed incorrect #<user>
                recipient_id = helper_id
                alt_response='Unable to deliver the last message.\n\n'+member_aka+' is not in this conversation.'
                partyName = ''
        else:
            recipient_id = helper_id
            partyName = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('first_name') # this should be the first_name of the sender
            #send message to helper
       

        print("Party first_name is {} and response is {}".format(partyName, self.user_response))
        if self.user_response and partyName:
            payload['message']['text'] = partyName+':'+alt_response
        else:
            payload['message']['text'] = '...'
            #payload['message']['text'] = 'Unable to deliver the last message.\n\n'+member_aka+' is not in this conversation.'
    
        payload['recipient']['id'] = recipient_id
        '''
        #If one of the party ends the conversation, it will go here.

        conversation_duration_hours = 0
        if (abs(datetime.now(timezone.utc)-conversation_ref.get().to_dict().get('lastactivedate')).days * 24):
            conversation_duration_hours=abs(datetime.now(timezone.utc)-conversation_ref.get().to_dict().get('lastactivedate')).days * 24
            end_conversation = True         

        if end_conversation:

            print('User has asked to end the conversation or it has been been more 12 hours for this conversation{}'.format(conversation_duration_hours))
            payload = response_payload.fb_payload('conversation_ended_request_review','...',self.user_id_on_platform,conversation_ref.get().id,payload)
            payload = self.request_review(payload,conversation_ref)
            counterPartyPayload= {}
            if self.user_id_on_platform == helper_id:
                recipient_id = helpee_id
            else:
                recipient_id = helper_id
            #we need to remove the entry for this helpee member from the active conversation list with helper
            active_conv_partners_dict= conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('active_conv_partners')
            member_short_id = list(active_conv_partners_dict.keys())[list(active_conv_partners_dict.values()).index(self.user_id_on_platform)]

            popCheck = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('active_conv_partners').pop(member_short_id, None)
            print ('Popped the key {}'.format(popCheck))
            counterPartyPayload = response_payload.fb_payload('conversation_ended_request_review','...',recipient_id,conversation_ref.get().id,counterPartyPayload)
            counterPartyPayload['message']['attachment']['payload']['text']='The other user has ended the conversation. Was this experience helpful?'
            payloads.append(counterPartyPayload)

        if member_needs_help:
            print('User has asked for help from the platform')
            customer_support_list = self.core_engine_obj.get_members_by_type('active_customer_support')
            for customer_support in customer_support_list:
                if customer_support.get().to_dict().get('fb_id') != self.user_id_on_platform:
                    requestForHelpPayload = {}
                    requestForHelpPayload = response_payload.fb_payload('help_request_from_user',self.user_response,customer_support.get().to_dict().get('fb_id'),conversation_ref.get().id,requestForHelpPayload)
                    payloads.append(requestForHelpPayload)
            #send a message to user acknowledging the help request
            payload = response_payload.fb_payload('need_help','...',self.user_id_on_platform,conversation_ref.get().id,payload)
            
        del payload['platform']
        payloads.append(payload)
        print("User payload is {}: ".format(payloads))
        return payloads

    def request_review(self,payload,conversation_ref):
        helpee_id = None
        helper_id = None
        if conversation_ref.get().to_dict().get('helpee_ref') is not None:
            helpee_id = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')

        if conversation_ref.get().to_dict().get('helper_ref') is not None:
            helper_id = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('fb_id')

        if self.user_id_on_platform == helper_id:
            conversation_ref.update({'helper_state':payload['platform'].get('next_state')})
        else:
            conversation_ref.update({'helpee_state':payload['platform'].get('next_state')})
        conversation_ref.update({'lastactivedate':datetime.now()})
        return payload

    def record_review(self,payload,conversation_ref):
        payloads = []
        helpee_id = None
        helper_id = None
        isHelpee = False
        isHelper = False
        #helper_fName = 'Jane'
        if conversation_ref.get().to_dict().get('helpee_ref') is not None:
            helpee_id = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')

        if conversation_ref.get().to_dict().get('helper_ref') is not None:
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
            isHelper = True
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
            #helper_fName = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('first_name')
            isHelpee = True
        conversation_ref.update({'lastactivedate':datetime.now()})
        payloads.append(payload)

        if payload['platform'].get('next_state')=='conversation_closed':
            if isHelpee and conversation_ref.get().to_dict().get('helper_ref') is not None:
                helper_name = conversation_ref.get().to_dict().get('helper_ref').get().to_dict().get('first_name')
                payload['message']['text']= Template(payload['platform'].get('helpee_message')).safe_substitute(arg1=helper_name)
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

def close_overdue_conversations():
    payloads = []
    core_engine_obj = core_engine.Platform()
    waiting_helpee_list = core_engine_obj.close_overdue_conversations()

    if len(waiting_helpee_list)>0:
        for helpee_ref in waiting_helpee_list:
            helpeePayload = {}
            helpeePayload = response_payload.fb_payload('overdue_conversation','response',helpee_ref.get().to_dict().get('fb_id'),'This is',helpeePayload)
            #print('Helpee Ref: {}'.format(helpee_ref))
            payloads.append(helpeePayload)
    return payloads 