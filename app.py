import random
import requests
import core_engine
from core_engine import Members
from flask import Flask, request

 
app = Flask(__name__)
ACCESS_TOKEN = 'EAAFRHrTy7U0BAJWebipgZAUCCMPggc8aV5RldgjpPZCD1IZACIwAmvkPfkYMQy8ZASAXkaIaJEi7H7f5eEddYUC4ovdw3vlaY9UzAuBZAZBHr7mhKImfcu6smyrZBfuXUP8aQA7ZB0VoH9mfL0qJCXaVUX0KmC5LesJ7aPVDP1ABVAZDZD'
VERIFY_TOKEN = 'EROS_TOKEN'
#bot = Bot(ACCESS_TOKEN)

payload = {}

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/webhook", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       print (output)
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            sender_id = message['sender']['id']
            member_ref=core_engine.Members(sender_id)
            member = member_ref.get_member()
            #print(member.get().to_dict().get('fb_id'))
            #conversation = member_ref.get_active_conversation(member)
            conversation_ref = member_ref.get_active_conversation_ref(member)
            #print(conversation_ref.get().id)
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                #reciever_id = 1609342142475258
                reciever_id=sender_id
                #core_engine.verify_member_state(sender_id)
                sender_msg = message['message'].get('text')
                if not conversation_ref:
                    # Prompt member if he needs help of wants to do something sele
                    quick_reply_response = message['message'].get('quick_reply')
                    if quick_reply_response:
                        #print(quick_reply_response['payload'])
                        #sender_msg = 'User has choosen the category. Inside conversation'
                        sender_msg = 'I can connect you to {} expert. Please share what are you looking for?  More descriptive the better!'.format(sender_msg)
                        conversation_ref = member_ref.add_conversation(member)
                        conversation_ref.update({'product_category':quick_reply_response['payload']})
                        payload = form_payload('plain_message',sender_msg,sender_id,'')
                    else :
                        payload = form_payload('welcome_buttons',sender_msg,sender_id,'')
                        # This means that this is the first time member is interacting with the platform.
                    send_message(payload)
                else:
                    #Log the conversation. Get the other party id and send it to them.
                    conversation = conversation_ref.get()
                    #quick_reply_response = message['message'].get('quick_reply')
                    #print(message['message'])
                    if conversation.to_dict().get('active'):
                        print("Send the message to the counter party")
                        sender_msg ="I am sending this message to counter party"
                        # Get the counter party from the conversation
                        counter_party = 'YP....'
                        payload = form_payload('plain_message',sender_msg,counter_party, conversation.id)
                        send_message(payload)
                    elif conversation.to_dict().get('conversation_state') == 'identify_timeframe':
                        # Ask user about his time frame for the purchase. Log the question. Move the conversation in Identify price state
                        conversation_ref.update({'conversation_state':'identify_price'})
                        conversation_ref.update({'question':sender_msg})
                        member_ref.log_message(member,conversation_ref,sender_msg)
                        sender_msg = "How soon do you want to buy this product?"
                        payload = form_payload('shopping_timeframe_quick_replies',sender_msg,sender_id, conversation.id)
                        send_message(payload)
                    elif conversation.to_dict().get('conversation_state') == 'identify_price':
                        payload_message = message['message']['quick_reply'].get('payload')
                         # Ask user about price for his purchase. Log the timeframe. Move the conversation in find expert state
                        conversation_ref.update({'conversation_state':'basic_info_gathered'})
                        conversation_ref.update({'time_frame':payload_message})
                        member_ref.log_message(member,conversation_ref,sender_msg)
                        sender_msg = "What price range do you have in mind?"
                        payload = form_payload('shopping_price_quick_replies',sender_msg,sender_id, conversation.id)
                        send_message(payload)
                    elif conversation.to_dict().get('conversation_state') == 'basic_info_gathered':
                        '''
                        payload_message = message['message']['quick_reply'].get('payload')
                        # Reach this state after all the member question onboarding is complete. Member 
                        member_ref.log_message(member,conversation_ref,sender_msg)
                        conversation_ref.update({'conversation_state':'find_expert'})
                        conversation_ref.update({'max_price':payload_message})
                        '''
                        sender_msg = "Thanks. Let me find an expert, who can help you make a decision."
                        payload = form_payload('plain_message',sender_msg,sender_id,conversation.id)
                       
                        #Broadcast this message, to the community of experts
                        # Get all the experts for this expertise 
                        query_results = member_ref.get_experts(conversation.to_dict().get('product_category')).get()
                        message_to_expert = 'We have a member, who is looking for an {} item within {}. Members question is : {}. Do you want to help?'.format(conversation.to_dict().get('product_category'),conversation.to_dict().get('max_price'),conversation.to_dict().get('question'))
                        for result in query_results:
                            expert_member_array = result.to_dict()['member']
                            for expert_member in expert_member_array:
                                expert_id=expert_member.get().to_dict().get('fb_id')
                                payload = form_payload('broadcast_to_experts',message_to_expert,expert_id, conversation.id)
                                send_message(payload)
                    elif conversation.to_dict().get('conversation_state') == 'find_expert':
                        sender_msg = "I am checking with the community to find the right expert for you. I will let you know once I have found someone who can help you"
                        payload = form_payload('plain_message',sender_msg,sender_id, conversation.id)
                        send_message(payload)  
                    elif conversation.to_dict().get('conversation_state') == 'conversation_in_progress':
                        helpee_id = conversation.to_dict().get('helpee_ref').get().to_dict().get('fb_id')
                        helper_id = conversation.to_dict().get('helper_ref').get().to_dict().get('fb_id')
                        print(sender_id)
                        #Deternine if this helper or helpee
                        if sender_id == helper_id:
                            #send message to helpee
                            sender_id = helpee_id
                            partyName = conversation.to_dict().get('helpee_ref').get().to_dict().get('Name')
                        else:
                            #send message to helper
                             sender_id = helper_id
                             partyName = conversation.to_dict().get('helper_ref').get().to_dict().get('Name')
                        #counterparty_id =  helpee_id if sender_id == helper_id else helper_id
                        print(sender_id)
                        msg =partyName+': '+message['message'].get('text')
                        #Send the message across. Get the other party's ID and send the message to them.#if the message has @concier then don't send the message to the other party
                        #sender_id = conversation.to_dict().get('helpee_ref').get().to_dict().get('fb_id')
                        payload = form_payload('plain_message',msg,sender_id, conversation.id)
                        send_message(payload)
                    #print(conversation.to_dict()['helper_ref'].get().to_dict()['fb_id'])
                #print(payload)
            elif message.get('postback'):
                #These are responses to the button
                conversation = message['postback'].get('payload').split(':')
                user_response = message['postback'].get('title')
                conversation_id_frm_msg = conversation[-1]
                print("Conversation ID from the message:{} , {} ".format(conversation, conversation_id_frm_msg))
                member_conversation_id = None
                if conversation_ref:
                    member_conversation_id = conversation_ref.get().id
                    print ('Responder active conv: '+ member_conversation_id)
                    
                #print ("Conversation ID from the response: ".format(conversation_id))
                conversation_ref = member_ref.get_active_conversation_ref_byID(conversation_id_frm_msg)
                print (conversation_ref.get().to_dict().get('conversation_state'))
                if (member_conversation_id==conversation_id_frm_msg):
                    print('This is active conversation or the person')
                    sender_msg ='Sender is recieving to himself'
                    payload = form_payload('plain_message',sender_msg,sender_id,conversation_id)
                else :
                    conversation_state = conversation_ref.get().to_dict().get('conversation_state')
                    print('Expert has responded to a broadcast message in the state: '.format(conversation_state))
                    if conversation_state == 'basic_info_gathered' and user_response =='YES':
                        conversation_ref.update({'helper_ref':member})
                        conversation_ref.update({'conversation_state':'conversation_in_progress'})
                        member.update({'conversations':[conversation_ref]})
                        helpee_ref = conversation_ref.get().to_dict().get('helpee_ref')
                        helper_msg ='Great. I am going to connect you to {}'.format(helpee_ref.get().get('Name'))
                        helpee_msg = 'We are going to connect you to {}'.format(member.get().get('Name'))
                        payload_other = form_payload('plain_message',helpee_msg,helpee_ref.get().get('fb_id'),'')
                        send_message(payload_other)
                        payload = form_payload('plain_message',helper_msg,sender_id,'')
                    else :
                        sender_msg ='We are still looking for an expert for you.'
                        payload = form_payload('plain_message',sender_msg,sender_id,'')
                ''' Determine if the responder is seeker or adviser
                
                if conversation_state == 'basic_info_gathered':
                    if user_response=='YES':
                '''
                #print(conversation_ref.get().to_dict().get('max_price'))
                sender_msg = message['postback'].get('title')
                if user_response == 'seekingAdvice':
                    print("Member is seeking help now...")
                    sender_msg='What are you shopping for?'
                    payload = form_payload('shopping_category_quick_replies',sender_msg,sender_id,conversation_id)
                elif user_response =='other':
                    print("Member wants to do something else, present other options")
                    payload = form_payload('other_buttons',sender_msg,sender_id,conversation_id)
                elif user_response =='expertRegsteration':
                    print("Member wants to register as expert")
                    #sender_msg = 'Please visit http://concier.org to register as expert'
                    # Add member to a expertise category
                    payload = form_payload('choose_expertise_category',sender_msg,sender_id,conversation_id)
                elif user_response =='phone' or user_response =='electronics' or user_response =='computers':
                    member_ref.add_expert(member,user_response)
                    sender_msg = 'Great I have added you as an expert for '+user_response
                    payload = form_payload('plain_message',sender_msg,sender_id,conversation_id)
                elif user_response =='manage_account':
                    print("Manage your account at http://concier.org/account")
                    payload = form_payload('plain_message',sender_msg,sender_id,conversation_id)
                else :
                    print("Some other option choosen")
                    #sender_msg = 'This is the back room of the Concier maze: '+sender_msg
                    #payload = form_payload('plain_message',sender_msg,sender_id,conversation_id)
                send_message(payload)
    return "Message Processed"

