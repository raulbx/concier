import random
import requests
import core_engine
import conversation_exchange
from core_engine import Members
from core_engine import Platform
from flask import Flask, request

app = Flask(__name__)
ACCESS_TOKEN = 'EAAFRHrTy7U0BAJWebipgZAUCCMPggc8aV5RldgjpPZCD1IZACIwAmvkPfkYMQy8ZASAXkaIaJEi7H7f5eEddYUC4ovdw3vlaY9UzAuBZAZBHr7mhKImfcu6smyrZBfuXUP8aQA7ZB0VoH9mfL0qJCXaVUX0KmC5LesJ7aPVDP1ABVAZDZD'
VERIFY_TOKEN = 'EROS_TOKEN'

#bot = Bot(ACCESS_TOKEN)

payloads = []

def check_active_conversations():
    print('Check if shopper wants to continue the message')
    active_conversation_refs= Platform.get_all_active_conversations('FB')
    print(active_conversation_refs)
    payloads = conversation_exchange.message_active_conversation(active_conversation_refs)
    for payload in payloads:
        print('Do nothing for now')
    #    send_message(payload)
    #Send it only once and disable if the user doesn't respond.
    return "Message Processed"

@app.route('/sixty_minute_reminder', methods=['GET'])
def remind_expert_to_respond():

    print('Remind experts---')

    return "remind expert to respond"

@app.route('/close_overdue_conversations', methods=['GET'])
def close_overdue_conversations():
    status='Done'
    #exchange_obj = conversation_exchange.Exchange('00000000000','FB',core_engine_obj,'No User response')

    payloads = conversation_exchange.close_overdue_conversations()

    for payload in payloads:
        #print('The payload from backend is {}'.format(payload))
        send_message(payload)
    return status

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
       print(output)
       print ('-------------Above is the message from FB--------------')
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            sender_id = message['sender']['id']
            #check if an attachment was sent
            
            core_engine_obj=core_engine.Members(sender_id) #This sets the facebook ID
            member_ref = core_engine_obj.get_member() #This is getting the firebase reference to the member obj. It will create member, if one doesn't exist.
            conversation_state = None
            msg_conversation_id = None
            if message.get('message'):
                user_response = message['message'].get('text')
                quick_reply_response = message['message'].get('quick_reply')
                if quick_reply_response:
                    conversation = quick_reply_response['payload'].split(':')
                    conversation_state = conversation[0]
                    msg_conversation_id = conversation[-1]
            elif message.get('postback'):
                user_response = message['postback'].get('title')
                conversation = message['postback'].get('payload').split(':')
                conversation_state = conversation[0]
                #user_response = message['postback'].get('title')
                msg_conversation_id = conversation[-1]

            '''
            first check if there is msg_conversation_id in the message. If there is a message conversation ID. 
            Use it to direct the user to the  appropriate conversation object.
            '''
            #Make sure we have correct conversation_ref
            print ('MSG Conversation ID IS: '.format(msg_conversation_id))
            if msg_conversation_id:
                conversation_ref=core_engine_obj.get_active_conversation_ref_byID(msg_conversation_id)
                if conversation_ref:
                    print('MSG Conversation ID is in chat message')
                else:
                    print('There is no conversation with the ID{}: '.format(msg_conversation_id))
            else:
                conversation_ref = core_engine_obj.get_active_conversation_ref(member_ref) #This gets the reference to the associated conversation object
                #print('Conversation Ref is {}'.format(conversation_ref))
                
                if conversation_ref == None:
                    print('There is no actual object: {}'.format(conversation_ref))
                elif conversation_ref.get().exists:
                    print('Retrieved Conversation ID: {} from the conversation ref {}'.format(conversation_ref.id, conversation_ref))
                    
            
           #print('Conversation Ref is: '.format(conversation_ref.get().id))
            #TODO: Fix the expert conversation references

            #You have got everything from the user_message. Now get the flow state from conversation. Per the conversation state respond to the message
            #Store the reference to the state in the conversation
            # Make the change here to make this code generic
            #print("User response is {} and conversation ref {}".format(user_response, conversation_ref))
            exchange_obj = conversation_exchange.Exchange(sender_id,'FB',core_engine_obj,user_response)
          #  exchange_obj.get_action()
            if not conversation_ref:
                #start the conversation
                core_engine_obj.update_member_details(member_ref,get_user_details(sender_id))
                payloads = exchange_obj.start_conversation(core_engine_obj)
            else:
                #Get the conversation flow state, from the payload and send it
                if conversation_state is None:
                    # First check if the request is coming from expert or person needing help. Based on this retrieving the state from the conversation
                    #helpee_id = conversation_ref.get().to_dict().get('helpee_ref').get().to_dict().get('fb_id')
                    helper_ref = conversation_ref.get().to_dict().get('helper_ref')
                    helper_id = None
                    if helper_ref:
                        helper_id=helper_ref.get().to_dict().get('fb_id')
                    #Deternine if this helper or helpee
                    state_to_get = ''
                    if sender_id == helper_id:
                        # this is helper
                        state_to_get='helper_state'
                    else:
                        # this is helpee
                        state_to_get='helpee_state'
                    conversation_state = conversation_ref.get().to_dict().get(state_to_get) 
                print("Conversation Flow State is:{}".format(conversation_state))

                payloads = exchange_obj.get_action(conversation_ref,conversation_state)
               # print(payloads)
              #  print('---------above  is the payload created by the platform -----')
    for payload in payloads:
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
    request_endpoint = 'https://graph.facebook.com/v3.1/me/messages'
    response = requests.post(
        request_endpoint,
        params=auth,
        json=payload
        )
    result = response.json()
    return result

def get_user_details(sender_id):
    request_endpoint = 'https://graph.facebook.com/v3.1/{}?fields=first_name,last_name&access_token={}'.format(sender_id,ACCESS_TOKEN)
    response = requests.get(request_endpoint)
    user_profile_json = response.json()
    return user_profile_json

def modify_fb_messanger_profile(profile_payload):
    request_endpoint = 'https://graph.facebook.com/v3.1/me/messenger_profile?&access_token={}'.format(sender_id,ACCESS_TOKEN)
    response = requests.post(
        request_endpoint,
        json=payload
        )
    result = response.json()
    return result

if __name__ == "__main__":
    app.run()