def receive_message_old():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       print (output)
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            sender_id = message['sender']['id']
            member_ref=core_engine.Members(sender_id)
            member = member_ref.get_member()
            #print(member.get().to_dict().get('fb_id'))
            #conversation = member_ref.get_active_conversation(member)
            conversation_ref = member_ref.get_active_conversation_ref(member)
            #print(conversation_ref.get().id)
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                #reciever_id = 1609342142475258
                reciever_id=sender_id
                #core_engine.verify_member_state(sender_id)
                sender_msg = message['message'].get('text')
                if not conversation_ref:
                    # Prompt member if he needs help of wants to do something sele
                    quick_reply_response = message['message'].get('quick_reply')
                    if quick_reply_response:
                        #print(quick_reply_response['payload'])
                        #sender_msg = 'User has choosen the category. Inside conversation'
                        sender_msg = 'I can connect you to {} expert. Please share what are you looking for?  More descriptive the better!'.format(sender_msg)
                        conversation_ref = member_ref.add_conversation(member)
                        conversation_ref.update({'product_category':quick_reply_response['payload']})
                        payload = form_payload('plain_message',sender_msg,sender_id,'')
                    else :
                        payload = form_payload('welcome_buttons',sender_msg,sender_id,'')
                        # This means that this is the first time member is interacting with the platform.
                    send_message(payload)
                else:
                    #Log the conversation. Get the other party id and send it to them.
                    conversation = conversation_ref.get()
                    #quick_reply_response = message['message'].get('quick_reply')
                    #print(message['message'])
                    if conversation.to_dict().get('active'):
                        print("Send the message to the counter party")
                        sender_msg ="I am sending this message to counter party"
                        # Get the counter party from the conversation
                        counter_party = 'YP....'
                        payload = form_payload('plain_message',sender_msg,counter_party, conversation.id)
                        send_message(payload)
                    elif conversation.to_dict().get('conversation_state') == 'identify_timeframe':
                        # Ask user about his time frame for the purchase. Log the question. Move the conversation in Identify price state
                        conversation_ref.update({'conversation_state':'identify_price'})
                        conversation_ref.update({'question':sender_msg})
                        member_ref.log_message(member,conversation_ref,sender_msg)
                        sender_msg = "How soon do you want to buy this product?"
                        payload = form_payload('shopping_timeframe_quick_replies',sender_msg,sender_id, conversation.id)
                        send_message(payload)
                    elif conversation.to_dict().get('conversation_state') == 'identify_price':
                        payload_message = message['message']['quick_reply'].get('payload')
                         # Ask user about price for his purchase. Log the timeframe. Move the conversation in find expert state
                        conversation_ref.update({'conversation_state':'basic_info_gathered'})
                        conversation_ref.update({'time_frame':payload_message})
                        member_ref.log_message(member,conversation_ref,sender_msg)
                        sender_msg = "What price range do you have in mind?"
                        payload = form_payload('shopping_price_quick_replies',sender_msg,sender_id, conversation.id)
                        send_message(payload)
                    elif conversation.to_dict().get('conversation_state') == 'basic_info_gathered':
                        '''
                        payload_message = message['message']['quick_reply'].get('payload')
                        # Reach this state after all the member question onboarding is complete. Member 
                        member_ref.log_message(member,conversation_ref,sender_msg)
                        conversation_ref.update({'conversation_state':'find_expert'})
                        conversation_ref.update({'max_price':payload_message})
                        '''
                        sender_msg = "Thanks. Let me find an expert, who can help you make a decision."
                        payload = form_payload('plain_message',sender_msg,sender_id,conversation.id)
                       
                        #Broadcast this message, to the community of experts
                        # Get all the experts for this expertise 
                        query_results = member_ref.get_experts(conversation.to_dict().get('product_category')).get()
                        message_to_expert = 'We have a member, who is looking for an {} item within {}. Members question is : {}. Do you want to help?'.format(conversation.to_dict().get('product_category'),conversation.to_dict().get('max_price'),conversation.to_dict().get('question'))
                        for result in query_results:
                            expert_member_array = result.to_dict()['member']
                            for expert_member in expert_member_array:
                                expert_id=expert_member.get().to_dict().get('fb_id')
                                payload = form_payload('broadcast_to_experts',message_to_expert,expert_id, conversation.id)
                                send_message(payload)
                    elif conversation.to_dict().get('conversation_state') == 'find_expert':
                        sender_msg = "I am checking with the community to find the right expert for you. I will let you know once I have found someone who can help you"
                        payload = form_payload('plain_message',sender_msg,sender_id, conversation.id)
                        send_message(payload)  
                    elif conversation.to_dict().get('conversation_state') == 'conversation_in_progress':
                        helpee_id = conversation.to_dict().get('helpee_ref').get().to_dict().get('fb_id')
                        helper_id = conversation.to_dict().get('helper_ref').get().to_dict().get('fb_id')
                        print(sender_id)
                        #Deternine if this helper or helpee
                        if sender_id == helper_id:
                            #send message to helpee
                            sender_id = helpee_id
                            partyName = conversation.to_dict().get('helpee_ref').get().to_dict().get('Name')
                        else:
                            #send message to helper
                             sender_id = helper_id
                             partyName = conversation.to_dict().get('helper_ref').get().to_dict().get('Name')
                        #counterparty_id =  helpee_id if sender_id == helper_id else helper_id
                        print(sender_id)
                        msg =partyName+': '+message['message'].get('text')
                        #Send the message across. Get the other party's ID and send the message to them.#if the message has @concier then don't send the message to the other party
                        #sender_id = conversation.to_dict().get('helpee_ref').get().to_dict().get('fb_id')
                        payload = form_payload('plain_message',msg,sender_id, conversation.id)
                        send_message(payload)
                    #print(conversation.to_dict()['helper_ref'].get().to_dict()['fb_id'])
                #print(payload)
            elif message.get('postback'):
                #These are responses to the button
                conversation = message['postback'].get('payload').split(':')
                user_response = message['postback'].get('title')
                conversation_id_frm_msg = conversation[-1]
                print("Conversation ID from the message:{} , {} ".format(conversation, conversation_id_frm_msg))
                member_conversation_id = None
                if conversation_ref:
                    member_conversation_id = conversation_ref.get().id
                    print ('Responder active conv: '+ member_conversation_id)
                    
                #print ("Conversation ID from the response: ".format(conversation_id))
                conversation_ref = member_ref.get_active_conversation_ref_byID(conversation_id_frm_msg)
                print (conversation_ref.get().to_dict().get('conversation_state'))
                if (member_conversation_id==conversation_id_frm_msg):
                    print('This is active conversation or the person')
                    sender_msg ='Sender is recieving to himself'
                    payload = form_payload('plain_message',sender_msg,sender_id,conversation_id)
                else :
                    conversation_state = conversation_ref.get().to_dict().get('conversation_state')
                    print('Expert has responded to a broadcast message in the state: '.format(conversation_state))
                    if conversation_state == 'basic_info_gathered' and user_response =='YES':
                        conversation_ref.update({'helper_ref':member})
                        conversation_ref.update({'conversation_state':'conversation_in_progress'})
                        member.update({'conversations':[conversation_ref]})
                        helpee_ref = conversation_ref.get().to_dict().get('helpee_ref')
                        helper_msg ='Great. I am going to connect you to {}'.format(helpee_ref.get().get('Name'))
                        helpee_msg = 'We are going to connect you to {}'.format(member.get().get('Name'))
                        payload_other = form_payload('plain_message',helpee_msg,helpee_ref.get().get('fb_id'),'')
                        send_message(payload_other)
                        payload = form_payload('plain_message',helper_msg,sender_id,'')
                    else :
                        sender_msg ='We are still looking for an expert for you.'
                        payload = form_payload('plain_message',sender_msg,sender_id,'')
                ''' Determine if the responder is seeker or adviser
                
                if conversation_state == 'basic_info_gathered':
                    if user_response=='YES':
                '''
                #print(conversation_ref.get().to_dict().get('max_price'))
                sender_msg = message['postback'].get('title')
                if user_response == 'seekingAdvice':
                    print("Member is seeking help now...")
                    sender_msg='What are you shopping for?'
                    payload = form_payload('shopping_category_quick_replies',sender_msg,sender_id,conversation_id)
                elif user_response =='other':
                    print("Member wants to do something else, present other options")
                    payload = form_payload('other_buttons',sender_msg,sender_id,conversation_id)
                elif user_response =='expertRegsteration':
                    print("Member wants to register as expert")
                    #sender_msg = 'Please visit http://concier.org to register as expert'
                    # Add member to a expertise category
                    payload = form_payload('choose_expertise_category',sender_msg,sender_id,conversation_id)
                elif user_response =='phone' or user_response =='electronics' or user_response =='computers':
                    member_ref.add_expert(member,user_response)
                    sender_msg = 'Great I have added you as an expert for '+user_response
                    payload = form_payload('plain_message',sender_msg,sender_id,conversation_id)
                elif user_response =='manage_account':
                    print("Manage your account at http://concier.org/account")
                    payload = form_payload('plain_message',sender_msg,sender_id,conversation_id)
                else :
                    print("Some other option choosen")
                    #sender_msg = 'This is the back room of the Concier maze: '+sender_msg
                    #payload = form_payload('plain_message',sender_msg,sender_id,conversation_id)
                send_message(payload)
    return "Message Processed"
 
def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def send_message(payload):
    #sends user the text message provided via input response parameter
    #bot.send_text_message(recipient_id, response)
    auth = {
    'access_token':ACCESS_TOKEN
    }
    request_endpoint = 'https://graph.facebook.com/v2.6/me/messages'
    response = requests.post(
        request_endpoint,
        params=auth,
        json=payload
        )
    result = response.json()
    return result

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
        #payload['notification_type'] = 'REGULAR'
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"Hey there! How can I help?",
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Get shopping advice?",
                    "payload":"seekingAdvice"
                    },
                    {
                    "type":"postback",
                    "title":"Other?",
                    "payload":"other"
                    }
                    ]
                }
            }
        }
    elif response_type =='choose_expertise_category':
        #payload['notification_type'] = 'REGULAR'
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"What kind of products you know well?",
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Phone",
                    "payload":"phone"
                    },
                    {
                    "type":"postback",
                    "title":"Electronics",
                    "payload":"electronics"
                    },
                    {
                    "type":"postback",
                    "title":"Computers",
                    "payload":"computers"
                    }
                    ]
                }
            }
        }
    elif response_type =='broadcast_to_experts':
        #payload['notification_type'] = 'REGULAR'
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":text_message,
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"YES",
                    "payload":"acceptAssignment:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"NO",
                    "payload":"declineAssignment:"+conversation_id
                    }
                    ]
                }
            }
        }
    elif response_type =='other_buttons':
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"Other things you can do?",
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Register as expert",
                    "payload":"expertRegsteration"
                    },
                    {
                    "type":"postback",
                    "title":"Manage Account",
                    "payload":"manage_account"
                    },
                    {
                    "type":"postback",
                    "title":"Something else",
                    "payload":"something_else"
                    }
                    ]
                }
            }
        }
    elif response_type =='shopping_category_buttons':
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":text_message,
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Electronics",
                    "payload":"electronics"
                    },
                    {
                    "type":"postback",
                    "title":"Computers",
                    "payload":"computers"
                    },
                    {
                    "type":"postback",
                    "title":"Household Item",
                    "payload":"house hold item"
                    },
                    {
                    "type":"postback",
                    "title":"Other",
                    "payload":"other item"
                    }
                    ]
                }
            }
        }
    elif response_type =='shopping_category_quick_replies':
        payload['message'] = {
        'text' : text_message,
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Phone",
            "payload":"phone"
            },
            {
            "content_type":"text",
            "title":"Electronics",
            "payload":"electronics"
            },
            {
            "content_type":"text",
            "title":"Computers",
            "payload":"computers"
            },
            {
            "content_type":"text",
            "title":"Household Items",
            "payload":"house_hold_items"
            }
            ]
        }
    elif response_type =='shopping_timeframe_quick_replies':
        payload['message'] = {
        'text' : text_message,
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Less than 24 hours",
            "payload":"24 hours"
            },
            {
            "content_type":"text",
            "title":"One week",
            "payload":"one week"
            },
            {
            "content_type":"text",
            "title":"One month",
            "payload":"one month"
            },
            {
            "content_type":"text",
            "title":"Don't have a timeframe",
            "payload":"no timeframe"
            }
            ]
        }
    elif response_type =='shopping_price_quick_replies':
        payload['message'] = {
        'text' : text_message,
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Do not know",
            "payload":"no price in mind"
            },
            {
            "content_type":"text",
            "title":"Max $1000",
            "payload":"$1000"
            },
            {
            "content_type":"text",
            "title":"Max $500",
            "payload":"$500"
            },
            {
            "content_type":"text",
            "title":"Max $100",
            "payload":"$100"
            },
            {
            "content_type":"text",
            "title":"Price doesn't matter",
            "payload":"Price doesn't matter"
            }
            ]
        }
    return payload

if __name__ == "__main__":
    app.run()